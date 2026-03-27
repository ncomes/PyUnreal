"""
Viewport Tools Example
======================

Demonstrates viewport control — focusing on actors, moving the camera,
and capturing screenshots.

Usage (run inside Unreal Engine Python console)::

    exec(open('/path/to/viewport_tools.py').read())

Dependencies:
    - PyUnreal (pyunreal package in Content/Python/)
    - At least one actor in the level
"""

from pyunreal.viewport import viewport
from pyunreal.scene import scene


# --- Focus on a specific actor -----------------------------------------

viewport.focus("Chair_01")
print("Viewport focused on Chair_01")


# --- Set the camera to a known position --------------------------------

# Top-down view looking straight down.
viewport.set_camera(
    location=(0, 0, 2000),
    rotation=(-90, 0, 0),
)
print("Camera set to top-down view")


# --- Get current camera position --------------------------------------

cam = viewport.get_camera()
print("Camera location:", cam["location"])
print("Camera rotation:", cam["rotation"])


# --- Capture a screenshot ----------------------------------------------

viewport.screenshot("C:/Shots/overview.png", width=1920, height=1080)
print("Screenshot saved to C:/Shots/overview.png")


# --- Iterate and screenshot each selected actor ------------------------

for actor in scene.selected():
    viewport.focus(actor)
    viewport.screenshot(
        "C:/Shots/{}.png".format(actor.name),
        width=1920,
        height=1080,
    )
    print("Screenshot: {}".format(actor.name))

print("Done!")
