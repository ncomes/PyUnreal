---
description: "Blueprint cookbook — Python recipes for creating Blueprints, adding components, setting variables, and batch setup in Unreal Engine."
---

# Blueprint Cookbook

Common recipes and patterns for Blueprint authoring with PyUnreal.

---

## Basic Actor Blueprint

Create a simple actor Blueprint with a mesh and collision component.

```python
from pyunreal import load
from pyunreal.blueprint import Blueprint

bp = Blueprint.create('/Game/Blueprints', 'BP_Pickup', parent='Actor')

# Add a static mesh as the root visual.
bp.add_component('StaticMeshComponent', name='PickupMesh')

# Add a sphere collision for overlap detection.
bp.add_component('SphereComponent', name='Trigger', parent='PickupMesh')

# Set defaults.
bp.set_default('PickupMesh.StaticMesh', load('/Game/Meshes/SM_Gem'))
bp.set_default('Trigger.SphereRadius', 150.0)

bp.compile()
```

---

## Variables with Defaults

Add typed variables to a Blueprint and set their default values.

```python
from pyunreal.blueprint import Blueprint

bp = Blueprint.load('/Game/Blueprints/BP_Pickup')

# Add gameplay variables.
bp.add_variable('PointValue', 'int', default=10)
bp.add_variable('IsCollected', 'bool', default=False)
bp.add_variable('DisplayName', 'str', default='Gem')
bp.add_variable('RespawnTime', 'float', default=5.0)

bp.compile()
```

Supported type names: `int`, `float`, `bool`, `str`, `name`, `text`, `byte`,
`vector`, `rotator`, `transform`, `color`. Any unrecognized name is passed
through as-is (e.g. `'IntProperty'`).

---

## Batch-Create Blueprints

Create multiple Blueprint variants in a loop.

```python
from pyunreal import load
from pyunreal.blueprint import Blueprint

PICKUPS = [
    {'name': 'BP_GoldCoin',   'mesh': '/Game/Meshes/SM_Coin_Gold',   'points': 50},
    {'name': 'BP_SilverCoin', 'mesh': '/Game/Meshes/SM_Coin_Silver', 'points': 25},
    {'name': 'BP_BronzeCoin', 'mesh': '/Game/Meshes/SM_Coin_Bronze', 'points': 10},
]

for info in PICKUPS:
    bp = Blueprint.create('/Game/Blueprints/Pickups', info['name'], parent='Actor')

    bp.add_component('StaticMeshComponent', name='Mesh')
    bp.add_component('SphereComponent', name='Trigger', parent='Mesh')

    bp.set_default('Mesh.StaticMesh', load(info['mesh']))
    bp.add_variable('PointValue', 'int', default=info['points'])

    bp.compile()
    print('Created:', info['name'])
```

---

## Introspection

Inspect an existing Blueprint's structure.

```python
from pyunreal.blueprint import Blueprint

bp = Blueprint.load('/Game/Blueprints/BP_Pickup')

# List components.
for comp in bp.components:
    print(f'  {comp.name} ({comp.component_class})')

# List variables.
for var in bp.variables:
    print(f'  {var.name}: {var.var_type} = {var.default}')

# List functions and events.
print('Functions:', bp.functions)
print('Events:', bp.events)
```

---

## Load vs Create

Use `load()` to open an existing Blueprint, `create()` to make a new one.
Use `find()` to search the asset registry.

```python
from pyunreal.blueprint import Blueprint

# Load by exact path.
bp = Blueprint.load('/Game/Blueprints/BP_Player')

# Create new -- raises if it already exists.
bp = Blueprint.create('/Game/Blueprints', 'BP_NewActor', parent='Actor')

# Search by name pattern.
results = Blueprint.find('BP_Pickup*')
for bp in results:
    print(bp.name, bp.path)
```

---

## Read/Write Defaults

Access the Class Default Object (CDO) to read and write property defaults.

```python
from pyunreal.blueprint import Blueprint

bp = Blueprint.load('/Game/Blueprints/BP_Pickup')

# Read a default.
current = bp.get_default('PointValue')
print('Current points:', current)

# Write a new default.
bp.set_default('PointValue', 100)
bp.compile()
```
