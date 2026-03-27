"""
Tests for pyunreal.scene — Actor and scene query functions.
"""

import unittest
from unittest.mock import MagicMock

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


def _make_mock_actor(label, class_name="StaticMeshActor",
                     location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    """
    Create a mock UE actor with the given properties.

    :param str label: Actor label (shown in Outliner)
    :param str class_name: Class name
    :param tuple location: (x, y, z) location
    :param tuple rotation: (pitch, yaw, roll) rotation
    :param tuple scale: (x, y, z) scale
    :return: A MagicMock configured as a UE actor
    """
    from tests.mock_unreal import MockVector, MockRotator

    actor = MagicMock()
    actor.get_actor_label.return_value = label
    actor.get_class.return_value.get_name.return_value = class_name
    actor.get_actor_location.return_value = MockVector(*location)
    actor.get_actor_rotation.return_value = MockRotator(*rotation)
    actor.get_actor_scale3d.return_value = MockVector(*scale)
    actor.is_hidden_ed.return_value = False
    return actor


class TestActor(unittest.TestCase):
    """Tests for the Actor wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_spawn_success(self):
        """Actor.spawn should call spawn_actor_from_class and return wrapper."""
        import unreal
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("MyActor")
        unreal.EditorLevelLibrary.spawn_actor_from_class.return_value = mock_actor

        actor = Actor.spawn("StaticMeshActor", name="MyActor", location=(100, 0, 0))

        self.assertIsInstance(actor, Actor)
        mock_actor.set_actor_label.assert_called_once_with("MyActor")

    def test_spawn_failure_raises(self):
        """Actor.spawn should raise when spawn returns None."""
        import unreal
        from pyunreal.scene import Actor
        from pyunreal.core.errors import InvalidOperationError

        unreal.EditorLevelLibrary.spawn_actor_from_class.return_value = None

        with self.assertRaises(InvalidOperationError):
            Actor.spawn("StaticMeshActor")

    def test_spawn_unknown_class_raises(self):
        """Actor.spawn should raise for unknown class names."""
        import unreal
        from pyunreal.scene import Actor
        from pyunreal.core.errors import InvalidOperationError

        # Remove the class attribute so getattr returns None.
        if hasattr(unreal, "FakeClass"):
            delattr(unreal, "FakeClass")

        with self.assertRaises(InvalidOperationError):
            Actor.spawn("FakeClass")

    def test_location_property(self):
        """location property should return (x, y, z) tuple."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A", location=(10, 20, 30))
        actor = Actor(mock_actor)

        self.assertEqual(actor.location, (10, 20, 30))

    def test_location_setter_tuple(self):
        """location setter should accept (x, y, z) tuple."""
        import unreal
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A")
        actor = Actor(mock_actor)

        actor.location = (100, 200, 300)
        mock_actor.set_actor_location.assert_called_once()

        # Verify the Vector was created with correct values.
        call_args = mock_actor.set_actor_location.call_args
        vec = call_args[0][0]
        self.assertEqual(vec.x, 100)
        self.assertEqual(vec.y, 200)
        self.assertEqual(vec.z, 300)

    def test_location_setter_dict(self):
        """location setter should accept {x, y, z} dict."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A")
        actor = Actor(mock_actor)

        actor.location = {"x": 10, "y": 20, "z": 30}
        mock_actor.set_actor_location.assert_called_once()

    def test_rotation_property(self):
        """rotation property should return (pitch, yaw, roll) tuple."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A", rotation=(10, 45, 0))
        actor = Actor(mock_actor)

        self.assertEqual(actor.rotation, (10, 45, 0))

    def test_scale_property(self):
        """scale property should return (x, y, z) tuple."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A", scale=(2, 2, 2))
        actor = Actor(mock_actor)

        self.assertEqual(actor.scale, (2, 2, 2))

    def test_name_property(self):
        """name property should return the actor label."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("Chair_01")
        actor = Actor(mock_actor)

        self.assertEqual(actor.name, "Chair_01")

    def test_name_setter(self):
        """name setter should call set_actor_label."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("Old")
        actor = Actor(mock_actor)

        actor.name = "New"
        mock_actor.set_actor_label.assert_called_with("New")

    def test_class_name(self):
        """class_name should return the UE class name."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A", class_name="PointLight")
        actor = Actor(mock_actor)

        self.assertEqual(actor.class_name, "PointLight")

    def test_destroy(self):
        """destroy should call destroy_actor and invalidate the wrapper."""
        from pyunreal.scene import Actor
        from pyunreal.core.errors import InvalidOperationError

        mock_actor = _make_mock_actor("A")
        actor = Actor(mock_actor)

        actor.destroy()
        mock_actor.destroy_actor.assert_called_once()

        # After destruction, the wrapper should be invalid.
        with self.assertRaises(InvalidOperationError):
            _ = actor.name

    def test_set_property(self):
        """set_property should delegate to set_editor_property."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A")
        actor = Actor(mock_actor)

        result = actor.set_property("bHidden", True)
        mock_actor.set_editor_property.assert_called_once_with("bHidden", True)
        self.assertIs(result, actor)

    def test_get_property(self):
        """get_property should delegate to get_editor_property."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A")
        mock_actor.get_editor_property.return_value = 42
        actor = Actor(mock_actor)

        val = actor.get_property("SomeValue")
        self.assertEqual(val, 42)

    def test_repr_live(self):
        """repr of a live actor should show label and class."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("Chair_01", "StaticMeshActor")
        actor = Actor(mock_actor)

        r = repr(actor)
        self.assertIn("Chair_01", r)
        self.assertIn("StaticMeshActor", r)

    def test_repr_destroyed(self):
        """repr of a destroyed actor should indicate destruction."""
        from pyunreal.scene import Actor

        mock_actor = _make_mock_actor("A")
        actor = Actor(mock_actor)
        actor.destroy()

        self.assertIn("destroyed", repr(actor))


class TestSceneQueries(unittest.TestCase):
    """Tests for scene-level query functions."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_all_returns_wrapped_actors(self):
        """scene.all() should return Actor wrappers for all level actors."""
        import unreal
        from pyunreal.scene import scene, Actor

        actors = [_make_mock_actor("A"), _make_mock_actor("B")]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = actors

        result = scene.all()
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Actor)

    def test_selected(self):
        """scene.selected() should return selected actor wrappers."""
        import unreal
        from pyunreal.scene import scene, Actor

        actors = [_make_mock_actor("Selected")]
        unreal.EditorLevelLibrary.get_selected_level_actors.return_value = actors

        result = scene.selected()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Selected")

    def test_find_by_pattern(self):
        """scene.find() should match actor labels by glob pattern."""
        import unreal
        from pyunreal.scene import scene

        actors = [
            _make_mock_actor("Chair_01"),
            _make_mock_actor("Chair_02"),
            _make_mock_actor("Table_01"),
        ]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = actors

        result = scene.find("Chair_*")
        self.assertEqual(len(result), 2)

    def test_find_case_insensitive(self):
        """scene.find() should be case-insensitive."""
        import unreal
        from pyunreal.scene import scene

        actors = [_make_mock_actor("MyActor")]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = actors

        result = scene.find("myactor")
        self.assertEqual(len(result), 1)

    def test_find_by_type(self):
        """scene.find_by_type() should match by class name."""
        import unreal
        from pyunreal.scene import scene

        actors = [
            _make_mock_actor("L1", "PointLight"),
            _make_mock_actor("L2", "PointLight"),
            _make_mock_actor("M1", "StaticMeshActor"),
        ]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = actors

        result = scene.find_by_type("PointLight")
        self.assertEqual(len(result), 2)

    def test_find_by_type_case_insensitive(self):
        """scene.find_by_type() should be case-insensitive."""
        import unreal
        from pyunreal.scene import scene

        actors = [_make_mock_actor("L1", "PointLight")]
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = actors

        result = scene.find_by_type("pointlight")
        self.assertEqual(len(result), 1)

    def test_select_with_actor_wrappers(self):
        """scene.select() should accept Actor wrapper objects."""
        import unreal
        from pyunreal.scene import scene, Actor

        mock_actor = _make_mock_actor("A")
        actor = Actor(mock_actor)

        scene.select([actor])
        unreal.EditorLevelLibrary.set_selected_level_actors.assert_called_once_with(
            [mock_actor]
        )

    def test_select_with_strings(self):
        """scene.select() should accept label strings."""
        import unreal
        from pyunreal.scene import scene

        mock_actor = _make_mock_actor("FindMe")
        unreal.EditorLevelLibrary.get_all_level_actors.return_value = [mock_actor]

        scene.select(["FindMe"])
        unreal.EditorLevelLibrary.set_selected_level_actors.assert_called_once()

        # Verify the correct actor was found and passed.
        call_args = unreal.EditorLevelLibrary.set_selected_level_actors.call_args
        self.assertEqual(call_args[0][0], [mock_actor])


if __name__ == "__main__":
    unittest.main()
