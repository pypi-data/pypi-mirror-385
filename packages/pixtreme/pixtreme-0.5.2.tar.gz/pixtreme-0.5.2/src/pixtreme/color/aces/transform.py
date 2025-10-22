"""
ACES Input Device Transforms (IDT) and Output Device Transforms (ODT).

This module provides high-level ACES color transformations following ACES 1.2
standard and Nuke/VFX industry conventions.

The default IDT (`rec709_to_aces2065_1`) follows the "Utility - sRGB - Texture"
approach, which is the standard for CG/VFX workflows (Nuke, Houdini, Maya, etc.).
White values remain normalized (≈1.0) for display-referred content.

References:
- ACES Technical Documentation: https://acescentral.com
- OpenColorIO-Configs ACES 1.2: https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES
"""

import cupy as cp
import numpy as np

from ...utils.dtypes import to_float32
from .eotf import rec709_inverse_oetf, rec709_oetf
from .matrix import rec709_to_aces2065_1 as matrix_rec709_to_aces
from .matrix import aces2065_1_to_rec709 as matrix_aces_to_rec709


def rec709_to_aces2065_1(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert Rec.709 to ACES2065-1 using ACES 1.2 IDT.

    This implements the "Utility - sRGB - Texture" IDT approach, which is the
    standard for CG/VFX workflows (Nuke, Houdini, Maya, etc.). The input is
    assumed to be display-referred Rec.709 encoded content.

    The transformation chain:
    1. Rec.709 Inverse OETF (decode gamma ~2.2 to linear)
    2. Color matrix transform (Rec.709 primaries → ACES AP0 primaries)

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        Rec.709 encoded image [0-1] (with gamma, not linear)

    Returns
    -------
    cp.ndarray | np.ndarray
        ACES2065-1 image (linear, scene-referred, AP0 primaries)
        White values remain normalized (≈1.0) for display-referred content.

    Notes
    -----
    This implementation follows the Nuke/VFX industry standard:
    - Input: Display-referred Rec.709 content (textures, graphics, graded footage)
    - Output: ACES2065-1 with normalized white level (≈1.0)
    - Compatible with: Nuke, Houdini, Maya, Blender ACES workflows

    For raw camera footage requiring scene-referred conversion with elevated
    white levels (≈16.3), different IDTs should be used.

    Examples
    --------
    >>> import pixtreme as px
    >>> # Load Rec.709 image (e.g., PNG from Photoshop)
    >>> img = px.imread("texture.png")
    >>> # Convert to ACES2065-1 for ACES workflow
    >>> aces_img = px.rec709_to_aces2065_1(img)
    """
    image = to_float32(image, clip=False)
    # Decode Rec.709 gamma to linear
    image = rec709_inverse_oetf(image)
    # Transform to ACES2065-1
    image = matrix_rec709_to_aces(image)
    return image


def aces2065_1_to_rec709(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert ACES2065-1 to Rec.709 using ACES 1.2 ODT.

    This implements the simplified Rec.709 ODT which outputs Rec.709 encoded
    signal suitable for display or further processing.

    The transformation chain:
    1. Color matrix transform (ACES AP0 primaries → Rec.709 primaries, linear)
    2. Clipping of out-of-gamut colors
    3. Rec.709 OETF (encode linear to gamma ~2.2)

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        ACES2065-1 image (linear, scene-referred, AP0 primaries)

    Returns
    -------
    cp.ndarray | np.ndarray
        Rec.709 encoded image [0-1] (with gamma, suitable for display)

    Notes
    -----
    Out-of-gamut colors (negative values after matrix transform) are clipped
    to zero. For more sophisticated tone mapping and gamut compression, consider
    using full RRT/ODT transforms or LUT-based approaches.

    Examples
    --------
    >>> import pixtreme as px
    >>> # ACES2065-1 image from rendering or grading
    >>> aces_img = px.imread("render_aces.exr")
    >>> # Convert to Rec.709 for display
    >>> rec709_img = px.aces2065_1_to_rec709(aces_img)
    >>> px.imwrite("output.png", rec709_img)
    """
    image = to_float32(image, clip=False)
    # Transform to Rec.709 linear
    image = matrix_aces_to_rec709(image)
    # Clip out-of-gamut colors (negative values)
    image = cp.clip(image, 0, None)
    # Encode to Rec.709 gamma
    image = rec709_oetf(image)
    image = cp.clip(image, 0, 1)
    return image
