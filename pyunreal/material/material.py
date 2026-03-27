"""
Material wrapper for Unreal Engine materials.

A Material wraps a ``UMaterial`` or ``UMaterialInstance`` UObject and
provides a Pythonic interface for creating materials, setting scalar
and color parameters, and assigning materials to actors in the level.

Usage::

    from pyunreal.material import Material

    mat = Material.create('M_Metal')
    mat.set_param('Roughness', 0.2)
    mat.set_param('BaseColor', (0.8, 0.8, 0.9, 1.0))
    mat.assign_to('Chair_01')

Dependencies:
    - ``unreal`` module (UE Python interpreter)
"""

import logging

from pyunreal.core.base import UnrealObjectWrapper
from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import AssetNotFoundError
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)


class Material(UnrealObjectWrapper):
    """
    Pythonic wrapper around a UE Material or MaterialInstance asset.

    Use :meth:`create` to make a new material, or :meth:`load` to open
    an existing one.  Direct construction is also supported::

        mat = Material(some_ue_material_object)

    :param ue_material: An existing UE material UObject
    """

    def __init__(self, ue_material):
        super().__init__(ue_material)

    # --- Class Methods (constructors) ----------------------------------

    @classmethod
    def create(cls, name, package_path="/Game/Materials"):
        """
        Create a new Material asset in the Content Browser.

        :param str name: Name for the new material asset
        :param str package_path: Content Browser folder
                                 (default '/Game/Materials')
        :return: Wrapped Material instance
        :rtype: Material
        :raises InvalidOperationError: if creation fails
        """
        require_unreal()
        import unreal

        full_path = "{}/{}".format(package_path, name)

        logger.info("Creating Material: %s", full_path)

        # Check if asset already exists.
        if unreal.EditorAssetLibrary.does_asset_exist(full_path):
            raise InvalidOperationError(
                "Material already exists at '{}'. Use Material.load() "
                "to open it.".format(full_path)
            )

        # Create using the Material factory.
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.MaterialFactoryNew()

        result = asset_tools.create_asset(
            name, package_path, unreal.Material, factory
        )

        if result is None:
            raise InvalidOperationError(
                "Failed to create Material '{}'. "
                "Check that the package path is valid.".format(full_path)
            )

        # Save immediately.
        unreal.EditorAssetLibrary.save_asset(full_path)

        logger.info("Created Material: %s", name)
        return cls(result)

    @classmethod
    def load(cls, asset_path):
        """
        Load an existing Material from the Content Browser.

        :param str asset_path: Full content path
        :return: Wrapped Material instance
        :rtype: Material
        :raises AssetNotFoundError: if no asset exists at the path
        """
        require_unreal()
        import unreal

        logger.info("Loading Material: %s", asset_path)

        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if asset is None:
            raise AssetNotFoundError(asset_path)

        return cls(asset)

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The asset name of this Material.

        :rtype: str
        """
        self._validate()
        return self._asset.get_name()

    @property
    def path(self):
        """
        The full Content Browser path of this Material.

        :rtype: str
        """
        self._validate()
        return self._asset.get_path_name()

    # --- Methods -------------------------------------------------------

    def set_param(self, param_name, value):
        """
        Set a material parameter value.

        Accepts scalar values (float/int) for scalar parameters, or
        color tuples ``(r, g, b)`` or ``(r, g, b, a)`` for color
        parameters.  Values are in 0-1 range.

        :param str param_name: Parameter name (e.g. 'BaseColor', 'Roughness')
        :param value: Scalar (float/int) or color tuple
        :return: self for method chaining
        :rtype: Material
        :raises InvalidOperationError: if the parameter cannot be set
        """
        require_unreal()
        import unreal

        self._validate()

        logger.info("Setting param '%s' = %s on %s", param_name, value, self.name)

        try:
            # Determine if this is a color or scalar parameter.
            if isinstance(value, (tuple, list)):
                # Color parameter — convert to LinearColor.
                r = value[0]
                g = value[1]
                b = value[2]
                a = value[3] if len(value) > 3 else 1.0
                color = unreal.LinearColor(r, g, b, a)
                self._asset.set_editor_property(param_name, color)
            else:
                # Scalar parameter.
                self._asset.set_editor_property(param_name, float(value))
        except Exception as e:
            raise InvalidOperationError(
                "Failed to set parameter '{}' on '{}': {}".format(
                    param_name, self.name, e
                )
            )

        # Save the material.
        unreal.EditorAssetLibrary.save_asset(self.path)

        return self

    def get_param(self, param_name):
        """
        Get a material parameter value.

        :param str param_name: Parameter name
        :return: The parameter value
        :raises InvalidOperationError: if the parameter cannot be read
        """
        self._validate()

        try:
            return self._asset.get_editor_property(param_name)
        except Exception as e:
            raise InvalidOperationError(
                "Failed to read parameter '{}' on '{}': {}".format(
                    param_name, self.name, e
                )
            )

    def assign_to(self, actor_or_name, slot=0):
        """
        Assign this material to an actor's mesh component.

        Finds the first StaticMeshComponent or MeshComponent on the
        actor and sets the material on the specified slot.

        :param actor_or_name: An Actor wrapper, UE actor, or actor
                              label string
        :param int slot: Material slot index (default 0)
        :return: self for method chaining
        :rtype: Material
        :raises InvalidOperationError: if the actor or mesh is not found
        """
        require_unreal()
        import unreal

        self._validate()

        # Resolve the actor.
        target = self._resolve_actor(actor_or_name)

        if target is None:
            raise InvalidOperationError(
                "Actor '{}' not found in the level.".format(actor_or_name)
            )

        logger.info(
            "Assigning '%s' to actor '%s' slot %d",
            self.name, target.get_actor_label(), slot
        )

        # Find a mesh component on the actor.
        mesh_comp = None

        # Try StaticMeshComponent first.
        comps = target.get_components_by_class(unreal.StaticMeshComponent)
        if comps:
            mesh_comp = comps[0]

        # Fall back to any MeshComponent.
        if mesh_comp is None:
            try:
                comps = target.get_components_by_class(unreal.MeshComponent)
                if comps:
                    mesh_comp = comps[0]
            except Exception:
                pass

        if mesh_comp is None:
            raise InvalidOperationError(
                "Actor '{}' has no mesh component to assign a material to.".format(
                    target.get_actor_label()
                )
            )

        # Set the material.
        mesh_comp.set_material(slot, self._asset)

        return self

    # --- Internal Helpers ----------------------------------------------

    def _resolve_actor(self, actor_or_name):
        """
        Resolve an actor argument to a UE actor object.

        :param actor_or_name: Actor wrapper, UE actor, or label string
        :return: UE actor object, or None
        """
        import unreal

        # Import here to avoid circular dependency.
        from pyunreal.scene.actor import Actor

        if isinstance(actor_or_name, Actor):
            return actor_or_name._asset

        if isinstance(actor_or_name, str):
            # Search by label.
            for a in unreal.EditorLevelLibrary.get_all_level_actors():
                if a.get_actor_label() == actor_or_name:
                    return a
            return None

        # Assume it is already a UE actor.
        return actor_or_name

    # --- String Representation -----------------------------------------

    def __repr__(self):
        try:
            name = self._asset.get_name() if self._asset else "None"
        except Exception:
            name = "invalid"
        return "<Material '{}'>".format(name)
