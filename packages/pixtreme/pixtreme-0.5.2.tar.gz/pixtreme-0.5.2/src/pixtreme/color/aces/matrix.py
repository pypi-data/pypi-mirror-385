"""
ACES color space matrix transformations.

References:
- OpenColorIO-Configs ACES 1.2: https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES
- SMPTE ST 2065-1: ACES2065-1 specification
- colour-science/colour: https://github.com/colour-science/colour
"""

import cupy as cp
import numpy as np

# ============================================================================
# ACES Primaries and Matrices
# ============================================================================

# ACES AP0 Primaries (ACES2065-1)
_AP0_PRIMARIES = np.array([
    [0.73470, 0.26530],  # Red
    [0.00000, 1.00000],  # Green
    [0.00010, -0.07700], # Blue
], dtype=np.float32)

# ACES AP0 ↔ XYZ Matrices
_MATRIX_AP0_TO_XYZ = np.array([
    [0.9525523959, 0.0000000000, 0.0000936786],
    [0.3439664498, 0.7281660966, -0.0721325464],
    [0.0000000000, 0.0000000000, 1.0088251844],
], dtype=np.float32)

_MATRIX_XYZ_TO_AP0 = np.array([
    [1.0498110175, 0.0000000000, -0.0000974845],
    [-0.4959030231, 1.3733130458, 0.0982400361],
    [0.0000000000, 0.0000000000, 0.9912520182],
], dtype=np.float32)

# ============================================================================
# Rec.709 / sRGB Matrices
# ============================================================================

# Rec.709 RGB ↔ XYZ Matrices (D65)
# Note: sRGB and Rec.709 share the same primaries and white point (D65)
_MATRIX_REC709_TO_XYZ_D65 = np.array([
    [0.4123907993, 0.3575843394, 0.1804807884],
    [0.2126390059, 0.7151686788, 0.0721923154],
    [0.0193308187, 0.1191947798, 0.9505321522],
], dtype=np.float32)

_MATRIX_XYZ_D65_TO_REC709 = np.array([
    [3.2409699419, -1.5373831776, -0.4986107603],
    [-0.9692436363, 1.8759675015, 0.0415550574],
    [0.0556300797, -0.2039769589, 1.0569715142],
], dtype=np.float32)

# ============================================================================
# Chromatic Adaptation: D65 ↔ D60
# ============================================================================

# Bradford chromatic adaptation matrix (D65 → D60)
_MATRIX_BRADFORD_D65_TO_D60 = np.array([
    [1.01303, 0.00610, -0.01497],
    [0.00769, 0.99816, -0.00503],
    [-0.00284, 0.00468, 0.92450],
], dtype=np.float32)

# Bradford chromatic adaptation matrix (D60 → D65)
_MATRIX_BRADFORD_D60_TO_D65 = np.array([
    [0.98722, -0.00611, 0.01596],
    [-0.00759, 1.00186, 0.00533],
    [0.00307, -0.00509, 1.08168],
], dtype=np.float32)

# ============================================================================
# Combined Matrices (OCIO ACES 1.2 standard)
# ============================================================================

# Rec.709 → ACES2065-1 (Direct matrix)
# Source: OpenColorIO-Configs ACES 1.2 (imageworks/colour-science)
# Computed as: XYZ_TO_AP0 @ REC709_TO_XYZ
# Reference: "Utility - Linear - Rec.709" to_reference transform
_MATRIX_REC709_TO_ACES2065_1 = np.array([
    [0.4396466315, 0.3829816580, 0.1773722917],
    [0.0897805765, 0.8134407997, 0.0967797637],
    [0.0175445601, 0.1115567982, 0.8708978295],
], dtype=np.float32)

# ACES2065-1 → Rec.709 (Direct matrix)
# Source: OpenColorIO-Configs ACES 1.2 (imageworks/colour-science)
# Computed as: inverse of REC709_TO_ACES2065_1
# Reference: "Utility - Linear - Rec.709" from_reference transform
_MATRIX_ACES2065_1_TO_REC709 = np.array([
    [2.5216495991, -1.1369100809, -0.3849769831],
    [-0.2752373815, 1.3696714640, -0.0942850783],
    [-0.0159372762, -0.1477973461, 1.1639230251],
], dtype=np.float32)


def apply_matrix_rgb(
    image: cp.ndarray | np.ndarray,
    matrix: np.ndarray
) -> cp.ndarray | np.ndarray:
    """
    Apply a 3x3 color matrix to an RGB image.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        RGB image of shape (H, W, 3)
    matrix : np.ndarray
        3x3 transformation matrix

    Returns
    -------
    cp.ndarray | np.ndarray
        Transformed RGB image
    """
    xp = cp.get_array_module(image)

    # Convert matrix to same array type as image
    if isinstance(image, cp.ndarray):
        matrix = cp.asarray(matrix, dtype=image.dtype)
    else:
        matrix = np.asarray(matrix, dtype=image.dtype)

    # Apply matrix: (H, W, 3) @ (3, 3).T = (H, W, 3)
    return xp.dot(image, matrix.T)


def rec709_to_aces2065_1(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert linear Rec.709 RGB to ACES2065-1.

    Note: Input must be linear (gamma-decoded) Rec.709.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        Linear Rec.709 RGB image [0-1+]

    Returns
    -------
    cp.ndarray | np.ndarray
        ACES2065-1 image [0-1+]
    """
    return apply_matrix_rgb(image, _MATRIX_REC709_TO_ACES2065_1)


def aces2065_1_to_rec709(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert ACES2065-1 to linear Rec.709 RGB.

    Note: Output is linear (gamma-decoded) Rec.709.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        ACES2065-1 image [0-1+]

    Returns
    -------
    cp.ndarray | np.ndarray
        Linear Rec.709 RGB image [0-1+]
    """
    return apply_matrix_rgb(image, _MATRIX_ACES2065_1_TO_REC709)


# ============================================================================
# Multi-step transformations (for reference/testing)
# ============================================================================

def rec709_to_xyz_d65(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """Convert linear Rec.709 RGB to CIE XYZ (D65)."""
    return apply_matrix_rgb(image, _MATRIX_REC709_TO_XYZ_D65)


def xyz_d65_to_rec709(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """Convert CIE XYZ (D65) to linear Rec.709 RGB."""
    return apply_matrix_rgb(image, _MATRIX_XYZ_D65_TO_REC709)


def xyz_d65_to_d60(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """Apply Bradford chromatic adaptation from D65 to D60."""
    return apply_matrix_rgb(image, _MATRIX_BRADFORD_D65_TO_D60)


def xyz_d60_to_d65(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """Apply Bradford chromatic adaptation from D60 to D65."""
    return apply_matrix_rgb(image, _MATRIX_BRADFORD_D60_TO_D65)


def xyz_d60_to_ap0(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """Convert CIE XYZ (D60) to ACES AP0 (ACES2065-1)."""
    return apply_matrix_rgb(image, _MATRIX_XYZ_TO_AP0)


def ap0_to_xyz_d60(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """Convert ACES AP0 (ACES2065-1) to CIE XYZ (D60)."""
    return apply_matrix_rgb(image, _MATRIX_AP0_TO_XYZ)
