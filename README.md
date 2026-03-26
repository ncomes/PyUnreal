# PyUnreal

Pythonic wrapper for Unreal Engine's Python API. **PyMEL for Unreal.**

UE's Python API exposes C++ function signatures directly -- verbose, static-library-based,
and hard to discover. PyUnreal wraps them in a clean, object-oriented, discoverable
Python interface built for Tech Artists.

## Quick Start

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

# Load assets
skeleton = load('/Game/Characters/SK_Mannequin')
idle_anim = load('/Game/Animations/Idle')
walk_anim = load('/Game/Animations/Walk')

# Create an AnimBP
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)

# Build a state machine
loco = abp.add_state_machine('Locomotion')
idle = loco.add_state('Idle', animation=idle_anim, default=True)
walk = loco.add_state('Walk', animation=walk_anim)

# Wire transitions
idle.transition_to(walk, crossfade=0.2)
walk.transition_to(idle, crossfade=0.2)

# Compile
abp.compile()
```

Compare that to the raw UE Python equivalent:

```python
import unreal
lib = unreal.MCAAnimBlueprintLibrary
skel = unreal.EditorAssetLibrary.load_asset('/Game/Characters/SK_Mannequin')
abp = lib.create_anim_blueprint('/Game/AnimBP', 'ABP_Character', skel)
lib.add_state_machine(abp, 'Locomotion', True)
lib.add_state(abp, 'Locomotion', 'Idle')
lib.add_state(abp, 'Locomotion', 'Walk')
lib.set_default_state(abp, 'Locomotion', 'Idle')
lib.set_state_animation(abp, 'Locomotion', 'Idle', idle_anim)
lib.set_state_animation(abp, 'Locomotion', 'Walk', walk_anim)
lib.add_transition(abp, 'Locomotion', 'Idle', 'Walk', 0.2)
lib.add_transition(abp, 'Locomotion', 'Walk', 'Idle', 0.2)
lib.compile_anim_blueprint(abp)
```

## Installation

### Inside Unreal Engine

Copy the `pyunreal/` folder to your project's `Content/Python/` directory,
or add its parent directory to your Python path in **Project Settings > Python > Additional Paths**.

### pip (for development/testing outside UE)

```bash
pip install pyunreal
```

## Two-Tier Architecture

PyUnreal works at two levels:

| Tier | Requires | Capabilities |
|------|----------|-------------|
| **Standalone** | UE Python interpreter | Asset loading, scene queries, standard `unreal.*` APIs |
| **MCA Editor** | [MCA Editor plugin](https://mcaeditor.com) | AnimBP graph editing, Blueprint node wiring, deep engine access |

When you call a method that requires MCA Editor and it is not installed,
you get a clear error message telling you what to install and where.

## Current Modules

### `pyunreal.anim` -- Animation Blueprint Authoring

| Class | Description |
|-------|-------------|
| `AnimBlueprint` | Create, load, compile AnimBPs |
| `StateMachine` | Add/list states within a state machine |
| `State` | Set animation, create transitions, set as default |
| `Transition` | Configure crossfade, auto-transition rules |

## Roadmap

- **Phase 2**: Blueprint wrappers (components, variables, compilation)
- **Phase 3**: Control Rig wrappers (controls, nulls, hierarchy)
- **Phase 4**: Scene and Actor wrappers (spawn, query, transform)
- **Phase 5**: Documentation site at [mcaeditor.com/docs/pyunreal](https://mcaeditor.com/docs/pyunreal/)

## Requirements

- Python 3.9+ (ships with UE 5.x)
- Unreal Engine 5.4+ (for `unreal` module)
- [MCA Editor](https://mcaeditor.com) plugin (optional, for advanced features)

## License

[MIT](LICENSE)
