"""
Tests for pyunreal.control_rig — ControlRig, Control, Null, Bone.
"""

import unittest
from unittest.mock import MagicMock

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


class TestControlRig(unittest.TestCase):
    """Tests for the ControlRig wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_load_success(self):
        """ControlRig.load should load and wrap the asset."""
        import unreal
        from pyunreal.control_rig import ControlRig

        mock_rig = MagicMock()
        mock_rig.__class__ = unreal.ControlRigBlueprint
        mock_rig.get_name.return_value = "CR_Test"
        mock_rig.get_path_name.return_value = "/Game/CR_Test"
        unreal.EditorAssetLibrary.load_asset.return_value = mock_rig

        rig = ControlRig.load("/Game/CR_Test")
        self.assertEqual(rig.name, "CR_Test")

    def test_load_not_found(self):
        """ControlRig.load should raise for missing asset."""
        import unreal
        from pyunreal.control_rig import ControlRig
        from pyunreal.core.errors import AssetNotFoundError

        unreal.EditorAssetLibrary.load_asset.return_value = None

        with self.assertRaises(AssetNotFoundError):
            ControlRig.load("/Game/Missing")

    def test_load_wrong_type(self):
        """ControlRig.load should raise for non-ControlRig assets."""
        import unreal
        from pyunreal.control_rig import ControlRig
        from pyunreal.core.errors import InvalidOperationError

        # Return something that is NOT a ControlRigBlueprint.
        mock_asset = MagicMock()
        mock_asset.__class__ = type("NotAControlRig", (), {})
        unreal.EditorAssetLibrary.load_asset.return_value = mock_asset

        with self.assertRaises(InvalidOperationError):
            ControlRig.load("/Game/WrongType")

    def _make_mock_rig_with_hierarchy(self):
        """Create a mock ControlRig with a fake hierarchy."""
        import unreal
        from pyunreal.control_rig import ControlRig
        from tests.mock_unreal import MockVector, MockQuaternion, MockTransform

        mock_rig = MagicMock()
        mock_rig.get_name.return_value = "CR_Test"
        mock_rig.get_path_name.return_value = "/Game/CR_Test"

        # Build fake hierarchy keys and data.
        keys = ["key_bone_root", "key_ctrl_hips", "key_null_group"]

        # Map each key to type/name/parent.
        type_map = {
            "key_bone_root": "ERigElementType.Bone",
            "key_ctrl_hips": "ERigElementType.Control",
            "key_null_group": "ERigElementType.Null",
        }
        name_map = {
            "key_bone_root": "root",
            "key_ctrl_hips": "Hips",
            "key_null_group": "Group",
        }

        hierarchy = MagicMock()
        hierarchy.get_all_keys.return_value = keys

        def get_type(key):
            return type_map.get(key, "Unknown")

        def get_name(key):
            return name_map.get(key, "")

        def get_parent(key):
            return None

        def get_initial_global_transform(key):
            t = MockTransform()
            return t

        hierarchy.get_type = get_type
        hierarchy.get_name = get_name
        hierarchy.get_parent = get_parent
        hierarchy.get_initial_global_transform = get_initial_global_transform
        mock_rig.hierarchy = hierarchy

        return ControlRig(mock_rig)

    def test_controls_property(self):
        """controls should filter to only Control elements."""
        rig = self._make_mock_rig_with_hierarchy()
        controls = rig.controls

        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0].name, "Hips")

    def test_bones_property(self):
        """bones should filter to only Bone elements."""
        rig = self._make_mock_rig_with_hierarchy()
        bones = rig.bones

        self.assertEqual(len(bones), 1)
        self.assertEqual(bones[0].name, "root")

    def test_nulls_property(self):
        """nulls should filter to only Null elements."""
        rig = self._make_mock_rig_with_hierarchy()
        nulls = rig.nulls

        self.assertEqual(len(nulls), 1)
        self.assertEqual(nulls[0].name, "Group")

    def test_get_control(self):
        """get_control should find a control by name."""
        rig = self._make_mock_rig_with_hierarchy()
        ctrl = rig.get_control("Hips")
        self.assertEqual(ctrl.name, "Hips")

    def test_get_control_not_found(self):
        """get_control should raise for unknown name."""
        from pyunreal.core.errors import InvalidOperationError

        rig = self._make_mock_rig_with_hierarchy()
        with self.assertRaises(InvalidOperationError):
            rig.get_control("DoesNotExist")

    def test_repr(self):
        """ControlRig repr should include the name."""
        import unreal
        from pyunreal.control_rig import ControlRig

        mock_rig = MagicMock()
        mock_rig.get_name.return_value = "CR_Test"
        rig = ControlRig(mock_rig)

        self.assertIn("CR_Test", repr(rig))


class TestControl(unittest.TestCase):
    """Tests for the Control wrapper."""

    def test_properties(self):
        """Control properties should return construction values."""
        from pyunreal.control_rig import Control

        ctrl = Control(MagicMock(), "Hips", "Root", {"location": {"x": 0, "y": 0, "z": 100}})

        self.assertEqual(ctrl.name, "Hips")
        self.assertEqual(ctrl.parent, "Root")
        self.assertEqual(ctrl.transform["location"]["z"], 100)

    def test_repr(self):
        """Control repr should include the name."""
        from pyunreal.control_rig import Control

        ctrl = Control(MagicMock(), "Spine_01")
        self.assertIn("Spine_01", repr(ctrl))


class TestBone(unittest.TestCase):
    """Tests for the Bone data class."""

    def test_properties(self):
        """Bone properties should return construction values."""
        from pyunreal.control_rig import Bone

        bone = Bone("pelvis", "root", {"location": {"x": 0, "y": 0, "z": 90}})

        self.assertEqual(bone.name, "pelvis")
        self.assertEqual(bone.parent, "root")
        self.assertIsNotNone(bone.transform)

    def test_repr(self):
        """Bone repr should include the name."""
        from pyunreal.control_rig import Bone

        bone = Bone("spine_01")
        self.assertIn("spine_01", repr(bone))


class TestNull(unittest.TestCase):
    """Tests for the Null data class."""

    def test_properties(self):
        """Null properties should return construction values."""
        from pyunreal.control_rig import Null

        null = Null("IKGroup", "Root")

        self.assertEqual(null.name, "IKGroup")
        self.assertEqual(null.parent, "Root")

    def test_repr(self):
        """Null repr should include the name."""
        from pyunreal.control_rig import Null

        null = Null("FKGroup")
        self.assertIn("FKGroup", repr(null))


class TestColorPresets(unittest.TestCase):
    """Tests for the color preset system."""

    def test_named_colors(self):
        """Named color presets should return correct RGBA tuples."""
        from pyunreal.control_rig.control import _resolve_color

        self.assertEqual(_resolve_color("red"), (1.0, 0.0, 0.0, 1.0))
        self.assertEqual(_resolve_color("green"), (0.0, 1.0, 0.0, 1.0))
        self.assertEqual(_resolve_color("blue"), (0.0, 0.0, 1.0, 1.0))
        self.assertEqual(_resolve_color("yellow"), (1.0, 1.0, 0.0, 1.0))

    def test_case_insensitive(self):
        """Color lookup should be case-insensitive."""
        from pyunreal.control_rig.control import _resolve_color

        self.assertEqual(_resolve_color("RED"), (1.0, 0.0, 0.0, 1.0))
        self.assertEqual(_resolve_color("Yellow"), (1.0, 1.0, 0.0, 1.0))

    def test_none_returns_none(self):
        """None input should return None."""
        from pyunreal.control_rig.control import _resolve_color

        self.assertIsNone(_resolve_color(None))

    def test_rgb_tuple(self):
        """3-tuple should get alpha appended."""
        from pyunreal.control_rig.control import _resolve_color

        self.assertEqual(_resolve_color((0.5, 0.5, 0.5)), (0.5, 0.5, 0.5, 1.0))

    def test_rgba_tuple(self):
        """4-tuple should pass through."""
        from pyunreal.control_rig.control import _resolve_color

        self.assertEqual(
            _resolve_color((0.1, 0.2, 0.3, 0.4)),
            (0.1, 0.2, 0.3, 0.4)
        )

    def test_unknown_color_raises(self):
        """Unknown color name should raise ValueError."""
        from pyunreal.control_rig.control import _resolve_color

        with self.assertRaises(ValueError):
            _resolve_color("chartreuse")


if __name__ == "__main__":
    unittest.main()
