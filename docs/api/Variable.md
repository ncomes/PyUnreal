# Variable

Wraps a user-defined Blueprint variable with read/write default access.

## Import

```python
from pyunreal.blueprint import Variable
```

## Accessing Variables

Variables are returned by `Blueprint.variables` or `Blueprint.add_variable()`:

```python
bp = Blueprint.load('/Game/Blueprints/BP_Pickup')
for var in bp.variables:
    print(var.name, var.var_type, var.default)
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Variable name |
| `var_type` | str | UE property type (e.g. `'IntProperty'`) |
| `default` | varies | Current default value |
| `blueprint` | Blueprint | Parent Blueprint |

## Methods

### set(value)

Set the default value on the Blueprint's Class Default Object.

```python
score_var = bp.add_variable('Score', 'int', default=0)
score_var.set(100)
```

## Type Mapping

When creating variables, you can use friendly type names:

| Friendly | UE Property Type |
|----------|-----------------|
| `'int'` | `IntProperty` |
| `'bool'` | `BoolProperty` |
| `'float'` | `FloatProperty` |
| `'double'` | `DoubleProperty` |
| `'str'` / `'string'` | `StrProperty` |
| `'name'` | `NameProperty` |
| `'text'` | `TextProperty` |
