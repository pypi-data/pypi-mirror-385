"""
Coordinate systems module for kerrpy.

This module contains implementations of different coordinate systems
used in general relativity, including Cartesian, spherical,
and Boyer-Lindquist coordinates.
"""

from .base import CoordinateBase
from .cartesian import Cartesian
from .spherical import Spherical
from .boyer_lindquist import BoyerLindquist

# Dictionary mapping coordinate system names to their classes
coordinate_systems = {
    "CoordinateBase": CoordinateBase,
    "Cartesian": Cartesian,
    "Spherical": Spherical,
    "BoyerLindquist": BoyerLindquist,
}

__all__ = [
    "CoordinateBase",
    "Cartesian",
    "Spherical",
    "BoyerLindquist",
    "coordinate_systems",
]
