"""
Bone wrapper for Control Rig skeleton bones.

A Bone is a read-only snapshot of a bone element in a Control Rig's
hierarchy.  Bones come from the skeleton and cannot be added or
removed through the Control Rig API — they are for inspection only.

Bones are discovered via :attr:`ControlRig.bones`, not instantiated
directly by users.
"""


class Bone:
    """
    A skeleton bone in a Control Rig hierarchy (read-only).

    :param str name: The bone name
    :param str parent: The parent element name, or empty string for root
    :param dict transform: Initial global transform {location, rotation, scale}
    """

    def __init__(self, name, parent="", transform=None):
        # Bone name from the skeleton.
        self._name = name

        # Parent element name (empty string for root bones).
        self._parent = parent

        # Transform snapshot — dict with location/rotation/scale sub-dicts.
        self._transform = transform

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The bone name.

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

        Each sub-key is a dict::

            {
                'location': {'x': 0, 'y': 0, 'z': 0},
                'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0},
                'scale': {'x': 1, 'y': 1, 'z': 1}
            }

        :rtype: dict or None
        """
        return self._transform

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<Bone '{}'>".format(self._name)
