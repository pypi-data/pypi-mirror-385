from io import BytesIO

import cupy as cp
import cv2
import numpy as np
import pytest

import pixtreme_source as px


class TestImencodeImdecode:
    """Test suite for imencode and imdecode functions"""

    @pytest.fixture
    def test_image_uint8(self):
        """Create a test image in uint8 format"""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        # Create a gradient pattern for better testing
        for i in range(100):
            for j in range(100):
                image[i, j] = [i * 2.55, j * 2.55, (i + j) * 1.275]
        return cp.asarray(image)

    @pytest.fixture
    def test_image_uint16(self):
        """Create a test image in uint16 format"""
        image = np.zeros((100, 100, 3), dtype=np.uint16)
        for i in range(100):
            for j in range(100):
                image[i, j] = [i * 655.35, j * 655.35, (i + j) * 327.675]
        return cp.asarray(image)

    @pytest.fixture
    def test_image_float32(self):
        """Create a test image in float32 format"""
        image = np.zeros((100, 100, 3), dtype=np.float32)
        for i in range(100):
            for j in range(100):
                image[i, j] = [i / 100.0, j / 100.0, (i + j) / 200.0]
        return cp.asarray(image)

    def test_png_roundtrip_uint8(self, test_image_uint8):
        """Test PNG encoding/decoding with uint8 image"""
        # Encode
        encoded = px.imencode(test_image_uint8, format="png")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

        # Decode
        decoded = px.imdecode(encoded)
        assert isinstance(decoded, cp.ndarray)
        assert decoded.shape == test_image_uint8.shape
        assert decoded.dtype == test_image_uint8.dtype

        # Check if images are identical (PNG is lossless)
        np.testing.assert_array_equal(cp.asnumpy(decoded), cp.asnumpy(test_image_uint8))

    def test_png_roundtrip_uint16(self, test_image_uint16):
        """Test PNG encoding/decoding with uint16 image"""
        # Encode
        encoded = px.imencode(test_image_uint16, format="png")
        assert isinstance(encoded, bytes)

        # Decode
        decoded = px.imdecode(encoded)
        assert isinstance(decoded, cp.ndarray)
        assert decoded.shape == test_image_uint16.shape
        assert decoded.dtype == test_image_uint16.dtype

        # Check if images are identical (PNG is lossless)
        np.testing.assert_array_equal(cp.asnumpy(decoded), cp.asnumpy(test_image_uint16))

    def test_png_roundtrip_float32(self, test_image_float32):
        """Test PNG encoding/decoding with float32 image"""
        # Encode (float32 will be converted to uint16)
        encoded = px.imencode(test_image_float32, format="png")
        assert isinstance(encoded, bytes)

        # Decode
        decoded = px.imdecode(encoded)
        assert isinstance(decoded, cp.ndarray)
        assert decoded.shape == test_image_float32.shape
        # Should be decoded as uint16
        assert decoded.dtype == np.uint16

        # Convert back to float32 for comparison
        decoded_float32 = px.to_float32(decoded)
        # Allow small tolerance due to conversion
        np.testing.assert_allclose(cp.asnumpy(decoded_float32), cp.asnumpy(test_image_float32), rtol=1e-4, atol=1e-4)

    def test_jpeg_roundtrip(self, test_image_uint8):
        """Test JPEG encoding/decoding"""
        # Test with different quality levels
        for quality in [50, 80, 100]:
            encoded = px.imencode(test_image_uint8, format="jpeg", param=quality)
            assert isinstance(encoded, bytes)
            assert len(encoded) > 0

            decoded = px.imdecode(encoded)
            assert isinstance(decoded, cp.ndarray)
            assert decoded.shape == test_image_uint8.shape
            assert decoded.dtype == test_image_uint8.dtype

            # JPEG is lossy, so we can't expect exact match
            # Just check that the difference is reasonable
            diff = np.abs(cp.asnumpy(decoded).astype(np.float32) - cp.asnumpy(test_image_uint8).astype(np.float32))
            assert np.mean(diff) < 10  # Average difference should be small

    def test_tiff_roundtrip(self, test_image_uint8):
        """Test TIFF encoding/decoding"""
        encoded = px.imencode(test_image_uint8, format="tiff")
        assert isinstance(encoded, bytes)

        decoded = px.imdecode(encoded)
        assert isinstance(decoded, cp.ndarray)
        assert decoded.shape == test_image_uint8.shape
        assert decoded.dtype == test_image_uint8.dtype

        # TIFF with default compression should be lossless
        np.testing.assert_array_equal(cp.asnumpy(decoded), cp.asnumpy(test_image_uint8))

    def test_swap_rb_encode(self, test_image_uint8):
        """Test swap_rb parameter in encoding"""
        # Create an image with distinct R and B channels
        test_rgb = cp.zeros((50, 50, 3), dtype=cp.uint8)
        test_rgb[:, :, 0] = 255  # Red channel
        test_rgb[:, :, 1] = 128  # Green channel
        test_rgb[:, :, 2] = 0  # Blue channel

        # Encode without swap
        encoded_normal = px.imencode(test_rgb, format="png", swap_rb=False)
        decoded_normal = px.imdecode(encoded_normal)

        # Encode with swap
        encoded_swapped = px.imencode(test_rgb, format="png", swap_rb=True)
        decoded_swapped = px.imdecode(encoded_swapped)

        # Check that channels are swapped
        np.testing.assert_array_equal(cp.asnumpy(decoded_normal)[:, :, 0], cp.asnumpy(decoded_swapped)[:, :, 2])
        np.testing.assert_array_equal(cp.asnumpy(decoded_normal)[:, :, 2], cp.asnumpy(decoded_swapped)[:, :, 0])

    def test_swap_rb_decode(self, test_image_uint8):
        """Test swap_rb parameter in decoding"""
        # Create an image with distinct R and B channels
        test_bgr = cp.zeros((50, 50, 3), dtype=cp.uint8)
        test_bgr[:, :, 0] = 255  # Blue channel (in BGR)
        test_bgr[:, :, 1] = 128  # Green channel
        test_bgr[:, :, 2] = 0  # Red channel (in BGR)

        # Encode
        encoded = px.imencode(test_bgr, format="png")

        # Decode without swap (BGR)
        decoded_bgr = px.imdecode(encoded, swap_rb=False)

        # Decode with swap (RGB)
        decoded_rgb = px.imdecode(encoded, swap_rb=True)

        # Check that channels are swapped
        np.testing.assert_array_equal(cp.asnumpy(decoded_bgr)[:, :, 0], cp.asnumpy(decoded_rgb)[:, :, 2])
        np.testing.assert_array_equal(cp.asnumpy(decoded_bgr)[:, :, 2], cp.asnumpy(decoded_rgb)[:, :, 0])

    def test_compression_parameters(self, test_image_uint8):
        """Test compression parameters for different formats"""
        # PNG compression levels (0-9)
        encoded_low = px.imencode(test_image_uint8, format="png", param=0)
        encoded_high = px.imencode(test_image_uint8, format="png", param=9)

        # Both should decode to the same image (lossless)
        decoded_low = px.imdecode(encoded_low)
        decoded_high = px.imdecode(encoded_high)
        np.testing.assert_array_equal(cp.asnumpy(decoded_low), cp.asnumpy(decoded_high))

        # JPEG quality levels
        encoded_q50 = px.imencode(test_image_uint8, format="jpeg", param=50)
        encoded_q100 = px.imencode(test_image_uint8, format="jpeg", param=100)

        # Higher quality should generally result in larger file size
        assert len(encoded_q100) > len(encoded_q50)

    def test_invalid_format(self, test_image_uint8):
        """Test error handling for invalid format"""
        with pytest.raises(ValueError, match="Unsupported image format"):
            px.imencode(test_image_uint8, format="invalid_format")

    def test_decode_invalid_data(self):
        """Test error handling for invalid data in decode"""
        invalid_data = b"This is not image data"
        with pytest.raises(RuntimeError, match="Failed to decode image"):
            px.imdecode(invalid_data)

    def test_different_dtypes(self):
        """Test encoding/decoding with different data types"""
        # Create test images with different dtypes
        dtypes = [(np.uint8, 255), (np.uint16, 65535), (np.float32, 1.0), (np.float16, 1.0)]

        for dtype, max_val in dtypes:
            # Create test image
            if dtype in [np.float32, np.float16]:
                image = cp.random.rand(50, 50, 3).astype(dtype)
            else:
                image = cp.random.randint(0, max_val, (50, 50, 3), dtype=dtype)

            # Test PNG encoding/decoding
            encoded = px.imencode(image, format="png")
            decoded = px.imdecode(encoded)

            # Check shape is preserved
            assert decoded.shape == image.shape

            # For float types, check they are converted to appropriate integer type
            if dtype in [np.float32, np.float16]:
                assert decoded.dtype in [np.uint8, np.uint16]

    def test_grayscale_image(self):
        """Test encoding/decoding of grayscale images"""
        # Create grayscale image
        gray_image = cp.random.randint(0, 255, (100, 100), dtype="uint8")

        # Encode/decode
        encoded = px.imencode(gray_image, format="png")
        decoded = px.imdecode(encoded)

        # Check that grayscale is preserved
        assert decoded.shape == gray_image.shape
        np.testing.assert_array_equal(cp.asnumpy(decoded), cp.asnumpy(gray_image))

    def test_alpha_channel(self):
        """Test encoding/decoding with alpha channel"""
        # Create RGBA image
        rgba_image = cp.random.randint(0, 255, (50, 50, 4), dtype="uint8")

        # PNG supports alpha channel
        encoded = px.imencode(rgba_image, format="png")
        decoded = px.imdecode(encoded)

        # Check that alpha channel is preserved
        assert decoded.shape == rgba_image.shape
        np.testing.assert_array_equal(cp.asnumpy(decoded), cp.asnumpy(rgba_image))

    @pytest.mark.parametrize(
        "format,ext",
        [
            ("png", "png"),
            ("PNG", "PNG"),
            ("jpeg", "jpeg"),
            ("jpg", "jpg"),
            ("JPEG", "JPEG"),
            ("tiff", "tiff"),
            ("tif", "tif"),
            ("TIFF", "TIFF"),
        ],
    )
    def test_format_case_insensitive(self, test_image_uint8, format, ext):
        """Test that format parameter is case-insensitive"""
        encoded = px.imencode(test_image_uint8, format=format)
        assert isinstance(encoded, bytes)

        decoded = px.imdecode(encoded)
        assert isinstance(decoded, cp.ndarray)
        assert decoded.shape == test_image_uint8.shape
