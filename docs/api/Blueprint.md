---
description: "Blueprint API reference — create, load, and manage Unreal Engine Blueprints with Python. Add components, variables, and set defaults."
---

# Blueprint

Wraps a `UBlueprint` asset for creating and managing Blueprints.

## Import

```python
from pyunreal.blueprint import Blueprint
```

## Creating a Blueprint

```python
bp = Blueprint.create('/Game/Blueprints', 'BP_Pickup', parent='Actor')
```

**Parameters:**

- `package_path` (str) -- Content Browser folder
- `asset_name` (str) -- Name for the new Blueprint
- `parent` (str) -- Parent class name (default `'Actor'`)

## Loading an Existing Blueprint

```python
bp = Blueprint.load('/Game/Blueprints/BP_Pickup')
```

## Finding Blueprints

```python
paths = Blueprint.find('/Game/Blueprints', class_filter='Actor', name_filter='Pickup')
for path in paths:
    bp = Blueprint.load(path)
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Asset name |
| `path` | str | Full Content Browser path |
| `parent_class` | str | Parent class name |
| `components` | list[Component] | Component hierarchy |
| `variables` | list[Variable] | User-defined variables |
| `functions` | list[str] | Function graph names |
| `events` | list[str] | Event names |

## Methods

### add_component(component_class, name=None, parent=None)

Add a component to the Blueprint.

```python
mesh = bp.add_component('StaticMeshComponent', name='PickupMesh')
trigger = bp.add_component('SphereComponent', name='Trigger', parent='PickupMesh')
```

### add_variable(name, var_type, default=None, category='')

Add a variable. Type can be friendly (`'int'`, `'bool'`, `'float'`, `'str'`)
or UE property type (`'IntProperty'`, etc.).

```python
bp.add_variable('PointValue', 'int', default=10, category='Gameplay')
bp.add_variable('IsActive', 'bool', default=True)
```

### set_default(property_name, value) / get_default(property_name)

Access Class Default Object properties.

```python
bp.set_default('MaxHealth', 100)
health = bp.get_default('MaxHealth')
```

### compile()

Compile the Blueprint. Call after all modifications.

```python
bp.compile()
```

## Related Classes

- [Component](Component.md) -- read-only component data
- [Variable](Variable.md) -- variable with read/write defaults
