"""
PyUnreal Example -- Batch Blueprint setup for pickup items.

Demonstrates the Blueprint workflow:
    1. Create a Blueprint with a parent class
    2. Add mesh and collision components
    3. Add variables with defaults
    4. Set class defaults
    5. Compile the Blueprint

Prerequisites:
    - Unreal Engine editor open with a project loaded
    - Assets at the paths below (adjust for your project)

Usage:
    Run this script in Unreal Engine's Python console, or execute
    via MCA Editor's code editor.

Side effects:
    - Creates new Blueprint assets in the Content Browser
"""

from pyunreal.blueprint import Blueprint


# --- Configuration ---------------------------------------------------------
# Update these paths to match your project.

PACKAGE_PATH = "/Game/Blueprints/Pickups"

# Define the pickups to create — each has a name, mesh path, and point value.
PICKUPS = [
    {"name": "BP_Gem", "points": 10},
    {"name": "BP_Coin", "points": 5},
    {"name": "BP_Star", "points": 50},
]


# --- Main Script -----------------------------------------------------------

def main():
    """Create a batch of pickup Blueprints with components and variables."""

    for pickup in PICKUPS:
        bp_name = pickup["name"]
        points = pickup["points"]

        print("Creating: {}".format(bp_name))

        # Create the Blueprint with Actor as parent.
        bp = Blueprint.create(PACKAGE_PATH, bp_name, parent="Actor")

        # Add a static mesh component for the visual.
        mesh = bp.add_component("StaticMeshComponent", name="PickupMesh")
        print("  Added component: {}".format(mesh))

        # Add a sphere collision component for overlap detection.
        trigger = bp.add_component(
            "SphereComponent", name="Trigger", parent="PickupMesh"
        )
        print("  Added component: {}".format(trigger))

        # Add gameplay variables.
        bp.add_variable("PointValue", "int", default=points, category="Gameplay")
        bp.add_variable("IsCollected", "bool", default=False, category="Gameplay")
        bp.add_variable("RespawnTime", "float", default=5.0, category="Gameplay")
        print("  Added variables: PointValue={}, IsCollected, RespawnTime".format(points))

        # Compile to finalize.
        bp.compile()
        print("  Compiled: {}".format(bp.name))

        # Inspect what we built.
        print("  Components: {}".format([c.name for c in bp.components]))
        print("  Variables: {}".format([v.name for v in bp.variables]))
        print()

    print("Done! Created {} pickup Blueprints.".format(len(PICKUPS)))


# --- Entry Point -----------------------------------------------------------

if __name__ == "__main__":
    main()
