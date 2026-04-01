---
description: "Install PyUnreal in Unreal Engine and run your first Python script. Setup guide for UE 5.4+ with pip install and Content/Python paths."
---

# Getting Started with PyUnreal

This guide walks you through installing PyUnreal and running your first script.

---

## Prerequisites

- Unreal Engine 5.4 or later
- [MCA Editor](https://mcaeditor.com) plugin installed (for AnimBP features)

---

## Installation

### Option 1: Copy to Project (Recommended)

1. Download or clone the PyUnreal repo
2. Copy the `pyunreal/` folder into your UE project's `Content/Python/` directory
3. Done -- UE will automatically add `Content/Python/` to the Python path

### Option 2: Add to Python Path

1. Place `pyunreal/` anywhere on disk
2. In UE: **Edit > Project Settings > Python > Additional Paths**
3. Add the parent directory of `pyunreal/`

### Option 3: sys.path (Quick Testing)

```python
import sys
sys.path.insert(0, 'E:/Projects/PyUnreal')

from pyunreal import load
```

---

## Your First Script

Open the UE Python console (**Window > Output Log**, switch to Python) or
MCA Editor, and run:

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

# Step 1: Load a skeleton asset from your project
skeleton = load('/Game/Characters/Mannequins/Meshes/SK_Mannequin')
print("Skeleton:", skeleton.get_name())

# Step 2: Create an AnimBP
abp = AnimBlueprint.create('/Game/Test', 'ABP_MyFirst', skeleton)
print("Created:", abp.name)

# Step 3: Add a state machine
loco = abp.add_state_machine('Locomotion')
print("State machine:", loco.name)

# Step 4: Add a state
idle = loco.add_state('Idle')
idle.set_default()
print("Default state: Idle")

# Step 5: Compile
abp.compile()
print("Compiled successfully!")
```

Check the Content Browser -- you should see `ABP_MyFirst` at `/Game/Test/`.
Double-click it to open the AnimBP editor and see the Locomotion state machine
with an Idle state.

---

## Adding Animations

To assign animations to states, first `load()` the animation asset, then pass
it to `add_state()` or `set_animation()`:

```python
idle_anim = load('/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle')
jog_anim  = load('/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd')

# Assign during creation (recommended)
idle = loco.add_state('Idle', animation=idle_anim, default=True)
jog  = loco.add_state('Jog',  animation=jog_anim)

# Or assign after creation
jump = loco.add_state('Jump')
jump.set_animation(load('/Game/Anims/Jump'))
```

---

## Wiring Transitions

Connect states with `transition_to()`:

```python
# Bidirectional: Idle <-> Jog
idle.transition_to(jog, crossfade=0.2)
jog.transition_to(idle, crossfade=0.2)

# One-way with fast blend
jog.transition_to(jump, crossfade=0.1)
```

For automatic transitions based on animation time remaining:

```python
# Jump automatically transitions to Idle when < 0.1s remaining
jump.auto_transition_to(idle, trigger_time=0.1)
```

---

## Loading Existing AnimBPs

To work with an AnimBP that already exists:

```python
abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')

# Inspect it
print("Name:", abp.name)
print("State machines:", [sm.name for sm in abp.state_machines])

for sm in abp.state_machines:
    print("  States in {}:".format(sm.name), [s.name for s in sm.states])
```

---

## Error Handling

PyUnreal raises clear exceptions when things go wrong:

```python
from pyunreal.core.errors import AssetNotFoundError, InvalidOperationError

try:
    skeleton = load('/Game/DoesNotExist')
except AssetNotFoundError as e:
    print("Bad path:", e.asset_path)

try:
    loco.add_state('Idle')  # Already exists
except InvalidOperationError as e:
    print("Failed:", e)
```

---

## Next Steps

- [AnimBP Cookbook](animbp-cookbook.md) -- Common recipes and patterns
- [API Reference](../api/AnimBlueprint.md) -- Full method documentation
