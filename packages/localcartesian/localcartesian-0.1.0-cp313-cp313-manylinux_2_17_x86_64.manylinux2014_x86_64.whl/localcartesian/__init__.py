"""
LocalCartesian: Fast GPS to local Cartesian coordinate conversion.

This package provides functions to convert GPS coordinates (latitude, longitude)
to local Cartesian coordinates (x, y) and vice versa using the GeographicLib library.
"""

__version__ = "0.1.0"

try:
    from ._core import gps2xy, xy2gps
except ImportError as e:
    raise ImportError(
        "Could not import the compiled extension module. "
        "Make sure the package was installed correctly and that "
        "GeographicLib is available on your system."
    ) from e

__all__ = ["gps2xy", "xy2gps"]
