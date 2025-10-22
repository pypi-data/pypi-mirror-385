import cupy as cp


def uyvy422_to_ycbcr444(uyvy_data: cp.ndarray, height: int, width: int) -> cp.ndarray:
    """
    Convert UYVY422 to YCbCr444.

    Parameters
    ----------
    uyvy_data : cp.ndarray
        The input UYVY422 data. The 1d array of the shape (height * width * 2).
    height : int
        The height of the input image.
    width : int
        The width of the input image.

    Returns
    -------
    yuv444p : cp.ndarray
        The output YCbCr444 data. The 3d array of the shape (height, width, 3).
    """

    total_pixels = height * width

    # Initialize the output array in YUV444P format
    yuv444_flat = cp.empty(total_pixels * 3, dtype=cp.uint8)

    # CUDA kernel launch parameters
    block_size = 256
    grid_size = (total_pixels + block_size - 1) // block_size

    # Launch the kernel
    uyvy422_to_ycbcr444_kernel(
        (grid_size,),
        (block_size,),
        (uyvy_data, yuv444_flat, height, width),
    )

    # Reshape the flat array to 3D array (height, width, 3)
    yuv_444p = yuv444_flat.reshape((height, width, 3))
    return yuv_444p


uyvy422_to_ycbcr444_kernel_code = """
extern "C" __global__
void uyvy422_to_ycbcr444_kernel(
    const unsigned char* uyvy_data,
    unsigned char* yuv444_data,
    int height,
    int width
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int total_pixels = height * width;

    if (idx >= total_pixels) return;

    int row = idx / width;
    int col = idx % width;

    // Position of the pixel in the UYVY422 format
    int pair_col = col / 2;
    int is_odd = col % 2;

    // Index in the UYVY422 data
    int uyvy_base_idx = row * width * 2 + pair_col * 4;

    // Extract Y value (even pixel: Y0, odd pixel: Y1)
    unsigned char y_val = uyvy_data[uyvy_base_idx + 1 + is_odd * 2];

    // Extract U and V values (shared between pixel pairs)
    unsigned char u_val = uyvy_data[uyvy_base_idx];
    unsigned char v_val = uyvy_data[uyvy_base_idx + 2];

    // YUV444 output index
    int yuv444_base_idx = idx * 3;

    // Write to YUV444 data
    yuv444_data[yuv444_base_idx] = y_val;
    yuv444_data[yuv444_base_idx + 1] = u_val;
    yuv444_data[yuv444_base_idx + 2] = v_val;
}
"""
uyvy422_to_ycbcr444_kernel = cp.RawKernel(code=uyvy422_to_ycbcr444_kernel_code, name="uyvy422_to_ycbcr444_kernel")
