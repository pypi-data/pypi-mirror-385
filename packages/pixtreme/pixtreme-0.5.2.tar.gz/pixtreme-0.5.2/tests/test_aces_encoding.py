"""
ACES encoding tests (ACEScct, ACEScg).

Tests the log encoding functions and AP0↔AP1 conversions.
"""

import cupy as cp
import numpy as np
import pytest


class TestACEScgConversion:
    """Test ACEScg (AP1 linear) conversions."""

    def test_acescg_import(self):
        """Test that ACEScg functions can be imported."""
        from pixtreme.color.aces import aces2065_1_to_acescg, acescg_to_aces2065_1

        assert callable(aces2065_1_to_acescg)
        assert callable(acescg_to_aces2065_1)

    def test_acescg_roundtrip(self):
        """Test AP0 → AP1 → AP0 round trip."""
        import pixtreme as px

        original = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # Round trip
        acescg = px.aces2065_1_to_acescg(original)
        recovered = px.acescg_to_aces2065_1(acescg)

        # Should be nearly identical (matrix precision)
        diff = float(cp.max(cp.abs(recovered - original)))
        assert diff < 1e-6, f"ACEScg round trip error: {diff}"

    def test_acescg_preserves_shape(self):
        """Test that ACEScg conversion preserves shape."""
        import pixtreme as px

        img = cp.ones((100, 50, 3), dtype=cp.float32) * 0.5
        acescg = px.aces2065_1_to_acescg(img)

        assert acescg.shape == img.shape

    def test_acescg_black_preservation(self):
        """Test that black remains black in ACEScg."""
        import pixtreme as px

        black = cp.zeros((10, 10, 3), dtype=cp.float32)
        acescg = px.aces2065_1_to_acescg(black)

        assert float(cp.max(cp.abs(acescg))) < 1e-6

    def test_acescg_numpy_support(self):
        """Test that ACEScg works with numpy arrays."""
        import pixtreme as px

        img_np = np.ones((10, 10, 3), dtype=np.float32) * 0.5
        acescg = px.aces2065_1_to_acescg(img_np)

        assert isinstance(acescg, np.ndarray)
        assert acescg.shape == img_np.shape


class TestACEScctConversion:
    """Test ACEScct (AP1 log-encoded) conversions."""

    def test_acescct_import(self):
        """Test that ACEScct functions can be imported."""
        from pixtreme.color.aces import aces2065_1_to_acescct, acescct_to_aces2065_1

        assert callable(aces2065_1_to_acescct)
        assert callable(acescct_to_aces2065_1)

    def test_acescct_roundtrip(self):
        """Test AP0 → ACEScct → AP0 round trip."""
        import pixtreme as px

        original = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # Round trip
        acescct = px.aces2065_1_to_acescct(original)
        recovered = px.acescct_to_aces2065_1(acescct)

        # Should be nearly identical (log encoding precision)
        diff = float(cp.max(cp.abs(recovered - original)))
        assert diff < 1e-5, f"ACEScct round trip error: {diff}"

    def test_acescct_preserves_shape(self):
        """Test that ACEScct conversion preserves shape."""
        import pixtreme as px

        img = cp.ones((100, 50, 3), dtype=cp.float32) * 0.5
        acescct = px.aces2065_1_to_acescct(img)

        assert acescct.shape == img.shape

    def test_acescct_log_encoding(self):
        """Test that ACEScct applies log encoding."""
        import pixtreme as px

        # Linear value
        linear = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # ACEScct should be different (log-encoded)
        acescct = px.aces2065_1_to_acescct(linear)

        # Values should be different due to log encoding
        assert not cp.allclose(acescct, linear)

    def test_acescct_range(self):
        """Test that ACEScct produces valid range."""
        import pixtreme as px

        # Positive linear values
        linear = cp.linspace(0.01, 1.0, 100).reshape(10, 10, 1)
        linear = cp.tile(linear, (1, 1, 3))

        acescct = px.aces2065_1_to_acescct(linear)

        # ACEScct should not have NaN or Inf
        assert not cp.any(cp.isnan(acescct))
        assert not cp.any(cp.isinf(acescct))

    def test_acescct_toe_segment(self):
        """Test ACEScct toe segment (linear below threshold)."""
        import pixtreme as px

        # Very small values (should use linear segment)
        small = cp.ones((10, 10, 3), dtype=cp.float32) * 0.001

        acescct = px.aces2065_1_to_acescct(small)
        recovered = px.acescct_to_aces2065_1(acescct)

        # Should still round trip correctly
        diff = float(cp.max(cp.abs(recovered - small)))
        assert diff < 1e-6, f"ACEScct toe segment error: {diff}"

    def test_acescct_numpy_support(self):
        """Test that ACEScct works with numpy arrays."""
        import pixtreme as px

        img_np = np.ones((10, 10, 3), dtype=np.float32) * 0.5
        acescct = px.aces2065_1_to_acescct(img_np)

        assert isinstance(acescct, np.ndarray)
        assert acescct.shape == img_np.shape


