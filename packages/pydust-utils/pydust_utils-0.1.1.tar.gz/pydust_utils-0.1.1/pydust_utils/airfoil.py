"""Convenience module for airfoil data generation.

This module provides airfoil data generation utilities.

Example:
    >>> from pydust_utils import airfoil
    >>> airfoil.generate_airfoil_data('naca0012', mach_range, alpha_range)
"""

from .c81generator import generate_airfoil_data

__all__ = ['generate_airfoil_data']