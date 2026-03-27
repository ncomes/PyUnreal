"""
Variable wrapper for Blueprint user-defined variables.

A Variable represents a single user-defined property on a Blueprint.
It stores its name, type, and a reference to the parent Blueprint so
it can read/write defaults through the Class Default Object (CDO).

Variables are created by :meth:`Blueprint.add_variable` or discovered
via :meth:`Blueprint.variables`, not instantiated directly.
"""

import logging

from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import InvalidOperationError

# Module-level logger.
logger = logging.getLogger(__name__)


# --- Type Mapping ---------------------------------------------------------
# Maps user-friendly type names to UE property type names used by
# BlueprintEditorLibrary.add_variable().  Users pass short names like
# "int" or "bool"; we map them to UE's internal property type strings.

TYPE_MAP = {
    "bool": "BoolProperty",
    "int": "IntProperty",
    "float": "FloatProperty",
    "double": "DoubleProperty",
    "str": "StrProperty",
    "string": "StrProperty",
    "name": "NameProperty",
    "text": "TextProperty",
}


def _map_type(var_type):
    """
    Map a user-friendly type name to a UE property type string.

    If the input is already a UE property type string (ends with
    "Property"), it is returned unchanged.

    :param str var_type: User-friendly type name or UE property type
    :return: UE property type string
    :rtype: str
    """
    # Already a UE property type string.
    if var_type.endswith("Property"):
        return var_type

    # Look up in the friendly-name map.
    mapped = TYPE_MAP.get(var_type.lower())
    if mapped:
        return mapped

    # Unknown — return as-is and let UE handle validation.
    return var_type


class Variable:
    """
    A user-defined variable on a Blueprint.

    :param blueprint: The parent Blueprint wrapper
    :param str name: The variable name
    :param str var_type: The UE property type string (e.g. 'IntProperty')
    :param default: The current default value (from the CDO), or None
    """

    def __init__(self, blueprint, name, var_type="", default=None):
        # Parent Blueprint — needed to reach the UE asset for write operations.
        self._blueprint = blueprint

        # Variable name as it appears in the Blueprint editor.
        self._name = name

        # UE property type string (e.g. "IntProperty", "BoolProperty").
        self._var_type = var_type

        # Cached default value from the CDO.
        self._default = default

    # --- Properties (read-only) ----------------------------------------

    @property
    def name(self):
        """
        The variable name.

        :rtype: str
        """
        return self._name

    @property
    def var_type(self):
        """
        The UE property type string (e.g. 'IntProperty', 'BoolProperty').

        :rtype: str
        """
        return self._var_type

    @property
    def default(self):
        """
        The current default value from the Class Default Object.

        This is the value set in the "Default Value" column of the
        Blueprint Variables panel.

        :rtype: varies
        """
        return self._default

    @property
    def blueprint(self):
        """
        The parent Blueprint this variable belongs to.

        :rtype: Blueprint
        """
        return self._blueprint

    # --- Methods -------------------------------------------------------

    def set(self, value):
        """
        Set the default value for this variable on the Blueprint's CDO.

        Compiles the Blueprint and saves the asset after updating.

        :param value: The new default value
        :return: self for method chaining
        :rtype: Variable
        :raises InvalidOperationError: if the set operation fails
        """
        require_unreal()
        import unreal

        bp_asset = self._blueprint._asset
        self._blueprint._validate()

        logger.info("Setting variable '%s' default to: %s", self._name, value)

        # Get the CDO to set the default value on.
        gen_class = bp_asset.generated_class()
        if gen_class is None:
            raise InvalidOperationError(
                "Blueprint '{}' has no generated class — compile first.".format(
                    self._blueprint.name
                )
            )

        cdo = unreal.get_default_object(gen_class)
        if cdo is None:
            raise InvalidOperationError(
                "Could not get Class Default Object for '{}'.".format(
                    self._blueprint.name
                )
            )

        try:
            with unreal.ScopedEditorTransaction("PyUnreal: set variable '{}'".format(self._name)):
                cdo.set_editor_property(self._name, value)
        except Exception as e:
            raise InvalidOperationError(
                "Failed to set variable '{}' to '{}': {}".format(
                    self._name, value, e
                )
            )

        # Update the cached default value.
        self._default = value

        # Save the asset so the change persists.
        asset_path = bp_asset.get_path_name()
        unreal.EditorAssetLibrary.save_asset(asset_path)

        return self

    # --- String Representation -----------------------------------------

    def __repr__(self):
        return "<Variable '{}' ({})>".format(self._name, self._var_type)
