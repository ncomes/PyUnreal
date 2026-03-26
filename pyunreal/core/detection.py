"""
Runtime detection of the Unreal Engine environment and C++ bridge plugin.

PyUnreal's AnimBP features require a C++ bridge that exposes graph editing
to Python.  Two bridges are supported:

- **PyUnrealBridge** (standalone, open source) — ``unreal.PyUnrealBlueprintLibrary``
- **MCA Editor** (premium, includes PyUnrealBridge) — ``unreal.MCAAnimBlueprintLibrary``

Detection checks for both and prefers PyUnrealBridge.  Results are cached
at module level so the import checks and hasattr calls run only once per
Python session.  All other PyUnreal modules should use the ``require_*``
helpers rather than doing their own import checks.
"""

from pyunreal.core.errors import PyUnrealEnvironmentError
from pyunreal.core.errors import BridgeNotAvailableError


# --- Cache -------------------------------------------------------------
# Module-level dict stores detection results.  Using a dict rather than
# bare globals so the cache is easy to reset in tests.
_cache = {}


# --- Detection Helpers -------------------------------------------------

def _unreal_available():
    """
    Check whether the ``unreal`` module can be imported.

    :return: True if running inside UE's Python interpreter
    :rtype: bool
    """
    if "unreal" not in _cache:
        try:
            import unreal  # noqa: F401 — side-effect import for detection
            _cache["unreal"] = True
        except ImportError:
            _cache["unreal"] = False
    return _cache["unreal"]


def _bridge_available():
    """
    Check whether a C++ bridge plugin is loaded.

    Checks for two bridge libraries in order of preference:
    1. ``PyUnrealBlueprintLibrary`` (standalone PyUnrealBridge plugin)
    2. ``MCAAnimBlueprintLibrary`` (MCA Editor plugin, backward compat)

    :return: True if either bridge library is available
    :rtype: bool
    """
    if "bridge" not in _cache:
        if not _unreal_available():
            _cache["bridge"] = False
            _cache["bridge_class"] = None
        else:
            import unreal

            # Prefer the standalone PyUnrealBridge first.
            if hasattr(unreal, "PyUnrealBlueprintLibrary"):
                _cache["bridge"] = True
                _cache["bridge_class"] = unreal.PyUnrealBlueprintLibrary
            # Fall back to MCA Editor's library for backward compatibility.
            elif hasattr(unreal, "MCAAnimBlueprintLibrary"):
                _cache["bridge"] = True
                _cache["bridge_class"] = unreal.MCAAnimBlueprintLibrary
            else:
                _cache["bridge"] = False
                _cache["bridge_class"] = None

    return _cache["bridge"]


def get_bridge_library():
    """
    Return the C++ bridge library class for AnimBP operations.

    Returns whichever is available: ``PyUnrealBlueprintLibrary`` (preferred)
    or ``MCAAnimBlueprintLibrary`` (backward compat).  Both expose the
    same function signatures.

    :return: The bridge library class
    :rtype: type
    :raises BridgeNotAvailableError: if no bridge is loaded
    """
    require_bridge()
    return _cache["bridge_class"]


# --- Backward Compatibility Aliases ------------------------------------
# These preserve the old API so existing code using require_mca_scripting
# continues to work without changes.

def _mca_scripting_available():
    """
    Check whether any AnimBP bridge is available.

    .. deprecated:: 0.2.0
        Use :func:`_bridge_available` instead.

    :return: True if a bridge library is available
    :rtype: bool
    """
    return _bridge_available()


# --- Requirement Gates -------------------------------------------------

def require_unreal():
    """
    Raise if not running inside Unreal Engine's Python interpreter.

    Call this at the top of any function that uses the ``unreal`` module.

    :raises PyUnrealEnvironmentError: if ``unreal`` cannot be imported
    """
    if not _unreal_available():
        raise PyUnrealEnvironmentError(
            "This function requires Unreal Engine's Python interpreter. "
            "The 'unreal' module is not available in this environment."
        )


def require_bridge(operation=""):
    """
    Raise if no C++ bridge plugin is loaded.

    Call this at the top of any function that needs AnimBP graph editing
    operations (state machines, states, transitions, etc.).

    :param str operation: Optional name of the operation for the error message
    :raises BridgeNotAvailableError: if no bridge plugin is loaded
    """
    # Also checks for unreal first — no point checking the plugin if
    # we are not even inside UE.
    require_unreal()
    if not _bridge_available():
        raise BridgeNotAvailableError(operation)


def require_mca_scripting(operation=""):
    """
    Raise if no AnimBP bridge is available.

    .. deprecated:: 0.2.0
        Use :func:`require_bridge` instead.  This alias is kept for
        backward compatibility.

    :param str operation: Optional name of the operation for the error message
    :raises BridgeNotAvailableError: if no bridge plugin is loaded
    """
    require_bridge(operation)


def reset_cache():
    """
    Clear the detection cache.  Useful in tests.
    """
    _cache.clear()
