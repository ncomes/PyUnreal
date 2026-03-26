"""
Shared utility functions for PyUnreal.

Provides convenience wrappers around common Unreal Engine operations like
loading assets.  These are intentionally thin — they return raw UE objects,
not PyUnreal wrappers, so they work as general-purpose helpers.
"""

import logging

from pyunreal.core.detection import require_unreal
from pyunreal.core.errors import AssetNotFoundError

# Module-level logger for tracking asset operations.
logger = logging.getLogger(__name__)


# --- Asset Loading -----------------------------------------------------

def load(asset_path):
    """
    Load an asset from the Content Browser by path.

    Wraps ``unreal.EditorAssetLibrary.load_asset()`` with validation.
    Returns the raw UE object — PyUnreal class constructors handle
    wrapping into Pythonic objects.

    :param str asset_path: Full content path (e.g. '/Game/Characters/SK_Mannequin')
    :return: The loaded UE asset object
    :rtype: unreal.Object
    :raises AssetNotFoundError: if the asset does not exist at the given path
    """
    require_unreal()
    import unreal

    logger.debug("Loading asset: %s", asset_path)
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)

    if asset is None:
        raise AssetNotFoundError(asset_path)

    logger.debug("Loaded: %s (%s)", asset_path, type(asset).__name__)
    return asset


def asset_exists(asset_path):
    """
    Check whether an asset exists in the Content Browser without loading it.

    :param str asset_path: Full content path to check
    :return: True if the asset exists
    :rtype: bool
    """
    require_unreal()
    import unreal

    return unreal.EditorAssetLibrary.does_asset_exist(asset_path)
