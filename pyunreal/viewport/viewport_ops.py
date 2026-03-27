"""
Viewport operations for Unreal Engine.

Module-level functions for controlling the editor viewport — focusing
on actors, positioning the camera, and capturing screenshots.  These
wrap the ``LevelEditorSubsystem``, ``UnrealEditorSubsystem``, and
``AutomationLibrary`` APIs into simple callable functions.

Usage::

    from pyunreal.viewport import viewport

    viewport.focus('Chair_01')
    viewport.set_camera(location=(0, 0, 500), rotation=(0, -90, 0))
    viewport.screenshot('C:/Shots/hero.png', width=1920, height=1080)

Dependencies:
    - ``unreal`` module (UE Python interpreter)
"""

import logging

from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import AssetNotFoundError
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)


# --- Viewport Focus ------------------------------------------------

def focus(actor_or_name):
    """
    Focus the viewport on an actor.

    Pilots the active level-editor viewport to frame the given actor.
    Accepts an Actor wrapper, a UE actor object, or a label string.

    :param actor_or_name: Actor wrapper, UE actor, or actor label string
    :raises AssetNotFoundError: if the actor cannot be found
    :raises InvalidOperationError: if the viewport focus fails
    """
    require_unreal()
    import unreal

    # Resolve the actor from the argument.
    target = _resolve_actor(actor_or_name)

    if target is None:
        raise AssetNotFoundError(
            "Actor '{}' not found in the level.".format(actor_or_name)
        )

    logger.info("Focusing viewport on '%s'", target.get_actor_label())

    try:
        # Get the LevelEditorSubsystem for viewport control.
        subsystem = unreal.get_editor_subsystem(
            unreal.LevelEditorSubsystem
        )
        subsystem.pilot_level_actor(target)
    except Exception as e:
        raise InvalidOperationError(
            "Failed to focus viewport on '{}': {}".format(
                target.get_actor_label(), e
            )
        )


# --- Camera Control ------------------------------------------------

def set_camera(location=None, rotation=None):
    """
    Set the viewport camera position and/or rotation.

    Either parameter can be omitted to leave that aspect unchanged.
    Location is ``(x, y, z)`` in world units.  Rotation is
    ``(pitch, yaw, roll)`` in degrees.

    :param tuple location: Camera world position as ``(x, y, z)``,
                           or None to keep current
    :param tuple rotation: Camera rotation as ``(pitch, yaw, roll)``
                           in degrees, or None to keep current
    :raises InvalidOperationError: if the camera cannot be set
    """
    require_unreal()
    import unreal

    logger.info(
        "Setting viewport camera: location=%s, rotation=%s",
        location, rotation
    )

    try:
        subsystem = unreal.get_editor_subsystem(
            unreal.UnrealEditorSubsystem
        )

        # Build Vector and Rotator from tuples.
        loc = unreal.Vector(*location) if location else unreal.Vector(0, 0, 0)
        rot = unreal.Rotator(*rotation) if rotation else unreal.Rotator(0, 0, 0)

        subsystem.set_level_viewport_camera_info(loc, rot)
    except Exception as e:
        raise InvalidOperationError(
            "Failed to set viewport camera: {}".format(e)
        )


def get_camera():
    """
    Get the current viewport camera position and rotation.

    :return: Dictionary with 'location' ``(x, y, z)`` and
             'rotation' ``(pitch, yaw, roll)`` tuples
    :rtype: dict
    :raises InvalidOperationError: if the camera info cannot be read
    """
    require_unreal()
    import unreal

    try:
        subsystem = unreal.get_editor_subsystem(
            unreal.UnrealEditorSubsystem
        )

        # get_level_viewport_camera_info returns (bool, Vector, Rotator).
        success, loc, rot = subsystem.get_level_viewport_camera_info()

        if not success:
            raise InvalidOperationError(
                "No active viewport camera found."
            )

        return {
            "location": (loc.x, loc.y, loc.z),
            "rotation": (rot.pitch, rot.yaw, rot.roll),
        }
    except InvalidOperationError:
        raise
    except Exception as e:
        raise InvalidOperationError(
            "Failed to get viewport camera info: {}".format(e)
        )


# --- Screenshot Capture --------------------------------------------

def screenshot(output_path, width=1920, height=1080):
    """
    Capture a high-resolution screenshot of the active viewport.

    :param str output_path: File path for the saved image (PNG)
    :param int width: Image width in pixels (default 1920)
    :param int height: Image height in pixels (default 1080)
    :raises InvalidOperationError: if the screenshot cannot be taken
    """
    require_unreal()
    import unreal

    logger.info(
        "Taking screenshot: %s (%dx%d)", output_path, width, height
    )

    try:
        unreal.AutomationLibrary.take_high_res_screenshot(
            width, height, output_path
        )
    except Exception as e:
        raise InvalidOperationError(
            "Failed to take screenshot '{}': {}".format(output_path, e)
        )


# --- Internal Helpers ----------------------------------------------

def _resolve_actor(actor_or_name):
    """
    Resolve an actor argument to a UE actor object.

    :param actor_or_name: Actor wrapper, UE actor, or label string
    :return: UE actor object, or None
    """
    import unreal

    # Import here to avoid circular dependency.
    from pyunreal.scene.actor import Actor

    # If it is a PyUnreal Actor wrapper, unwrap it.
    if isinstance(actor_or_name, Actor):
        return actor_or_name._asset

    # If it is a string, search by actor label.
    if isinstance(actor_or_name, str):
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if a.get_actor_label() == actor_or_name:
                return a
        return None

    # Assume it is already a raw UE actor object.
    return actor_or_name
