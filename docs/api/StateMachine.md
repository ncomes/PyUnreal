# StateMachine

```python
from pyunreal.anim import StateMachine
```

Represents a state machine inside an AnimBP's AnimGraph.  A StateMachine is a
name-based reference -- it stores its name and a back-reference to its parent
`AnimBlueprint`, then passes both to the C++ API for every operation.

StateMachine instances are returned by
[`AnimBlueprint.add_state_machine()`](AnimBlueprint.md#add_state_machine) and
the [`AnimBlueprint.state_machines`](AnimBlueprint.md#properties) property.

**Requires:** MCA Editor plugin.

---

## Properties

All properties are read-only.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | The state machine name |
| `anim_blueprint` | `AnimBlueprint` | The parent AnimBlueprint |
| `states` | `list[State]` | All states in this machine (queries live state) |

```python
loco = abp.add_state_machine('Locomotion')
print(loco.name)           # 'Locomotion'
print(loco.anim_blueprint) # <AnimBlueprint 'ABP_Character'>

for state in loco.states:
    print(state.name)      # 'Idle', 'Walk', etc.
```

---

## Methods

### add_state()

```python
sm.add_state(name, animation=None, default=False)
```

Add a new state to this state machine.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | | Name for the new state |
| `animation` | `unreal.AnimSequenceBase` | `None` | Animation to assign (from `load()`) |
| `default` | `bool` | `False` | Make this the entry state |

**Returns:** [`State`](State.md) instance.

**Raises:** `InvalidOperationError` if a state with this name already exists.

The `animation` and `default` parameters are convenience shortcuts.  These
two calls are equivalent:

```python
# Shorthand (recommended)
idle = loco.add_state('Idle', animation=idle_anim, default=True)

# Longhand (explicit)
idle = loco.add_state('Idle')
idle.set_animation(idle_anim)
idle.set_default()
```

### Examples

```python
# Simple state
idle = loco.add_state('Idle')

# State with animation
walk = loco.add_state('Walk', animation=load('/Game/Anims/Walk'))

# Default state with animation (the entry point)
idle = loco.add_state('Idle', animation=load('/Game/Anims/Idle'), default=True)

# Chain: add states, then wire transitions
idle = loco.add_state('Idle', animation=idle_anim, default=True)
walk = loco.add_state('Walk', animation=walk_anim)
run  = loco.add_state('Run',  animation=run_anim)

idle.transition_to(walk, crossfade=0.2)
walk.transition_to(run,  crossfade=0.15)
```

---

## String Representation

```python
print(repr(loco))  # <StateMachine 'Locomotion'>
```

---

## See Also

- [`AnimBlueprint`](AnimBlueprint.md) -- parent class
- [`State`](State.md) -- returned by `add_state()`
