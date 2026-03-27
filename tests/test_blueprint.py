"""
Tests for pyunreal.blueprint — Blueprint, Component, Variable.
"""

import unittest
from unittest.mock import MagicMock

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


class TestBlueprint(unittest.TestCase):
    """Tests for the Blueprint wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_create_success(self):
        """Blueprint.create should create and return a wrapper."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_bp.get_path_name.return_value = "/Game/BP_Test"
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        asset_tools.create_asset.return_value = mock_bp

        bp = Blueprint.create("/Game/Blueprints", "BP_Test", parent="Actor")

        self.assertIsInstance(bp, Blueprint)
        self.assertEqual(bp.name, "BP_Test")

    def test_create_duplicate_raises(self):
        """Blueprint.create should raise if asset already exists."""
        import unreal
        from pyunreal.blueprint import Blueprint
        from pyunreal.core.errors import InvalidOperationError

        unreal.EditorAssetLibrary.does_asset_exist.return_value = True

        with self.assertRaises(InvalidOperationError):
            Blueprint.create("/Game/Blueprints", "BP_Exists")

    def test_create_unknown_parent_raises(self):
        """Blueprint.create should raise for unknown parent class."""
        import unreal
        from pyunreal.blueprint import Blueprint
        from pyunreal.core.errors import InvalidOperationError

        # Remove the attribute so getattr returns None.
        if hasattr(unreal, "NonExistentClass"):
            delattr(unreal, "NonExistentClass")

        with self.assertRaises(InvalidOperationError):
            Blueprint.create("/Game/Blueprints", "BP_Bad", parent="NonExistentClass")

    def test_load_success(self):
        """Blueprint.load should load and wrap the asset."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.__class__ = unreal.Blueprint
        mock_bp.get_name.return_value = "BP_Loaded"
        mock_bp.get_path_name.return_value = "/Game/BP_Loaded"
        unreal.EditorAssetLibrary.load_asset.return_value = mock_bp

        bp = Blueprint.load("/Game/BP_Loaded")
        self.assertEqual(bp.name, "BP_Loaded")

    def test_load_not_found(self):
        """Blueprint.load should raise for missing asset."""
        import unreal
        from pyunreal.blueprint import Blueprint
        from pyunreal.core.errors import AssetNotFoundError

        unreal.EditorAssetLibrary.load_asset.return_value = None

        with self.assertRaises(AssetNotFoundError):
            Blueprint.load("/Game/Missing")

    def test_parent_class_property(self):
        """parent_class should return the parent class name."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_parent = MagicMock()
        mock_parent.get_name.return_value = "Actor"
        mock_gen = MagicMock()
        mock_gen.get_super_class.return_value = mock_parent
        mock_bp.generated_class.return_value = mock_gen

        bp = Blueprint(mock_bp)
        self.assertEqual(bp.parent_class, "Actor")

    def test_add_variable(self):
        """add_variable should call BlueprintEditorLibrary and return Variable."""
        import unreal
        from pyunreal.blueprint import Blueprint, Variable

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_bp.get_path_name.return_value = "/Game/BP_Test"
        mock_gen = MagicMock()
        mock_bp.generated_class.return_value = mock_gen

        bp = Blueprint(mock_bp)
        var = bp.add_variable("Score", "int", default=100, category="Gameplay")

        self.assertIsInstance(var, Variable)
        self.assertEqual(var.name, "Score")
        self.assertEqual(var.var_type, "IntProperty")
        unreal.BlueprintEditorLibrary.add_variable.assert_called_once()

    def test_add_component(self):
        """add_component should create an SCS node."""
        import unreal
        from pyunreal.blueprint import Blueprint, Component
        from tests.mock_unreal import MockSCSNode

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_bp.get_path_name.return_value = "/Game/BP_Test"

        # Set up SCS mock.
        mock_scs = MagicMock()
        mock_node = MockSCSNode("MyMesh", "StaticMeshComponent")
        mock_scs.create_node.return_value = mock_node
        mock_scs.get_all_nodes.return_value = []
        mock_bp.simple_construction_script = mock_scs

        bp = Blueprint(mock_bp)
        comp = bp.add_component("StaticMeshComponent", name="MyMesh")

        self.assertIsInstance(comp, Component)
        self.assertEqual(comp.name, "MyMesh")
        self.assertEqual(comp.component_class, "StaticMeshComponent")

    def test_compile(self):
        """compile should call KismetEditorUtilities and return True."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_bp.get_path_name.return_value = "/Game/BP_Test"
        mock_bp.get_editor_property.return_value = "BlueprintStatus.BS_UpToDate"

        bp = Blueprint(mock_bp)
        result = bp.compile()

        self.assertTrue(result)
        unreal.KismetEditorUtilities.compile_blueprint.assert_called_once_with(mock_bp)

    def test_set_default(self):
        """set_default should write to the CDO."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_bp.get_path_name.return_value = "/Game/BP_Test"
        mock_gen = MagicMock()
        mock_cdo = MagicMock()
        mock_bp.generated_class.return_value = mock_gen
        unreal.get_default_object.return_value = mock_cdo

        bp = Blueprint(mock_bp)
        result = bp.set_default("MaxHealth", 100)

        self.assertIs(result, bp)
        mock_cdo.set_editor_property.assert_called_once_with("MaxHealth", 100)

    def test_get_default(self):
        """get_default should read from the CDO."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        mock_gen = MagicMock()
        mock_cdo = MagicMock()
        mock_cdo.get_editor_property.return_value = 42
        mock_bp.generated_class.return_value = mock_gen
        unreal.get_default_object.return_value = mock_cdo

        bp = Blueprint(mock_bp)
        val = bp.get_default("Score")
        self.assertEqual(val, 42)

    def test_repr(self):
        """Blueprint repr should include the name."""
        import unreal
        from pyunreal.blueprint import Blueprint

        mock_bp = MagicMock()
        mock_bp.get_name.return_value = "BP_Test"
        bp = Blueprint(mock_bp)

        self.assertIn("BP_Test", repr(bp))


class TestComponent(unittest.TestCase):
    """Tests for the Component data class."""

    def test_properties(self):
        """Component properties should return construction values."""
        from pyunreal.blueprint import Component

        comp = Component(
            "MyMesh", "StaticMeshComponent", "Root",
            location={"x": 1, "y": 2, "z": 3},
            rotation={"pitch": 0, "yaw": 45, "roll": 0},
            scale={"x": 1, "y": 1, "z": 1},
        )

        self.assertEqual(comp.name, "MyMesh")
        self.assertEqual(comp.component_class, "StaticMeshComponent")
        self.assertEqual(comp.parent, "Root")
        self.assertEqual(comp.location["x"], 1)
        self.assertEqual(comp.rotation["yaw"], 45)

    def test_repr(self):
        """Component repr should show name and class."""
        from pyunreal.blueprint import Component

        comp = Component("Mesh", "StaticMeshComponent")
        r = repr(comp)
        self.assertIn("Mesh", r)
        self.assertIn("StaticMeshComponent", r)


class TestVariable(unittest.TestCase):
    """Tests for the Variable wrapper."""

    def test_properties(self):
        """Variable properties should return construction values."""
        from pyunreal.blueprint import Variable

        var = Variable(MagicMock(), "Score", "IntProperty", 100)

        self.assertEqual(var.name, "Score")
        self.assertEqual(var.var_type, "IntProperty")
        self.assertEqual(var.default, 100)

    def test_repr(self):
        """Variable repr should show name and type."""
        from pyunreal.blueprint import Variable

        var = Variable(MagicMock(), "Health", "FloatProperty")
        r = repr(var)
        self.assertIn("Health", r)
        self.assertIn("FloatProperty", r)


class TestTypeMapping(unittest.TestCase):
    """Tests for the type mapping utility."""

    def test_friendly_names(self):
        """Common type names should map to UE property types."""
        from pyunreal.blueprint.variable import _map_type

        self.assertEqual(_map_type("int"), "IntProperty")
        self.assertEqual(_map_type("bool"), "BoolProperty")
        self.assertEqual(_map_type("float"), "FloatProperty")
        self.assertEqual(_map_type("str"), "StrProperty")
        self.assertEqual(_map_type("string"), "StrProperty")
        self.assertEqual(_map_type("double"), "DoubleProperty")
        self.assertEqual(_map_type("name"), "NameProperty")
        self.assertEqual(_map_type("text"), "TextProperty")

    def test_case_insensitive(self):
        """Type mapping should be case-insensitive."""
        from pyunreal.blueprint.variable import _map_type

        self.assertEqual(_map_type("INT"), "IntProperty")
        self.assertEqual(_map_type("Bool"), "BoolProperty")

    def test_passthrough(self):
        """Already-qualified types should pass through unchanged."""
        from pyunreal.blueprint.variable import _map_type

        self.assertEqual(_map_type("IntProperty"), "IntProperty")
        self.assertEqual(_map_type("StructProperty"), "StructProperty")

    def test_unknown_passthrough(self):
        """Unknown types should pass through as-is."""
        from pyunreal.blueprint.variable import _map_type

        self.assertEqual(_map_type("CustomThing"), "CustomThing")


if __name__ == "__main__":
    unittest.main()
