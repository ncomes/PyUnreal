"""
Tests for pyunreal.viewport — viewport operations.
"""

import unittest
from unittest.mock import MagicMock, call

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


def _make_mock_actor(label):
    """
    Create a mock UE actor with the given label.

    :param str label: Actor label
    :return: A MagicMock configured as a UE actor
    """
    actor = MagicMock()
    actor.get_actor_label.return_value = label
    return actor


class TestViewportFocus(unittest.TestCase):
    """Tests for viewport.focus()."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_focus_by_label(self):
        """focus() should find actor by label and pilot to it."""
        import unreal
        from pyunreal.viewport import viewport

        mock_actor = _make_mock_actor("Chair_01")
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = [mock_actor]

        viewport.focus("Chair_01")

        # Should have called pilot_level_actor on the subsystem.
        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        subsystem.pilot_level_actor.assert_called_once_with(mock_actor)

    def test_focus_actor_not_found_raises(self):
        """focus() should raise AssetNotFoundError for missing actors."""
        import unreal
        from pyunreal.viewport import viewport
        from pyunreal.core.errors import AssetNotFoundError

        unreal.EditorLevelLibrary.get_all_level_actors.return_value = []

        with self.assertRaises(AssetNotFoundError):
            viewport.focus("Missing_Actor")

    def test_focus_with_raw_actor(self):
        """focus() should accept a raw UE actor object."""
        import unreal
        from pyunreal.viewport import viewport

        mock_actor = _make_mock_actor("Direct")

        viewport.focus(mock_actor)

        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        subsystem.pilot_level_actor.assert_called_once_with(mock_actor)

    def test_focus_with_actor_wrapper(self):
        """focus() should accept an Actor wrapper."""
        import unreal
        from pyunreal.viewport import viewport
        from pyunreal.scene.actor import Actor

        mock_actor = _make_mock_actor("Wrapped")
        mock_actor.get_class.return_value.get_name.return_value = "StaticMeshActor"
        from tests.mock_unreal import MockVector, MockRotator
        mock_actor.get_actor_location.return_value = MockVector()
        mock_actor.get_actor_rotation.return_value = MockRotator()
        mock_actor.get_actor_scale3d.return_value = MockVector(1, 1, 1)
        mock_actor.is_hidden_ed.return_value = False

        wrapper = Actor(mock_actor)
        viewport.focus(wrapper)

        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        subsystem.pilot_level_actor.assert_called_once_with(mock_actor)


class TestViewportCamera(unittest.TestCase):
    """Tests for viewport.set_camera() and get_camera()."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_set_camera_location_and_rotation(self):
        """set_camera() should create Vector and Rotator from tuples."""
        import unreal
        from pyunreal.viewport import viewport

        viewport.set_camera(location=(100, 200, 300), rotation=(10, 20, 30))

        subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        subsystem.set_level_viewport_camera_info.assert_called_once()

        # Verify the Vector and Rotator values.
        call_args = subsystem.set_level_viewport_camera_info.call_args
        vec = call_args[0][0]
        rot = call_args[0][1]
        self.assertEqual(vec.x, 100)
        self.assertEqual(vec.y, 200)
        self.assertEqual(vec.z, 300)
        self.assertEqual(rot.pitch, 10)
        self.assertEqual(rot.yaw, 20)
        self.assertEqual(rot.roll, 30)

    def test_set_camera_location_only(self):
        """set_camera() with only location should use zero rotation."""
        import unreal
        from pyunreal.viewport import viewport

        viewport.set_camera(location=(500, 0, 0))

        subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        call_args = subsystem.set_level_viewport_camera_info.call_args
        rot = call_args[0][1]
        self.assertEqual(rot.pitch, 0)

    def test_set_camera_rotation_only(self):
        """set_camera() with only rotation should use zero location."""
        import unreal
        from pyunreal.viewport import viewport

        viewport.set_camera(rotation=(0, -90, 0))

        subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        call_args = subsystem.set_level_viewport_camera_info.call_args
        vec = call_args[0][0]
        self.assertEqual(vec.x, 0)

    def test_get_camera_success(self):
        """get_camera() should return location and rotation dicts."""
        import unreal
        from pyunreal.viewport import viewport
        from tests.mock_unreal import MockVector, MockRotator

        subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        subsystem.get_level_viewport_camera_info.return_value = (
            True,
            MockVector(100, 200, 300),
            MockRotator(10, 20, 30),
        )

        result = viewport.get_camera()

        self.assertEqual(result["location"], (100, 200, 300))
        self.assertEqual(result["rotation"], (10, 20, 30))

    def test_get_camera_no_viewport_raises(self):
        """get_camera() should raise when no active viewport."""
        import unreal
        from pyunreal.viewport import viewport
        from pyunreal.core.errors import InvalidOperationError

        subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        subsystem.get_level_viewport_camera_info.return_value = (False, None, None)

        with self.assertRaises(InvalidOperationError):
            viewport.get_camera()


class TestViewportScreenshot(unittest.TestCase):
    """Tests for viewport.screenshot()."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_screenshot_default_size(self):
        """screenshot() should use default 1920x1080."""
        import unreal
        from pyunreal.viewport import viewport

        viewport.screenshot("C:/Shots/test.png")

        unreal.AutomationLibrary.take_high_res_screenshot.assert_called_once_with(
            1920, 1080, "C:/Shots/test.png"
        )

    def test_screenshot_custom_size(self):
        """screenshot() should accept custom width and height."""
        import unreal
        from pyunreal.viewport import viewport

        viewport.screenshot("C:/Shots/wide.png", width=3840, height=2160)

        unreal.AutomationLibrary.take_high_res_screenshot.assert_called_once_with(
            3840, 2160, "C:/Shots/wide.png"
        )

    def test_screenshot_failure_raises(self):
        """screenshot() should raise on failure."""
        import unreal
        from pyunreal.viewport import viewport
        from pyunreal.core.errors import InvalidOperationError

        unreal.AutomationLibrary.take_high_res_screenshot.side_effect = (
            RuntimeError("render failed")
        )

        with self.assertRaises(InvalidOperationError):
            viewport.screenshot("C:/Shots/fail.png")


if __name__ == "__main__":
    unittest.main()