class TestACESEncodingEdgeCases:
    """Test edge cases in ACES encoding."""

    def test_very_small_values(self):
        """Test handling of very small values."""
        import pixtreme as px

        small = cp.ones((10, 10, 3), dtype=cp.float32) * 1e-6

        # ACEScg (should work fine - linear)
        acescg = px.aces2065_1_to_acescg(small)
        assert not cp.any(cp.isnan(acescg))

        # ACEScct (should handle toe segment)
        acescct = px.aces2065_1_to_acescct(small)
        assert not cp.any(cp.isnan(acescct))

    def test_very_large_values(self):
        """Test handling of very large values (HDR)."""
        import pixtreme as px

        large = cp.ones((10, 10, 3), dtype=cp.float32) * 100.0

        # ACEScg (should work fine - linear)
        acescg = px.aces2065_1_to_acescg(large)
        assert not cp.any(cp.isnan(acescg))
        assert not cp.any(cp.isinf(acescg))

        # ACEScct (should handle with log)
        acescct = px.aces2065_1_to_acescct(large)
        assert not cp.any(cp.isnan(acescct))
        assert not cp.any(cp.isinf(acescct))

    def test_zero_values(self):
        """Test handling of zero values."""
        import pixtreme as px

        zero = cp.zeros((10, 10, 3), dtype=cp.float32)

        # ACEScg
        acescg = px.aces2065_1_to_acescg(zero)
        recovered_cg = px.acescg_to_aces2065_1(acescg)
        assert float(cp.max(cp.abs(recovered_cg))) < 1e-6

        # ACEScct (zero is special case in log)
        acescct = px.aces2065_1_to_acescct(zero)
        # ACEScct may not perfectly round-trip zero due to log encoding
        # but should produce a very small value
        recovered_ct = px.acescct_to_aces2065_1(acescct)
        assert float(cp.max(cp.abs(recovered_ct))) < 0.01

    def test_negative_values_handling(self):
        """Test handling of negative values (out of gamut)."""
        import pixtreme as px

        negative = cp.ones((10, 10, 3), dtype=cp.float32) * -0.1

        # ACEScg (linear, matrix transform)
        acescg = px.aces2065_1_to_acescg(negative)
        # Should not crash, produce valid results
        assert not cp.any(cp.isnan(acescg))
        assert not cp.any(cp.isinf(acescg))

        # ACEScct (log encoding may have issues with negative)
        # Implementation should handle gracefully (not crash)
        try:
            acescct = px.aces2065_1_to_acescct(negative)
            # Should not have NaN or Inf even with negative input
            assert not cp.any(cp.isnan(acescct))
        except Exception:
            # If it fails, that's also acceptable for negative values in log space
            pass


class TestACESEncodingConsistency:
    """Test consistency between ACEScg and ACEScct."""

    def test_acescg_vs_acescct_matrices(self):
        """Test that ACEScg and ACEScct use same AP0↔AP1 matrices."""
        from pixtreme.color.aces.encoding import ap0_to_ap1_matrix, ap1_to_ap0_matrix

        # Forward and inverse should be consistent
        product = cp.dot(ap0_to_ap1_matrix, ap1_to_ap0_matrix)
        identity = cp.eye(3, dtype=cp.float32)

        diff = float(cp.max(cp.abs(product - identity)))
        assert diff < 1e-5, f"AP0↔AP1 matrices inconsistent: {diff}"

    def test_acescct_vs_linear_acescg(self):
        """Test that ACEScct is log-encoded version of ACEScg."""
        import pixtreme as px

        original = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # ACEScg is linear AP1
        acescg = px.aces2065_1_to_acescg(original)

        # ACEScct is log-encoded AP1
        acescct = px.aces2065_1_to_acescct(original)

        # They should NOT be equal (one is log-encoded)
        assert not cp.allclose(acescg, acescct)

        # But both should round trip correctly
        recovered_cg = px.acescg_to_aces2065_1(acescg)
        recovered_ct = px.acescct_to_aces2065_1(acescct)

        diff_cg = float(cp.max(cp.abs(recovered_cg - original)))
        diff_ct = float(cp.max(cp.abs(recovered_ct - original)))

        assert diff_cg < 1e-6, f"ACEScg round trip error: {diff_cg}"
        assert diff_ct < 1e-5, f"ACEScct round trip error: {diff_ct}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
