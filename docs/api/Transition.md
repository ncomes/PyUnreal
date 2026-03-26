# Transition

```python
from pyunreal.anim import Transition
```

Represents a directional transition between two states in an AnimBP state
machine.  Transitions are lightweight, name-based references -- they identify
the edge by its source state, destination state, and parent state machine.

Transition instances are returned by
[`State.transition_to()`](State.md#transition_to) and
[`State.auto_transition_to()`](State.md#auto_transition_to).

**Requires:** MCA Editor plugin.

---

## Properties

All properties are read-only.

| Property | Type | Description |
|----------|------|-------------|
| `from_state` | `str` | Name of the source state |
| `to_state` | `str` | Name of the destination state |
| `crossfade` | `float` | Crossfade duration in seconds |
| `state_machine` | `StateMachine` | The parent state machine |

```python
t = idle.transition_to(walk, crossfade=0.2)
print(t.from_state)     # 'Idle'
print(t.to_state)       # 'Walk'
print(t.crossfade)      # 0.2
print(t.state_machine)  # <StateMachine 'Locomotion'>
```

---

## Methods

### set_auto_rule()

```python
transition.set_auto_rule(trigger_time=0.0)
```

Set an automatic transition rule based on remaining animation time.  When the
source state's animation has less than `trigger_time` seconds remaining, the
transition fires automatically.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `trigger_time` | `float` | `0.0` | Seconds of remaining time to trigger at |

**Returns:** `self` (for method chaining).

**Raises:** `InvalidOperationError` if the operation fails.

```python
# Create transition, then add auto rule
t = idle.transition_to(walk, crossfade=0.2)
t.set_auto_rule(trigger_time=0.5)

# Method chaining
idle.transition_to(walk, crossfade=0.2).set_auto_rule(trigger_time=0.5)
```

---

## String Representation

```python
t = idle.transition_to(walk, crossfade=0.2)
print(repr(t))  # <Transition Idle -> Walk (crossfade: 0.20s)>
```

---

## See Also

- [`State.transition_to()`](State.md#transition_to) -- creates transitions
- [`State.auto_transition_to()`](State.md#auto_transition_to) -- creates transitions with auto rules
