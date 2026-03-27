"""
Actor wrapper for level actors in Unreal Engine.

An Actor wraps a UE actor instance in the current level, providing
Pythonic access to transforms, properties, and lifecycle operations.

Actors are spawned via :meth:`Actor.spawn`, discovered via scene
queries, or wrapped directly from a UE actor object.

Usage::

    from pyunreal.scene import Actor

    chair = Actor.spawn('StaticMeshActor', name='Chair_01')
    chair.location = (100, 200, 0)
    print(chair.location)  # (100.0, 200.0, 0.0)

Dependencies:
    - ``unreal`` module (UE Python interpreter)
"""

import logging

from pyunreal.core.base import UnrealObjectWrapper
from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)


class Actor(UnrealObjectWrapper):
    """
    Pythonic wrapper around a UE level actor.

    Use :meth:`spawn` to create new actors, or wrap an existing UE
    actor object directly::

        actor = Actor(some_ue_actor_object)

    :param ue_actor: An existing UE actor object
    """

    def __init__(self, ue_actor):
        super().__init__(ue_actor)

    # --- Class Methods (constructors) ----------------------------------

    @classmethod
    def spawn(cls, class_name, name=None, location=None, rotation=None,
              scale=None):
        """
        Spawn a new actor into the current level.

        :param str class_name: UE actor class name (e.g. 'StaticMeshActor',
                               'PointLight', 'CameraActor'). Can also pass
                               a loaded UE class object.
        :param str name: Label for the actor in the Outliner (optional)
        :param location: Spawn location as (x, y, z) tuple (optional)
        :param rotation: Spawn rotation as (pitch, yaw, roll) tuple (optional)
        :param scale: Scale as (x, y, z) tuple (optional)
        :return: Wrapped Actor instance
        :rtype: Actor
        :raises InvalidOperationError: if spawning fails
        """
        require_unreal()
        import unreal

        # Resolve the actor class.
        if isinstance(class_name, str):
            actor_cls = getattr(unreal, class_name, None)
            if actor_cls is None:
                raise InvalidOperationError(
                    "Unknown actor class '{}'. Pass a valid UE class name "
                    "(e.g. 'StaticMeshActor', 'PointLight').".format(class_name)
                )
        else:
            actor_cls = class_name

        # Build location and rotation.
        loc = unreal.Vector(0, 0, 0)
        rot = unreal.Rotator(0, 0, 0)

        if location is not None:
            if isinstance(location, dict):
                loc = unreal.Vector(location["x"], location["y"], location["z"])
            else:
                loc = unreal.Vector(location[0], location[1], location[2])

        if rotation is not None:
            if isinstance(rotation, dict):
                rot = unreal.Rotator(
                    rotation["pitch"], rotation["yaw"], rotation["roll"]
                )
            else:
                rot = unreal.Rotator(rotation[0], rotation[1], rotation[2])

        logger.info("Spawning actor: %s (name=%s)", class_name, name)

        # Spawn the actor.
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            actor_cls, loc, rot
        )

        if actor is None:
            raise InvalidOperationError(
                "Failed to spawn actor of class '{}'.".format(class_name)
            )

        # Set the label in the World Outliner.
        if name:
            actor.set_actor_label(name)

        # Set scale if specified.
        if scale is not None:
            if isinstance(scale, dict):
                sc = unreal.Vector(scale["x"], scale["y"], scale["z"])
            else:
                sc = unreal.Vector(scale[0], scale[1], scale[2])
            actor.set_actor_scale3d(sc)

        return cls(actor)

    # --- Properties (read-write) ---------------------------------------

    @property
    def name(self):
        """
        The actor label as shown in the World Outliner.

        :rtype: str
        """
        self._validate()
        return self._asset.get_actor_label()

    @name.setter
    def name(self, value):
        """
        Set the actor label.

        :param str value: New label
        """
        self._validate()
        self._asset.set_actor_label(value)

    @property
    def class_name(self):
        """
        The UE class name of this actor.

        :rtype: str
        """
        self._validate()
        return self._asset.get_class().get_name()

    @property
    def location(self):
        """
        World location as an (x, y, z) tuple.

        :rtype: tuple
        """
        self._validate()
        loc = self._asset.get_actor_location()
        return (loc.x, loc.y, loc.z)

    @location.setter
    def location(self, value):
        """
        Set world location.

        Accepts (x, y, z) tuple, list, or dict with x/y/z keys.

        :param value: New location
        """
        require_unreal()
        import unreal

        self._validate()

        if isinstance(value, dict):
            vec = unreal.Vector(value["x"], value["y"], value["z"])
        else:
            vec = unreal.Vector(value[0], value[1], value[2])

        self._asset.set_actor_location(vec, False, False)

    @property
    def rotation(self):
        """
        World rotation as a (pitch, yaw, roll) tuple.

        :rtype: tuple
        """
        self._validate()
        rot = self._asset.get_actor_rotation()
        return (rot.pitch, rot.yaw, rot.roll)

    @rotation.setter
    def rotation(self, value):
        """
        Set world rotation.

        Accepts (pitch, yaw, roll) tuple, list, or dict.

        :param value: New rotation
        """
        require_unreal()
        import unreal

        self._validate()

        if isinstance(value, dict):
            rot = unreal.Rotator(value["pitch"], value["yaw"], value["roll"])
        else:
            rot = unreal.Rotator(value[0], value[1], value[2])

        self._asset.set_actor_rotation(rot, False)

    @property
    def scale(self):
        """
        World scale as an (x, y, z) tuple.

        :rtype: tuple
        """
        self._validate()
        sc = self._asset.get_actor_scale3d()
        return (sc.x, sc.y, sc.z)

    @scale.setter
    def scale(self, value):
        """
        Set world scale.

        Accepts (x, y, z) tuple, list, or dict.

        :param value: New scale
        """
        require_unreal()
        import unreal

        self._validate()

        if isinstance(value, dict):
            sc = unreal.Vector(value["x"], value["y"], value["z"])
        else:
            sc = unreal.Vector(value[0], value[1], value[2])

        self._asset.set_actor_scale3d(sc)

    @property
    def hidden(self):
        """
        Whether this actor is hidden in the editor.

        :rtype: bool
        """
        self._validate()
        return self._asset.is_hidden_ed()

    # --- Methods -------------------------------------------------------

    def set_property(self, name, value):
        """
        Set an editor property on this actor.

        :param str name: Property name
        :param value: Property value
        :return: self for method chaining
        :rtype: Actor
        :raises InvalidOperationError: if the property cannot be set
        """
        self._validate()

        try:
            self._asset.set_editor_property(name, value)
        except Exception as e:
            raise InvalidOperationError(
                "Failed to set property '{}' on '{}': {}".format(
                    name, self.name, e
                )
            )

        return self

    def get_property(self, name):
        """
        Get an editor property from this actor.

        :param str name: Property name
        :return: The property value
        :raises InvalidOperationError: if the property cannot be read
        """
        self._validate()

        try:
            return self._asset.get_editor_property(name)
        except Exception as e:
            raise InvalidOperationError(
                "Failed to get property '{}' on '{}': {}".format(
                    name, self.name, e
                )
            )

    def destroy(self):
        """
        Delete this actor from the level.

        The wrapper becomes invalid after this call.
        """
        self._validate()
        logger.info("Destroying actor: %s", self.name)
        self._asset.destroy_actor()
        self._asset = None

    # --- String Representation -----------------------------------------

    def __repr__(self):
        try:
            if self._asset is not None:
                label = self._asset.get_actor_label()
                cls = self._asset.get_class().get_name()
                return "<Actor '{}' ({})>".format(label, cls)
        except Exception:
            pass
        return "<Actor (destroyed)>"
