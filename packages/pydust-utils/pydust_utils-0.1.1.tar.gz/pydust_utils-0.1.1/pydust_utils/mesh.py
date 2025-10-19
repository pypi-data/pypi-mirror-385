"""Convenience module for mesh building.

This module provides all mesh-related classes and functions in one place.

Example:
    >>> from pydust_utils import mesh
    >>> config = mesh.MeshConfig('Wing', 'v', 20, 'uniform', 0.25)
    >>> point = mesh.Point(0, 0, 0, 1.0, 0, 'naca0012')
    >>> my_mesh = mesh.PointwiseMesh(config, [point], lines)
"""

from .build_mesh import (
    Point,
    Line,
    Section,
    Region,
    MeshConfig,
    PointwiseMesh,
    ParametricMesh,
    write_pointwise_mesh,
    write_parametric_mesh,
)

__all__ = [
    'Point',
    'Line',
    'Section',
    'Region',
    'MeshConfig',
    'PointwiseMesh',
    'ParametricMesh',
    'write_pointwise_mesh',
    'write_parametric_mesh',
]