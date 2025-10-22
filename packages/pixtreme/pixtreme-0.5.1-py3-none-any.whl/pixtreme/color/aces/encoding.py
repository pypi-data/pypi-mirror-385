"""
ACES log encoding and color space transformations (ACEScct, ACEScg).

ACEScg (AP1):
    Linear working space for CG/VFX, using AP1 primaries.

ACEScct (AP1 Log):
    Log-encoded version of ACEScg, commonly used in color grading.
    Uses a log curve optimized for grading controls.

References:
- SMPTE S-2016-001: ACEScg specification
- Academy TB-2014-004: ACEScct specification
"""

import cupy as cp
import numpy as np

from ...utils.dlpack import to_cupy
from ...utils.dtypes import to_float32

# AP0 (ACES2065-1) ↔ AP1 (ACEScg) transformation matrices
ap0_to_ap1_matrix = cp.array(
    [
        [1.4514393161, -0.2365107469, -0.2149285693],
        [-0.0765537734, 1.1762296998, -0.0996759264],
        [0.0083161484, -0.0060324498, 0.9977163014],
    ]
)

ap1_to_ap0_matrix = cp.array(
    [
        [0.6954522414, 0.1406786965, 0.1638690622],
        [0.0447945634, 0.8596711185, 0.0955343182],
        [-0.0055258826, 0.0040252103, 1.0015006723],
    ]
)


def aces2065_1_to_acescct(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert ACES2065-1 (AP0) to ACEScct (AP1 log-encoded).

    ACEScct uses a log curve optimized for color grading, commonly used
    in DaVinci Resolve and other grading applications.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        ACES2065-1 image (AP0, linear)

    Returns
    -------
    cp.ndarray | np.ndarray
        ACEScct image (AP1, log-encoded)
    """
    image = to_float32(image, clip=False)

    # Remember input type
    was_numpy = isinstance(image, np.ndarray)

    # Convert to CuPy for processing
    if was_numpy:
        image = to_cupy(image)

    # AP0 → AP1
    ap1_image = cp.dot(image, ap0_to_ap1_matrix.T)

    # Apply ACEScct log curve
    acescct_image = cp.where(
        ap1_image <= 0.0078125,
        10.5402377416545 * ap1_image + 0.0729055341958355,
        (cp.log2(ap1_image) + 9.72) / 17.52,
    )

    # Convert back to original type
    if was_numpy:
        return cp.asnumpy(acescct_image)
    return acescct_image


def acescct_to_aces2065_1(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert ACEScct (AP1 log-encoded) to ACES2065-1 (AP0).

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        ACEScct image (AP1, log-encoded)

    Returns
    -------
    cp.ndarray | np.ndarray
        ACES2065-1 image (AP0, linear)
    """
    image = to_float32(image, clip=False)

    # Remember input type
    was_numpy = isinstance(image, np.ndarray)

    # Convert to CuPy for processing
    if was_numpy:
        image = to_cupy(image)

    # Apply inverse ACEScct log curve
    ap1_image = cp.where(
        image <= 0.155251141552511,
        (image - 0.0729055341958355) / 10.5402377416545,
        cp.where(
            image < cp.log2(65504),
            2 ** ((image * 17.52) - 9.72),
            65504,
        ),
    )

    # AP1 → AP0
    ap0_image = cp.dot(ap1_image, ap1_to_ap0_matrix.T)

    # Convert back to original type
    if was_numpy:
        return cp.asnumpy(ap0_image)
    return ap0_image


def aces2065_1_to_acescg(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert ACES2065-1 (AP0) to ACEScg (AP1 linear).

    ACEScg is the linear working space for CG/VFX using AP1 primaries.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        ACES2065-1 image (AP0, linear)

    Returns
    -------
    cp.ndarray | np.ndarray
        ACEScg image (AP1, linear)
    """
    image = to_float32(image, clip=False)

    # Remember input type
    was_numpy = isinstance(image, np.ndarray)

    # Convert to CuPy for processing
    if was_numpy:
        image = to_cupy(image)

    ap1_image = cp.dot(image, ap0_to_ap1_matrix.T)

    # Convert back to original type
    if was_numpy:
        return cp.asnumpy(ap1_image)
    return ap1_image


def acescg_to_aces2065_1(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Convert ACEScg (AP1 linear) to ACES2065-1 (AP0).

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        ACEScg image (AP1, linear)

    Returns
    -------
    cp.ndarray | np.ndarray
        ACES2065-1 image (AP0, linear)
    """
    image = to_float32(image, clip=False)

    # Remember input type
    was_numpy = isinstance(image, np.ndarray)

    # Convert to CuPy for processing
    if was_numpy:
        image = to_cupy(image)

    ap0_image = cp.dot(image, ap1_to_ap0_matrix.T)

    # Convert back to original type
    if was_numpy:
        return cp.asnumpy(ap0_image)
    return ap0_image
