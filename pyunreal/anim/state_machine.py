"""
StateMachine wrapper for AnimBP state machines.

A StateMachine is a name-based reference — it does not hold a UObject
pointer.  The C++ bridge API identifies state machines by name within
an AnimBlueprint, so this class stores its name and a back-reference
to the parent AnimBlueprint wrapper.

State machines are created by :meth:`AnimBlueprint.add_state_machine`,
not instantiated directly.
"""

import logging

from pyunreal.core.detection import require_bridge
from pyunreal.core.detection import get_bridge_library
from pyunreal.core.errors import InvalidOperationError
from pyunreal.anim.state import State

# Module-level logger.
logger = logging.getLogger(__name__)


class StateMachine:
    """
    A state machine inside an AnimBP's AnimGraph.

    :param anim_bp: The parent AnimBlueprint wrapper
    :param str name: The state machine name
    """

    def __init__(self, anim_bp, name):
        # Parent AnimBlueprint — needed to reach the UAnimBlueprint UObject
        # that the C++ functions require as their first parameter.
        self._anim_bp = anim_bp

        # State machine name — the C++ API identifies SMs by name.
        self._name = name

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The state machine name.

        :rtype: str
        """
        return self._name

    @property
    def anim_blueprint(self):
        """
        The parent AnimBlueprint this state machine belongs to.

        :rtype: AnimBlueprint
        """
        return self._anim_bp

    @property
    def states(self):
        """
        List of states in this state machine.

        Queries the live state from UE every time — no caching, so the
        result always reflects the current state of the AnimBP.

        :return: List of State wrapper objects
        :rtype: list[State]
        """
        require_bridge("StateMachine.states")
        lib = get_bridge_library()

        names = lib.list_states(self._anim_bp._asset, self._name)

        # Wrap each name in a State object.
        return [State(self, name) for name in names]

    # --- Methods -------------------------------------------------------

    def add_state(self, name, animation=None, default=False):
        """
        Add a new state to this state machine.

        Convenience parameters ``animation`` and ``default`` let you
        configure the common case in a single call instead of three::

            # These two are equivalent:
            idle = loco.add_state('Idle', animation=idle_anim, default=True)

            idle = loco.add_state('Idle')
            idle.set_animation(idle_anim)
            idle.set_default()

        :param str name: Name for the new state
        :param animation: Optional UE animation asset to assign (e.g. from ``load()``)
        :param bool default: If True, make this the default (entry) state
        :return: The new State wrapper
        :rtype: State
        :raises InvalidOperationError: if the C++ call fails
        """
        require_bridge("StateMachine.add_state")
        lib = get_bridge_library()

        anim_bp_asset = self._anim_bp._asset

        logger.info("Adding state '%s' to state machine '%s'", name, self._name)

        success = lib.add_state(anim_bp_asset, self._name, name)

        if not success:
            raise InvalidOperationError(
                "Failed to add state '{}' to state machine '{}'. "
                "A state with this name may already exist.".format(name, self._name)
            )

        # Wrap in a State object for further operations.
        state = State(self, name)

        # Apply optional convenience parameters.
        if animation is not None:
            state.set_animation(animation)

        if default:
            state.set_default()

        return state

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<StateMachine '{}'>".format(self._name)
