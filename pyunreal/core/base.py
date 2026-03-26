"""
Base wrapper class for all PyUnreal objects.

Every PyUnreal wrapper (AnimBlueprint, StateMachine, State, etc.) inherits
from :class:`UnrealObjectWrapper`.  The base class holds a reference to the
underlying Unreal Engine object and provides common utilities for validation,
string representation, and equality comparison.
"""

from pyunreal.core.errors import InvalidOperationError


class UnrealObjectWrapper:
    """
    Base class for PyUnreal objects that wrap a UE UObject.

    Subclasses that wrap an actual UObject (like AnimBlueprint) store it in
    ``self._asset``.  Subclasses that are name-based references (like
    StateMachine, State) may not use ``_asset`` and instead store a name
    string plus a parent reference.

    :param ue_object: The underlying Unreal Engine UObject, or None for
                      name-based wrappers.
    """

    def __init__(self, ue_object=None):
        # The actual Unreal Engine UObject being wrapped.
        # Will be None for name-based reference types (StateMachine, State, etc.).
        self._asset = ue_object

    def _validate(self):
        """
        Check that the underlying UE object is still valid.

        UE objects can be garbage collected while Python wrappers still
        exist.  This method should be called before any operation that
        touches the underlying object.

        :raises InvalidOperationError: if the wrapped object is None
        """
        if self._asset is None:
            raise InvalidOperationError(
                "Wrapped UE object is None — it may have been deleted or "
                "garbage collected by Unreal Engine."
            )

    @property
    def ue_object(self):
        """
        Direct access to the underlying UE UObject.

        For advanced users who need to call UE Python APIs directly
        on the wrapped object.

        :return: The raw Unreal Engine object
        :rtype: unreal.Object or None
        """
        return self._asset

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "<{}>".format(cls_name)

    def __eq__(self, other):
        if not isinstance(other, UnrealObjectWrapper):
            return NotImplemented
        return self._asset == other._asset

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
