"""
Tests for pyunreal.anim — AnimBlueprint, StateMachine, State, Transition.
"""

import unittest
from unittest.mock import MagicMock

from tests.mock_unreal import install_mock_unreal, uninstall_mock_unreal


class TestAnimBlueprint(unittest.TestCase):
    """Tests for the AnimBlueprint wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()

    def tearDown(self):
        uninstall_mock_unreal()

    def test_create_success(self):
        """AnimBlueprint.create should call bridge and return a wrapper."""
        import unreal
        from pyunreal.anim import AnimBlueprint

        # Set up the mock to return a fake AnimBP.
        mock_abp = MagicMock()
        mock_abp.get_name.return_value = "ABP_Test"
        unreal.PyUnrealBlueprintLibrary.create_anim_blueprint.return_value = mock_abp

        skeleton = MagicMock()
        abp = AnimBlueprint.create("/Game/Test", "ABP_Test", skeleton)

        self.assertIsInstance(abp, AnimBlueprint)
        self.assertEqual(abp.name, "ABP_Test")
        unreal.PyUnrealBlueprintLibrary.create_anim_blueprint.assert_called_once_with(
            "/Game/Test", "ABP_Test", skeleton
        )

    def test_create_failure_raises(self):
        """AnimBlueprint.create should raise on None return."""
        import unreal
        from pyunreal.anim import AnimBlueprint
        from pyunreal.core.errors import InvalidOperationError

        unreal.PyUnrealBlueprintLibrary.create_anim_blueprint.return_value = None

        with self.assertRaises(InvalidOperationError):
            AnimBlueprint.create("/Game/Test", "ABP_Fail", MagicMock())

    def test_load_success(self):
        """AnimBlueprint.load should load and wrap the asset."""
        import unreal
        from pyunreal.anim import AnimBlueprint

        mock_abp = MagicMock()
        mock_abp.__class__ = unreal.AnimBlueprint
        mock_abp.get_name.return_value = "ABP_Loaded"
        mock_abp.get_path_name.return_value = "/Game/ABP_Loaded"
        unreal.EditorAssetLibrary.load_asset.return_value = mock_abp

        abp = AnimBlueprint.load("/Game/ABP_Loaded")
        self.assertEqual(abp.name, "ABP_Loaded")

    def test_load_not_found(self):
        """AnimBlueprint.load should raise AssetNotFoundError."""
        import unreal
        from pyunreal.anim import AnimBlueprint
        from pyunreal.core.errors import AssetNotFoundError

        unreal.EditorAssetLibrary.load_asset.return_value = None

        with self.assertRaises(AssetNotFoundError):
            AnimBlueprint.load("/Game/Missing")

    def test_add_state_machine(self):
        """add_state_machine should call bridge and return StateMachine."""
        import unreal
        from pyunreal.anim import AnimBlueprint, StateMachine

        mock_abp = MagicMock()
        mock_abp.get_name.return_value = "ABP_Test"
        abp = AnimBlueprint(mock_abp)

        sm = abp.add_state_machine("Locomotion", connect_to_root=True)

        self.assertIsInstance(sm, StateMachine)
        self.assertEqual(sm.name, "Locomotion")
        unreal.PyUnrealBlueprintLibrary.add_state_machine.assert_called_once_with(
            mock_abp, "Locomotion", True
        )

    def test_add_state_machine_failure(self):
        """add_state_machine should raise on False return."""
        import unreal
        from pyunreal.anim import AnimBlueprint
        from pyunreal.core.errors import InvalidOperationError

        mock_abp = MagicMock()
        mock_abp.get_name.return_value = "ABP_Test"
        unreal.PyUnrealBlueprintLibrary.add_state_machine.return_value = False

        abp = AnimBlueprint(mock_abp)
        with self.assertRaises(InvalidOperationError):
            abp.add_state_machine("Duplicate")

    def test_compile(self):
        """compile should call bridge and return True."""
        import unreal
        from pyunreal.anim import AnimBlueprint

        mock_abp = MagicMock()
        mock_abp.get_name.return_value = "ABP_Test"
        abp = AnimBlueprint(mock_abp)

        result = abp.compile()
        self.assertTrue(result)
        unreal.PyUnrealBlueprintLibrary.compile_anim_blueprint.assert_called_once_with(mock_abp)

    def test_state_machines_property(self):
        """state_machines should return a list of StateMachine wrappers."""
        import unreal
        from pyunreal.anim import AnimBlueprint

        mock_abp = MagicMock()
        mock_abp.get_name.return_value = "ABP_Test"
        unreal.PyUnrealBlueprintLibrary.list_state_machines.return_value = ["Loco", "UpperBody"]

        abp = AnimBlueprint(mock_abp)
        sms = abp.state_machines

        self.assertEqual(len(sms), 2)
        self.assertEqual(sms[0].name, "Loco")
        self.assertEqual(sms[1].name, "UpperBody")

    def test_repr(self):
        """AnimBlueprint repr should include the name."""
        import unreal
        from pyunreal.anim import AnimBlueprint

        mock_abp = MagicMock()
        mock_abp.get_name.return_value = "ABP_Test"
        abp = AnimBlueprint(mock_abp)

        self.assertIn("ABP_Test", repr(abp))


class TestStateMachine(unittest.TestCase):
    """Tests for the StateMachine wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()
        import unreal
        from pyunreal.anim import AnimBlueprint

        self.mock_abp = MagicMock()
        self.mock_abp.get_name.return_value = "ABP_Test"
        self.abp = AnimBlueprint(self.mock_abp)

    def tearDown(self):
        uninstall_mock_unreal()

    def test_add_state(self):
        """add_state should call bridge and return State."""
        from pyunreal.anim import State

        sm = self.abp.add_state_machine("Loco")
        state = sm.add_state("Idle")

        self.assertIsInstance(state, State)
        self.assertEqual(state.name, "Idle")

    def test_add_state_with_animation_and_default(self):
        """add_state with animation and default should call all three ops."""
        import unreal

        sm = self.abp.add_state_machine("Loco")
        anim = MagicMock()
        state = sm.add_state("Idle", animation=anim, default=True)

        # Should have called set_state_animation and set_default_state.
        lib = unreal.PyUnrealBlueprintLibrary
        lib.set_state_animation.assert_called_once()
        lib.set_default_state.assert_called_once()

    def test_states_property(self):
        """states should return a list of State wrappers."""
        import unreal

        unreal.PyUnrealBlueprintLibrary.list_states.return_value = ["Idle", "Walk"]

        sm = self.abp.add_state_machine("Loco")
        states = sm.states

        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].name, "Idle")
        self.assertEqual(states[1].name, "Walk")


