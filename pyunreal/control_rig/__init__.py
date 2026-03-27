"""
Control Rig authoring module for PyUnreal.

Provides Pythonic wrappers for inspecting and building Control Rig
hierarchies — controls, nulls, and bones.  All operations use standard
UE Python APIs — no C++ bridge required.

Usage::

    from pyunreal.control_rig import ControlRig

    rig = ControlRig.load('/Game/Rigs/CR_Character')
    print(rig.controls)
    hips = rig.add_control('Hips', shape='Box', color='yellow')
"""

from pyunreal.control_rig.rig import ControlRig
from pyunreal.control_rig.control import Control
from pyunreal.control_rig.null import Null
from pyunreal.control_rig.bone import Bone
