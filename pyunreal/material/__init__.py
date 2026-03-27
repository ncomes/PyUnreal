"""
Material authoring module for PyUnreal.

Provides Pythonic wrappers for creating materials, setting parameters,
and assigning materials to actors.  All operations use standard UE
Python APIs — no C++ bridge required.

Usage::

    from pyunreal.material import Material

    mat = Material.create('M_Glowing', package_path='/Game/Materials')
    mat.set_param('BaseColor', (1.0, 0.2, 0.0, 1.0))
    mat.set_param('Roughness', 0.3)
    mat.assign_to('Chair_01')
"""

from pyunreal.material.material import Material
