"""
Custom exception hierarchy for PyUnreal.

All PyUnreal exceptions inherit from :class:`PyUnrealError` so callers
can catch the base class for broad handling or specific subclasses for
targeted recovery.
"""


# --- Base Exception ----------------------------------------------------

class PyUnrealError(Exception):
    """Base exception for all PyUnreal errors."""
    pass


# --- Environment Errors ------------------------------------------------

class PyUnrealEnvironmentError(PyUnrealError):
    """
    Raised when PyUnreal is used outside of Unreal Engine's Python interpreter.

    The ``unreal`` module only exists inside UE's embedded Python.  If this
    exception fires, the caller is running in standalone Python, Maya, or
    another host that does not provide the ``unreal`` module.
    """
    pass


class MCAScriptingNotAvailableError(PyUnrealError):
    """
    Raised when an operation requires the MCA Editor plugin but it is not loaded.

    Advanced features like AnimBP graph editing need the MCAEditorScripting
    C++ module that ships with MCA Editor.  This exception includes the
    install URL so the user knows where to get it.
    """

    def __init__(self, operation=""):
        # Build a helpful message that tells the user exactly what to do.
        msg = (
            "This operation requires the MCA Editor plugin "
            "(MCAEditorScripting C++ module)."
        )
        if operation:
            msg = "'{}' requires the MCA Editor plugin.".format(operation)
        msg += " Install from: https://mcaeditor.com"
        super().__init__(msg)
        self.operation = operation


# --- Asset Errors ------------------------------------------------------

class AssetNotFoundError(PyUnrealError):
    """
    Raised when an asset path resolves to None in the Content Browser.

    Stores the path that failed so callers can inspect it programmatically.
    """

    def __init__(self, asset_path):
        super().__init__("Asset not found: '{}'".format(asset_path))
        self.asset_path = asset_path


# --- Operation Errors --------------------------------------------------

class InvalidOperationError(PyUnrealError):
    """
    Raised when a PyUnreal operation fails logically.

    Examples: adding a duplicate state, compiling a corrupt blueprint,
    operating on a stale wrapper whose underlying UE object was deleted.
    """
    pass
