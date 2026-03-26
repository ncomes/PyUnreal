"""
AnimBP authoring module for PyUnreal.

Provides Pythonic wrappers for creating and configuring Animation Blueprints,
state machines, states, and transitions.  All graph-editing operations
require the MCA Editor plugin (MCAEditorScripting C++ module).

Usage::

    from pyunreal.anim import AnimBlueprint

    abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)
    loco = abp.add_state_machine('Locomotion')
    idle = loco.add_state('Idle', animation=idle_anim, default=True)
"""

from pyunreal.anim.anim_blueprint import AnimBlueprint
from pyunreal.anim.state_machine import StateMachine
from pyunreal.anim.state import State
from pyunreal.anim.transition import Transition
