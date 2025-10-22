from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from .utils import MuJoPyModelItem

if TYPE_CHECKING:
    from mujopy.src.mujopy_model import MuJoPyModel
    from mujopy.src.mujopy_model.body import Body
    from mujoco._structs import MjModelGeom


class Geom(MuJoPyModelItem):
    def __init__(
        self,
        mujopy_model: MuJoPyModel,
        geom_id: int,
        mujoco_view: MjModelGeom,
    ) -> None:

        super().__init__(mujoco_view=mujoco_view)
        self.id = geom_id
        self.mujopy_model = mujopy_model

    def __repr__(self) -> str:
        raw_name = self.mujoco_view.name
        name = raw_name if raw_name and raw_name.strip() else "notset"
        return f"<Geom id={self.id}, name={name}>"

    @property
    def body(self) -> Body:
        """Body of the MuJoCo model that geom is attached to."""
        body_id = int(np.asarray(self.mujoco_view.bodyid).item())
        return self.mujopy_model.body(body_id)
