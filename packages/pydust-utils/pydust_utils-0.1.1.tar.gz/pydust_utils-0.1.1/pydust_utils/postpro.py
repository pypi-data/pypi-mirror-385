"""Convenience module for post-processing.

This module provides all post-processing parsers and data structures in one place.

Example:
    >>> from pydust_utils import postpro
    >>> data = postpro.read_sectional('sectional_loads.dat')
    >>> print(data.sec.shape)
"""

from .parse_postpro_files import (
    SectionalData,
    ProbesData,
    ChordwiseData,
    IntegralData,
    HingeData,
    read_sectional,
    read_probes,
    read_chordwise,
    read_integral,
    read_hinge,
)

__all__ = [
    'SectionalData',
    'ProbesData',
    'ChordwiseData',
    'IntegralData',
    'HingeData',
    'read_sectional',
    'read_probes',
    'read_chordwise',
    'read_integral',
    'read_hinge',
]