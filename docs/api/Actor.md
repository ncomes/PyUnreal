---
description: "Actor API reference — spawn, transform, and manipulate Unreal Engine level actors with Python. Pythonic property access and component queries."
---

# Actor

Wraps a UE level actor with Pythonic property access and transform manipulation.

## Import

```python
from pyunreal.scene import Actor
```

## Spawning Actors

```python
light = Actor.spawn('PointLight', name='MyLight', location=(200, 0, 300))
cube = Actor.spawn('StaticMeshActor', name='Cube_01',
                   location=(0, 0, 50), rotation=(0, 45, 0), scale=(2, 2, 2))
```

## Properties (read-write)

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Actor label in World Outliner |
| `location` | tuple | World location `(x, y, z)` |
| `rotation` | tuple | World rotation `(pitch, yaw, roll)` |
| `scale` | tuple | World scale `(x, y, z)` |

Set properties with tuples or dicts:

```python
actor.location = (100, 200, 0)
actor.rotation = {'pitch': 0, 'yaw': 45, 'roll': 0}
```

## Properties (read-only)

| Property | Type | Description |
|----------|------|-------------|
| `class_name` | str | UE class name |
| `hidden` | bool | Whether hidden in editor |

## Methods

### set_property(name, value) / get_property(name)

Access arbitrary editor properties.

```python
actor.set_property('bHidden', True)
value = actor.get_property('MaxDrawDistance')
```

### destroy()

Remove the actor from the level.

```python
actor.destroy()
# actor is now invalid
```
