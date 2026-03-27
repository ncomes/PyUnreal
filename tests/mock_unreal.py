"""
Mock ``unreal`` module for testing PyUnreal outside of Unreal Engine.

Creates a fake ``unreal`` module with all the classes and functions that
PyUnreal's wrapper code calls.  Install it into ``sys.modules`` before
importing any PyUnreal modules.

Usage::

    from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal

    install_mock_unreal()
    # ... import and test pyunreal modules ...
    uninstall_mock_unreal()
"""

import sys
from unittest.mock import MagicMock, PropertyMock


# --- Mock Classes ----------------------------------------------------------
# Minimal stubs that behave enough like the real UE Python objects for
# PyUnreal's wrapper code to function.

class MockVector:
    """Minimal mock for unreal.Vector."""

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "Vector({}, {}, {})".format(self.x, self.y, self.z)


class MockRotator:
    """Minimal mock for unreal.Rotator."""

    def __init__(self, pitch=0, yaw=0, roll=0):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

    def quaternion(self):
        return MockQuaternion(self.pitch, self.yaw, self.roll)

    def __repr__(self):
        return "Rotator({}, {}, {})".format(self.pitch, self.yaw, self.roll)


class MockQuaternion:
    """Minimal mock for unreal.Quat."""

    def __init__(self, p=0, y=0, r=0):
        self._p = p
        self._y = y
        self._r = r

    def rotator(self):
        return MockRotator(self._p, self._y, self._r)


class MockTransform:
    """Minimal mock for unreal.Transform."""

    def __init__(self):
        self.translation = MockVector(0, 0, 0)
        self.rotation = MockQuaternion()
        self.scale3d = MockVector(1, 1, 1)


