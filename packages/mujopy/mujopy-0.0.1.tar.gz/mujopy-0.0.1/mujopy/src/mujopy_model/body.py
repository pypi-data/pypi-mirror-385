from __future__ import annotations
from typing import List, TYPE_CHECKING
from .utils import MuJoPyModelItem

if TYPE_CHECKING:
    from mujopy.src.mujopy_model import MuJoPyModel, Joint, Geom
    from mujoco._structs import MjModelBody


class Body(MuJoPyModelItem):
    def __init__(
        self, mujopy_model: MuJoPyModel, body_id: int, mujoco_view: MjModelBody
    ) -> None:
        super().__init__(mujoco_view=mujoco_view)
        self.mujopy_model = mujopy_model
        self.id = body_id

    def __repr__(self) -> str:
        raw_name = self.mujoco_view.name
        name = raw_name if raw_name and raw_name.strip() else "notset"
        return f"<Body id={self.id}, name={name}>"

    @property
    def children(self) -> List[Body]:
        """Direct child bodies of this body in MuJoCo model order."""
        return [
            self.mujopy_model.body(child_id)
            for child_id in self.mujopy_model._children_by_parent.get(self.id, [])
        ]

    @property
    def joints(self) -> List[Joint]:
        """Joints that connect this body to its children."""
        return [
            self.mujopy_model.joint(joint_id)
            for joint_id in self.mujopy_model._joints_by_body.get(self.id, [])
        ]

    @property
    def geoms(self) -> List[Geom]:
        """Geometric primitives attached to this body."""
        return [
            self.mujopy_model.geom(geom_id)
            for geom_id in self.mujopy_model._geoms_by_body.get(self.id, [])
        ]
