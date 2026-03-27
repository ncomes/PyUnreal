"""
Control wrapper for Control Rig controls.

A Control represents a single animation control in a Control Rig
hierarchy.  Controls are the elements that animators interact with
to pose a character.

Controls are created by :meth:`ControlRig.add_control` or discovered
via :attr:`ControlRig.controls`, not instantiated directly by users.
"""

import logging

from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)

# --- Color Presets ---------------------------------------------------------
# User-friendly color names mapped to RGBA tuples (0-1 range).

COLOR_PRESETS = {
    "red": (1.0, 0.0, 0.0, 1.0),
    "green": (0.0, 1.0, 0.0, 1.0),
    "blue": (0.0, 0.0, 1.0, 1.0),
    "yellow": (1.0, 1.0, 0.0, 1.0),
    "cyan": (0.0, 1.0, 1.0, 1.0),
    "magenta": (1.0, 0.0, 1.0, 1.0),
    "white": (1.0, 1.0, 1.0, 1.0),
    "orange": (1.0, 0.5, 0.0, 1.0),
    "purple": (0.5, 0.0, 1.0, 1.0),
}


def _resolve_color(color):
    """
    Resolve a color argument to an RGBA tuple.

    Accepts a preset name string (e.g. 'red'), a tuple/list of 3-4 floats,
    or None (returns None).

    :param color: Color preset name, RGBA tuple, or None
    :return: RGBA tuple (0-1 range) or None
    :rtype: tuple or None
    """
    if color is None:
        return None

    if isinstance(color, str):
        preset = COLOR_PRESETS.get(color.lower())
        if preset is None:
            raise ValueError(
                "Unknown color preset '{}'. Available: {}".format(
                    color, ", ".join(sorted(COLOR_PRESETS.keys()))
                )
            )
        return preset

    # Assume it is a tuple/list of floats.
    color = tuple(color)
    if len(color) == 3:
        return color + (1.0,)
    return color


class Control:
    """
    An animation control in a Control Rig hierarchy.

    :param rig: The parent ControlRig wrapper
    :param str name: The control name
    :param str parent: The parent element name, or empty string for root
    :param dict transform: Initial global transform {location, rotation, scale}
    """

    def __init__(self, rig, name, parent="", transform=None):
        # Parent ControlRig — needed to reach the UE asset for write ops.
        self._rig = rig

        # Control name.
        self._name = name

        # Parent element name.
        self._parent = parent

        # Transform snapshot.
        self._transform = transform

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The control name.

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

    @property
    def rig(self):
        """
        The parent ControlRig this control belongs to.

        :rtype: ControlRig
        """
        return self._rig

    # --- Methods -------------------------------------------------------

    def set_transform(self, location=None, rotation=None, scale=None):
        """
        Set the initial global transform of this control.

        Pass only the components you want to change — unspecified
        components are preserved from the current transform.

        :param location: Location as (x, y, z) tuple or dict, or None
        :param rotation: Rotation as (pitch, yaw, roll) tuple or dict, or None
        :param scale: Scale as (x, y, z) tuple or dict, or None
        :return: self for method chaining
        :rtype: Control
        :raises InvalidOperationError: if the transform cannot be set
        """
        require_unreal()
        import unreal

        self._rig._validate()
        rig_bp = self._rig._asset
        hierarchy = rig_bp.hierarchy

        # Find the element key for this control.
        target_key = _find_element_key(hierarchy, self._name, "Control")
        if target_key is None:
            raise InvalidOperationError(
                "Control '{}' not found in hierarchy.".format(self._name)
            )

        logger.info("Setting transform on control '%s'", self._name)

        # Get the current transform as a baseline.
        current = hierarchy.get_initial_global_transform(target_key)

        # Apply location if provided.
        if location is not None:
            loc = _to_tuple(location)
            current.translation = unreal.Vector(loc[0], loc[1], loc[2])

        # Apply rotation if provided.
        if rotation is not None:
            rot = _to_tuple(rotation)
            rotator = unreal.Rotator(rot[0], rot[1], rot[2])
            current.rotation = rotator.quaternion()

        # Apply scale if provided.
        if scale is not None:
            sc = _to_tuple(scale)
            current.scale3d = unreal.Vector(sc[0], sc[1], sc[2])

        with unreal.ScopedEditorTransaction("PyUnreal: set control transform"):
            hierarchy.set_initial_global_transform(target_key, current)

        unreal.EditorAssetLibrary.save_asset(rig_bp.get_path_name())

        # Update the cached transform.
        self._transform = _transform_to_dict(current)

        return self

    def set_shape(self, shape_name, color=None):
        """
        Set the visual shape and color of this control.

        :param str shape_name: Shape name (e.g. 'Circle', 'Box', 'Square')
        :param color: Color preset name ('red', 'yellow', etc.) or RGBA tuple
        :return: self for method chaining
        :rtype: Control
        :raises InvalidOperationError: if the shape cannot be set
        """
        require_unreal()
        import unreal

        self._rig._validate()
        rig_bp = self._rig._asset
        hierarchy = rig_bp.hierarchy

        # Find the element key for this control.
        target_key = _find_element_key(hierarchy, self._name, "Control")
        if target_key is None:
            raise InvalidOperationError(
                "Control '{}' not found in hierarchy.".format(self._name)
            )

        logger.info(
            "Setting shape '%s' on control '%s'", shape_name, self._name
        )

        with unreal.ScopedEditorTransaction("PyUnreal: set control shape"):
            # Get current settings to modify.
            settings = hierarchy.get_control_settings(target_key)

            # Set shape name.
            settings.shape_name = shape_name

            # Set color if provided.
            if color is not None:
                rgba = _resolve_color(color)
                settings.shape_color = unreal.LinearColor(
                    rgba[0], rgba[1], rgba[2], rgba[3]
                )

            hierarchy.set_control_settings(target_key, settings)

        unreal.EditorAssetLibrary.save_asset(rig_bp.get_path_name())

        return self

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<Control '{}'>".format(self._name)


