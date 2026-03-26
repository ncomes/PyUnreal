# Utility Functions

Top-level convenience functions available from `pyunreal`.

```python
from pyunreal import load, asset_exists
```

---

## load()

```python
load(asset_path)
```

Load an asset from the Content Browser by path.

Wraps `unreal.EditorAssetLibrary.load_asset()` with validation.  Returns the
raw UE object -- pass it to PyUnreal class constructors or methods that accept
assets (like `State.set_animation()`).

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `asset_path` | `str` | Full content path (e.g. `'/Game/Characters/SK_Mannequin'`) |

### Returns

The loaded Unreal Engine asset object (`unreal.Object`).

### Raises

| Exception | When |
|-----------|------|
| `AssetNotFoundError` | No asset exists at the given path |
| `PyUnrealEnvironmentError` | Not running inside UE's Python interpreter |

### Examples

```python
from pyunreal import load

# Load a skeleton
skeleton = load('/Game/Characters/Mannequins/Meshes/SK_Mannequin')

# Load an animation
idle_anim = load('/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle')

# Load a mesh
mesh = load('/Game/Props/SM_Chair')

# Handles errors cleanly
try:
    asset = load('/Game/DoesNotExist')
except AssetNotFoundError as e:
    print(e)  # "Asset not found: '/Game/DoesNotExist'"
    print(e.asset_path)  # '/Game/DoesNotExist'
```

---

## asset_exists()

```python
asset_exists(asset_path)
```

Check whether an asset exists in the Content Browser without loading it.

Useful for conditional logic where you want to check before loading.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `asset_path` | `str` | Full content path to check |

### Returns

`bool` -- `True` if the asset exists.

### Examples

```python
from pyunreal import asset_exists

if asset_exists('/Game/AnimBP/ABP_Character'):
    print("AnimBP already exists, skipping creation")
else:
    # Create it
    abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)
```
