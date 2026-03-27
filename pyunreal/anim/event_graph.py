"""
EventGraph wrapper for Blueprints and Animation Blueprints.

Provides a Pythonic interface for creating nodes in a Blueprint's EventGraph
and wiring them together — event nodes, function calls, casts, variable
get/set nodes, and pin connections.

This wraps the C++ bridge functions for EventGraph manipulation. Requires
either PyUnrealBridge or MCA Editor plugin.

Usage::

    from pyunreal.anim import AnimBlueprint

    abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')
    eg = abp.event_graph

    init = eg.add_event('BlueprintInitializeAnimation')
    pawn = eg.add_call('TryGetPawnOwner')
    init.connect('then', pawn, 'execute')

Dependencies:
    - ``unreal`` module (UE Python interpreter)
    - PyUnrealBridge or MCA Editor plugin (C++ bridge)
"""

import logging

from pyunreal.core.detection import require_bridge
from pyunreal.core.detection import get_bridge_library
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)


class EventGraph:
    """
    Wrapper for a Blueprint's EventGraph.

    Provides methods to add nodes and wire them together. Get an instance
    via ``AnimBlueprint.event_graph`` or ``Blueprint.event_graph``.

    :param blueprint_wrapper: The parent Blueprint or AnimBlueprint wrapper
    """

    def __init__(self, blueprint_wrapper):
        # Store a reference to the parent wrapper.
        self._bp_wrapper = blueprint_wrapper

    # --- Properties ----------------------------------------------------

    @property
    def blueprint(self):
        """
        The parent Blueprint wrapper.

        :return: The Blueprint or AnimBlueprint wrapper
        """
        return self._bp_wrapper

    @property
    def nodes(self):
        """
        List all nodes in the EventGraph.

        Returns a list of dicts with 'id', 'class', and 'title' keys.

        :return: List of node info dicts
        :rtype: list[dict]
        """
        require_bridge("EventGraph.nodes")
        lib = get_bridge_library()

        self._bp_wrapper._validate()

        node_strings = lib.list_event_graph_nodes(self._bp_wrapper._asset)

        # Parse "NodeId:ClassName:Title" strings.
        result = []
        for s in node_strings:
            parts = s.split(":", 2)
            if len(parts) >= 3:
                result.append({
                    "id": parts[0],
                    "class": parts[1],
                    "title": parts[2],
                })

        return result

    # --- Node Creation -------------------------------------------------

    def add_event(self, event_name):
        """
        Add an event node to the EventGraph.

        Creates a node for a UE event like ``BlueprintInitializeAnimation``,
        ``BlueprintUpdateAnimation``, ``ReceiveBeginPlay``, etc.

        :param str event_name: The UE event function name
        :return: A GraphNode wrapper for the created node
        :rtype: GraphNode
        :raises InvalidOperationError: if creation fails
        """
        require_bridge("EventGraph.add_event")
        lib = get_bridge_library()

        self._bp_wrapper._validate()

        logger.info("Adding event node: %s", event_name)

        node_id = lib.add_event_node(self._bp_wrapper._asset, event_name)

        if not node_id:
            raise InvalidOperationError(
                "Failed to add event '{}' to EventGraph.".format(event_name)
            )

        return GraphNode(self, node_id, event_name)

    def add_call(self, function_name, target_class=""):
        """
        Add a function call node to the EventGraph.

        :param str function_name: Name of the function to call
                                  (e.g. 'TryGetPawnOwner', 'GetVelocity')
        :param str target_class: Class that owns the function (optional).
                                 If empty, searches the Blueprint's class
                                 and common engine classes.
        :return: A GraphNode wrapper for the created node
        :rtype: GraphNode
        :raises InvalidOperationError: if the function is not found
        """
        require_bridge("EventGraph.add_call")
        lib = get_bridge_library()

        self._bp_wrapper._validate()

        logger.info("Adding function call: %s (class: %s)", function_name, target_class)

        node_id = lib.add_function_call_node(
            self._bp_wrapper._asset, function_name, target_class
        )

        if not node_id:
            raise InvalidOperationError(
                "Failed to add function call '{}'. "
                "Function not found on class '{}'.".format(
                    function_name, target_class or "(auto)"
                )
            )

        return GraphNode(self, node_id, function_name)

    def add_cast(self, target_class):
        """
        Add a Cast node to the EventGraph.

        :param str target_class: Name of the class to cast to
                                 (e.g. 'WCompanionCharacter')
        :return: A GraphNode wrapper for the created node
        :rtype: GraphNode
        :raises InvalidOperationError: if the class is not found
        """
        require_bridge("EventGraph.add_cast")
        lib = get_bridge_library()

        self._bp_wrapper._validate()

        logger.info("Adding cast to: %s", target_class)

        node_id = lib.add_cast_node(self._bp_wrapper._asset, target_class)

        if not node_id:
            raise InvalidOperationError(
                "Failed to add cast to '{}'. Class not found.".format(target_class)
            )

        return GraphNode(self, node_id, "Cast to {}".format(target_class))

    def add_variable_get(self, var_name):
        """
        Add a Variable GET node to the EventGraph.

        :param str var_name: Name of the variable to read
        :return: A GraphNode wrapper
        :rtype: GraphNode
        :raises InvalidOperationError: if creation fails
        """
        require_bridge("EventGraph.add_variable_get")
        lib = get_bridge_library()

        self._bp_wrapper._validate()

        logger.info("Adding variable GET: %s", var_name)

        node_id = lib.add_variable_get_node(self._bp_wrapper._asset, var_name)

        if not node_id:
            raise InvalidOperationError(
                "Failed to add GET node for variable '{}'.".format(var_name)
            )

        return GraphNode(self, node_id, "Get {}".format(var_name))

    def add_variable_set(self, var_name):
        """
        Add a Variable SET node to the EventGraph.

        :param str var_name: Name of the variable to write
        :return: A GraphNode wrapper
        :rtype: GraphNode
        :raises InvalidOperationError: if creation fails
        """
        require_bridge("EventGraph.add_variable_set")
        lib = get_bridge_library()

        self._bp_wrapper._validate()

        logger.info("Adding variable SET: %s", var_name)

        node_id = lib.add_variable_set_node(self._bp_wrapper._asset, var_name)

        if not node_id:
            raise InvalidOperationError(
                "Failed to add SET node for variable '{}'.".format(var_name)
            )

        return GraphNode(self, node_id, "Set {}".format(var_name))

    # --- String Representation -----------------------------------------

    def __repr__(self):
        try:
            name = self._bp_wrapper._asset.get_name() if self._bp_wrapper._asset else "None"
        except Exception:
            name = "invalid"
        return "<EventGraph of '{}'>".format(name)


