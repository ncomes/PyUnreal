"""
Component wrapper for Blueprint SCS (SimpleConstructionScript) nodes.

A Component represents a single component in a Blueprint's component
hierarchy.  It is a read-only snapshot — the data is captured when
:attr:`Blueprint.components` is accessed and reflects the state at
that moment.

Components are discovered via :meth:`Blueprint.components`, not
instantiated directly by users.
"""


class Component:
    """
    A component in a Blueprint's construction hierarchy.

    :param str name: The component instance name
    :param str component_class: The UE class name (e.g. 'StaticMeshComponent')
    :param str parent: The parent component name, or empty string for root
    :param dict location: Relative location {x, y, z} or None
    :param dict rotation: Relative rotation {pitch, yaw, roll} or None
    :param dict scale: Relative scale {x, y, z} or None
    """

    def __init__(self, name, component_class, parent="", location=None,
                 rotation=None, scale=None):
        # Component instance name.
        self._name = name

        # UE class name (e.g. "StaticMeshComponent").
        self._component_class = component_class

        # Parent component name (empty string for root-level components).
        self._parent = parent

        # Transform data as dicts — None if not available.
        self._location = location
        self._rotation = rotation
        self._scale = scale

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The component instance name.

        :rtype: str
        """
        return self._name

    @property
    def component_class(self):
        """
        The UE class name (e.g. 'StaticMeshComponent').

        :rtype: str
        """
        return self._component_class

    @property
    def parent(self):
        """
        The parent component name, or empty string for root-level.

        :rtype: str
        """
        return self._parent

    @property
    def location(self):
        """
        Relative location as a dict with x, y, z keys, or None.

        :rtype: dict or None
        """
        return self._location

    @property
    def rotation(self):
        """
        Relative rotation as a dict with pitch, yaw, roll keys, or None.

        :rtype: dict or None
        """
        return self._rotation

    @property
    def scale(self):
        """
        Relative scale as a dict with x, y, z keys, or None.

        :rtype: dict or None
        """
        return self._scale

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<Component '{}' ({})>".format(self._name, self._component_class)
