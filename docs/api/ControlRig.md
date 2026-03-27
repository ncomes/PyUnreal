# ControlRig

Wraps a `UControlRigBlueprint` for inspecting and building rig hierarchies.

## Import

```python
from pyunreal.control_rig import ControlRig
```

## Loading a Control Rig

```python
rig = ControlRig.load('/Game/Rigs/CR_Character')
```

## Finding Control Rigs

```python
paths = ControlRig.find('/Game/Rigs')
for path in paths:
    rig = ControlRig.load(path)
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Asset name |
| `path` | str | Full Content Browser path |
| `controls` | list[Control] | All controls in the hierarchy |
| `bones` | list[Bone] | All bones (read-only, from skeleton) |
| `nulls` | list[Null] | All null/space/group elements |

## Methods

### add_control(name, parent=None, shape='Circle', color=None, location=None, rotation=None, scale=None)

Add a control to the hierarchy.

```python
hips = rig.add_control('Hips', parent='Root', shape='Box', color='yellow',
                        location=(0, 0, 100))
```

**Color presets:** `'red'`, `'green'`, `'blue'`, `'yellow'`, `'cyan'`,
`'magenta'`, `'white'`, `'orange'`, `'purple'`. Also accepts `(r, g, b)`
or `(r, g, b, a)` tuples (0-1 range).

### add_null(name, parent=None, location=None, rotation=None)

Add a null (space/group) to the hierarchy.

```python
root = rig.add_null('CustomControls')
```

### get_control(name)

Get an existing control by name.

```python
hips = rig.get_control('Hips')
hips.set_transform(location=(0, 0, 95))
```

## Related Classes

- [Control](Control.md) -- control with transform and shape access
- [Bone](Bone.md) -- read-only skeleton bone
- [Null](Null.md) -- space/group element
