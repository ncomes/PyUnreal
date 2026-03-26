"""
State wrapper for AnimBP state machine states.

A State represents a single state node inside an AnimBP state machine.
Like StateMachine, it is a name-based reference — it stores its name and
a reference to its parent StateMachine, then passes both to the C++ bridge
for every operation.

States are created by :meth:`StateMachine.add_state`, not instantiated
directly.
"""

import logging

from pyunreal.core.detection import require_bridge
from pyunreal.core.detection import get_bridge_library
from pyunreal.core.errors import InvalidOperationError
from pyunreal.anim.transition import Transition

# Module-level logger.
logger = logging.getLogger(__name__)


class State:
    """
    A single state in an AnimBP state machine.

    :param state_machine: The parent StateMachine wrapper
    :param str name: The state name
    """

    def __init__(self, state_machine, name):
        # Parent state machine — used to reach the AnimBlueprint UObject.
        self._state_machine = state_machine

        # State name — the C++ API identifies states by name.
        self._name = name

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The state name.

        :rtype: str
        """
        return self._name

    @property
    def state_machine(self):
        """
        The parent StateMachine this state belongs to.

        :rtype: StateMachine
        """
        return self._state_machine

    @property
    def anim_blueprint(self):
        """
        The AnimBlueprint that owns this state's state machine.

        :rtype: AnimBlueprint
        """
        return self._state_machine._anim_bp

    # --- Animation Assignment ------------------------------------------

    def set_animation(self, anim_asset):
        """
        Set the animation played by this state.

        Updates the animation player node inside this state's graph.
        The ``anim_asset`` should be a loaded UE animation object
        (AnimSequence, BlendSpace, etc.).

        :param anim_asset: Loaded UE animation asset (e.g. from ``load()``)
        :return: self for method chaining
        :rtype: State
        :raises InvalidOperationError: if the C++ call fails
        """
        require_bridge("State.set_animation")
        lib = get_bridge_library()

        anim_bp = self._state_machine._anim_bp._asset
        sm_name = self._state_machine._name

        logger.info("Setting animation on state '%s': %s", self._name, anim_asset)

        success = lib.set_state_animation(
            anim_bp, sm_name, self._name, anim_asset
        )

        if not success:
            raise InvalidOperationError(
                "Failed to set animation on state '{}' in '{}'. "
                "The state may not have an animation player node.".format(
                    self._name, sm_name
                )
            )

        return self

    # --- Default State -------------------------------------------------

    def set_default(self):
        """
        Make this state the default (entry) state of its state machine.

        Wires the state machine's entry node to point at this state.

        :return: self for method chaining
        :rtype: State
        :raises InvalidOperationError: if the C++ call fails
        """
        require_bridge("State.set_default")
        lib = get_bridge_library()

        anim_bp = self._state_machine._anim_bp._asset
        sm_name = self._state_machine._name

        logger.info("Setting default state to '%s' in '%s'", self._name, sm_name)

        success = lib.set_default_state(
            anim_bp, sm_name, self._name
        )

        if not success:
            raise InvalidOperationError(
                "Failed to set '{}' as default state in '{}'. "
                "Does the state exist?".format(self._name, sm_name)
            )

        return self

    # --- Transitions ---------------------------------------------------

    def transition_to(self, target, crossfade=0.2):
        """
        Create a transition from this state to a target state.

        :param target: Destination state — either a State instance or a
                       string name.  If a State, it must belong to the
                       same state machine.
        :param float crossfade: Crossfade blend duration in seconds
        :return: The new Transition object
        :rtype: Transition
        :raises InvalidOperationError: if the C++ call fails
        :raises ValueError: if the target state is from a different state machine
        """
        require_bridge("State.transition_to")
        lib = get_bridge_library()

        # Resolve target to a name string.
        target_name = self._resolve_target(target)

        anim_bp = self._state_machine._anim_bp._asset
        sm_name = self._state_machine._name

        logger.info(
            "Adding transition: %s -> %s (crossfade: %.2fs)",
            self._name, target_name, crossfade
        )

        success = lib.add_transition(
            anim_bp, sm_name, self._name, target_name, crossfade
        )

        if not success:
            raise InvalidOperationError(
                "Failed to add transition from '{}' to '{}' in '{}'. "
                "Both states must exist in the state machine.".format(
                    self._name, target_name, sm_name
                )
            )

        return Transition(self._state_machine, self._name, target_name, crossfade)

    def auto_transition_to(self, target, trigger_time=0.0, crossfade=0.2):
        """
        Create a transition with an automatic time-remaining trigger.

        If a transition from this state to the target already exists, it
        will set the auto rule on the existing transition.  If no transition
        exists yet, one is created first.

        :param target: Destination state — State instance or string name
        :param float trigger_time: Seconds of remaining animation time to trigger
        :param float crossfade: Crossfade blend duration (used only if creating
                                a new transition)
        :return: The Transition object with the auto rule applied
        :rtype: Transition
        :raises InvalidOperationError: if either operation fails
        """
        require_bridge("State.auto_transition_to")
        lib = get_bridge_library()

        target_name = self._resolve_target(target)
        anim_bp = self._state_machine._anim_bp._asset
        sm_name = self._state_machine._name

        # Ensure a transition exists first.  add_transition returns False
        # if it already exists, which is fine — we just need it to be there.
        logger.info(
            "Setting up auto-transition: %s -> %s (trigger: %.2fs)",
            self._name, target_name, trigger_time
        )

        lib.add_transition(
            anim_bp, sm_name, self._name, target_name, crossfade
        )

        # Now set the auto rule on the transition.
        success = lib.set_auto_transition_rule(
            anim_bp, sm_name, self._name, target_name, trigger_time
        )

        if not success:
            raise InvalidOperationError(
                "Failed to set auto-transition rule for {} -> {} in '{}'. "
                "Transition may not exist.".format(
                    self._name, target_name, sm_name
                )
            )

        trans = Transition(self._state_machine, self._name, target_name, crossfade)
        return trans

    # --- Internal Helpers ----------------------------------------------

    def _resolve_target(self, target):
        """
        Resolve a target state argument to a name string.

        Accepts either a State instance or a plain string.  If a State
        instance is given, validates that it belongs to the same state
        machine.

        :param target: State instance or string name
        :return: State name string
        :rtype: str
        :raises ValueError: if target is a State from a different state machine
        """
        if isinstance(target, State):
            # Validate same state machine.
            if target._state_machine is not self._state_machine:
                raise ValueError(
                    "Target state '{}' belongs to state machine '{}', "
                    "but this state ('{}') is in '{}'. Transitions must "
                    "be within the same state machine.".format(
                        target._name, target._state_machine._name,
                        self._name, self._state_machine._name
                    )
                )
            return target._name
        # Assume it is a string name.
        return str(target)

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<State '{}' in {}>".format(
            self._name, self._state_machine._name
        )
