"""
Tests for pyunreal.core — base classes, detection, errors, and utilities.
"""

import unittest
from unittest.mock import MagicMock

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


class TestErrors(unittest.TestCase):
    """Tests for the custom exception hierarchy."""

    def test_all_errors_inherit_from_base(self):
        """Every PyUnreal error should be catchable via PyUnrealError."""
        from pyunreal.core.errors import (
            PyUnrealError, PyUnrealEnvironmentError,
            BridgeNotAvailableError, AssetNotFoundError,
            InvalidOperationError,
        )

        self.assertTrue(issubclass(PyUnrealEnvironmentError, PyUnrealError))
        self.assertTrue(issubclass(BridgeNotAvailableError, PyUnrealError))
        self.assertTrue(issubclass(AssetNotFoundError, PyUnrealError))
        self.assertTrue(issubclass(InvalidOperationError, PyUnrealError))

    def test_asset_not_found_stores_path(self):
        """AssetNotFoundError should store the asset path."""
        from pyunreal.core.errors import AssetNotFoundError

        err = AssetNotFoundError("/Game/Missing")
        self.assertEqual(err.asset_path, "/Game/Missing")
        self.assertIn("/Game/Missing", str(err))

    def test_bridge_not_available_includes_install_guidance(self):
        """BridgeNotAvailableError message should include install URLs."""
        from pyunreal.core.errors import BridgeNotAvailableError

        err = BridgeNotAvailableError("add_state_machine")
        msg = str(err)
        self.assertIn("add_state_machine", msg)
        self.assertIn("PyUnrealBridge", msg)
        self.assertIn("mcaeditor.com", msg)

    def test_backward_compat_alias(self):
        """MCAScriptingNotAvailableError should be an alias."""
        from pyunreal.core.errors import (
            MCAScriptingNotAvailableError, BridgeNotAvailableError,
        )
        self.assertIs(MCAScriptingNotAvailableError, BridgeNotAvailableError)


class TestBaseWrapper(unittest.TestCase):
    """Tests for UnrealObjectWrapper."""

    def test_validate_raises_on_none(self):
        """_validate should raise InvalidOperationError for None asset."""
        from pyunreal.core.base import UnrealObjectWrapper
        from pyunreal.core.errors import InvalidOperationError

        wrapper = UnrealObjectWrapper(None)
        with self.assertRaises(InvalidOperationError):
            wrapper._validate()

    def test_validate_passes_with_asset(self):
        """_validate should not raise when asset is set."""
        from pyunreal.core.base import UnrealObjectWrapper

        wrapper = UnrealObjectWrapper("some_object")
        wrapper._validate()  # Should not raise.

    def test_ue_object_property(self):
        """ue_object should return the underlying asset."""
        from pyunreal.core.base import UnrealObjectWrapper

        wrapper = UnrealObjectWrapper("test_asset")
        self.assertEqual(wrapper.ue_object, "test_asset")

    def test_equality(self):
        """Two wrappers with the same asset should be equal."""
        from pyunreal.core.base import UnrealObjectWrapper

        a = UnrealObjectWrapper("same")
        b = UnrealObjectWrapper("same")
        c = UnrealObjectWrapper("different")

        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(a.__eq__("not_a_wrapper"), NotImplemented)


class TestDetection(unittest.TestCase):
    """Tests for the runtime detection system."""

    def setUp(self):
        from pyunreal.core.detection import reset_cache
        reset_cache()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_unreal_not_available_outside_ue(self):
        """Without mock, unreal should not be available."""
        from pyunreal.core.detection import _unreal_available
        self.assertFalse(_unreal_available())

    def test_unreal_available_with_mock(self):
        """With mock installed, unreal should be detected."""
        install_mock_unreal()
        from pyunreal.core.detection import _unreal_available
        self.assertTrue(_unreal_available())

    def test_bridge_available_with_mock(self):
        """Mock installs PyUnrealBlueprintLibrary, so bridge should be found."""
        install_mock_unreal()
        from pyunreal.core.detection import _bridge_available
        self.assertTrue(_bridge_available())

    def test_require_unreal_raises_outside_ue(self):
        """require_unreal should raise outside UE."""
        from pyunreal.core.detection import require_unreal
        from pyunreal.core.errors import PyUnrealEnvironmentError

        with self.assertRaises(PyUnrealEnvironmentError):
            require_unreal()

    def test_require_unreal_passes_with_mock(self):
        """require_unreal should pass with mock installed."""
        install_mock_unreal()
        from pyunreal.core.detection import require_unreal
        require_unreal()  # Should not raise.

    def test_get_bridge_library(self):
        """get_bridge_library should return the bridge class."""
        install_mock_unreal()
        from pyunreal.core.detection import get_bridge_library
        import unreal

        lib = get_bridge_library()
        self.assertIs(lib, unreal.PyUnrealBlueprintLibrary)

    def test_cache_reset(self):
        """reset_cache should clear all cached detection results."""
        install_mock_unreal()
        from pyunreal.core.detection import _cache, reset_cache

        # Cache should have entries after detection.
        from pyunreal.core.detection import _unreal_available
        _unreal_available()
        self.assertIn("unreal", _cache)

        reset_cache()
        self.assertEqual(len(_cache), 0)


class TestUtils(unittest.TestCase):
    """Tests for core utility functions."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_load_success(self):
        """load() should return the asset when found."""
        from pyunreal.core.utils import load
        import unreal

        mock_asset = MagicMock()
        unreal.EditorAssetLibrary.load_asset.return_value = mock_asset

        result = load("/Game/Test/Asset")
        self.assertIs(result, mock_asset)
        unreal.EditorAssetLibrary.load_asset.assert_called_with("/Game/Test/Asset")

    def test_load_not_found(self):
        """load() should raise AssetNotFoundError when asset is None."""
        from pyunreal.core.utils import load
        from pyunreal.core.errors import AssetNotFoundError
        import unreal

        unreal.EditorAssetLibrary.load_asset.return_value = None

        with self.assertRaises(AssetNotFoundError):
            load("/Game/Missing")

    def test_asset_exists(self):
        """asset_exists() should delegate to EditorAssetLibrary."""
        from pyunreal.core.utils import asset_exists
        import unreal

        unreal.EditorAssetLibrary.does_asset_exist.return_value = True
        self.assertTrue(asset_exists("/Game/Exists"))

        unreal.EditorAssetLibrary.does_asset_exist.return_value = False
        self.assertFalse(asset_exists("/Game/Missing"))


if __name__ == "__main__":
    unittest.main()
