"""
ACES Color Management

Provides ACES 1.2 color transformations following Nuke/VFX industry standards.

This package implements the Academy Color Encoding System (ACES), a color management
framework developed by the Academy of Motion Picture Arts and Sciences. The implementation
follows the ACES 1.2 standard and is compatible with industry-standard VFX applications
like Nuke, Houdini, and Maya.

Main Modules
------------
transform : High-level IDT/ODT functions
    rec709_to_aces2065_1 : Rec.709 → ACES2065-1 (Default IDT)
    aces2065_1_to_rec709 : ACES2065-1 → Rec.709 (Default ODT)

encoding : ACES color space conversions
    aces2065_1_to_acescct : ACES2065-1 → ACEScct (log-encoded AP1)
    acescct_to_aces2065_1 : ACEScct → ACES2065-1
    aces2065_1_to_acescg : ACES2065-1 → ACEScg (linear AP1)
    acescg_to_aces2065_1 : ACEScg → ACES2065-1

matrix : Low-level matrix transformations
eotf : Transfer functions (gamma encoding/decoding)

Workflow
--------
The default workflow follows the "Utility - sRGB - Texture" IDT approach:

1. Input: Display-referred content (textures, graphics, graded footage)
2. IDT: rec709_to_aces2065_1() - Gamma decode + matrix transform
3. Working space: ACES2065-1 (AP0, linear) or ACEScg (AP1, linear)
4. ODT: aces2065_1_to_rec709() - Matrix transform + gamma encode
5. Output: Display-ready Rec.709 content

White Level
-----------
This implementation maintains normalized white levels (≈1.0) for display-referred
content, which is the standard for CG/VFX workflows. This differs from some video
workflows that use elevated white levels (≈16.3) for scene-referred content.

References
----------
- ACES Project: https://acescentral.com
- ACES Technical Documentation: https://docs.acescentral.com
- OpenColorIO ACES Configs: https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES
- SMPTE ST 2065-1: ACES2065-1 specification
"""

from .encoding import (
    aces2065_1_to_acescct,
    aces2065_1_to_acescg,
    acescct_to_aces2065_1,
    acescg_to_aces2065_1,
)
from .transform import aces2065_1_to_rec709, rec709_to_aces2065_1

__all__ = [
    # Main IDT/ODT
    "rec709_to_aces2065_1",
    "aces2065_1_to_rec709",
    # Color space conversions
    "aces2065_1_to_acescct",
    "acescct_to_aces2065_1",
    "aces2065_1_to_acescg",
    "acescg_to_aces2065_1",
]
