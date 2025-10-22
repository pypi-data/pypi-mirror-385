"""
Basic ACES functionality tests.

Tests the core ACES 1.2 implementation including IDT, ODT, and color space conversions.
"""

import cupy as cp
import numpy as np
import pytest

import pixtreme as px


class TestACESBasicFunctionality:
    """Test basic ACES transformations."""

    def test_rec709_to_aces2065_1_shape(self):
        """Test that IDT preserves image shape."""
        img = cp.ones((100, 100, 3), dtype=cp.float32) * 0.5
        aces = px.rec709_to_aces2065_1(img)

        assert aces.shape == img.shape
        assert isinstance(aces, cp.ndarray)
        assert aces.dtype == cp.float32

    def test_aces2065_1_to_rec709_shape(self):
        """Test that ODT preserves image shape."""
        aces = cp.ones((100, 100, 3), dtype=cp.float32) * 0.5
        rec709 = px.aces2065_1_to_rec709(aces)

        assert rec709.shape == aces.shape
        assert isinstance(rec709, cp.ndarray)
        assert rec709.dtype == cp.float32

    def test_aces2065_1_to_acescg_shape(self):
        """Test AP0 to AP1 conversion preserves shape."""
        aces = cp.ones((100, 100, 3), dtype=cp.float32) * 0.5
        acescg = px.aces2065_1_to_acescg(aces)

        assert acescg.shape == aces.shape
        assert isinstance(acescg, cp.ndarray)

    def test_aces2065_1_to_acescct_shape(self):
        """Test AP0 to ACEScct conversion preserves shape."""
        aces = cp.ones((100, 100, 3), dtype=cp.float32) * 0.5
        acescct = px.aces2065_1_to_acescct(aces)

        assert acescct.shape == aces.shape
        assert isinstance(acescct, cp.ndarray)

    def test_output_range(self):
        """Test that ODT output is in valid range [0-1]."""
        aces = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5
        rec709 = px.aces2065_1_to_rec709(aces)

        assert float(cp.min(rec709)) >= 0.0
        assert float(cp.max(rec709)) <= 1.0

    def test_numpy_input(self):
        """Test that numpy arrays are accepted."""
        img_np = np.ones((10, 10, 3), dtype=np.float32) * 0.5
        aces = px.rec709_to_aces2065_1(img_np)

        assert isinstance(aces, np.ndarray)
        assert aces.shape == img_np.shape


class TestACESRoundTrip:
    """Test round-trip conversions."""

    def test_rec709_roundtrip(self):
        """Test Rec.709 → ACES → Rec.709 round trip."""
        original = cp.array([[[0.5, 0.5, 0.5]]], dtype=cp.float32)

        # Round trip
        aces = px.rec709_to_aces2065_1(original)
        recovered = px.aces2065_1_to_rec709(aces)

        # Should be approximately equal (small numerical error acceptable)
        diff = float(cp.max(cp.abs(recovered - original)))
        assert diff < 0.01, f"Round trip error: {diff}"

    def test_acescg_roundtrip(self):
        """Test AP0 → AP1 → AP0 round trip."""
        original = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # Round trip
        acescg = px.aces2065_1_to_acescg(original)
        recovered = px.acescg_to_aces2065_1(acescg)

        # Should be nearly identical
        diff = float(cp.max(cp.abs(recovered - original)))
        assert diff < 1e-6, f"AP0↔AP1 round trip error: {diff}"

    def test_acescct_roundtrip(self):
        """Test AP0 → ACEScct → AP0 round trip."""
        original = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # Round trip
        acescct = px.aces2065_1_to_acescct(original)
        recovered = px.acescct_to_aces2065_1(acescct)

        # Should be nearly identical
        diff = float(cp.max(cp.abs(recovered - original)))
        assert diff < 1e-5, f"AP0↔ACEScct round trip error: {diff}"


