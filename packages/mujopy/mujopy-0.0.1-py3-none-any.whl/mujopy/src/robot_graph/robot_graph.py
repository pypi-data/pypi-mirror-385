import networkx as nx
from pathlib import Path
import numpy as np
import yaml
from typing import Tuple

from mujopy.src.mujopy_model.mujopy_model import MuJoPyModel
from mujopy.src.mujopy_model.body import Body
from mujopy.src.mujopy_model.joint import Joint
from mujopy.src.mujopy_model.geom import Geom

from .feature_processor import FeatureProcessor


class NoValidGraphException(Exception):
    def __init__(self, message="Graph is not a valid tree structure"):
        self.message = message
        super().__init__(self.message)


class RobotGraph(nx.DiGraph):
    """
    Directed graph representation of a MuJoCo model's hierarchy and
    the features of bodies and joints.
    """

    def __init__(self, xml_path: Path, feature_config_path: Path):
        super().__init__()

        # Build mujoco model from xml
        self.mujopy_model = MuJoPyModel(xml_path=xml_path)
        self.mujopy_model.register_default_properties()
        with open(feature_config_path, "r") as file:
            self._feature_config = yaml.safe_load(file)
        self.feature_processor = FeatureProcessor()

        # Build namespaces for joints and bodies
        self.joint_namespace = {
            joint.id: f"joint_{joint.name}" for joint in self.mujopy_model.joints
        }
        self.body_namespace = {
            body.id: f"body_{body.name}" for body in self.mujopy_model.bodies
        }

        # Build graph and store feature matrix
        self._build_graph()
        self.BODY_DIM, self.JOINT_DIM = self._build_features()
        self._feature_matrix = self._build_feature_matrix()

    def _build_graph(self) -> None:
        """
        Builds the graph.
        """

        # Add nodes
        for body in self.mujopy_model.bodies:
            self.add_node(
                self.body_namespace[body.id],
                name=body.name,
                type="body",
                mujopy_model_object=body,
            )

        for joint in self.mujopy_model.joints:
            self.add_node(
                self.joint_namespace[joint.id],
                name=joint.name,
                type="joint",
                mujopy_model_object=joint,
            )

        # Add edges
        for parent in self.mujopy_model.bodies:
            parent_node = self.body_namespace[parent.id]
            for child in parent.children:
                child_node = self.body_namespace[child.id]
                for joint in child.joints:
                    joint_node = self.joint_namespace[joint.id]
                    self.add_edge(parent_node, joint_node)
                    self.add_edge(joint_node, child_node)

        return self

    def _build_features(self) -> Tuple[int, int]:

        for _, data in self.nodes(data=True):
            mujopy_model_object = data["mujopy_model_object"]

            feature_vector = None

            if isinstance(mujopy_model_object, Body):
                feature_vector = self._extract_body_features(mujopy_model_object)
            elif isinstance(mujopy_model_object, Joint):
                feature_vector = self._extract_joint_features(mujopy_model_object)
            else:
                raise Exception("Unsupported object.")

            data["feature_vector"] = feature_vector

        # Check shapes
        return self._check_feature_shapes()

    def _check_feature_shapes(self) -> Tuple[int, int]:
        body_dim: int | None = None
        joint_dim: int | None = None

        for node, data in self.nodes(data=True):
            feature_vector = data.get("feature_vector")
            if feature_vector is None:
                raise ValueError(f"{node!r} has no feature_vector")

            length = len(feature_vector)
            node_type = data.get("type")

            if node_type == "body":
                if body_dim is None:
                    body_dim = length
                elif length != body_dim:
                    raise ValueError(
                        f"Body node {node!r} has length {length}, expected {body_dim}"
                    )
            elif node_type == "joint":
                if joint_dim is None:
                    joint_dim = length
                elif length != joint_dim:
                    raise ValueError(
                        f"Joint node {node!r} has length {length}, expected {joint_dim}"
                    )
            else:
                raise ValueError(f"Unknown node type {node_type!r} on {node!r}")

        return (body_dim or 0, joint_dim or 0)

    def _extract_joint_features(self, joint_object: Joint) -> np.array:
        requested_features = self._feature_config["joint_features"]
        joint_features = self._extract_feature(
            requested_features=requested_features, mujopy_model_object=joint_object
        )
        return np.concatenate(joint_features, dtype=np.float32)

    def _extract_body_features(self, body_object: Body) -> np.array:

        # Collect body and inertial features
        requested_features_body = (
            list(self._feature_config["body_features"])
            + self._feature_config["inertial_features"]
        )
        body_inertial_features = self._extract_feature(
            requested_features_body, body_object
        )

        # Collect features of primitive geoms
        requested_features_geoms = self._feature_config["geom_features"]
        primitive_geoms = [geom for geom in body_object.geoms if geom.is_primitive]
        if len(primitive_geoms) > 0:
            first_primitive_geom = primitive_geoms[0]
            geom_features = self._extract_feature(
                requested_features_geoms, first_primitive_geom
            )
        else:
            geom_features = [0]

        all_features = body_inertial_features + geom_features

        return np.concatenate(all_features, dtype=np.float32)

    def _extract_feature(
        self, requested_features, mujopy_model_object: Body | Joint | Geom
    ) -> list[np.float32]:

        pieces: list[np.ndarray] = []

        for entry in requested_features:
            raw = getattr(mujopy_model_object, entry["name"], None)
            processed = self.feature_processor.process(
                raw, entry.get("process", "identity")
            )
            pieces.append(np.atleast_1d(np.asarray(processed, dtype=np.float32)))
        return pieces

    def _build_feature_matrix(self) -> np.ndarray:
        rows: list[np.ndarray] = []

        # bodies first, in model order
        for body in self.mujopy_model.bodies:
            node = self.body_namespace[body.id]
            feats = self.nodes[node]["feature_vector"]
            row = np.concatenate(
                (
                    feats,
                    np.zeros(self.JOINT_DIM, dtype=np.float32),
                ),
                dtype=np.float32,
            )
            rows.append(row)

        # then joints
        for joint in self.mujopy_model.joints:
            node = self.joint_namespace[joint.id]
            feats = self.nodes[node]["feature_vector"]
            row = np.concatenate(
                (
                    np.zeros(self.BODY_DIM, dtype=np.float32),
                    feats,
                ),
                dtype=np.float32,
            )
            rows.append(row)

        return np.stack(rows, axis=0, dtype=np.float32)

    @property
    def feature_matrix(self):
        return self._feature_matrix
