# viewport (module)

Module-level functions for controlling the Unreal Editor viewport.

## Import

```python
from pyunreal.viewport import viewport
```

## Functions

### viewport.focus(actor_or_name)

Focus the viewport on an actor. Pilots the active level-editor viewport to frame the given actor.

```python
viewport.focus('Chair_01')
viewport.focus(some_actor_wrapper)
```

**Raises:** `AssetNotFoundError` if the actor cannot be found.

### viewport.set_camera(location=None, rotation=None)

Set the viewport camera position and/or rotation.

```python
viewport.set_camera(location=(0, 0, 500), rotation=(0, -90, 0))
viewport.set_camera(location=(1000, 0, 200))
viewport.set_camera(rotation=(0, 45, 0))
```

- `location` -- `(x, y, z)` in world units, or None
- `rotation` -- `(pitch, yaw, roll)` in degrees, or None

### viewport.get_camera()

Get the current viewport camera position and rotation.

```python
cam = viewport.get_camera()
print(cam['location'])   # (x, y, z)
print(cam['rotation'])   # (pitch, yaw, roll)
```

**Returns:** Dictionary with `'location'` and `'rotation'` tuples.

### viewport.screenshot(output_path, width=1920, height=1080)

Capture a high-resolution screenshot of the active viewport.

```python
viewport.screenshot('C:/Shots/hero.png')
viewport.screenshot('C:/Shots/4k.png', width=3840, height=2160)
```

**Parameters:**
- `output_path` *(str)* -- File path for the saved PNG
- `width` *(int)* -- Image width in pixels (default 1920)
- `height` *(int)* -- Image height in pixels (default 1080)
