import cupy as cp
import cv2
import numpy as np

from ..color.bgr import bgr_to_rgb
from ..utils.dtypes import to_float16, to_float32, to_uint8, to_uint16


def imdecode(src: bytes, dtype: str = "fp32", swap_rb: bool = False) -> cp.ndarray:
    """
    Decode an image from a bytes object into a CuPy array.

    Args:
        src (bytes): The input image data as bytes.
        dtype (str): The desired data type for the output array. Default is "fp32".
        swap_rb (bool): If True, the image will be converted from BGR to RGB after decoding. Default is False (BGR).
    Returns:
        cp.ndarray: The image as a CuPy array.
    """
    # Decode the image from the bytes object
    image = cv2.imdecode(np.frombuffer(src, np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise RuntimeError("Failed to decode image from bytes")

    image = cp.asarray(image)
    if swap_rb:
        image = bgr_to_rgb(image)

    if dtype == "fp32":
        image = to_float32(image)
    elif dtype == "uint8":
        image = to_uint8(image)
    elif dtype == "uint16":
        image = to_uint16(image)
    elif dtype == "fp16":
        image = to_float16(image)
    else:
        image = to_float32(image)

    return image
