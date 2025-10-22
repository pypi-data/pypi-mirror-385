"""
pixtreme-legacy: Backward compatibility for _cp functions

This package provides legacy _cp functions for backward compatibility.
These functions are no longer available in the main pixtreme package as of v0.5.1.

Users are encouraged to migrate to the standard functions (without _cp suffix)
in the main pixtreme package, or continue using this legacy package if needed.

Functions
---------
apply_lut_cp : Apply 3D LUT with CuPy implementation
uyvy422_to_ycbcr444_cp : Convert UYVY422 to YCbCr444
ndi_uyvy422_to_ycbcr444_cp : Convert NDI UYVY422 to YCbCr444
yuv420p_to_ycbcr444_cp : Convert YUV420 to YCbCr444
yuv422p10le_to_ycbcr444_cp : Convert YUV422p10le to YCbCr444

Example
-------
>>> from pixtreme_legacy import apply_lut_cp
>>> result = apply_lut_cp(image, lut)

Migration
---------
Replace _cp functions with their standard equivalents:

>>> # Old (legacy)
>>> from pixtreme_legacy import apply_lut_cp
>>> result = apply_lut_cp(image, lut)
>>>
>>> # New (recommended)
>>> from pixtreme import apply_lut
>>> result = apply_lut(image, lut)
"""

from .color import (
    apply_lut_cp,
    ndi_uyvy422_to_ycbcr444_cp,
    uyvy422_to_ycbcr444_cp,
    yuv420p_to_ycbcr444_cp,
    yuv422p10le_to_ycbcr444_cp,
)

__version__ = "0.5.1"

__all__ = [
    "apply_lut_cp",
    "uyvy422_to_ycbcr444_cp",
    "ndi_uyvy422_to_ycbcr444_cp",
    "yuv420p_to_ycbcr444_cp",
    "yuv422p10le_to_ycbcr444_cp",
]