class MockLinearColor:
    """Minimal mock for unreal.LinearColor."""

    def __init__(self, r=0, g=0, b=0, a=1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


class MockAssetData:
    """Minimal mock for asset registry results."""

    def __init__(self, name, package, class_name="Blueprint"):
        self.asset_name = name
        self.package_name = package
        self.asset_class_path = MagicMock()
        self.asset_class_path.asset_name = class_name

    def is_valid(self):
        return True


class MockScopedTransaction:
    """Minimal mock for unreal.ScopedEditorTransaction."""

    def __init__(self, desc=""):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MockSCSNode:
    """Minimal mock for an SCS node."""

    def __init__(self, name, class_name):
        self.component_template = MagicMock()
        self.component_template.get_name.return_value = name
        self.component_template.get_class.return_value.get_name.return_value = class_name
        self._children = []

    def add_child_node(self, child):
        self._children.append(child)

    def get_editor_property(self, prop):
        if prop == "parent_component_or_variable_name":
            return ""
        return None


# --- Build the mock unreal module ------------------------------------------

def _build_mock_unreal():
    """
    Create and return a mock ``unreal`` module.

    :return: A MagicMock configured to behave like the unreal module
    :rtype: MagicMock
    """
    unreal = MagicMock()

    # --- Geometry types ------------------------------------------------
    unreal.Vector = MockVector
    unreal.Rotator = MockRotator
    unreal.Transform = MockTransform
    unreal.LinearColor = MockLinearColor

    # --- Transaction context manager -----------------------------------
    unreal.ScopedEditorTransaction = MockScopedTransaction

    # --- Blueprint types -----------------------------------------------
    # Make isinstance() checks work for AnimBlueprint, Blueprint, etc.
    unreal.AnimBlueprint = type("AnimBlueprint", (), {})
    unreal.Blueprint = type("Blueprint", (), {})
    unreal.ControlRigBlueprint = type("ControlRigBlueprint", (), {})

    # --- Common actor/class types for spawn ----------------------------
    unreal.Actor = type("Actor", (), {})
    unreal.StaticMeshActor = type("StaticMeshActor", (), {})
    unreal.PointLight = type("PointLight", (), {})
    unreal.StaticMeshComponent = type("StaticMeshComponent", (), {})
    unreal.SphereComponent = type("SphereComponent", (), {})

    # --- RigElement types for Control Rig ------------------------------
    unreal.RigElementKey = MagicMock
    unreal.RigControlSettings = MagicMock
    unreal.RigControlValue = MagicMock

    # --- Material types ------------------------------------------------
    unreal.Material = type("Material", (), {})
    unreal.MaterialFactoryNew = MagicMock
    unreal.MeshComponent = type("MeshComponent", (), {})

    # --- Viewport/Subsystem types --------------------------------------
    unreal.LevelEditorSubsystem = type("LevelEditorSubsystem", (), {})
    unreal.UnrealEditorSubsystem = type("UnrealEditorSubsystem", (), {})
    unreal.AutomationLibrary = MagicMock()

    # --- Factory types -------------------------------------------------
    unreal.BlueprintFactory = MagicMock

    # --- Static library classes ----------------------------------------
    # EditorAssetLibrary
    unreal.EditorAssetLibrary = MagicMock()
    unreal.EditorAssetLibrary.load_asset = MagicMock(return_value=None)
    unreal.EditorAssetLibrary.save_asset = MagicMock(return_value=True)
    unreal.EditorAssetLibrary.does_asset_exist = MagicMock(return_value=False)

    # EditorLevelLibrary
    unreal.EditorLevelLibrary = MagicMock()
    unreal.EditorLevelLibrary.get_all_level_actors = MagicMock(return_value=[])
    unreal.EditorLevelLibrary.get_selected_level_actors = MagicMock(return_value=[])
    unreal.EditorLevelLibrary.set_selected_level_actors = MagicMock()
    unreal.EditorLevelLibrary.spawn_actor_from_class = MagicMock(return_value=None)

    # AssetRegistry
    mock_registry = MagicMock()
    mock_registry.get_assets = MagicMock(return_value=[])
    unreal.AssetRegistryHelpers = MagicMock()
    unreal.AssetRegistryHelpers.get_asset_registry = MagicMock(return_value=mock_registry)
    unreal.ARFilter = MagicMock

    # AssetTools
    unreal.AssetToolsHelpers = MagicMock()
    unreal.AssetToolsHelpers.get_asset_tools = MagicMock(return_value=MagicMock())

    # KismetEditorUtilities
    unreal.KismetEditorUtilities = MagicMock()
    unreal.KismetEditorUtilities.compile_blueprint = MagicMock()

    # BlueprintEditorLibrary
    unreal.BlueprintEditorLibrary = MagicMock()
    unreal.BlueprintEditorLibrary.add_variable = MagicMock()
    unreal.BlueprintEditorLibrary.set_variable_category = MagicMock()
    unreal.BlueprintEditorLibrary.get_function_graphs = MagicMock(return_value=[])

    # get_default_object
    unreal.get_default_object = MagicMock(return_value=MagicMock())

    # --- Subsystem accessor -------------------------------------------
    # get_editor_subsystem returns a mock subsystem keyed by class.
    _subsystem_mocks = {}

    def _get_editor_subsystem(subsystem_class):
        if subsystem_class not in _subsystem_mocks:
            _subsystem_mocks[subsystem_class] = MagicMock()
        return _subsystem_mocks[subsystem_class]

    unreal.get_editor_subsystem = _get_editor_subsystem

    # AutomationLibrary screenshot.
    unreal.AutomationLibrary.take_high_res_screenshot = MagicMock()

    # --- Bridge libraries (for AnimBP tests) ---------------------------
    bridge = MagicMock()
    bridge.create_anim_blueprint = MagicMock(return_value=None)
    bridge.add_state_machine = MagicMock(return_value=True)
    bridge.list_state_machines = MagicMock(return_value=[])
    bridge.add_state = MagicMock(return_value=True)
    bridge.set_default_state = MagicMock(return_value=True)
    bridge.list_states = MagicMock(return_value=[])
    bridge.set_state_animation = MagicMock(return_value=True)
    bridge.add_transition = MagicMock(return_value=True)
    bridge.set_auto_transition_rule = MagicMock(return_value=True)
    bridge.compile_anim_blueprint = MagicMock(return_value=True)
    unreal.PyUnrealBlueprintLibrary = bridge

    return unreal


# --- Install/Uninstall Helpers -----------------------------------------

_mock_module = None


def install_mock_unreal():
    """
    Install the mock unreal module into sys.modules.

    Call this before importing any PyUnreal modules in tests.
    Also resets the detection cache so PyUnreal re-checks for
    the unreal module.
    """
    global _mock_module
    _mock_module = _build_mock_unreal()
    sys.modules["unreal"] = _mock_module

    # Reset PyUnreal's detection cache so it picks up the mock.
    from pyunreal.core.detection import reset_cache
    reset_cache()

    return _mock_module


def uninstall_mock_unreal():
    """
    Remove the mock unreal module from sys.modules.

    Call this in tearDown or after tests to clean up.
    """
    global _mock_module
    sys.modules.pop("unreal", None)
    _mock_module = None

    # Reset detection cache.
    from pyunreal.core.detection import reset_cache
    reset_cache()


def get_mock_unreal():
    """
    Return the currently installed mock unreal module.

    :return: The mock unreal module, or None if not installed
    :rtype: MagicMock or None
    """
    return _mock_module
