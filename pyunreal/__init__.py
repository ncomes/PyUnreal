"""
PyUnreal — Pythonic wrapper for Unreal Engine's Python API.

A PyMEL-style library that makes UE Python feel like Python, not C++
with Python syntax.  Focused on Tech Art workflows: AnimBP authoring,
Blueprint construction, and Control Rig setup.

Two-tier architecture:
    - Standalone: wraps standard ``unreal.*`` APIs for any UE project
    - MCA Editor: unlocks advanced features (AnimBP graph editing, etc.)
      when the MCA Editor plugin is installed

Quick start::

    from pyunreal import load
    from pyunreal.anim import AnimBlueprint

    skeleton = load('/Game/Characters/SK_Mannequin')
    abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)
    loco = abp.add_state_machine('Locomotion')
    idle = loco.add_state('Idle', animation=load('/Game/Anims/Idle'), default=True)

Dependencies:
    - ``unreal`` module (only available inside UE's Python interpreter)
    - MCA Editor plugin (optional, for advanced features)
"""

__version__ = "0.1.0"
__app_name__ = "PyUnreal"

# --- Top-level convenience imports -------------------------------------
# These let users write `from pyunreal import load` without reaching
# into the core subpackage.
from pyunreal.core.utils import load
from pyunreal.core.utils import asset_exists
