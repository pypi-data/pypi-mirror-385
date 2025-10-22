import cupy as cp


def yuv420p_to_ycbcr444(yuv420_data: cp.ndarray, width: int, height: int, interpolation: int = 1) -> cp.ndarray:
    """
    Convert YUV 4:2:0 to YCbCr 4:4:4

    Parameters
    ----------
    yuv420_data : cp.ndarray
        Input frame. Shape 1D array (uint8).
    width : int
        Width of the frame.
    height : int
        Height of the frame.

    Returns
    -------
    image_ycbcr444 : cp.ndarray
        Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
    """
    yuv420_data = yuv420_data.astype(cp.float32) / 255.0
    image_ycbcr444 = cp.empty((height, width, 3), dtype=cp.float32)

    block = (32, 32)
    grid = ((width + block[0] - 1) // block[0], (height + block[1] - 1) // block[1])

    if interpolation == 0:
        yuv420p_to_ycbcr444_nearest_kernel(grid, block, (yuv420_data, image_ycbcr444, width, height))
    elif interpolation == 1:
        yuv420p_to_ycbcr444_bilinear_kernel(grid, block, (yuv420_data, image_ycbcr444, width, height))

    return image_ycbcr444


yuv420p_to_ycbcr444_bilinear_kernel_code = """
extern "C" __global__
void yuv420p_to_ycbcr444_bilinear_kernel(const float* src, float* dst, int width, int height) {
    const int x = blockIdx.x * blockDim.x + threadIdx.x;
    const int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x >= width || y >= height) return;

    const int image_size = width * height;
    const float fx = x / 2.0f;
    const float fy = y / 2.0f;
    const int src_x = int(fx);
    const int src_y = int(fy);
    const float dx = fx - src_x;
    const float dy = fy - src_y;
    const int image_size_quarter = image_size / 4;
    const int width_half = width / 2;

    const int uv_index = image_size + src_y * (width_half) + src_x;
    const int next_x_index = min(src_x + 1, width_half - 1);
    const int next_y_index = min(src_y + 1, height / 2 - 1);
    const int uv_index_next_x = image_size + src_y * (width_half) + next_x_index;
    const int uv_index_next_y = image_size + next_y_index * (width_half) + src_x;
    const int uv_index_next_xy = image_size + next_y_index * (width_half) + next_x_index;

    float u_component = (1 - dx) * (1 - dy) * src[uv_index] +
              dx * (1 - dy) * src[uv_index_next_x] +
              (1 - dx) * dy * src[uv_index_next_y] +
              dx * dy * src[uv_index_next_xy];

    float v_component = (1 - dx) * (1 - dy) * src[uv_index + image_size_quarter] +
              dx * (1 - dy) * src[uv_index_next_x + image_size_quarter] +
              (1 - dx) * dy * src[uv_index_next_y + image_size_quarter] +
              dx * dy * src[uv_index_next_xy + image_size_quarter];

    float y_component = src[y * width + x];

    const int dst_index = (y * width + x) * 3;
    dst[dst_index] = y_component;
    dst[dst_index + 1] = u_component;
    dst[dst_index + 2] = v_component;
}
"""
yuv420p_to_ycbcr444_bilinear_kernel = cp.RawKernel(
    code=yuv420p_to_ycbcr444_bilinear_kernel_code, name="yuv420p_to_ycbcr444_bilinear_kernel"
)


yuv420p_to_ycbcr444_nearest_kernel_code = """
extern "C" __global__
void yuv420p_to_ycbcr444_nearest_kernel(const float* src, float* dst, int width, int height) {
    const int x = blockIdx.x * blockDim.x + threadIdx.x;
    const int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x >= width || y >= height) return;

    const int image_size = width * height;
    const int src_x = x / 2;
    const int src_y = y / 2;

    const int uv_index = image_size + src_y * (width / 2) + src_x;

    float u_component = src[uv_index];
    float v_component = src[uv_index + image_size / 4];

    float y_component = src[y * width + x];

    y_component = max(0.0f, min(1.0f, (y_component - 64.0f / 1023.0f) * (1023.0f / (940.0f - 64.0f))));


    const int dst_index = (y * width + x) * 3;
    dst[dst_index] = y_component;
    dst[dst_index + 1] = u_component;
    dst[dst_index + 2] = v_component;
}
"""
yuv420p_to_ycbcr444_nearest_kernel = cp.RawKernel(
    code=yuv420p_to_ycbcr444_nearest_kernel_code, name="yuv420p_to_ycbcr444_nearest_kernel"
)
