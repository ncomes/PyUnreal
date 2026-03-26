# Exceptions

```python
from pyunreal.core.errors import PyUnrealError, AssetNotFoundError, ...
```

All PyUnreal exceptions inherit from `PyUnrealError`.  You can catch the base
class for broad handling or specific subclasses for targeted recovery.

---

## Exception Hierarchy

```
PyUnrealError
    PyUnrealEnvironmentError
    MCAScriptingNotAvailableError
    AssetNotFoundError
    InvalidOperationError
```

---

## PyUnrealError

Base exception for all PyUnreal errors.

```python
try:
    # Any PyUnreal operation
    abp = AnimBlueprint.create(...)
except PyUnrealError as e:
    print("PyUnreal error:", e)
```

---

## PyUnrealEnvironmentError

Raised when PyUnreal is used outside of Unreal Engine's Python interpreter.

The `unreal` module only exists inside UE's embedded Python.  If this fires,
you are running in standalone Python, Maya, or another host.

```python
# Running in standard Python (not UE):
from pyunreal import load
load('/Game/Something')
# Raises: PyUnrealEnvironmentError: This function requires Unreal Engine's
#         Python interpreter. The 'unreal' module is not available.
```

---

## MCAScriptingNotAvailableError

Raised when an operation requires the MCA Editor plugin but it is not loaded.

Includes the install URL in the error message.

```python
# UE running without MCA Editor plugin:
abp.add_state_machine('Locomotion')
# Raises: MCAScriptingNotAvailableError: 'AnimBlueprint.add_state_machine'
#         requires the MCA Editor plugin. Install from: https://mcaeditor.com
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `operation` | `str` | The operation that was attempted |

---

## AssetNotFoundError

Raised when an asset path resolves to `None` in the Content Browser.

```python
from pyunreal import load
try:
    load('/Game/DoesNotExist')
except AssetNotFoundError as e:
    print(e.asset_path)  # '/Game/DoesNotExist'
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `asset_path` | `str` | The path that was not found |

---

## InvalidOperationError

Raised when a PyUnreal operation fails logically.  Examples:

- Adding a duplicate state name
- Compiling a corrupt AnimBP
- Operating on a stale wrapper whose UE object was garbage collected
- Trying to create a transition between states in different state machines

```python
# Adding a duplicate state:
loco.add_state('Idle')
loco.add_state('Idle')
# Raises: InvalidOperationError: Failed to add state 'Idle' to state machine
#         'Locomotion'. A state with this name may already exist.
```
