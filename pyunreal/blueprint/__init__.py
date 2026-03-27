"""
Blueprint authoring module for PyUnreal.

Provides Pythonic wrappers for creating and configuring Blueprints,
adding components, managing variables, and setting class defaults.
All operations use standard UE Python APIs — no C++ bridge required.

Usage::

    from pyunreal.blueprint import Blueprint

    bp = Blueprint.create('/Game/Blueprints', 'BP_Pickup', parent='Actor')
    mesh = bp.add_component('StaticMeshComponent', name='PickupMesh')
    bp.add_variable('PointValue', 'int', default=10)
    bp.compile()
"""

from pyunreal.blueprint.blueprint import Blueprint
from pyunreal.blueprint.component import Component
from pyunreal.blueprint.variable import Variable
