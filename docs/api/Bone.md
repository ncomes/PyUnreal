# Bone

Read-only snapshot of a skeleton bone in a Control Rig hierarchy.

## Import

```python
from pyunreal.control_rig import Bone
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Bone name |
| `parent` | str | Parent element name |
| `transform` | dict | Initial global transform |

Bones come from the skeleton and cannot be added or modified through
the Control Rig API.

## Usage

```python
rig = ControlRig.load('/Game/Rigs/CR_Character')
for bone in rig.bones:
    loc = bone.transform['location']
    print(f"{bone.name}: ({loc['x']}, {loc['y']}, {loc['z']})")
```
