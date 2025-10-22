from __future__ import annotations
from typing import Callable, Any

import mujoco
import numpy as np

from mujopy.src.mujopy_model.body import Body
from mujopy.src.mujopy_model.joint import Joint
from mujopy.src.mujopy_model.geom import Geom
from mujopy.src.mujopy_model.property_packs import (
    _DEFAULT_BODY_PROPERTIES,
    _DEFAULT_JOINT_PROPERTIES,
    _DEFAULT_GEOM_PROPERTIES,
)


class MuJoPyModel:
    """Pythonic access to MuJoCo model topology (bodies, joints, geoms)."""

    def __init__(
        self,
        xml_path: str,
        *,
        include_world_body: bool = False,
        include_free_joints: bool = False,
    ) -> None:

        # Load MuJoCo model
        self.xml_path = xml_path
        self._mujoco_model = mujoco.MjModel.from_xml_path(self.xml_path)

        self._build_body_wrappers()
        self._build_joint_wrappers()
        self._build_geom_wrappers()

        self._build_model(
            include_world_body=include_world_body,
            include_free_joints=include_free_joints,
        )

    def __repr__(self) -> str:
        return (
            f"<MuJoPyModel wrapping the MuJoCo model defined in file {self.xml_path}>"
        )

    def _build_body_wrappers(self) -> None:
        self._body_wrappers = tuple(
            Body(self, body_id, self._mujoco_model.body(body_id))
            for body_id in range(self._mujoco_model.nbody)
        )

    def _build_joint_wrappers(self) -> None:
        self._joint_wrappers = tuple(
            Joint(self, joint_id, self._mujoco_model.joint(joint_id))
            for joint_id in range(self._mujoco_model.njnt)
        )

    def _build_geom_wrappers(self) -> None:
        self._geom_wrappers = tuple(
            Geom(self, geom_id, self._mujoco_model.geom(geom_id))
            for geom_id in range(self._mujoco_model.ngeom)
        )

    def _build_model(
        self, include_world_body: bool = False, include_free_joints: bool = False
    ) -> None:
        start_body_id = 0 if include_world_body else 1

        self._bodies = self._body_wrappers[start_body_id:]
        self._joints = tuple(
            joint
            for joint in self._joint_wrappers
            if (
                include_free_joints
                or self._mujoco_model.joint(joint.id).type != mujoco.mjtJoint.mjJNT_FREE
            )
        )
        self._geoms = self._geom_wrappers

        self._children_by_parent = {
            body_id: [] for body_id in range(self._mujoco_model.nbody)
        }
        self._joints_by_body = {
            body_id: [] for body_id in range(self._mujoco_model.nbody)
        }
        self._geoms_by_body = {
            body_id: [] for body_id in range(self._mujoco_model.nbody)
        }

        for body_id in range(1, self._mujoco_model.nbody):
            parent_id = int(
                np.asarray(self._mujoco_model.body(body_id).parentid).item()
            )
            if parent_id != -1:
                self._children_by_parent[parent_id].append(body_id)

        for joint_id in range(self._mujoco_model.njnt):
            if self._mujoco_model.joint(joint_id).type == mujoco.mjtJoint.mjJNT_FREE:
                continue
            body_id = int(np.asarray(self._mujoco_model.joint(joint_id).bodyid).item())
            self._joints_by_body[body_id].append(joint_id)

        for geom_id in range(self._mujoco_model.ngeom):
            body_id = int(np.asarray(self._mujoco_model.geom(geom_id).bodyid).item())
            self._geoms_by_body[body_id].append(geom_id)

    @staticmethod
    def register_body_property(name: str, fn: Callable[[Body], Any]) -> None:
        """Attach a custom read-only property to every body wrapper."""
        setattr(Body, name, property(fn))

    @staticmethod
    def register_joint_property(name: str, fn: Callable[[Joint], Any]) -> None:
        """Attach a custom read-only property to every joint wrapper."""
        setattr(Joint, name, property(fn))

    @staticmethod
    def register_geom_property(name: str, fn: Callable[[Geom], Any]) -> None:
        """Attach a custom read-only property to every geom wrapper."""
        setattr(Geom, name, property(fn))

    @staticmethod
    def register_default_properties() -> None:
        """Attach the built-in property packs to the core wrappers."""
        for name, fn in _DEFAULT_BODY_PROPERTIES:
            MuJoPyModel.register_body_property(name=name, fn=fn)

        for name, fn in _DEFAULT_JOINT_PROPERTIES:
            MuJoPyModel.register_joint_property(name=name, fn=fn)

        for name, fn in _DEFAULT_GEOM_PROPERTIES:
            MuJoPyModel.register_geom_property(name=name, fn=fn)

    def body(self, body_id: int) -> Body:
        """Return the `Body` wrapper with the given MuJoCo body id."""
        return self._body_wrappers[body_id]

    def joint(self, joint_id: int) -> Joint:
        """Return the `Joint` wrapper with the given MuJoCo joint id."""
        return self._joint_wrappers[joint_id]

    def geom(self, geom_id: int) -> Geom:
        """Return the `Geom` wrapper with the given MuJoCo geom id."""
        return self._geom_wrappers[geom_id]

    @property
    def bodies(self) -> tuple[Body, ...]:
        """Sequence of `Body` wrappers in model order (optionally including world)."""
        return self._bodies

    @property
    def joints(self) -> tuple[Joint, ...]:
        """Sequence of `Joint` wrappers in model order (optionally excluding free joints)."""
        return self._joints

    @property
    def geoms(self) -> tuple[Geom, ...]:
        """Sequence of `Geom` wrappers in model order."""
        return self._geoms
