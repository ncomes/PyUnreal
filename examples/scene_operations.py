"""
PyUnreal Example -- Scene operations and actor manipulation.

Demonstrates the Scene/Actor workflow:
    1. Spawn actors into the level
    2. Set transforms using Pythonic properties
    3. Query the scene for actors by type and name
    4. Bulk operations on groups of actors
    5. Select and inspect actors

Prerequisites:
    - Unreal Engine editor open with a project loaded

Usage:
    Run this script in Unreal Engine's Python console, or execute
    via MCA Editor's code editor.

Side effects:
    - Spawns new actors in the current level
"""

from pyunreal.scene import Actor, scene


# --- Main Script -----------------------------------------------------------

def main():
    """Demonstrate spawning, querying, and manipulating actors."""

    # --- Spawn actors ---------------------------------------------------
    print("--- Spawning Actors ---")

    # Spawn a point light with a name and position.
    light = Actor.spawn(
        "PointLight",
        name="MyLight",
        location=(200, 0, 300),
    )
    print("Spawned: {}".format(light))

    # Spawn several cube actors in a row.
    cubes = []
    for i in range(5):
        cube = Actor.spawn(
            "StaticMeshActor",
            name="Cube_{}".format(i),
            location=(i * 150, 0, 50),
        )
        cubes.append(cube)
        print("Spawned: {}".format(cube))

    # --- Transform manipulation -----------------------------------------
    print("\n--- Transform Manipulation ---")

    # Move the light using property assignment.
    light.location = (200, 100, 400)
    print("Moved light to: {}".format(light.location))

    # Rotate a cube.
    cubes[0].rotation = (0, 45, 0)
    print("Rotated Cube_0: {}".format(cubes[0].rotation))

    # Scale a cube.
    cubes[1].scale = (2, 2, 2)
    print("Scaled Cube_1: {}".format(cubes[1].scale))

    # --- Scene queries --------------------------------------------------
    print("\n--- Scene Queries ---")

    # Find all lights in the scene.
    lights = scene.find_by_type("PointLight")
    print("Point lights in scene: {}".format(len(lights)))

    # Find actors by name pattern.
    found_cubes = scene.find("Cube_*")
    print("Found cubes matching 'Cube_*': {}".format(len(found_cubes)))

    # Get currently selected actors.
    selected = scene.selected()
    print("Currently selected: {}".format(len(selected)))

    # --- Bulk operations ------------------------------------------------
    print("\n--- Bulk Operations ---")

    # Raise all cubes by 50 units.
    for cube in found_cubes:
        x, y, z = cube.location
        cube.location = (x, y, z + 50)

    print("Raised {} cubes by 50 units".format(len(found_cubes)))

    # Select all the cubes we spawned.
    scene.select(found_cubes)
    print("Selected {} cubes".format(len(found_cubes)))

    # --- Actor inspection -----------------------------------------------
    print("\n--- Actor Info ---")
    for cube in found_cubes:
        print("  {} | class: {} | location: {}".format(
            cube.name, cube.class_name, cube.location
        ))

    print("\nDone!")


# --- Entry Point -----------------------------------------------------------

if __name__ == "__main__":
    main()
