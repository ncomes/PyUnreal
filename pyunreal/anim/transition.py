"""
Transition wrapper for AnimBP state machine transitions.

A Transition represents a directional edge between two states in an
AnimBP state machine.  It is a lightweight, name-based reference — it
does not hold a UObject pointer but instead identifies the transition
by its source state, destination state, and parent state machine.

Transitions are created by :meth:`State.transition_to` or
:meth:`State.auto_transition_to`, not instantiated directly.
"""

import logging

from pyunreal.core.detection import require_mca_scripting
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)


class Transition:
    """
    A directional transition between two states in an AnimBP state machine.

    :param state_machine: The parent StateMachine wrapper
    :param str from_name: Source state name
    :param str to_name: Destination state name
    :param float crossfade: Crossfade duration in seconds
    """

    def __init__(self, state_machine, from_name, to_name, crossfade=0.2):
        # Parent state machine — used to reach the AnimBlueprint UObject.
        self._state_machine = state_machine

        # Source and destination state names identify this transition.
        self._from_name = from_name
        self._to_name = to_name

        # Crossfade duration set at creation time.
        self._crossfade = crossfade

    # --- Properties (read-only) ----------------------------------------

    @property
    def from_state(self):
        """
        Name of the source state.

        :rtype: str
        """
        return self._from_name

    @property
    def to_state(self):
        """
        Name of the destination state.

        :rtype: str
        """
        return self._to_name

    @property
    def crossfade(self):
        """
        Crossfade duration in seconds.

        :rtype: float
        """
        return self._crossfade

    @property
    def state_machine(self):
        """
        The parent StateMachine this transition belongs to.

        :rtype: StateMachine
        """
        return self._state_machine

    # --- Methods -------------------------------------------------------

    def set_auto_rule(self, trigger_time=0.0):
        """
        Set an automatic transition rule based on remaining animation time.

        When the source state's animation has less than ``trigger_time``
        seconds remaining, the transition fires automatically.

        :param float trigger_time: Seconds of remaining time to trigger at
        :return: self for method chaining
        :rtype: Transition
        :raises InvalidOperationError: if the C++ call fails
        """
        require_mca_scripting("Transition.set_auto_rule")
        import unreal

        # Get the AnimBlueprint UObject from the ownership chain.
        anim_bp = self._state_machine._anim_bp._asset
        sm_name = self._state_machine._name

        logger.info(
            "Setting auto-transition rule: %s -> %s (trigger: %.2fs)",
            self._from_name, self._to_name, trigger_time
        )

        success = unreal.MCAAnimBlueprintLibrary.set_auto_transition_rule(
            anim_bp, sm_name, self._from_name, self._to_name, trigger_time
        )

        if not success:
            raise InvalidOperationError(
                "Failed to set auto-transition rule for {} -> {} in '{}'. "
                "Does the transition exist?".format(
                    self._from_name, self._to_name, sm_name
                )
            )

        return self

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<Transition {} -> {} (crossfade: {:.2f}s)>".format(
            self._from_name, self._to_name, self._crossfade
        )
