"""
Viewport control module for PyUnreal.

Provides functions for manipulating the Unreal Editor viewport —
focusing on actors, setting camera transforms, and taking screenshots.

Usage::

    from pyunreal.viewport import viewport

    viewport.focus('Chair_01')
    viewport.set_camera(location=(0, 0, 500), rotation=(0, -90, 0))
    viewport.screenshot('/Game/Screenshots/shot.png', width=1920, height=1080)
"""

from pyunreal.viewport import viewport_ops as viewport