class TestState(unittest.TestCase):
    """Tests for the State wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()
        import unreal
        from pyunreal.anim import AnimBlueprint

        self.mock_abp = MagicMock()
        self.mock_abp.get_name.return_value = "ABP_Test"
        self.abp = AnimBlueprint(self.mock_abp)
        self.sm = self.abp.add_state_machine("Loco")

    def tearDown(self):
        uninstall_mock_unreal()

    def test_transition_to(self):
        """transition_to should call bridge and return Transition."""
        from pyunreal.anim import Transition

        idle = self.sm.add_state("Idle")
        walk = self.sm.add_state("Walk")

        trans = idle.transition_to(walk, crossfade=0.3)

        self.assertIsInstance(trans, Transition)
        self.assertEqual(trans.from_state, "Idle")
        self.assertEqual(trans.to_state, "Walk")
        self.assertEqual(trans.crossfade, 0.3)

    def test_transition_to_string_target(self):
        """transition_to should accept a string target name."""
        idle = self.sm.add_state("Idle")

        trans = idle.transition_to("Walk", crossfade=0.2)
        self.assertEqual(trans.to_state, "Walk")

    def test_transition_to_wrong_state_machine(self):
        """transition_to should reject states from different SMs."""
        other_sm = self.abp.add_state_machine("Other")
        idle = self.sm.add_state("Idle")
        other_state = other_sm.add_state("Jump")

        with self.assertRaises(ValueError):
            idle.transition_to(other_state)

    def test_auto_transition_to(self):
        """auto_transition_to should set both transition and rule."""
        import unreal

        idle = self.sm.add_state("Idle")
        trans = idle.auto_transition_to("Walk", trigger_time=0.1)

        lib = unreal.PyUnrealBlueprintLibrary
        lib.add_transition.assert_called()
        lib.set_auto_transition_rule.assert_called()

    def test_set_animation_chains(self):
        """set_animation should return self for chaining."""
        idle = self.sm.add_state("Idle")
        result = idle.set_animation(MagicMock())
        self.assertIs(result, idle)

    def test_set_default_chains(self):
        """set_default should return self for chaining."""
        idle = self.sm.add_state("Idle")
        result = idle.set_default()
        self.assertIs(result, idle)


class TestTransition(unittest.TestCase):
    """Tests for the Transition wrapper."""

    def setUp(self):
        self.mock = install_mock_unreal()
        import unreal
        from pyunreal.anim import AnimBlueprint

        self.mock_abp = MagicMock()
        self.mock_abp.get_name.return_value = "ABP_Test"
        self.abp = AnimBlueprint(self.mock_abp)
        self.sm = self.abp.add_state_machine("Loco")

    def tearDown(self):
        uninstall_mock_unreal()

    def test_properties(self):
        """Transition properties should return correct values."""
        from pyunreal.anim import Transition

        trans = Transition(self.sm, "Idle", "Walk", 0.25)
        self.assertEqual(trans.from_state, "Idle")
        self.assertEqual(trans.to_state, "Walk")
        self.assertEqual(trans.crossfade, 0.25)
        self.assertIs(trans.state_machine, self.sm)

    def test_set_auto_rule(self):
        """set_auto_rule should call bridge and return self."""
        from pyunreal.anim import Transition

        trans = Transition(self.sm, "Idle", "Walk", 0.2)
        result = trans.set_auto_rule(trigger_time=0.1)
        self.assertIs(result, trans)

    def test_repr(self):
        """Transition repr should show from/to states."""
        from pyunreal.anim import Transition

        trans = Transition(self.sm, "Idle", "Walk", 0.2)
        r = repr(trans)
        self.assertIn("Idle", r)
        self.assertIn("Walk", r)


if __name__ == "__main__":
    unittest.main()
