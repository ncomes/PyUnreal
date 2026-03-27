"""
PyUnreal — Pythonic wrapper for Unreal Engine's Python API.

A PyMEL-style library that makes UE Python feel like Python, not C++
with Python syntax.  Focused on Tech Art workflows: AnimBP authoring,
Blueprint construction, Control Rig setup, and scene manipulation.

Two-tier architecture:
    - Standalone: wraps standard ``unreal.*`` APIs for any UE project
    - MCA Editor: unlocks advanced features (AnimBP graph editing, etc.)
      when the MCA Editor plugin is installed

Modules:
    - ``pyunreal.anim`` — AnimBlueprint, StateMachine, State, Transition
    - ``pyunreal.blueprint`` — Blueprint, Component, Variable
    - ``pyunreal.control_rig`` — ControlRig, Control, Null, Bone
    - ``pyunreal.scene`` — Actor, scene queries (find, select, spawn)

Quick start::

    from pyunreal import load
    from pyunreal.anim import AnimBlueprint
    from pyunreal.blueprint import Blueprint
    from pyunreal.control_rig import ControlRig
    from pyunreal.scene import Actor, scene

Dependencies:
    - ``unreal`` module (only available inside UE's Python interpreter)
    - MCA Editor plugin (optional, for AnimBP graph editing)
"""

__version__ = "0.2.0"
__app_name__ = "PyUnreal"

# --- Top-level convenience imports -------------------------------------
# These let users write `from pyunreal import load` without reaching
# into the core subpackage.
from pyunreal.core.utils import load
from pyunreal.core.utils import asset_exists
