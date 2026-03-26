# PyUnreal Documentation

Pythonic wrapper for Unreal Engine's Python API. **PyMEL for Unreal.**

---

## What is PyUnreal?

PyUnreal wraps Unreal Engine's verbose, C++-style Python API into a clean,
object-oriented interface built for Tech Artists.  If you've used PyMEL in
Maya, you'll feel right at home.

**Before (raw UE Python):**

```python
import unreal
lib = unreal.MCAAnimBlueprintLibrary
skel = unreal.EditorAssetLibrary.load_asset('/Game/Characters/SK_Mannequin')
abp = lib.create_anim_blueprint('/Game/AnimBP', 'ABP_Character', skel)
lib.add_state_machine(abp, 'Locomotion', True)
lib.add_state(abp, 'Locomotion', 'Idle')
lib.set_default_state(abp, 'Locomotion', 'Idle')
lib.set_state_animation(abp, 'Locomotion', 'Idle', idle_anim)
lib.add_state(abp, 'Locomotion', 'Walk')
lib.set_state_animation(abp, 'Locomotion', 'Walk', walk_anim)
lib.add_transition(abp, 'Locomotion', 'Idle', 'Walk', 0.2)
lib.add_transition(abp, 'Locomotion', 'Walk', 'Idle', 0.2)
lib.compile_anim_blueprint(abp)
```

**After (PyUnreal):**

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

skeleton = load('/Game/Characters/SK_Mannequin')
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)

loco = abp.add_state_machine('Locomotion')
idle = loco.add_state('Idle', animation=load('/Game/Anims/Idle'), default=True)
walk = loco.add_state('Walk', animation=load('/Game/Anims/Walk'))

idle.transition_to(walk, crossfade=0.2)
walk.transition_to(idle, crossfade=0.2)

abp.compile()
```

---

## Installation

### Inside Unreal Engine

Copy the `pyunreal/` folder to your project's `Content/Python/` directory,
or add its parent directory to your Python path in
**Project Settings > Python > Additional Paths**.

### pip (for development outside UE)

```bash
pip install pyunreal
```

---

## Two-Tier Architecture

PyUnreal works at two levels:

| Tier | Requires | What You Get |
|------|----------|--------------|
| **Standalone** | UE Python interpreter | Asset loading, scene queries, standard `unreal.*` wrappers |
| **MCA Editor** | [MCA Editor plugin](https://mcaeditor.com) | AnimBP graph editing, Blueprint node wiring, deep engine access |

Methods that require MCA Editor will raise a clear error with install
instructions if the plugin is not loaded.

---

## Guides

- [Getting Started](guides/getting-started.md) -- Install, configure, and run your first script
- [AnimBP Cookbook](guides/animbp-cookbook.md) -- Common AnimBP recipes and patterns

## API Reference

### Utilities
- [`load()`](api/load.md) -- Load assets from the Content Browser
- [`asset_exists()`](api/load.md#asset_exists) -- Check if an asset exists

### Animation Blueprint
- [`AnimBlueprint`](api/AnimBlueprint.md) -- Create, load, and compile Animation Blueprints
- [`StateMachine`](api/StateMachine.md) -- Add and list states within a state machine
- [`State`](api/State.md) -- Set animation, create transitions, set as default
- [`Transition`](api/Transition.md) -- Configure crossfade and auto-transition rules

### Exceptions
- [`PyUnrealError`](api/errors.md) -- Base exception and subclasses

---

## Requirements

- Python 3.9+ (ships with UE 5.x)
- Unreal Engine 5.4+
- [MCA Editor](https://mcaeditor.com) plugin (optional, for advanced features)

## License

[MIT](https://github.com/ncomes/pyunreal/blob/main/LICENSE)
