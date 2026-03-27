"""
ControlRig wrapper — the top-level entry point for Control Rig authoring.

A ControlRig wraps a ``UControlRigBlueprint`` UObject and provides a
Pythonic interface for inspecting and building rig hierarchies —
controls, nulls, and bones.  All operations use standard UE Python
APIs — no C++ bridge required.

Usage::

    from pyunreal.control_rig import ControlRig

    rig = ControlRig.load('/Game/Rigs/CR_Character')
    root = rig.add_null('Root')
    hips = rig.add_control('Hips', parent='Root', shape='Box', color='yellow')

Dependencies:
    - ``unreal`` module (UE Python interpreter)
"""

import logging

from pyunreal.core.base import UnrealObjectWrapper
from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import AssetNotFoundError
from pyunreal.core.errors import InvalidOperationError
from pyunreal.control_rig.control import Control
from pyunreal.control_rig.control import _find_element_key
from pyunreal.control_rig.null import Null
from pyunreal.control_rig.bone import Bone

# Module-level logger.
logger = logging.getLogger(__name__)


class ControlRig(UnrealObjectWrapper):
    """
    Pythonic wrapper around a UControlRigBlueprint asset.

    Use :meth:`load` to get an instance.  Direct construction is also
    supported for wrapping an existing UObject::

        rig = ControlRig(some_ue_control_rig_blueprint)

    :param ue_control_rig: An existing ``unreal.ControlRigBlueprint`` UObject
    """

    def __init__(self, ue_control_rig):
        super().__init__(ue_control_rig)

    # --- Class Methods (constructors) ----------------------------------

    @classmethod
    def load(cls, asset_path):
        """
        Load an existing Control Rig Blueprint from the Content Browser.

        :param str asset_path: Full content path (e.g. '/Game/Rigs/CR_Character')
        :return: Wrapped ControlRig instance
        :rtype: ControlRig
        :raises AssetNotFoundError: if no asset exists at the path
        :raises InvalidOperationError: if the asset is not a ControlRigBlueprint
        """
        require_unreal()
        import unreal

        logger.info("Loading ControlRig: %s", asset_path)

        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if asset is None:
            raise AssetNotFoundError(asset_path)

        # Verify this is actually a Control Rig Blueprint.
        if not isinstance(asset, unreal.ControlRigBlueprint):
            raise InvalidOperationError(
                "Asset at '{}' is a {}, not a ControlRigBlueprint.".format(
                    asset_path, type(asset).__name__
                )
            )

        return cls(asset)

    @classmethod
    def find(cls, path="/Game"):
        """
        Search the Content Browser for Control Rig Blueprint assets.

        Returns a list of asset paths (strings), not loaded rigs.
        Call :meth:`load` on individual paths to get wrapper objects.

        :param str path: Content path to search under (default '/Game')
        :return: List of matching asset paths
        :rtype: list[str]
        """
        require_unreal()
        import unreal

        logger.debug("Finding Control Rigs under: %s", path)

        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        ar_filter = unreal.ARFilter()
        ar_filter.package_paths = [path]
        ar_filter.recursive_paths = True
        ar_filter.class_names = ["ControlRigBlueprint"]

        assets = registry.get_assets(ar_filter)

        return [str(ad.package_name) for ad in assets]

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The asset name of this Control Rig.

        :rtype: str
        """
        self._validate()
        return self._asset.get_name()

    @property
    def path(self):
        """
        The full Content Browser path of this Control Rig.

        :rtype: str
        """
        self._validate()
        return self._asset.get_path_name()

    @property
    def controls(self):
        """
        List of controls in this Control Rig.

        Queries the live hierarchy from UE every time — no caching.

        :return: List of Control wrapper objects
        :rtype: list[Control]
        """
        return self._get_elements_by_type("Control")

    @property
    def bones(self):
        """
        List of bones in this Control Rig.

        Bones are read-only — they come from the skeleton and cannot
        be added or removed through the Control Rig API.

        :return: List of Bone wrapper objects
        :rtype: list[Bone]
        """
        return self._get_elements_by_type("Bone")

    @property
    def nulls(self):
        """
        List of nulls (spaces/groups) in this Control Rig.

        :return: List of Null wrapper objects
        :rtype: list[Null]
        """
        return self._get_elements_by_type("Null")

    # --- Methods -------------------------------------------------------

    def add_control(self, name, parent=None, shape="Circle", color=None,
                    location=None, rotation=None, scale=None):
        """
        Add a new control to this Control Rig's hierarchy.

        :param str name: Name for the new control
        :param str parent: Parent element name to attach under (optional)
        :param str shape: Shape name for the control gizmo (default 'Circle')
        :param color: Color preset name ('red', 'yellow', etc.) or RGBA tuple
        :param location: Initial location as (x, y, z) tuple (optional)
        :param rotation: Initial rotation as (pitch, yaw, roll) tuple (optional)
        :param scale: Initial scale as (x, y, z) tuple (optional)
        :return: The new Control wrapper
        :rtype: Control
        :raises InvalidOperationError: if the add operation fails
        """
        require_unreal()
        import unreal

        self._validate()

        logger.info("Adding control '%s' to %s", name, self.name)

        controller = self._asset.get_controller()
        if controller is None:
            raise InvalidOperationError(
                "Could not get hierarchy controller for '{}'.".format(self.name)
            )

        # Build the initial transform.
        loc = location or (0, 0, 0)
        rot = rotation or (0, 0, 0)
        sc = scale or (1, 1, 1)

        # Handle dict-style args.
        if isinstance(loc, dict):
            loc = (loc["x"], loc["y"], loc["z"])
        if isinstance(rot, dict):
            rot = (rot["pitch"], rot["yaw"], rot["roll"])
        if isinstance(sc, dict):
            sc = (sc["x"], sc["y"], sc["z"])

        transform = unreal.Transform()
        transform.translation = unreal.Vector(loc[0], loc[1], loc[2])
        rotator = unreal.Rotator(rot[0], rot[1], rot[2])
        transform.rotation = rotator.quaternion()
        transform.scale3d = unreal.Vector(sc[0], sc[1], sc[2])

        # Resolve parent key.
        parent_key = unreal.RigElementKey()
        if parent:
            found = _find_element_key(self._asset.hierarchy, parent)
            if found is not None:
                parent_key = found
            else:
                logger.warning(
                    "Parent element '%s' not found — adding at root", parent
                )

        with unreal.ScopedEditorTransaction("PyUnreal: add control"):
            # Build control settings.
            settings = unreal.RigControlSettings()
            value = unreal.RigControlValue()

            new_key = controller.add_control(name, parent_key, settings, value)

            if new_key is None:
                raise InvalidOperationError(
                    "Failed to add control '{}' to '{}'.".format(name, self.name)
                )

            # Set the initial transform.
            self._asset.hierarchy.set_initial_global_transform(new_key, transform)

        # Save the asset.
        unreal.EditorAssetLibrary.save_asset(self.path)

        # Create the wrapper with the shape/color applied.
        control = Control(self, name, parent or "")

        # Set shape and color if specified.
        if shape != "Circle" or color is not None:
            control.set_shape(shape, color)

        return control

    def add_null(self, name, parent=None, location=None, rotation=None):
        """
        Add a null (space/group) to this Control Rig's hierarchy.

        :param str name: Name for the new null
        :param str parent: Parent element name to attach under (optional)
        :param location: Initial location as (x, y, z) tuple (optional)
        :param rotation: Initial rotation as (pitch, yaw, roll) tuple (optional)
        :return: The new Null wrapper
        :rtype: Null
        :raises InvalidOperationError: if the add operation fails
        """
        require_unreal()
        import unreal

        self._validate()

        logger.info("Adding null '%s' to %s", name, self.name)

        controller = self._asset.get_controller()
        if controller is None:
            raise InvalidOperationError(
                "Could not get hierarchy controller for '{}'.".format(self.name)
            )

        # Build the initial transform.
        loc = location or (0, 0, 0)
        rot = rotation or (0, 0, 0)

        if isinstance(loc, dict):
            loc = (loc["x"], loc["y"], loc["z"])
        if isinstance(rot, dict):
            rot = (rot["pitch"], rot["yaw"], rot["roll"])

        transform = unreal.Transform()
        transform.translation = unreal.Vector(loc[0], loc[1], loc[2])
        rotator = unreal.Rotator(rot[0], rot[1], rot[2])
        transform.rotation = rotator.quaternion()

        # Resolve parent key.
        parent_key = unreal.RigElementKey()
        if parent:
            found = _find_element_key(self._asset.hierarchy, parent)
            if found is not None:
                parent_key = found
            else:
                logger.warning(
                    "Parent element '%s' not found — adding at root", parent
                )

        with unreal.ScopedEditorTransaction("PyUnreal: add null"):
            new_key = controller.add_null(name, parent_key, transform)

            if new_key is None:
                raise InvalidOperationError(
                    "Failed to add null '{}' to '{}'.".format(name, self.name)
                )

        unreal.EditorAssetLibrary.save_asset(self.path)

        return Null(name, parent or "")

    def get_control(self, name):
        """
        Get a Control wrapper for an existing control by name.

        :param str name: The control name to find
        :return: Control wrapper
        :rtype: Control
        :raises InvalidOperationError: if the control is not found
        """
        for ctrl in self.controls:
            if ctrl.name == name:
                return ctrl

        raise InvalidOperationError(
            "Control '{}' not found in '{}'.".format(name, self.name)
        )

    # --- Internal Helpers ----------------------------------------------

    def _get_elements_by_type(self, element_type):
        """
        Query the hierarchy for elements of a specific type.

        :param str element_type: Type to filter ('Control', 'Bone', 'Null')
        :return: List of wrapper objects
        :rtype: list
        """
        require_unreal()

        self._validate()
        hierarchy = self._asset.hierarchy
        results = []

        for key in hierarchy.get_all_keys():
            key_type = str(hierarchy.get_type(key))

            # Check if this element matches the requested type.
            if element_type.lower() not in key_type.lower():
                continue

            elem_name = hierarchy.get_name(key)

            # Get parent name.
            parent_key = hierarchy.get_parent(key)
            parent_name = ""
            if parent_key is not None:
                try:
                    parent_name = hierarchy.get_name(parent_key)
                except Exception:
                    pass

            # Get transform.
            transform = None
            try:
                t = hierarchy.get_initial_global_transform(key)
                loc = t.translation
                rot = t.rotation.rotator()
                sc = t.scale3d
                transform = {
                    "location": {"x": loc.x, "y": loc.y, "z": loc.z},
                    "rotation": {"pitch": rot.pitch, "yaw": rot.yaw, "roll": rot.roll},
                    "scale": {"x": sc.x, "y": sc.y, "z": sc.z},
                }
            except Exception:
                pass

            # Create the appropriate wrapper type.
            if element_type == "Control":
                results.append(Control(self, elem_name, parent_name, transform))
            elif element_type == "Bone":
                results.append(Bone(elem_name, parent_name, transform))
            elif element_type == "Null":
                results.append(Null(elem_name, parent_name, transform))

        return results

    # --- String Representation -----------------------------------------

    def __repr__(self):
        try:
            name = self._asset.get_name() if self._asset else "None"
        except Exception:
            name = "invalid"
        return "<ControlRig '{}'>".format(name)
