---
description: "Material API reference — create, load, and assign Unreal Engine materials with Python. Set parameters on material instances."
---

# Material

Pythonic wrapper around a UE Material or MaterialInstance asset.

## Import

```python
from pyunreal.material import Material
```

## Class Methods

### Material.create(name, package_path='/Game/Materials')

Create a new Material asset in the Content Browser.

```python
mat = Material.create('M_Metal')
mat = Material.create('M_Glowing', package_path='/Game/FX/Materials')
```

**Parameters:**
- `name` *(str)* -- Asset name
- `package_path` *(str)* -- Content Browser folder (default `'/Game/Materials'`)

**Raises:** `InvalidOperationError` if creation fails or asset already exists.

### Material.load(asset_path)

Load an existing Material from the Content Browser.

```python
mat = Material.load('/Game/Materials/M_Metal')
```

**Parameters:**
- `asset_path` *(str)* -- Full content path

**Raises:** `AssetNotFoundError` if the asset does not exist.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Asset name (read-only) |
| `path` | str | Full Content Browser path (read-only) |

## Methods

### set_param(param_name, value)

Set a material parameter. Accepts scalar values (float/int) or color tuples.

```python
mat.set_param('Roughness', 0.2)
mat.set_param('BaseColor', (0.8, 0.1, 0.0, 1.0))
mat.set_param('Metallic', 1)
```

Color tuples can be `(r, g, b)` or `(r, g, b, a)` in 0-1 range. Alpha defaults to 1.0.

Returns `self` for method chaining.

### get_param(param_name)

Read a material parameter value.

```python
roughness = mat.get_param('Roughness')
```

### assign_to(actor_or_name, slot=0)

Assign this material to an actor's mesh component.

```python
mat.assign_to('Chair_01')
mat.assign_to('Table_01', slot=2)
```

Finds the first `StaticMeshComponent` (or any `MeshComponent`) on the actor. Accepts Actor wrappers, UE actors, or label strings.

Returns `self` for method chaining.

## Example

```python
from pyunreal.material import Material

mat = Material.create('M_Gold')
mat.set_param('BaseColor', (1.0, 0.84, 0.0, 1.0))
mat.set_param('Metallic', 1.0)
mat.set_param('Roughness', 0.15)
mat.assign_to('Trophy_01')
```
