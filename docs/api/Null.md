# Null

A space/group element in a Control Rig hierarchy.

## Import

```python
from pyunreal.control_rig import Null
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Null name |
| `parent` | str | Parent element name |
| `transform` | dict | Initial global transform |

Nulls are created by `ControlRig.add_null()` or discovered via
`ControlRig.nulls`.