# --- Module-Level Helpers --------------------------------------------------

def _find_element_key(hierarchy, name, expected_type=None):
    """
    Find a hierarchy element key by name.

    :param hierarchy: The UE RigHierarchy object
    :param str name: Element name to find
    :param str expected_type: Optional type filter (e.g. 'Control', 'Bone')
    :return: The element key, or None if not found
    """
    for key in hierarchy.get_all_keys():
        if hierarchy.get_name(key) == name:
            if expected_type:
                element_type = str(hierarchy.get_type(key))
                if expected_type.lower() not in element_type.lower():
                    continue
            return key
    return None


def _to_tuple(value):
    """
    Convert a location/rotation/scale value to a 3-tuple.

    Accepts dicts, tuples, lists, or UE vector/rotator objects.

    :param value: The value to convert
    :return: A 3-tuple of floats
    :rtype: tuple
    """
    if isinstance(value, dict):
        # Support both {x,y,z} and {pitch,yaw,roll} dicts.
        if "x" in value:
            return (value["x"], value["y"], value["z"])
        elif "pitch" in value:
            return (value["pitch"], value["yaw"], value["roll"])

    if isinstance(value, (tuple, list)):
        return tuple(value[:3])

    # Assume it is a UE object with x/y/z or pitch/yaw/roll.
    if hasattr(value, "x"):
        return (value.x, value.y, value.z)
    if hasattr(value, "pitch"):
        return (value.pitch, value.yaw, value.roll)

    return (0, 0, 0)


def _transform_to_dict(transform):
    """
    Convert a UE Transform to a dict for caching.

    :param transform: A UE Transform object
    :return: Dict with location, rotation, scale sub-dicts
    :rtype: dict
    """
    loc = transform.translation
    rot = transform.rotation.rotator()
    sc = transform.scale3d

    return {
        "location": {"x": loc.x, "y": loc.y, "z": loc.z},
        "rotation": {"pitch": rot.pitch, "yaw": rot.yaw, "roll": rot.roll},
        "scale": {"x": sc.x, "y": sc.y, "z": sc.z},
    }
