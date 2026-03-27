# Control

An animation control in a Control Rig hierarchy.

## Import

```python
from pyunreal.control_rig import Control
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Control name |
| `parent` | str | Parent element name |
| `transform` | dict | Initial global transform `{location, rotation, scale}` |
| `rig` | ControlRig | Parent rig |

## Methods

### set_transform(location=None, rotation=None, scale=None)

Set the initial global transform. Pass only what you want to change.

```python
ctrl.set_transform(location=(0, 0, 100))
ctrl.set_transform(rotation=(0, 45, 0))
ctrl.set_transform(location=(10, 0, 50), scale=(2, 2, 2))
```

Accepts tuples `(x, y, z)` or dicts `{'x': 0, 'y': 0, 'z': 0}`.

### set_shape(shape_name, color=None)

Set the control's visual shape and color.

```python
ctrl.set_shape('Box', color='yellow')
ctrl.set_shape('Circle', color=(0.5, 0.8, 1.0))
```
