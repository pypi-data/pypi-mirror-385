# MuJoPy

## Table of Contents
- [Project Motivation](#project-motivation)
- [Installation](#installation)
- [File Descriptions](#file-descriptions)
- [Usage](#usage)
- [Licensing](#licensing)

## Project Motivation
MuJoPy provides pythonic access to MuJoCo models by wrapping the low-level structs of the model in dataclasses and by this deriving a navigable graph of bodies, joints and geoms. By this, downstream usage of robot models, e.g. feature extraction is faster without the need of custom parsing logic for the MuJoCo models.

With `RobotGraph()` the package also exposes an example of using the MuJoPy wrapper by providing a graph representation alongside of a feature matrix of the model.
## Installation
Install the package together with its MuJoCo dependency:

```bash
pip install mujopy
```

For development work inside this repository, install in editable mode with the testing extras:

```bash
pip install -e ".[test]"
```

## File Descriptions
- `mujopy/src/mujopy_model/`: Core wrappers (`Body`, `Joint`, `Geom`, `MuJoPyModel`) that expose MuJoCo fields as Python properties.
- `mujopy/src/robot_graph/`: Graph utilities built on top of NetworkX, including the `RobotGraph` and feature extraction pipeline.
- `tests/`: PyTest-based unit tests and fixtures covering the main APIs.
- `pyproject.toml`: Packaging metadata, dependencies, and tool configuration.

## Usage
```python
from pathlib import Path
from mujopy import MuJoPyModel, RobotGraph

# Load a MuJoCo XML and register the default property packs
model = MuJoPyModel(
    xml_path=str(Path("path/to/model.xml")),
    include_world_body=True,
    include_free_joints=False,
)
model.register_default_properties()

# Inspect bodies, joints, and geoms
trunk = model.body(0)
print(trunk.name, trunk.children_ids, trunk.primitive_geoms)

# Build a graph with feature vectors
graph = RobotGraph(
    xml_path=Path("path/to/model.xml"),
    feature_config_path=Path("path/to/feature_config.yml"),
)
print(graph.number_of_nodes(), graph.feature_matrix.shape)
```

Each wrapper exposes the underlying MuJoCo struct through the `mujoco_view` attribute—use it when you need direct access to raw MuJoCo fields:

```python
body_view = trunk.mujoco_view  # mujoco.MjDataView for the body
print(body_view.pos)
```

### Registering Custom Properties
Extend the core wrappers with your own read-only properties by registering callables on `MuJoPyModel`:

```python
from mujopy import MuJoPyModel

def _body_is_not_root(body: Body) -> bool:
        return int(np.asarray(body.mujoco_view.parentid).item()) != body.id

model = MuJoPyModel(xml_path="path/to/model.xml")
MuJoPyModel.register_body_property("_body_is_not_root", is_not_root)
model.register_default_properties()

print(model.body(0).is_not_root)
```

## Licensing
This project is distributed under the MIT License—see the license text in `pyproject.toml` for details.