class GraphNode:
    """
    Lightweight wrapper around a node in the EventGraph.

    Created by the ``add_*`` methods on :class:`EventGraph`. Provides
    methods for wiring pins and inspecting the node.

    :param EventGraph event_graph: The parent EventGraph
    :param str node_id: Unique node ID (GUID string from C++ bridge)
    :param str label: Human-readable label for logging
    """

    def __init__(self, event_graph, node_id, label=""):
        self._event_graph = event_graph
        self._node_id = node_id
        self._label = label

    # --- Properties ----------------------------------------------------

    @property
    def id(self):
        """
        The unique node ID.

        :rtype: str
        """
        return self._node_id

    @property
    def label(self):
        """
        A human-readable label for this node.

        :rtype: str
        """
        return self._label

    @property
    def pins(self):
        """
        List all pins on this node.

        Returns a list of dicts with 'direction', 'name', and 'type' keys.

        :return: List of pin info dicts
        :rtype: list[dict]
        """
        require_bridge("GraphNode.pins")
        lib = get_bridge_library()

        bp = self._event_graph._bp_wrapper._asset
        pin_strings = lib.get_node_pins(bp, self._node_id)

        result = []
        for s in pin_strings:
            parts = s.split(":", 2)
            if len(parts) >= 3:
                result.append({
                    "direction": parts[0],
                    "name": parts[1],
                    "type": parts[2],
                })

        return result

    # --- Wiring --------------------------------------------------------

    def connect(self, source_pin, target_node, target_pin):
        """
        Connect an output pin on this node to an input pin on another node.

        :param str source_pin: Pin name on this node (e.g. 'then', 'ReturnValue')
        :param GraphNode target_node: The target node to connect to
        :param str target_pin: Pin name on the target node (e.g. 'execute', 'self')
        :return: self for method chaining
        :rtype: GraphNode
        :raises InvalidOperationError: if the connection fails
        """
        require_bridge("GraphNode.connect")
        lib = get_bridge_library()

        bp = self._event_graph._bp_wrapper._asset

        logger.info(
            "Connecting %s.%s -> %s.%s",
            self._label, source_pin, target_node._label, target_pin
        )

        success = lib.connect_pins(
            bp,
            self._node_id, source_pin,
            target_node._node_id, target_pin
        )

        if not success:
            raise InvalidOperationError(
                "Failed to connect {}.{} -> {}.{}. "
                "Check pin names and types.".format(
                    self._label, source_pin,
                    target_node._label, target_pin
                )
            )

        return self

    def set_position(self, x, y):
        """
        Set the position of this node in the graph editor.

        :param int x: X position in graph coordinates
        :param int y: Y position in graph coordinates
        :return: self for method chaining
        :rtype: GraphNode
        """
        require_bridge("GraphNode.set_position")
        lib = get_bridge_library()

        bp = self._event_graph._bp_wrapper._asset
        lib.set_node_position(bp, self._node_id, x, y)

        return self

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<GraphNode '{}' ({})>".format(self._label, self._node_id[:8])