class TestACESKnownValues:
    """Test against known values."""

    def test_black_value(self):
        """Test that black stays black."""
        black = cp.zeros((1, 1, 3), dtype=cp.float32)

        aces = px.rec709_to_aces2065_1(black)
        assert float(cp.max(cp.abs(aces))) < 1e-6

    def test_white_normalized(self):
        """Test that white (1.0) remains normalized in display-referred workflow."""
        white = cp.ones((1, 1, 3), dtype=cp.float32)

        aces = px.rec709_to_aces2065_1(white)

        # In display-referred workflow (Nuke/VFX standard), white should remain normalized
        # Not elevated to ~16.3 (that's for scene-referred video workflows)
        white_value = float(cp.max(aces))
        assert 0.9 < white_value < 1.5, f"White value should be normalized, got {white_value}"

    def test_mid_gray(self):
        """Test mid-gray value (0.5 in Rec.709)."""
        mid_gray = cp.ones((1, 1, 3), dtype=cp.float32) * 0.5

        aces = px.rec709_to_aces2065_1(mid_gray)
        recovered = px.aces2065_1_to_rec709(aces)

        # Should recover approximately to 0.5
        recovered_value = float(recovered[0, 0, 0])
        assert abs(recovered_value - 0.5) < 0.01, f"Expected ~0.5, got {recovered_value}"


class TestACESBackwardCompatibility:
    """Test backward compatibility with existing API."""

    def test_import_from_pixtreme(self):
        """Test that functions are accessible from pixtreme namespace."""
        assert hasattr(px, 'rec709_to_aces2065_1')
        assert hasattr(px, 'aces2065_1_to_rec709')
        assert hasattr(px, 'aces2065_1_to_acescct')
        assert hasattr(px, 'acescct_to_aces2065_1')
        assert hasattr(px, 'aces2065_1_to_acescg')
        assert hasattr(px, 'acescg_to_aces2065_1')

    def test_import_from_color(self):
        """Test that functions are accessible from pixtreme.color namespace."""
        from pixtreme.color import (
            rec709_to_aces2065_1,
            aces2065_1_to_rec709,
            aces2065_1_to_acescct,
            acescct_to_aces2065_1,
            aces2065_1_to_acescg,
            acescg_to_aces2065_1,
        )
        assert callable(rec709_to_aces2065_1)
        assert callable(aces2065_1_to_rec709)

    def test_import_from_aces_module(self):
        """Test that functions are accessible from pixtreme.color.aces namespace."""
        from pixtreme.color.aces import (
            rec709_to_aces2065_1,
            aces2065_1_to_rec709,
            aces2065_1_to_acescct,
            acescct_to_aces2065_1,
            aces2065_1_to_acescg,
            acescg_to_aces2065_1,
        )
        assert callable(rec709_to_aces2065_1)
        assert callable(aces2065_1_to_rec709)


class TestACESEdgeCases:
    """Test edge cases and error conditions."""

    def test_negative_values(self):
        """Test handling of negative values (out of gamut)."""
        # Negative values shouldn't crash
        img = cp.ones((10, 10, 3), dtype=cp.float32) * -0.1
        aces = px.rec709_to_aces2065_1(img)

        # Should produce valid output
        assert not cp.any(cp.isnan(aces))
        assert not cp.any(cp.isinf(aces))

    def test_high_values(self):
        """Test handling of values > 1.0."""
        # HDR values shouldn't crash
        img = cp.ones((10, 10, 3), dtype=cp.float32) * 2.0
        aces = px.rec709_to_aces2065_1(img)

        # Should produce valid output
        assert not cp.any(cp.isnan(aces))
        assert not cp.any(cp.isinf(aces))

    def test_empty_image(self):
        """Test handling of minimum size image."""
        img = cp.ones((1, 1, 3), dtype=cp.float32) * 0.5
        aces = px.rec709_to_aces2065_1(img)
        rec709 = px.aces2065_1_to_rec709(aces)

        assert aces.shape == (1, 1, 3)
        assert rec709.shape == (1, 1, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
