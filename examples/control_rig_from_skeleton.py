"""
PyUnreal Example -- Inspect and extend a Control Rig.

Demonstrates the Control Rig workflow:
    1. Load an existing Control Rig
    2. List existing bones, controls, and nulls
    3. Add a null (space/group) to the hierarchy
    4. Add controls with shapes and colors
    5. Set control transforms

Prerequisites:
    - Unreal Engine editor open with a project loaded
    - A Control Rig Blueprint at the path below

Usage:
    Run this script in Unreal Engine's Python console, or execute
    via MCA Editor's code editor.

Side effects:
    - Modifies the specified Control Rig asset
"""

from pyunreal.control_rig import ControlRig


# --- Configuration ---------------------------------------------------------
# Update this path to match your project.

CONTROL_RIG_PATH = "/Game/Rigs/CR_Character"


# --- Main Script -----------------------------------------------------------

def main():
    """Load a Control Rig, inspect it, and add controls."""

    # Load the Control Rig.
    rig = ControlRig.load(CONTROL_RIG_PATH)
    print("Loaded: {}".format(rig))

    # Inspect existing hierarchy.
    print("\n--- Bones ({}) ---".format(len(rig.bones)))
    for bone in rig.bones[:10]:
        print("  {} (parent: {})".format(bone.name, bone.parent))
    if len(rig.bones) > 10:
        print("  ... and {} more".format(len(rig.bones) - 10))

    print("\n--- Controls ({}) ---".format(len(rig.controls)))
    for ctrl in rig.controls:
        print("  {} (parent: {})".format(ctrl.name, ctrl.parent))

    print("\n--- Nulls ({}) ---".format(len(rig.nulls)))
    for null in rig.nulls:
        print("  {} (parent: {})".format(null.name, null.parent))

    # Add a root null to organize our new controls.
    root = rig.add_null("CustomControls")
    print("\nAdded null: {}".format(root))

    # Add controls with different shapes and colors.
    hips = rig.add_control(
        "Hips_Ctrl",
        parent="CustomControls",
        shape="Box",
        color="yellow",
        location=(0, 0, 100),
    )
    print("Added control: {} at {}".format(hips.name, hips.transform))

    spine = rig.add_control(
        "Spine_01_Ctrl",
        parent="CustomControls",
        shape="Circle",
        color="cyan",
        location=(0, 0, 130),
    )
    print("Added control: {}".format(spine.name))

    # Move a control by setting its transform.
    hips.set_transform(location=(0, 0, 95))
    print("Moved Hips_Ctrl to z=95")

    # Change a control's shape and color.
    spine.set_shape("Square", color="green")
    print("Changed Spine_01_Ctrl shape to Square (green)")

    # Final summary.
    print("\n--- Updated Hierarchy ---")
    print("Controls: {}".format([c.name for c in rig.controls]))
    print("Nulls: {}".format([n.name for n in rig.nulls]))

    return rig


# --- Entry Point -----------------------------------------------------------

if __name__ == "__main__":
    main()
