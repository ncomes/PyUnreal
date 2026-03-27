# Component

Read-only snapshot of a Blueprint SCS (SimpleConstructionScript) node.

## Import

```python
from pyunreal.blueprint import Component
```

## Accessing Components

Components are returned by `Blueprint.components`:

```python
bp = Blueprint.load('/Game/Blueprints/BP_Pickup')
for comp in bp.components:
    print(comp.name, comp.component_class, comp.parent)
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Component instance name |
| `component_class` | str | UE class name (e.g. `'StaticMeshComponent'`) |
| `parent` | str | Parent component name (empty for root) |
| `location` | dict or None | Relative location `{x, y, z}` |
| `rotation` | dict or None | Relative rotation `{pitch, yaw, roll}` |
| `scale` | dict or None | Relative scale `{x, y, z}` |
