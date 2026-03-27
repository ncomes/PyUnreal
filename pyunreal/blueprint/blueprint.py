"""
Blueprint wrapper — the top-level entry point for Blueprint authoring.

A Blueprint wraps a ``UBlueprint`` UObject and provides a Pythonic
interface for creating Blueprints, adding components and variables,
setting class defaults, and compiling.  All operations use standard
UE Python APIs — no C++ bridge required.

Usage::

    from pyunreal.blueprint import Blueprint

    bp = Blueprint.create('/Game/Blueprints', 'BP_Pickup', parent='Actor')
    bp.add_component('StaticMeshComponent', name='PickupMesh')
    bp.add_variable('PointValue', 'int', default=10)
    bp.compile()

Dependencies:
    - ``unreal`` module (UE Python interpreter)
"""

import logging

from pyunreal.core.base import UnrealObjectWrapper
from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import AssetNotFoundError
from pyunreal.core.errors import InvalidOperationError
from pyunreal.blueprint.component import Component
from pyunreal.blueprint.variable import Variable
from pyunreal.blueprint.variable import _map_type

# Module-level logger.
logger = logging.getLogger(__name__)


class Blueprint(UnrealObjectWrapper):
    """
    Pythonic wrapper around a UBlueprint asset.

    Use the class methods :meth:`create` or :meth:`load` to get an instance.
    Direct construction is also supported for wrapping an existing UObject::

        bp = Blueprint(some_ue_blueprint_object)

    :param ue_blueprint: An existing ``unreal.Blueprint`` UObject
    """

    def __init__(self, ue_blueprint):
        super().__init__(ue_blueprint)

    # --- Class Methods (constructors) ----------------------------------

    @classmethod
    def create(cls, package_path, asset_name, parent="Actor"):
        """
        Create a new Blueprint asset with the specified parent class.

        :param str package_path: Content Browser folder (e.g. '/Game/Blueprints')
        :param str asset_name: Name for the new Blueprint asset
        :param str parent: Parent class name (default 'Actor'). Can also pass
                           a loaded UE class object.
        :return: Wrapped Blueprint instance
        :rtype: Blueprint
        :raises InvalidOperationError: if creation fails
        """
        require_unreal()
        import unreal

        logger.info(
            "Creating Blueprint: %s/%s (parent: %s)",
            package_path, asset_name, parent
        )

        # Resolve parent class — accept either a string name or a UE class.
        if isinstance(parent, str):
            parent_cls = getattr(unreal, parent, None)
            if parent_cls is None:
                raise InvalidOperationError(
                    "Unknown parent class '{}'. Pass a valid UE class name "
                    "(e.g. 'Actor', 'Pawn', 'Character').".format(parent)
                )
        else:
            parent_cls = parent

        # Check if the asset already exists.
        full_path = "{}/{}".format(package_path, asset_name)
        if unreal.EditorAssetLibrary.does_asset_exist(full_path):
            raise InvalidOperationError(
                "Blueprint already exists at '{}'. Use Blueprint.load() "
                "to open it, or choose a different name.".format(full_path)
            )

        # Create using the Blueprint factory.
        with unreal.ScopedEditorTransaction("PyUnreal: create Blueprint"):
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", parent_cls)

            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            result = asset_tools.create_asset(
                asset_name, package_path, unreal.Blueprint, factory
            )

        if result is None:
            raise InvalidOperationError(
                "Failed to create Blueprint '{}/{}'. "
                "Check that the package path is valid.".format(
                    package_path, asset_name
                )
            )

        # Save immediately so the asset persists in the Content Browser.
        unreal.EditorAssetLibrary.save_asset(full_path)

        logger.info("Created Blueprint: %s", result.get_name())
        return cls(result)

    @classmethod
    def load(cls, asset_path):
        """
        Load an existing Blueprint from the Content Browser.

        :param str asset_path: Full content path (e.g. '/Game/Blueprints/BP_Pickup')
        :return: Wrapped Blueprint instance
        :rtype: Blueprint
        :raises AssetNotFoundError: if no asset exists at the path
        :raises InvalidOperationError: if the asset is not a Blueprint
        """
        require_unreal()
        import unreal

        logger.info("Loading Blueprint: %s", asset_path)

        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if asset is None:
            raise AssetNotFoundError(asset_path)

        # Verify this is actually a Blueprint.
        if not isinstance(asset, unreal.Blueprint):
            raise InvalidOperationError(
                "Asset at '{}' is a {}, not a Blueprint.".format(
                    asset_path, type(asset).__name__
                )
            )

        return cls(asset)

    @classmethod
    def find(cls, path="/Game", class_filter=None, name_filter=None):
        """
        Search the Content Browser for Blueprint assets.

        Returns a list of asset paths (strings), not loaded Blueprints.
        Call :meth:`load` on individual paths to get wrapper objects.

        :param str path: Content path to search under (default '/Game')
        :param str class_filter: Only return BPs whose parent class matches
        :param str name_filter: Only return BPs whose name contains this substring
        :return: List of matching asset paths
        :rtype: list[str]
        """
        require_unreal()
        import unreal

        logger.debug(
            "Finding Blueprints: path=%s, class=%s, name=%s",
            path, class_filter, name_filter
        )

        # Query the asset registry for Blueprint assets.
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        ar_filter = unreal.ARFilter()
        ar_filter.package_paths = [path]
        ar_filter.recursive_paths = True
        ar_filter.class_names = ["Blueprint"]

        assets = registry.get_assets(ar_filter)

        results = []
        for asset_data in assets:
            asset_name = str(asset_data.asset_name)
            package_name = str(asset_data.package_name)

            # Apply name filter if specified.
            if name_filter and name_filter.lower() not in asset_name.lower():
                continue

            # Apply class filter if specified — requires loading the asset.
            if class_filter:
                bp = unreal.EditorAssetLibrary.load_asset(package_name)
                if bp is not None:
                    gen_class = bp.generated_class()
                    if gen_class is not None:
                        parent = gen_class.get_super_class()
                        if parent is not None:
                            parent_name = parent.get_name()
                            if class_filter.lower() != parent_name.lower():
                                continue

            results.append(package_name)

        return results

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The asset name of this Blueprint.

        :rtype: str
        """
        self._validate()
        return self._asset.get_name()

    @property
    def path(self):
        """
        The full Content Browser path of this Blueprint.

        :rtype: str
        """
        self._validate()
        return self._asset.get_path_name()

    @property
    def parent_class(self):
        """
        The name of this Blueprint's parent class.

        :rtype: str
        """
        self._validate()
        gen_class = self._asset.generated_class()
        if gen_class is not None:
            parent = gen_class.get_super_class()
            if parent is not None:
                return parent.get_name()
        return ""

    @property
    def components(self):
        """
        List of components in this Blueprint's construction hierarchy.

        Queries the live state from UE every time — no caching.

        :return: List of Component wrapper objects
        :rtype: list[Component]
        """
        require_unreal()
        import unreal

        self._validate()

        scs = self._asset.simple_construction_script
        if scs is None:
            return []

        nodes = scs.get_all_nodes()
        results = []

        for node in nodes:
            template = node.component_template
            if template is None:
                continue

            comp_name = template.get_name()
            comp_class = template.get_class().get_name()

            # Get parent component name.
            try:
                parent_name = str(
                    node.get_editor_property("parent_component_or_variable_name")
                )
            except Exception:
                parent_name = ""

            # Get transform data if available (only for SceneComponents).
            location = None
            rotation = None
            scale = None
            try:
                loc = template.get_editor_property("relative_location")
                location = {"x": loc.x, "y": loc.y, "z": loc.z}
            except Exception:
                pass
            try:
                rot = template.get_editor_property("relative_rotation")
                rotation = {"pitch": rot.pitch, "yaw": rot.yaw, "roll": rot.roll}
            except Exception:
                pass
            try:
                sc = template.get_editor_property("relative_scale3d")
                scale = {"x": sc.x, "y": sc.y, "z": sc.z}
            except Exception:
                pass

            results.append(Component(
                comp_name, comp_class, parent_name,
                location, rotation, scale
            ))

        return results

    @property
    def variables(self):
        """
        List of user-defined variables on this Blueprint.

        Returns Variable wrapper objects that can read and write defaults.
        Queries the live state from UE every time — no caching.

        :return: List of Variable wrapper objects
        :rtype: list[Variable]
        """
        require_unreal()
        import unreal

        self._validate()

        gen_class = self._asset.generated_class()
        if gen_class is None:
            return []

        # Get the parent class to filter out inherited properties.
        parent_class = gen_class.get_super_class()
        parent_props = set()
        if parent_class is not None:
            try:
                parent_cdo = unreal.get_default_object(parent_class)
                if parent_cdo is not None:
                    parent_props = set(dir(parent_cdo))
            except Exception:
                pass

        # Get the CDO to read default values.
        cdo = unreal.get_default_object(gen_class)
        if cdo is None:
            return []

        # User-defined variables = CDO properties minus parent properties,
        # minus internal/private names.
        all_props = set(dir(cdo))
        user_props = all_props - parent_props

        results = []
        for prop_name in sorted(user_props):
            # Skip private/internal properties.
            if prop_name.startswith("_"):
                continue

            # Read the default value and infer the type.
            try:
                value = cdo.get_editor_property(prop_name)
            except Exception:
                continue

            # Determine the property type from the Python value type.
            var_type = _infer_type(value)

            results.append(Variable(self, prop_name, var_type, value))

        return results

    @property
    def functions(self):
        """
        List of user-defined function names on this Blueprint.

        :return: List of function graph names
        :rtype: list[str]
        """
        require_unreal()
        import unreal

        self._validate()

        try:
            graphs = unreal.BlueprintEditorLibrary.get_function_graphs(self._asset)
            return [g.get_name() for g in graphs]
        except Exception:
            return []

    @property
    def events(self):
        """
        List of event names in this Blueprint's EventGraph.

        :return: List of event names
        :rtype: list[str]
        """
        require_unreal()

        self._validate()

        try:
            ubergraph_pages = self._asset.get_editor_property("ubergraph_pages")
        except Exception:
            return []

        results = []
        for graph in ubergraph_pages:
            try:
                nodes = graph.get_editor_property("nodes")
            except Exception:
                continue

            for node in nodes:
                class_name = node.get_class().get_name()

                # Only include event nodes.
                if "Event" not in class_name:
                    continue

                # Try to get the event name from various properties.
                event_name = None
                try:
                    event_name = str(node.get_editor_property("custom_function_name"))
                except Exception:
                    pass

                if not event_name or event_name == "None":
                    event_name = node.get_name()

                results.append(event_name)

        return results

    # --- Methods -------------------------------------------------------

    def add_component(self, component_class, name=None, parent=None):
        """
        Add a component to this Blueprint's construction script.

        :param str component_class: UE component class name
            (e.g. 'StaticMeshComponent', 'SphereComponent')
        :param str name: Instance name for the component (optional)
        :param str parent: Name of the parent component to attach to (optional)
        :return: The new Component wrapper
        :rtype: Component
        :raises InvalidOperationError: if the component class is unknown or add fails
        """
        require_unreal()
        import unreal

        self._validate()

        logger.info(
            "Adding component '%s' (%s) to %s",
            name or component_class, component_class, self.name
        )

        # Resolve the component class.
        comp_cls = getattr(unreal, component_class, None)
        if comp_cls is None:
            raise InvalidOperationError(
                "Unknown component class '{}'. Pass a valid UE component "
                "class name (e.g. 'StaticMeshComponent').".format(component_class)
            )

        scs = self._asset.simple_construction_script
        if scs is None:
            raise InvalidOperationError(
                "Blueprint '{}' has no SimpleConstructionScript. "
                "This may not be an Actor-based Blueprint.".format(self.name)
            )

        with unreal.ScopedEditorTransaction("PyUnreal: add component"):
            # Create the new SCS node.
            new_node = scs.create_node(comp_cls, name or "")

            if new_node is None:
                raise InvalidOperationError(
                    "Failed to create component '{}' ({}).".format(
                        name or "", component_class
                    )
                )

            # Attach to parent if specified.
            if parent:
                parent_node = self._find_scs_node(parent)
                if parent_node is not None:
                    parent_node.add_child_node(new_node)

        # Compile and save so the component shows up.
        unreal.KismetEditorUtilities.compile_blueprint(self._asset)
        unreal.EditorAssetLibrary.save_asset(self.path)

        # Return a Component wrapper with the info we know.
        comp_name = name or component_class
        if new_node.component_template is not None:
            comp_name = new_node.component_template.get_name()

        return Component(comp_name, component_class, parent or "")

    def add_variable(self, name, var_type, default=None, category=""):
        """
        Add a new variable to this Blueprint.

        :param str name: Variable name
        :param str var_type: Type — either a friendly name ('int', 'bool',
                             'float', 'str') or a UE property type string
                             ('IntProperty', 'BoolProperty', etc.)
        :param default: Default value for the variable (optional)
        :param str category: Category to organize the variable under (optional)
        :return: The new Variable wrapper
        :rtype: Variable
        :raises InvalidOperationError: if the add operation fails
        """
        require_unreal()
        import unreal

        self._validate()

        # Map the user-friendly type to a UE property type string.
        ue_type = _map_type(var_type)

        logger.info(
            "Adding variable '%s' (%s) to %s",
            name, ue_type, self.name
        )

        with unreal.ScopedEditorTransaction("PyUnreal: add variable '{}'".format(name)):
            try:
                unreal.BlueprintEditorLibrary.add_variable(
                    self._asset, name, ue_type
                )
            except Exception as e:
                raise InvalidOperationError(
                    "Failed to add variable '{}' ({}): {}".format(
                        name, ue_type, e
                    )
                )

            # Set category if provided.
            if category:
                try:
                    unreal.BlueprintEditorLibrary.set_variable_category(
                        self._asset, name, category
                    )
                except Exception:
                    logger.warning(
                        "Could not set category '%s' for variable '%s'",
                        category, name
                    )

        # Compile so the variable appears on the CDO.
        unreal.KismetEditorUtilities.compile_blueprint(self._asset)

        # Set the default value if provided.
        if default is not None:
            gen_class = self._asset.generated_class()
            if gen_class is not None:
                cdo = unreal.get_default_object(gen_class)
                if cdo is not None:
                    try:
                        cdo.set_editor_property(name, default)
                    except Exception as e:
                        logger.warning(
                            "Could not set default for '%s': %s", name, e
                        )

        # Save the asset.
        unreal.EditorAssetLibrary.save_asset(self.path)

        return Variable(self, name, ue_type, default)

    def set_default(self, property_name, value):
        """
        Set a Class Default Object property value.

        This sets values in the Blueprint's "Class Defaults" panel.

        :param str property_name: The property name on the CDO
        :param value: The value to set
        :return: self for method chaining
        :rtype: Blueprint
        :raises InvalidOperationError: if the set operation fails
        """
        require_unreal()
        import unreal

        self._validate()

        gen_class = self._asset.generated_class()
        if gen_class is None:
            raise InvalidOperationError(
                "Blueprint '{}' has no generated class — compile first.".format(
                    self.name
                )
            )

        cdo = unreal.get_default_object(gen_class)
        if cdo is None:
            raise InvalidOperationError(
                "Could not get CDO for '{}'.".format(self.name)
            )

        logger.info("Setting default '%s' = %s on %s", property_name, value, self.name)

        try:
            with unreal.ScopedEditorTransaction("PyUnreal: set default"):
                cdo.set_editor_property(property_name, value)
        except Exception as e:
            raise InvalidOperationError(
                "Failed to set default '{}' on '{}': {}".format(
                    property_name, self.name, e
                )
            )

        unreal.EditorAssetLibrary.save_asset(self.path)
        return self

    def get_default(self, property_name):
        """
        Get a Class Default Object property value.

        :param str property_name: The property name on the CDO
        :return: The property value
        :raises InvalidOperationError: if the property cannot be read
        """
        require_unreal()
        import unreal

        self._validate()

        gen_class = self._asset.generated_class()
        if gen_class is None:
            raise InvalidOperationError(
                "Blueprint '{}' has no generated class.".format(self.name)
            )

        cdo = unreal.get_default_object(gen_class)
        if cdo is None:
            raise InvalidOperationError(
                "Could not get CDO for '{}'.".format(self.name)
            )

        try:
            return cdo.get_editor_property(property_name)
        except Exception as e:
            raise InvalidOperationError(
                "Failed to read default '{}' on '{}': {}".format(
                    property_name, self.name, e
                )
            )

    def compile(self):
        """
        Compile this Blueprint.

        Should be called after adding components, variables, or
        modifying class defaults.

        :return: True if compilation succeeded
        :rtype: bool
        :raises InvalidOperationError: if compilation fails
        """
        require_unreal()
        import unreal

        self._validate()

        logger.info("Compiling Blueprint: %s", self.name)

        try:
            unreal.KismetEditorUtilities.compile_blueprint(self._asset)
        except Exception as e:
            raise InvalidOperationError(
                "Compilation failed for Blueprint '{}': {}".format(self.name, e)
            )

        # Check compilation status.
        try:
            status = self._asset.get_editor_property("status")
            # BlueprintStatus.BS_Error = 1
            if str(status) == "BlueprintStatus.BS_Error":
                raise InvalidOperationError(
                    "Blueprint '{}' compiled with errors. "
                    "Check the Output Log in UE for details.".format(self.name)
                )
        except InvalidOperationError:
            raise
        except Exception:
            pass

        # Save after compilation.
        unreal.EditorAssetLibrary.save_asset(self.path)

        logger.info("Compilation succeeded: %s", self.name)
        return True

    # --- Internal Helpers ----------------------------------------------

    def _find_scs_node(self, component_name):
        """
        Find an SCS node by component name.

        :param str component_name: The component instance name to find
        :return: The SCS node, or None if not found
        """
        scs = self._asset.simple_construction_script
        if scs is None:
            return None

        for node in scs.get_all_nodes():
            template = node.component_template
            if template is not None and template.get_name() == component_name:
                return node

        return None

    # --- String Representation -----------------------------------------

    def __repr__(self):
        try:
            name = self._asset.get_name() if self._asset else "None"
        except Exception:
            name = "invalid"
        return "<Blueprint '{}'>".format(name)


# --- Module-Level Helpers --------------------------------------------------

def _infer_type(value):
    """
    Infer a UE property type string from a Python value.

    :param value: A Python value read from a CDO
    :return: Best-guess UE property type string
    :rtype: str
    """
    if isinstance(value, bool):
        return "BoolProperty"
    elif isinstance(value, int):
        return "IntProperty"
    elif isinstance(value, float):
        return "FloatProperty"
    elif isinstance(value, str):
        return "StrProperty"
    else:
        return type(value).__name__
