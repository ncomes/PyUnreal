"""
Module-level scene query functions for PyUnreal.

These functions operate on the current level — finding, selecting, and
listing actors.  They return :class:`Actor` wrapper objects for
Pythonic access to actor properties and transforms.

Usage::

    from pyunreal.scene import scene

    selected = scene.selected()
    lights = scene.find_by_type('PointLight')
    all_actors = scene.all()

Dependencies:
    - ``unreal`` module (UE Python interpreter)
"""

import fnmatch
import logging

from pyunreal.core.detection import require_unreal

# Module-level logger.
logger = logging.getLogger(__name__)


def all():
    """
    Get all actors in the current level.

    :return: List of Actor wrapper objects
    :rtype: list[Actor]
    """
    require_unreal()
    import unreal

    # Lazy import to avoid circular dependency — Actor imports scene_queries
    # through the __init__.py, so we import Actor here instead.
    from pyunreal.scene.actor import Actor

    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    return [Actor(a) for a in actors]


def selected():
    """
    Get the currently selected actors in the level viewport.

    :return: List of selected Actor wrapper objects
    :rtype: list[Actor]
    """
    require_unreal()
    import unreal

    from pyunreal.scene.actor import Actor

    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    return [Actor(a) for a in actors]


def select(actors_or_names):
    """
    Set the level viewport selection to the specified actors.

    Accepts a list of Actor wrapper objects, UE actor objects, or
    actor label strings.

    :param list actors_or_names: Actors to select
    """
    require_unreal()
    import unreal

    from pyunreal.scene.actor import Actor

    # Resolve to UE actor objects.
    ue_actors = []
    for item in actors_or_names:
        if isinstance(item, Actor):
            ue_actors.append(item._asset)
        elif isinstance(item, str):
            # Find by label name.
            for a in unreal.EditorLevelLibrary.get_all_level_actors():
                if a.get_actor_label() == item:
                    ue_actors.append(a)
                    break
        else:
            # Assume it is a UE actor object.
            ue_actors.append(item)

    unreal.EditorLevelLibrary.set_selected_level_actors(ue_actors)
    logger.info("Selected %d actors", len(ue_actors))


def find(name_pattern):
    """
    Find actors by name pattern (supports wildcards).

    Uses ``fnmatch`` for pattern matching against actor labels.
    The pattern is case-insensitive.

    :param str name_pattern: Glob pattern (e.g. 'Chair_*', '*Light*')
    :return: List of matching Actor wrapper objects
    :rtype: list[Actor]
    """
    require_unreal()
    import unreal

    from pyunreal.scene.actor import Actor

    results = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        label = a.get_actor_label()
        if fnmatch.fnmatch(label.lower(), name_pattern.lower()):
            results.append(Actor(a))

    return results


def find_by_type(class_name):
    """
    Find all actors of a specific type in the current level.

    Matches against the actor's class name (case-insensitive).

    :param str class_name: UE class name (e.g. 'PointLight', 'StaticMeshActor')
    :return: List of matching Actor wrapper objects
    :rtype: list[Actor]
    """
    require_unreal()
    import unreal

    from pyunreal.scene.actor import Actor

    results = []
    target = class_name.lower()

    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        actor_class = a.get_class().get_name().lower()
        if actor_class == target or target in actor_class:
            results.append(Actor(a))

    return results


def find_by_tag(tag):
    """
    Find all actors that have a specific tag.

    :param str tag: Actor tag to search for
    :return: List of matching Actor wrapper objects
    :rtype: list[Actor]
    """
    require_unreal()
    import unreal

    from pyunreal.scene.actor import Actor

    results = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            tags = a.get_editor_property("tags")
            if tag in [str(t) for t in tags]:
                results.append(Actor(a))
        except Exception:
            continue

    return results
