"""
Electro-Optical Transfer Functions (EOTF) for ACES workflows.

EOTF: Electrical signal → Optical light (display decoding)
Inverse EOTF (= OETF): Optical light → Electrical signal (camera encoding)

This module provides transfer functions used in ACES color transformations,
particularly for Rec.709/sRGB input and output transforms.

References:
- ITU-R BT.709: Rec.709 OETF specification
- ITU-R BT.1886: Rec.709 reference display EOTF
- IEC 61966-2-1:1999: sRGB specification
"""

import cupy as cp
import numpy as np


def srgb_eotf(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    sRGB EOTF (Electro-Optical Transfer Function).
    Decodes sRGB gamma-encoded values to linear light.

    Reference: IEC 61966-2-1:1999
    Effective gamma: ≈ 2.2

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        sRGB gamma-encoded image [0-1]

    Returns
    -------
    cp.ndarray | np.ndarray
        Linear light image [0-1]
    """
    xp = cp.get_array_module(image)

    return xp.where(
        image <= 0.04045,
        image / 12.92,  # Linear segment
        xp.power((image + 0.055) / 1.055, 2.4)  # Power 2.4
    )


def srgb_inverse_eotf(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    sRGB Inverse EOTF (= sRGB OETF).
    Encodes linear light to sRGB gamma-encoded values.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        Linear light image [0-1]

    Returns
    -------
    cp.ndarray | np.ndarray
        sRGB gamma-encoded image [0-1]
    """
    xp = cp.get_array_module(image)

    return xp.where(
        image <= 0.0031308,
        image * 12.92,  # Linear segment
        1.055 * xp.power(image, 1/2.4) - 0.055  # Power 1/2.4
    )


def bt1886_eotf(image: cp.ndarray | np.ndarray, L_w: float = 100.0, L_b: float = 0.0) -> cp.ndarray | np.ndarray:
    """
    BT.1886 EOTF (Rec.709 reference display).
    Decodes BT.1886 gamma-encoded values to linear light.

    Reference: ITU-R BT.1886
    Gamma: 2.4 (with black level adjustment)

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        BT.1886 gamma-encoded image [0-1]
    L_w : float, optional
        White luminance in cd/m² (default: 100.0 nits)
    L_b : float, optional
        Black luminance in cd/m² (default: 0.0 for perfect black)

    Returns
    -------
    cp.ndarray | np.ndarray
        Linear light image [0-1]
    """
    xp = cp.get_array_module(image)

    # BT.1886 with black offset
    # L = a * max(V + b, 0)^γ
    # where γ = 2.4

    gamma = 2.4

    if L_b == 0.0:
        # Perfect black (simplified case)
        a = L_w
        b = 0.0
    else:
        # Black offset adjustment
        a = xp.power(xp.power(L_w, 1/gamma) - xp.power(L_b, 1/gamma), gamma)
        b = xp.power(L_b, 1/gamma) / (xp.power(L_w, 1/gamma) - xp.power(L_b, 1/gamma))

    # Apply BT.1886 curve
    result = a * xp.power(xp.maximum(image + b, 0), gamma)

    # Normalize to [0-1] range
    result = result / L_w

    return result


def bt1886_inverse_eotf(image: cp.ndarray | np.ndarray, L_w: float = 100.0, L_b: float = 0.0) -> cp.ndarray | np.ndarray:
    """
    BT.1886 Inverse EOTF (= BT.1886 OETF).
    Encodes linear light to BT.1886 gamma-encoded values.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        Linear light image [0-1]
    L_w : float, optional
        White luminance in cd/m² (default: 100.0 nits)
    L_b : float, optional
        Black luminance in cd/m² (default: 0.0 for perfect black)

    Returns
    -------
    cp.ndarray | np.ndarray
        BT.1886 gamma-encoded image [0-1]
    """
    xp = cp.get_array_module(image)

    gamma = 2.4

    # Denormalize from [0-1] to luminance
    L = image * L_w

    if L_b == 0.0:
        # Perfect black (simplified case)
        # V = (L / a)^(1/γ)
        a = L_w
        result = xp.power(L / a, 1/gamma)
    else:
        # Black offset adjustment
        a = xp.power(xp.power(L_w, 1/gamma) - xp.power(L_b, 1/gamma), gamma)
        b = xp.power(L_b, 1/gamma) / (xp.power(L_w, 1/gamma) - xp.power(L_b, 1/gamma))

        # V = (L / a)^(1/γ) - b
        result = xp.power(L / a, 1/gamma) - b

    return xp.clip(result, 0, 1)


def rec709_oetf(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Rec.709 OETF (Camera encoding).
    Encodes linear scene light to Rec.709 video signal.

    This is used in ACES ODT (Output Device Transform) to encode
    ACES linear values to Rec.709 display signal.

    Reference: ITU-R BT.709
    Note: This is the CAMERA side encoding, NOT display decoding.
    For display, use bt1886_eotf instead.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        Linear scene light [0-1]

    Returns
    -------
    cp.ndarray | np.ndarray
        Rec.709 encoded signal [0-1]
    """
    xp = cp.get_array_module(image)

    return xp.where(
        image < 0.018,
        4.5 * image,  # Linear segment
        1.099 * xp.power(image, 0.45) - 0.099  # Power ~1/2.2
    )


def rec709_inverse_oetf(image: cp.ndarray | np.ndarray) -> cp.ndarray | np.ndarray:
    """
    Rec.709 Inverse OETF.
    Decodes Rec.709 video signal to linear scene light.

    This is used in ACES IDT (Input Device Transform) to decode
    Rec.709 display signal to ACES linear values.

    Note: This is the inverse of camera encoding, NOT the display EOTF.
    For display, use bt1886_eotf instead.

    Parameters
    ----------
    image : cp.ndarray | np.ndarray
        Rec.709 encoded signal [0-1]

    Returns
    -------
    cp.ndarray | np.ndarray
        Linear scene light [0-1]
    """
    xp = cp.get_array_module(image)

    return xp.where(
        image < 0.081,
        image / 4.5,  # Linear segment
        xp.power((image + 0.099) / 1.099, 1/0.45)  # Power ~2.2
    )
