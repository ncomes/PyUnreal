"""
PyUnreal Example -- Create a locomotion AnimBP from scratch.

Demonstrates the full AnimBlueprint workflow:
    1. Load a skeleton asset
    2. Create a new AnimBP targeting that skeleton
    3. Add a state machine with Idle, Walk, Run states
    4. Wire transitions between all states
    5. Set auto-transition rules
    6. Compile the AnimBP

Prerequisites:
    - Unreal Engine editor open with a project loaded
    - MCA Editor plugin loaded (for AnimBP graph editing)
    - Skeleton and animation assets at the paths below

Usage:
    Run this script in Unreal Engine's Python console, or execute
    via MCA Editor's code editor.

Side effects:
    - Creates a new AnimBP asset in the Content Browser
"""

from pyunreal import load
from pyunreal.anim import AnimBlueprint


# --- Configuration -----------------------------------------------------
# Update these paths to match your project's assets.

SKELETON_PATH = "/Game/Characters/Mannequin/Mesh/SK_Mannequin"
PACKAGE_PATH = "/Game/AnimBlueprints"
ABP_NAME = "ABP_Locomotion"

IDLE_ANIM_PATH = "/Game/Characters/Mannequin/Animations/ThirdPersonIdle"
WALK_ANIM_PATH = "/Game/Characters/Mannequin/Animations/ThirdPersonWalk"
RUN_ANIM_PATH = "/Game/Characters/Mannequin/Animations/ThirdPersonRun"


# --- Main Script -------------------------------------------------------

def main():
    """Create a locomotion AnimBP with three states and transitions."""

    # Load the skeleton and animation assets.
    skeleton = load(SKELETON_PATH)
    idle_anim = load(IDLE_ANIM_PATH)
    walk_anim = load(WALK_ANIM_PATH)
    run_anim = load(RUN_ANIM_PATH)

    # Create the AnimBP targeting our skeleton.
    abp = AnimBlueprint.create(PACKAGE_PATH, ABP_NAME, skeleton)
    print("Created: {}".format(abp))

    # Add a locomotion state machine wired to the AnimGraph output.
    loco = abp.add_state_machine("Locomotion", connect_to_root=True)
    print("Added state machine: {}".format(loco))

    # Add states with their animations.  The first state is the default.
    idle = loco.add_state("Idle", animation=idle_anim, default=True)
    walk = loco.add_state("Walk", animation=walk_anim)
    run = loco.add_state("Run", animation=run_anim)
    print("Added states: Idle, Walk, Run")

    # Wire transitions between states.
    idle.transition_to(walk, crossfade=0.2)
    walk.transition_to(idle, crossfade=0.2)
    walk.transition_to(run, crossfade=0.15)
    run.transition_to(walk, crossfade=0.15)
    print("Wired transitions")

    # Set an auto-transition rule: when Idle's animation has less than
    # 0.1 seconds remaining, automatically transition to Walk.
    idle.auto_transition_to(walk, trigger_time=0.1)
    print("Set auto-transition: Idle -> Walk")

    # Compile the AnimBP to validate everything.
    abp.compile()
    print("Compiled successfully!")

    # Inspect what we built.
    print("\n--- Summary ---")
    print("AnimBP: {}".format(abp.name))
    print("State machines: {}".format([sm.name for sm in abp.state_machines]))
    print("States in Locomotion: {}".format([s.name for s in loco.states]))

    return abp


# --- Entry Point -------------------------------------------------------

if __name__ == "__main__":
    main()
