"""
Tests for pyunreal.material — Material wrapper.
"""

import unittest
from unittest.mock import MagicMock

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


class TestMaterialCreate(unittest.TestCase):
    """Tests for Material.create class method."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_create_success(self):
        """create() should return a Material wrapper on success."""
        import unreal
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Metal"
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        tools.create_asset.return_value = mock_mat

        mat = Material.create("M_Metal")

        self.assertIsInstance(mat, Material)
        tools.create_asset.assert_called_once()
        unreal.EditorAssetLibrary.save_asset.assert_called()

    def test_create_already_exists_raises(self):
        """create() should raise if the asset already exists."""
        import unreal
        from pyunreal.material import Material
        from pyunreal.core.errors import InvalidOperationError

        unreal.EditorAssetLibrary.does_asset_exist.return_value = True

        with self.assertRaises(InvalidOperationError):
            Material.create("M_Existing")

    def test_create_failure_raises(self):
        """create() should raise when create_asset returns None."""
        import unreal
        from pyunreal.material import Material
        from pyunreal.core.errors import InvalidOperationError

        tools = unreal.AssetToolsHelpers.get_asset_tools()
        tools.create_asset.return_value = None

        with self.assertRaises(InvalidOperationError):
            Material.create("M_Bad")

    def test_create_custom_package_path(self):
        """create() should use the provided package_path."""
        import unreal
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Test"
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        tools.create_asset.return_value = mock_mat

        Material.create("M_Test", package_path="/Game/Custom")

        call_args = tools.create_asset.call_args
        self.assertEqual(call_args[0][1], "/Game/Custom")


class TestMaterialLoad(unittest.TestCase):
    """Tests for Material.load class method."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_load_success(self):
        """load() should return a Material wrapper for an existing asset."""
        import unreal
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Loaded"
        unreal.EditorAssetLibrary.load_asset.return_value = mock_mat

        mat = Material.load("/Game/Materials/M_Loaded")

        self.assertIsInstance(mat, Material)

    def test_load_not_found_raises(self):
        """load() should raise AssetNotFoundError if the asset is not found."""
        import unreal
        from pyunreal.material import Material
        from pyunreal.core.errors import AssetNotFoundError

        unreal.EditorAssetLibrary.load_asset.return_value = None

        with self.assertRaises(AssetNotFoundError):
            Material.load("/Game/Materials/Missing")


