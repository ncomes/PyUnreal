"""
Runtime detection of the Unreal Engine environment and optional MCA Editor plugin.

Results are cached at module level so the import checks and hasattr calls
run only once per Python session.  All other PyUnreal modules should use
the ``require_*`` helpers rather than doing their own import checks.
"""

from pyunreal.core.errors import PyUnrealEnvironmentError
from pyunreal.core.errors import MCAScriptingNotAvailableError


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


def _mca_scripting_available():
    """
    Check whether the MCAEditorScripting C++ module is loaded.

    This module ships with the MCA Editor plugin and exposes
    ``unreal.MCAAnimBlueprintLibrary`` among other classes.

    :return: True if MCAEditorScripting is available
    :rtype: bool
    """
    if "mca" not in _cache:
        if not _unreal_available():
            _cache["mca"] = False
        else:
            import unreal
            _cache["mca"] = hasattr(unreal, "MCAAnimBlueprintLibrary")
    return _cache["mca"]


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


def require_mca_scripting(operation=""):
    """
    Raise if the MCA Editor plugin is not loaded.

    Call this at the top of any function that needs MCAEditorScripting
    C++ functions (AnimBP graph editing, etc.).

    :param str operation: Optional name of the operation for the error message
    :raises MCAScriptingNotAvailableError: if the plugin is not loaded
    """
    # Also checks for unreal first — no point checking the plugin if
    # we are not even inside UE.
    require_unreal()
    if not _mca_scripting_available():
        raise MCAScriptingNotAvailableError(operation)


def reset_cache():
    """
    Clear the detection cache.  Useful in tests.
    """
    _cache.clear()
