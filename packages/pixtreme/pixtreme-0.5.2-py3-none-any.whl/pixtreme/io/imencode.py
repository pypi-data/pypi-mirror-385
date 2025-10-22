import cupy as cp
import cv2
import numpy as np

from ..color.bgr import rgb_to_bgr
from ..utils.dtypes import to_uint8, to_uint16


def imencode(image: cp.ndarray, ext: str = ".png", param: int = -1, swap_rb: bool = False) -> bytes:
    """
    Encode an image to a bytes object from a CuPy array.

    Args:
        image (cp.ndarray): The input image as a CuPy array.
        format (str): The image format to encode. Default is "png".
        param (int): Optional parameter for image encoding.
        swap_rb (bool): If True, the image will be encoded with red and blue channels swapped. Default is False.
    Returns:
        bytes: The encoded image as bytes.
    """
    if swap_rb:
        image = rgb_to_bgr(image)
    image = cp.asnumpy(image)

    # Encode image to bytes

    if "jpg" in ext.lower() or "jpeg" in ext.lower():
        if param == -1:
            param = 100
        image = to_uint8(image)
        options = [cv2.IMWRITE_JPEG_QUALITY, param]
    elif "png" in ext.lower():
        if param == -1:
            param = 3
        if image.dtype != np.uint8:
            image = to_uint16(image)
        options = [cv2.IMWRITE_PNG_COMPRESSION, param]
    elif "tiff" in ext.lower() or "tif" in ext.lower():
        if param == -1:
            param = 5
        if image.dtype != np.uint8:
            image = to_uint16(image)
        options = [cv2.IMWRITE_TIFF_COMPRESSION, param]
    else:
        raise ValueError(f"Unsupported image format: {format}")

    success, encoded_image = cv2.imencode(f".{ext.lower()}", image, options)
    if not success:
        raise RuntimeError(f"Failed to encode image to {ext} format")
    return encoded_image.tobytes()
