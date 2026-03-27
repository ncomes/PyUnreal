"""
Null wrapper for Control Rig null/space/group elements.

A Null represents a space or group node in a Control Rig hierarchy.
Nulls are used to organize controls and create intermediate transform
spaces for rigging.

Nulls are created by :meth:`ControlRig.add_null` or discovered via
:attr:`ControlRig.nulls`, not instantiated directly by users.
"""


class Null:
    """
    A null (space/group) element in a Control Rig hierarchy.

    :param str name: The null name
    :param str parent: The parent element name, or empty string for root
    :param dict transform: Initial global transform {location, rotation, scale}
    """

    def __init__(self, name, parent="", transform=None):
        # Null element name.
        self._name = name

        # Parent element name (empty string for root-level nulls).
        self._parent = parent

        # Transform snapshot.
        self._transform = transform

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The null name.

        :rtype: str
        """
        return self._name

    @property
    def parent(self):
        """
        The parent element name, or empty string for root.

        :rtype: str
        """
        return self._parent

    @property
    def transform(self):
        """
        Initial global transform as a dict with location, rotation, scale.

        :rtype: dict or None
        """
        return self._transform

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<Null '{}'>".format(self._name)
