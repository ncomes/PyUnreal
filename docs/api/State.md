# State

```python
from pyunreal.anim import State
```

Represents a single state node inside an AnimBP state machine.  Like
`StateMachine`, this is a name-based reference -- it stores its name and a
reference to its parent state machine.

State instances are returned by
[`StateMachine.add_state()`](StateMachine.md#add_state) and the
[`StateMachine.states`](StateMachine.md#properties) property.

**Requires:** MCA Editor plugin.

---

## Properties

All properties are read-only.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | The state name |
| `state_machine` | `StateMachine` | The parent state machine |
| `anim_blueprint` | `AnimBlueprint` | The AnimBlueprint (shortcut through parent chain) |

```python
idle = loco.add_state('Idle')
print(idle.name)            # 'Idle'
print(idle.state_machine)   # <StateMachine 'Locomotion'>
print(idle.anim_blueprint)  # <AnimBlueprint 'ABP_Character'>
```

---

## Methods

### set_animation()

```python
state.set_animation(anim_asset)
```

Set the animation played by this state.

| Parameter | Type | Description |
|-----------|------|-------------|
| `anim_asset` | `unreal.AnimSequenceBase` | Animation asset (from `load()`) |

**Returns:** `self` (for method chaining).

**Raises:** `InvalidOperationError` if the operation fails.

```python
idle = loco.add_state('Idle')
idle.set_animation(load('/Game/Anims/Idle'))

# Method chaining
idle = loco.add_state('Idle').set_animation(idle_anim).set_default()
```

---

### set_default()

```python
state.set_default()
```

Make this state the default (entry) state of its state machine.  Wires the
state machine's entry node to point at this state.

**Returns:** `self` (for method chaining).

**Raises:** `InvalidOperationError` if the operation fails.

```python
idle = loco.add_state('Idle')
idle.set_default()  # Entry arrow now points to Idle
```

---

### transition_to()

```python
state.transition_to(target, crossfade=0.2)
```

Create a transition from this state to a target state.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | `State` or `str` | | Destination state |
| `crossfade` | `float` | `0.2` | Crossfade blend duration in seconds |

**Returns:** [`Transition`](Transition.md) instance.

**Raises:**
- `InvalidOperationError` if the C++ call fails.
- `ValueError` if `target` is a `State` from a different state machine.

The `target` parameter accepts either a `State` instance or a string name:

```python
# Using State instance (recommended -- validates same state machine)
idle.transition_to(walk, crossfade=0.2)

# Using string name
idle.transition_to('Walk', crossfade=0.2)
```

### Full Example

```python
idle = loco.add_state('Idle', animation=idle_anim, default=True)
walk = loco.add_state('Walk', animation=walk_anim)
run  = loco.add_state('Run',  animation=run_anim)

# Bidirectional transitions
idle.transition_to(walk, crossfade=0.2)
walk.transition_to(idle, crossfade=0.2)

# Walk <-> Run with faster blend
walk.transition_to(run,  crossfade=0.15)
run.transition_to(walk,  crossfade=0.15)
```

---

### auto_transition_to()

```python
state.auto_transition_to(target, trigger_time=0.0, crossfade=0.2)
```

Create a transition with an automatic time-remaining trigger.  When this
state's animation has less than `trigger_time` seconds remaining, the
transition fires automatically.

If no transition to the target exists yet, one is created first.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | `State` or `str` | | Destination state |
| `trigger_time` | `float` | `0.0` | Seconds of remaining time to trigger at |
| `crossfade` | `float` | `0.2` | Crossfade duration (if creating new transition) |

**Returns:** [`Transition`](Transition.md) instance with the auto rule applied.

**Raises:** `InvalidOperationError` if the operation fails.

```python
# Auto-transition from Jump to Idle when Jump has < 0.1s remaining
jump.auto_transition_to(idle, trigger_time=0.1)

# Can also be called on transitions that already exist
idle.transition_to(walk, crossfade=0.2)
idle.auto_transition_to(walk, trigger_time=0.5)  # Adds rule to existing transition
```

---

## String Representation

```python
print(repr(idle))  # <State 'Idle' in Locomotion>
```

---

## See Also

- [`StateMachine`](StateMachine.md) -- parent class
- [`Transition`](Transition.md) -- returned by `transition_to()`
