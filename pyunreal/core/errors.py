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


class BridgeNotAvailableError(PyUnrealError):
    """
    Raised when an operation requires a C++ bridge plugin but none is loaded.

    Advanced features like AnimBP graph editing need a C++ bridge that
    exposes graph manipulation to Python.  Two bridges are supported:

    - **PyUnrealBridge** (free, standalone) — install in your UE project
    - **MCA Editor** (premium, includes the bridge) — https://mcaeditor.com

    This exception includes install guidance so the user knows what to do.
    """

    def __init__(self, operation=""):
        # Build a helpful message that tells the user exactly what to do.
        if operation:
            msg = "'{}' requires a C++ bridge plugin (PyUnrealBridge or MCA Editor).".format(operation)
        else:
            msg = "This operation requires a C++ bridge plugin (PyUnrealBridge or MCA Editor)."

        msg += (
            "\n\nInstall one of:\n"
            "  - PyUnrealBridge (free): https://github.com/ncomes/pyunreal\n"
            "  - MCA Editor (premium): https://mcaeditor.com"
        )
        super().__init__(msg)
        self.operation = operation


# Backward compatibility alias — old code may catch this by name.
MCAScriptingNotAvailableError = BridgeNotAvailableError


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
