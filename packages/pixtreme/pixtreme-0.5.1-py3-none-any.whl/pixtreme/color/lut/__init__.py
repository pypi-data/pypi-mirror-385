"""
3D LUT Operations

Provides functions for reading and applying 3D Lookup Tables (LUTs) for color grading
and transformation workflows.

Functions
---------
read_lut : Load .cube LUT files
    Reads 3D LUT data from .cube format files with MD5-based caching for performance.
    Returns CuPy ndarray with shape (N, N, N, 3).

apply_lut : Apply 3D LUT to images (CUDA kernel)
    GPU-accelerated LUT application using custom CUDA kernels.
    Supports trilinear and tetrahedral interpolation methods.

Interpolation Methods
---------------------
0 : Trilinear interpolation (default)
    Fast, smooth interpolation suitable for most use cases.

1 : Tetrahedral interpolation
    More accurate color preservation, slightly slower.
    Recommended for critical color grading workflows.

Usage
-----
```python
import pixtreme as px

# Load LUT file
lut = px.color.lut.read_lut("path/to/lut.cube")

# Apply to image (trilinear interpolation)
result = px.color.lut.apply_lut(image, lut, interpolation=0)

# Apply with tetrahedral interpolation
result = px.color.lut.apply_lut(image, lut, interpolation=1)
```

Performance
-----------
- LUT files are cached in user cache directory with MD5 hashing
- CUDA kernel implementation provides high-performance GPU acceleration
- All functions operate on GPU memory (CuPy arrays)
"""

from .apply_lut import apply_lut
from .read_lut import read_lut

__all__ = [
    "read_lut",
    "apply_lut",
]