class TestMaterialParams(unittest.TestCase):
    """Tests for set_param and get_param."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def _make_material(self):
        """Create a Material wrapper with a mock UE object."""
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Test"
        mock_mat.get_path_name.return_value = "/Game/Materials/M_Test"
        return Material(mock_mat), mock_mat

    def test_set_scalar_param(self):
        """set_param with float should call set_editor_property with a float."""
        mat, mock_mat = self._make_material()

        result = mat.set_param("Roughness", 0.5)

        mock_mat.set_editor_property.assert_called_once_with("Roughness", 0.5)
        # Should return self for chaining.
        self.assertIs(result, mat)

    def test_set_color_param_rgba(self):
        """set_param with 4-tuple should create a LinearColor."""
        mat, mock_mat = self._make_material()

        mat.set_param("BaseColor", (1.0, 0.5, 0.0, 1.0))

        call_args = mock_mat.set_editor_property.call_args
        self.assertEqual(call_args[0][0], "BaseColor")
        # The second argument should be a LinearColor.
        color = call_args[0][1]
        self.assertAlmostEqual(color.r, 1.0)
        self.assertAlmostEqual(color.g, 0.5)
        self.assertAlmostEqual(color.b, 0.0)
        self.assertAlmostEqual(color.a, 1.0)

    def test_set_color_param_rgb(self):
        """set_param with 3-tuple should default alpha to 1.0."""
        mat, mock_mat = self._make_material()

        mat.set_param("BaseColor", (0.8, 0.2, 0.1))

        call_args = mock_mat.set_editor_property.call_args
        color = call_args[0][1]
        self.assertAlmostEqual(color.a, 1.0)

    def test_set_param_int_converted_to_float(self):
        """set_param with int should convert to float."""
        mat, mock_mat = self._make_material()

        mat.set_param("Metallic", 1)

        call_args = mock_mat.set_editor_property.call_args
        self.assertEqual(call_args[0][1], 1.0)
        self.assertIsInstance(call_args[0][1], float)

    def test_set_param_failure_raises(self):
        """set_param should raise if set_editor_property fails."""
        from pyunreal.core.errors import InvalidOperationError

        mat, mock_mat = self._make_material()
        mock_mat.set_editor_property.side_effect = RuntimeError("bad param")

        with self.assertRaises(InvalidOperationError):
            mat.set_param("FakeParam", 0.5)

    def test_get_param_success(self):
        """get_param should delegate to get_editor_property."""
        mat, mock_mat = self._make_material()
        mock_mat.get_editor_property.return_value = 0.3

        val = mat.get_param("Roughness")

        self.assertEqual(val, 0.3)

    def test_get_param_failure_raises(self):
        """get_param should raise if get_editor_property fails."""
        from pyunreal.core.errors import InvalidOperationError

        mat, mock_mat = self._make_material()
        mock_mat.get_editor_property.side_effect = RuntimeError("no such param")

        with self.assertRaises(InvalidOperationError):
            mat.get_param("FakeParam")

    def test_set_param_saves_asset(self):
        """set_param should save the asset after setting."""
        import unreal

        mat, mock_mat = self._make_material()
        mat.set_param("Roughness", 0.5)

        unreal.EditorAssetLibrary.save_asset.assert_called()


class TestMaterialAssign(unittest.TestCase):
    """Tests for Material.assign_to."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def _make_material(self):
        """Create a Material wrapper."""
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Test"
        mock_mat.get_path_name.return_value = "/Game/Materials/M_Test"
        return Material(mock_mat), mock_mat

    def test_assign_to_actor_by_name(self):
        """assign_to should find actor by label and set material."""
        import unreal

        mat, mock_mat = self._make_material()

        # Set up a mock actor with a static mesh component.
        mock_actor = MagicMock()
        mock_actor.get_actor_label.return_value = "Chair_01"
        mock_mesh = MagicMock()
        mock_actor.get_components_by_class.return_value = [mock_mesh]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = [mock_actor]

        result = mat.assign_to("Chair_01")

        mock_mesh.set_material.assert_called_once_with(0, mock_mat)
        self.assertIs(result, mat)

    def test_assign_to_with_slot(self):
        """assign_to should use the provided slot index."""
        import unreal

        mat, mock_mat = self._make_material()

        mock_actor = MagicMock()
        mock_actor.get_actor_label.return_value = "Chair_01"
        mock_mesh = MagicMock()
        mock_actor.get_components_by_class.return_value = [mock_mesh]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = [mock_actor]

        mat.assign_to("Chair_01", slot=2)

        mock_mesh.set_material.assert_called_once_with(2, mock_mat)

    def test_assign_to_actor_not_found_raises(self):
        """assign_to should raise if the actor is not found."""
        import unreal
        from pyunreal.core.errors import InvalidOperationError

        mat, _ = self._make_material()
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = []

        with self.assertRaises(InvalidOperationError):
            mat.assign_to("Missing_Actor")

    def test_assign_to_no_mesh_raises(self):
        """assign_to should raise if actor has no mesh component."""
        import unreal
        from pyunreal.core.errors import InvalidOperationError

        mat, _ = self._make_material()

        mock_actor = MagicMock()
        mock_actor.get_actor_label.return_value = "NoMesh"
        # Return empty components for both StaticMesh and Mesh queries.
        mock_actor.get_components_by_class.return_value = []
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = [mock_actor]

        with self.assertRaises(InvalidOperationError):
            mat.assign_to("NoMesh")


class TestMaterialProperties(unittest.TestCase):
    """Tests for Material read-only properties."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_name_property(self):
        """name should return the asset name."""
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Gold"
        mat = Material(mock_mat)

        self.assertEqual(mat.name, "M_Gold")

    def test_path_property(self):
        """path should return the full content path."""
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_path_name.return_value = "/Game/Materials/M_Gold"
        mat = Material(mock_mat)

        self.assertEqual(mat.path, "/Game/Materials/M_Gold")

    def test_repr(self):
        """repr should show the material name."""
        from pyunreal.material import Material

        mock_mat = MagicMock()
        mock_mat.get_name.return_value = "M_Gold"
        mat = Material(mock_mat)

        self.assertIn("M_Gold", repr(mat))


if __name__ == "__main__":
    unittest.main()
