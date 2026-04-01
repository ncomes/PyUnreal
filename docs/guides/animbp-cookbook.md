---
description: "AnimBP cookbook — Python recipes for creating locomotion state machines, blend spaces, transitions, and EventGraph wiring in Unreal Engine."
---

# AnimBP Cookbook

Common recipes and patterns for AnimBP authoring with PyUnreal.

---

## Basic Locomotion (Idle / Walk / Run)

The most common AnimBP pattern -- three states with bidirectional transitions.

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

skeleton = load('/Game/Characters/Meshes/SK_Mannequin')
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Locomotion', skeleton)

loco = abp.add_state_machine('Locomotion')

idle = loco.add_state('Idle', animation=load('/Game/Anims/Idle'), default=True)
walk = loco.add_state('Walk', animation=load('/Game/Anims/Walk'))
run  = loco.add_state('Run',  animation=load('/Game/Anims/Run'))

# Idle <-> Walk
idle.transition_to(walk, crossfade=0.2)
walk.transition_to(idle, crossfade=0.2)

# Walk <-> Run
walk.transition_to(run,  crossfade=0.15)
run.transition_to(walk,  crossfade=0.15)

abp.compile()
```

---

## Jump with Auto-Return

A jump state that automatically transitions back to idle when the animation
finishes.

```python
idle = loco.add_state('Idle', animation=idle_anim, default=True)
jump = loco.add_state('Jump', animation=jump_anim)

idle.transition_to(jump, crossfade=0.1)

# Auto-return: when Jump has < 0.1s remaining, blend back to Idle
jump.auto_transition_to(idle, trigger_time=0.1, crossfade=0.25)
```

---

## Batch Create from Data

Build state machines from a dictionary of state definitions.

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

# Define states as data
STATES = {
    'Idle':  {'anim': '/Game/Anims/Idle',  'default': True},
    'Walk':  {'anim': '/Game/Anims/Walk',  'default': False},
    'Run':   {'anim': '/Game/Anims/Run',   'default': False},
    'Jump':  {'anim': '/Game/Anims/Jump',  'default': False},
}

# Define transitions as (from, to, crossfade) tuples
TRANSITIONS = [
    ('Idle', 'Walk', 0.2),
    ('Walk', 'Idle', 0.2),
    ('Walk', 'Run',  0.15),
    ('Run',  'Walk', 0.15),
    ('Idle', 'Jump', 0.1),
]

# Auto-transitions as (from, to, trigger_time) tuples
AUTO_TRANSITIONS = [
    ('Jump', 'Idle', 0.1),
]

# Build it
skeleton = load('/Game/Characters/Meshes/SK_Mannequin')
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_DataDriven', skeleton)
loco = abp.add_state_machine('Locomotion')

# Create all states
state_map = {}
for name, config in STATES.items():
    state_map[name] = loco.add_state(
        name,
        animation=load(config['anim']),
        default=config['default']
    )

# Wire transitions
for from_name, to_name, crossfade in TRANSITIONS:
    state_map[from_name].transition_to(state_map[to_name], crossfade=crossfade)

# Wire auto-transitions
for from_name, to_name, trigger_time in AUTO_TRANSITIONS:
    state_map[from_name].auto_transition_to(state_map[to_name], trigger_time=trigger_time)

abp.compile()
print("Created {} states, {} transitions".format(len(STATES), len(TRANSITIONS)))
```

---

## Inspect an Existing AnimBP

Read the structure of an AnimBP without modifying it.

```python
from pyunreal.anim import AnimBlueprint

abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')

print("AnimBP: {}".format(abp.name))
print("Skeleton: {}".format(abp.skeleton.get_name()))
print()

for sm in abp.state_machines:
    print("State Machine: {}".format(sm.name))
    for state in sm.states:
        print("  State: {}".format(state.name))
```

---

## Multiple State Machines

An AnimBP can have multiple state machines for layered animation.

```python
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Layered', skeleton)

# Primary locomotion (wired to output)
loco = abp.add_state_machine('Locomotion', connect_to_root=True)
idle = loco.add_state('Idle', animation=idle_anim, default=True)
walk = loco.add_state('Walk', animation=walk_anim)
idle.transition_to(walk, crossfade=0.2)
walk.transition_to(idle, crossfade=0.2)

# Upper body overlay (NOT wired to output -- for manual blending)
upper = abp.add_state_machine('UpperBody', connect_to_root=False)
relaxed = upper.add_state('Relaxed', animation=relaxed_anim, default=True)
aiming  = upper.add_state('Aiming',  animation=aim_anim)
relaxed.transition_to(aiming, crossfade=0.15)
aiming.transition_to(relaxed, crossfade=0.15)

abp.compile()
```

---

## Tips

**Always compile last.**  Make all your state and transition changes first,
then call `compile()` once at the end.  Compiling after each change is
wasteful.

**Use `default=True` on exactly one state** per state machine.  This is the
state the machine starts in.  If you forget, the state machine will have no
entry point and compilation may warn.

**Crossfade values are in seconds.**  `0.2` = 200ms blend.  Use shorter
values (0.1-0.15) for snappy transitions (walk->run) and longer values
(0.25-0.5) for smooth ones (idle->walk).

**String names work for targets.**  `idle.transition_to('Walk')` works, but
using the State object (`idle.transition_to(walk)`) is safer because it
validates that both states are in the same state machine.
