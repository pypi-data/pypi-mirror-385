from __future__ import annotations

from typing import Callable, Any

import mujoco
import numpy as np

from mujopy.src.mujopy_model.body import Body
from mujopy.src.mujopy_model.joint import Joint
from mujopy.src.mujopy_model.geom import Geom


_PRIMITIVE_GEOM_TYPES = {
    mujoco.mjtGeom.mjGEOM_SPHERE,
    mujoco.mjtGeom.mjGEOM_CAPSULE,
    mujoco.mjtGeom.mjGEOM_ELLIPSOID,
    mujoco.mjtGeom.mjGEOM_CYLINDER,
    mujoco.mjtGeom.mjGEOM_BOX,
}


# --------------------------- body properties ---------------------------------
def _body_parent(body: Body) -> Body | None:
    """Return the parent body wrapper or `None` for the world body."""
    parent_id = int(body.mujoco_view.parentid)
    if parent_id < 0:
        return None
    return body.mujopy_model.body(parent_id)


def _body_is_root(body: Body) -> bool:
    """True if the body is the world body (parent id equals its own id)."""
    return int(body.mujoco_view.parentid) == body.id


def _body_children_ids(body: Body) -> list[int]:
    """MuJoCo ids of direct child bodies."""
    return list(body.mujopy_model._children_by_parent.get(body.id, []))


def _body_joint_ids(body: Body) -> list[int]:
    """MuJoCo joint ids that originate from this body."""
    return list(body.mujopy_model._joints_by_body.get(body.id, []))


def _body_primitive_geoms(body: Body) -> list[Geom]:
    """Geoms attached to this body whose type is one of the primitive shapes."""
    return [geom for geom in body.geoms if _geom_is_primitive(geom)]


_DEFAULT_BODY_PROPERTIES: list[tuple[str, Callable[[Body], Any]]] = [
    ("parent", _body_parent),
    ("is_root", _body_is_root),
    ("children_ids", _body_children_ids),
    ("joint_ids", _body_joint_ids),
    ("primitive_geoms", _body_primitive_geoms),
]


# --------------------------- joint properties --------------------------------


def _joint_type_name(joint: Joint) -> str:
    """Human-readable MuJoCo joint type name."""
    joint_type = mujoco.mjtJoint(int(joint.mujoco_view.type))
    return joint_type.name


_DEFAULT_JOINT_PROPERTIES: list[tuple[str, Callable[[Joint], Any]]] = [
    ("type_name", _joint_type_name),
]


# --------------------------- geom properties ---------------------------------


def _geom_type_enum(geom: Geom) -> mujoco.mjtGeom:
    """MuJoCo enumeration for the geom type."""
    return mujoco.mjtGeom(int(np.asarray(geom.mujoco_view.type).item()))


def _geom_type_name(geom: Geom) -> str:
    """Human-readable geom type name."""
    return _geom_type_enum(geom).name


def _geom_is_primitive(geom: Geom) -> bool:
    """True when the geom type is among MuJoCo's primitive shapes."""
    return _geom_type_enum(geom) in _PRIMITIVE_GEOM_TYPES


def _geom_size(geom: Geom) -> np.ndarray:
    """Size vector of the geom as a float64 numpy array."""
    return np.asarray(geom.mujoco_view.size, dtype=np.float64)


def _geom_color(geom: Geom) -> np.ndarray:
    """RGBA color assigned to the geom."""
    model = geom.mujopy_model._mujoco_model
    return np.asarray(model.geom_rgba[geom.id], dtype=np.float64)


def _geom_friction(geom: Geom) -> np.ndarray:
    """Friction tuple for the geom."""
    model = geom.mujopy_model._mujoco_model
    return np.asarray(model.geom_friction[geom.id], dtype=np.float64)


def _geom_density(geom: Geom) -> float:
    """Density value assigned to the geom."""
    model = geom.mujopy_model._mujoco_model
    return float(model.geom_density[geom.id])


def _geom_mesh_name(geom: Geom) -> str | None:
    """Mesh asset name if the geom references a mesh, otherwise `None`."""
    if not _geom_is_mesh(geom):
        return None
    model = geom.mujopy_model._mujoco_model
    mesh_id = int(geom.mujoco_view.dataid)
    try:
        name = model.mesh_id2name(mesh_id)
    except AttributeError:
        return None
    return name


def _geom_is_mesh(geom: Geom) -> bool:
    """True when the geom is backed by a mesh asset."""
    return _geom_type_enum(geom) == mujoco.mjtGeom.mjGEOM_MESH


def _geom_bounding_sphere_radius(geom: Geom) -> float:
    """Radius of a bounding sphere that encloses the geom."""
    size = _geom_size(geom)
    geom_type = _geom_type_enum(geom)
    if geom_type == mujoco.mjtGeom.mjGEOM_SPHERE:
        return float(size[0])
    if geom_type == mujoco.mjtGeom.mjGEOM_BOX:
        return float(np.linalg.norm(size))
    if geom_type == mujoco.mjtGeom.mjGEOM_CYLINDER:
        radius = float(size[0])
        half_height = float(size[1])
        return float(np.sqrt(radius**2 + half_height**2))
    return float(np.linalg.norm(size))


_DEFAULT_GEOM_PROPERTIES: list[tuple[str, Callable[[Geom], Any]]] = [
    ("type_name", _geom_type_name),
    ("is_primitive", _geom_is_primitive),
    ("size_vec", _geom_size),
    ("color", _geom_color),
    ("friction", _geom_friction),
    ("density", _geom_density),
    ("mesh_name", _geom_mesh_name),
    ("bounding_sphere_radius", _geom_bounding_sphere_radius),
]


__all__ = [
    "_DEFAULT_BODY_PROPERTIES",
    "_DEFAULT_JOINT_PROPERTIES",
    "_DEFAULT_GEOM_PROPERTIES",
]
