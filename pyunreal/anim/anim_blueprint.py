"""
AnimBlueprint wrapper — the top-level entry point for AnimBP authoring.

An AnimBlueprint wraps a ``UAnimBlueprint`` UObject and provides a Pythonic
interface for creating state machines, wiring states and transitions, and
compiling.  All graph-editing operations require a C++ bridge plugin —
either PyUnrealBridge (standalone) or MCA Editor.

Usage::

    from pyunreal import load
    from pyunreal.anim import AnimBlueprint

    skeleton = load('/Game/Characters/SK_Mannequin')
    abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)
    loco = abp.add_state_machine('Locomotion')

Dependencies:
    - ``unreal`` module (UE Python interpreter)
    - PyUnrealBridge or MCA Editor plugin (for graph editing operations)
"""

import logging

from pyunreal.core.base import UnrealObjectWrapper
from pyunreal.core.detection import require_unreal
from pyunreal.core.detection import require_bridge
from pyunreal.core.detection import get_bridge_library
from pyunreal.core.errors import AssetNotFoundError
from pyunreal.core.errors import InvalidOperationError
from pyunreal.anim.state_machine import StateMachine
from pyunreal.anim.event_graph import EventGraph

# Module-level logger.
logger = logging.getLogger(__name__)


class AnimBlueprint(UnrealObjectWrapper):
    """
    Pythonic wrapper around a UAnimBlueprint asset.

    Use the class methods :meth:`create` or :meth:`load` to get an instance.
    Direct construction is also supported for wrapping an existing UObject::

        abp = AnimBlueprint(some_ue_anim_blueprint_object)

    :param ue_anim_blueprint: An existing ``unreal.AnimBlueprint`` UObject
    """

    def __init__(self, ue_anim_blueprint):
        super().__init__(ue_anim_blueprint)

    # --- Class Methods (constructors) ----------------------------------

    @classmethod
    def create(cls, package_path, asset_name, skeleton):
        """
        Create a new Animation Blueprint targeting the given skeleton.

        Creates the asset in the Content Browser at the specified location.
        The AnimBP is NOT compiled automatically — call :meth:`compile`
        after setting up states and transitions.

        :param str package_path: Content Browser folder (e.g. '/Game/AnimBP')
        :param str asset_name: Name for the new AnimBP asset
        :param skeleton: Loaded UE Skeleton asset (e.g. from ``load()``)
        :return: Wrapped AnimBlueprint instance
        :rtype: AnimBlueprint
        :raises InvalidOperationError: if creation fails
        """
        require_bridge("AnimBlueprint.create")
        lib = get_bridge_library()

        logger.info(
            "Creating AnimBlueprint: %s/%s (skeleton: %s)",
            package_path, asset_name, skeleton
        )

        result = lib.create_anim_blueprint(
            package_path, asset_name, skeleton
        )

        if result is None:
            raise InvalidOperationError(
                "Failed to create AnimBlueprint '{}/{}'. "
                "Check that the package path is valid and the skeleton "
                "asset is loaded.".format(package_path, asset_name)
            )

        logger.info("Created AnimBlueprint: %s", result.get_name())
        return cls(result)

    @classmethod
    def load(cls, asset_path):
        """
        Load an existing Animation Blueprint from the Content Browser.

        :param str asset_path: Full content path (e.g. '/Game/AnimBP/ABP_Character')
        :return: Wrapped AnimBlueprint instance
        :rtype: AnimBlueprint
        :raises AssetNotFoundError: if no asset exists at the path
        :raises InvalidOperationError: if the asset is not an AnimBlueprint
        """
        require_unreal()
        import unreal

        logger.info("Loading AnimBlueprint: %s", asset_path)

        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if asset is None:
            raise AssetNotFoundError(asset_path)

        # Verify this is actually an AnimBlueprint.
        if not isinstance(asset, unreal.AnimBlueprint):
            raise InvalidOperationError(
                "Asset at '{}' is a {}, not an AnimBlueprint.".format(
                    asset_path, type(asset).__name__
                )
            )

        return cls(asset)

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The asset name of this AnimBlueprint.

        :rtype: str
        """
        self._validate()
        return self._asset.get_name()

    @property
    def path(self):
        """
        The full Content Browser path of this AnimBlueprint.

        :rtype: str
        """
        self._validate()
        return self._asset.get_path_name()

    @property
    def skeleton(self):
        """
        The target skeleton for this AnimBlueprint.

        :return: The UE Skeleton asset
        :rtype: unreal.Skeleton
        """
        self._validate()
        return self._asset.target_skeleton

    @property
    def event_graph(self):
        """
        The EventGraph for this AnimBlueprint.

        Returns an :class:`EventGraph` wrapper that lets you add nodes
        (events, function calls, casts, variable get/set) and wire them
        together programmatically.

        :return: EventGraph wrapper
        :rtype: EventGraph
        """
        self._validate()
        return EventGraph(self)

    @property
    def state_machines(self):
        """
        List of state machines in this AnimBlueprint's AnimGraph.

        Queries the live state from UE every time — no caching, so the
        result always reflects the current state of the AnimBP.

        :return: List of StateMachine wrapper objects
        :rtype: list[StateMachine]
        """
        require_bridge("AnimBlueprint.state_machines")
        lib = get_bridge_library()

        self._validate()

        names = lib.list_state_machines(self._asset)

        # Wrap each name in a StateMachine object.
        return [StateMachine(self, name) for name in names]

    # --- Methods -------------------------------------------------------

    def add_state_machine(self, name, connect_to_root=True):
        """
        Add a new state machine to this AnimBlueprint's AnimGraph.

        :param str name: Name for the new state machine
        :param bool connect_to_root: If True, wire the state machine's
                                     output pose to the AnimGraph's output.
                                     Usually True for the primary state machine.
        :return: The new StateMachine wrapper
        :rtype: StateMachine
        :raises InvalidOperationError: if the C++ call fails
        """
        require_bridge("AnimBlueprint.add_state_machine")
        lib = get_bridge_library()

        self._validate()

        logger.info(
            "Adding state machine '%s' to %s (connect_to_root=%s)",
            name, self.name, connect_to_root
        )

        success = lib.add_state_machine(
            self._asset, name, connect_to_root
        )

        if not success:
            raise InvalidOperationError(
                "Failed to add state machine '{}' to AnimBlueprint '{}'. "
                "A state machine with this name may already exist.".format(
                    name, self.name
                )
            )

        return StateMachine(self, name)

    def compile(self):
        """
        Compile this AnimBlueprint.

        Should be called after all states, transitions, and animations
        are set up.  Compilation validates the graph and generates the
        runtime data structures.

        :return: True if compilation succeeded
        :rtype: bool
        :raises InvalidOperationError: if compilation fails
        """
        require_bridge("AnimBlueprint.compile")
        lib = get_bridge_library()

        self._validate()

        logger.info("Compiling AnimBlueprint: %s", self.name)

        success = lib.compile_anim_blueprint(self._asset)

        if not success:
            raise InvalidOperationError(
                "Compilation failed for AnimBlueprint '{}'. "
                "Check the Output Log in UE for details.".format(self.name)
            )

        logger.info("Compilation succeeded: %s", self.name)
        return True

    # --- String Representation -----------------------------------------

    def __repr__(self):
        # Safely get name — the asset might be None if invalidated.
        try:
            name = self._asset.get_name() if self._asset else "None"
        except Exception:
            name = "invalid"
        return "<AnimBlueprint '{}'>".format(name)
