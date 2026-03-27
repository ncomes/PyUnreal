"""
Material Setup Example
======================

Creates materials with different parameter configurations and
assigns them to actors in the level.

Usage (run inside Unreal Engine Python console)::

    exec(open('/path/to/material_setup.py').read())

Dependencies:
    - PyUnreal (pyunreal package in Content/Python/)
    - Actors named 'Chair_01', 'Table_01', 'Lamp_01' in the level
"""

from pyunreal.material import Material


# --- Create a metallic gold material -----------------------------------

gold = Material.create("M_Gold")
gold.set_param("BaseColor", (1.0, 0.84, 0.0, 1.0))
gold.set_param("Metallic", 1.0)
gold.set_param("Roughness", 0.15)

# Assign to a chair in the level.
gold.assign_to("Chair_01")

print("Gold material applied to Chair_01")


# --- Create a matte red material with chaining -------------------------

red = Material.create("M_MatteRed")
red.set_param("BaseColor", (0.8, 0.1, 0.05, 1.0)) \
   .set_param("Metallic", 0.0) \
   .set_param("Roughness", 0.9) \
   .assign_to("Table_01")

print("Matte red material applied to Table_01")


# --- Load and modify an existing material ------------------------------

# existing = Material.load("/Game/Materials/M_Glass")
# existing.set_param("Opacity", 0.3)
# existing.assign_to("Lamp_01", slot=1)


# --- Batch-create material variants ------------------------------------

# Create a set of colored materials from a palette.
PALETTE = {
    "M_Blue": (0.1, 0.3, 0.8),
    "M_Green": (0.2, 0.7, 0.1),
    "M_Purple": (0.5, 0.1, 0.7),
}

for name, color in PALETTE.items():
    mat = Material.create(name)
    mat.set_param("BaseColor", color)
    mat.set_param("Roughness", 0.5)
    print("Created: {}".format(name))

print("Done! {} materials created.".format(2 + len(PALETTE)))
