"""
Scene and Actor module for PyUnreal.

Provides Pythonic wrappers for working with level actors and scene
queries.  The ``scene`` module offers top-level functions for finding,
selecting, and spawning actors.  The ``Actor`` class wraps individual
actors with property access and transform manipulation.

Usage::

    from pyunreal.scene import Actor, scene

    # Spawn an actor.
    chair = Actor.spawn('StaticMeshActor', name='Chair_01')
    chair.location = (100, 200, 0)

    # Scene queries.
    selected = scene.selected()
    lights = scene.find_by_type('PointLight')
    all_chairs = scene.find('Chair_*')
"""

from pyunreal.scene.actor import Actor
from pyunreal.scene import scene_queries as scene
