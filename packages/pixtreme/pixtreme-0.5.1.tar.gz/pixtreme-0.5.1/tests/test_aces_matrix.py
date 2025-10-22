"""
ACES matrix transformation tests.

Tests the low-level matrix transformations and verifies OCIO ACES 1.2 standard compliance.
"""

import cupy as cp
import numpy as np
import pytest


class TestACESMatrixTransforms:
    """Test ACES matrix transformations."""

    def test_matrix_import(self):
        """Test that matrix module can be imported."""
        from pixtreme.color.aces import matrix

        assert hasattr(matrix, 'rec709_to_aces2065_1')
        assert hasattr(matrix, 'aces2065_1_to_rec709')
        assert hasattr(matrix, 'apply_matrix_rgb')

    def test_matrix_constants(self):
        """Test that matrix constants are defined."""
        from pixtreme.color.aces import matrix

        # Check that matrices exist and have correct shape
        assert hasattr(matrix, '_MATRIX_REC709_TO_ACES2065_1')
        assert hasattr(matrix, '_MATRIX_ACES2065_1_TO_REC709')

        # Verify shape (3x3)
        assert matrix._MATRIX_REC709_TO_ACES2065_1.shape == (3, 3)
        assert matrix._MATRIX_ACES2065_1_TO_REC709.shape == (3, 3)

    def test_matrix_ocio_values(self):
        """Test that matrix values match OCIO ACES 1.2 standard."""
        from pixtreme.color.aces import matrix

        # OCIO ACES 1.2 reference values (from OpenColorIO-Config-ACES)
        expected_rec709_to_aces = np.array([
            [0.4396466315, 0.3829816580, 0.1773722917],
            [0.0897805765, 0.8134407997, 0.0967797637],
            [0.0175445601, 0.1115567982, 0.8708978295],
        ], dtype=np.float32)

        # Check values (with small tolerance for floating point)
        diff = np.abs(matrix._MATRIX_REC709_TO_ACES2065_1 - expected_rec709_to_aces)
        assert np.max(diff) < 1e-6, f"Matrix values don't match OCIO standard, max diff: {np.max(diff)}"

    def test_linear_to_linear_transform(self):
        """Test that matrix transforms work on linear values."""
        from pixtreme.color.aces import matrix

        # Linear mid-gray
        linear = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # Transform
        aces = matrix.rec709_to_aces2065_1(linear)

        # Should not be NaN or Inf
        assert not cp.any(cp.isnan(aces))
        assert not cp.any(cp.isinf(aces))

    def test_matrix_roundtrip(self):
        """Test matrix round trip (linear → linear)."""
        from pixtreme.color.aces import matrix

        original = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        # Round trip
        aces = matrix.rec709_to_aces2065_1(original)
        recovered = matrix.aces2065_1_to_rec709(aces)

        # Should be nearly identical
        diff = float(cp.max(cp.abs(recovered - original)))
        assert diff < 2e-4, f"Matrix round trip error: {diff}"

    def test_apply_matrix_rgb_identity(self):
        """Test apply_matrix_rgb with identity matrix."""
        from pixtreme.color.aces import matrix

        identity = np.eye(3, dtype=np.float32)
        img = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        result = matrix.apply_matrix_rgb(img, identity)

        # Should be identical to input
        diff = float(cp.max(cp.abs(result - img)))
        assert diff < 1e-7, f"Identity matrix should preserve values, diff: {diff}"

    def test_numpy_matrix_input(self):
        """Test that numpy arrays work with matrix functions."""
        from pixtreme.color.aces import matrix

        img_np = np.ones((10, 10, 3), dtype=np.float32) * 0.5
        aces = matrix.rec709_to_aces2065_1(img_np)

        assert isinstance(aces, np.ndarray)
        assert aces.shape == img_np.shape


class TestACESColorSpaceProperties:
    """Test ACES color space properties."""

    def test_ap0_to_ap1_matrix(self):
        """Test AP0 to AP1 transformation matrix."""
        from pixtreme.color.aces.encoding import ap0_to_ap1_matrix, ap1_to_ap0_matrix

        # Matrices should be inverse of each other
        product = cp.dot(ap0_to_ap1_matrix, ap1_to_ap0_matrix)
        identity = cp.eye(3, dtype=cp.float32)

        diff = float(cp.max(cp.abs(product - identity)))
        assert diff < 1e-5, f"AP0↔AP1 matrices should be inverses, diff: {diff}"

    def test_xyz_transforms_available(self):
        """Test that XYZ transform functions are available."""
        from pixtreme.color.aces import matrix

        assert hasattr(matrix, 'rec709_to_xyz_d65')
        assert hasattr(matrix, 'xyz_d65_to_rec709')
        assert hasattr(matrix, 'xyz_d65_to_d60')
        assert hasattr(matrix, 'xyz_d60_to_d65')

    def test_chromatic_adaptation(self):
        """Test Bradford chromatic adaptation matrices."""
        from pixtreme.color.aces import matrix

        # D65 → D60 → D65 should be identity
        img = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5

        converted = matrix.xyz_d65_to_d60(img)
        recovered = matrix.xyz_d60_to_d65(converted)

        diff = float(cp.max(cp.abs(recovered - img)))
        assert diff < 1e-5, f"Chromatic adaptation round trip error: {diff}"


class TestACESMatrixPerformance:
    """Test matrix transformation performance characteristics."""

    def test_matrix_transform_large_image(self):
        """Test that matrix transforms work on large images."""
        from pixtreme.color.aces import matrix

        # Large image
        img = cp.ones((2000, 2000, 3), dtype=cp.float32) * 0.5

        # Should complete without error
        aces = matrix.rec709_to_aces2065_1(img)

        assert aces.shape == img.shape

    def test_matrix_preserves_dtype(self):
        """Test that matrix transforms preserve data type."""
        from pixtreme.color.aces import matrix

        # Test with float32
        img32 = cp.ones((10, 10, 3), dtype=cp.float32) * 0.5
        result32 = matrix.rec709_to_aces2065_1(img32)
        assert result32.dtype == cp.float32

        # Test with float64
        img64 = cp.ones((10, 10, 3), dtype=cp.float64) * 0.5
        result64 = matrix.rec709_to_aces2065_1(img64)
        assert result64.dtype == cp.float64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
