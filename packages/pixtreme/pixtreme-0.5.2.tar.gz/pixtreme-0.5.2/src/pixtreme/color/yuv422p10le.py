import cupy as cp


def yuv422p10le_to_ycbcr444(ycbcr422_data: cp.ndarray, width: int, height: int) -> cp.ndarray:
    """
    Convert YCbCr 4:2:2 to YCbCr 4:4:4

    Parameters
    ----------
    ycbcr422_data : cp.ndarray
        Input frame. Shape 1D array in YUV 4:2:2 10bit format. (uint8)
    width : int
        Width of the frame.
    height : int
        Height of the frame.

    Returns
    -------
    frame_ycbcr444 : cp.ndarray
        Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
    """
    frame_ycbcr444 = cp.empty((height, width, 3), dtype=cp.float32)

    block = (32, 32)
    grid = ((width + block[0] - 1) // block[0], (height + block[1] - 1) // block[1])

    yuv422p10le_to_ycbcr444_kernel(grid, block, (ycbcr422_data, frame_ycbcr444, width, height))

    return frame_ycbcr444


yuv422p10le_to_ycbcr444_kernel_code = """
extern "C" __global__
void yuv422p10le_to_ycbcr444_kernel(const unsigned short* src, float* dst, int width, int height) {
    const int x = blockIdx.x * blockDim.x + threadIdx.x;
    const int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x >= width || y >= height) return;

    const int frame_size = width * height;
    const int uv_width = width / 2;
    const int y_index = y * width + x;

    const int u_index = frame_size + y * uv_width + x / 2;
    const int v_index = u_index + frame_size / 2;

    float y_component = ((float)(src[y_index] & 0x03FF)) / 1023.0f;

    float u_component = ((float)(src[u_index] & 0x03FF)) / 1023.0f;
    if (x % 2 == 1 && x < width - 1) {
        float u_next = ((float)(src[u_index + 1] & 0x03FF)) / 1023.0f;
        u_component = (u_component + u_next) / 2.0f;
    }

    float v_component = ((float)(src[v_index] & 0x03FF)) / 1023.0f;
    if (x % 2 == 1 && x < width - 1) {
        float v_next = ((float)(src[v_index + 1] & 0x03FF)) / 1023.0f;
        v_component = (v_component + v_next) / 2.0f;
    }

    const int dst_index = (y * width + x) * 3;
    dst[dst_index] = y_component;
    dst[dst_index + 1] = u_component;
    dst[dst_index + 2] = v_component;
}


"""
yuv422p10le_to_ycbcr444_kernel = cp.RawKernel(code=yuv422p10le_to_ycbcr444_kernel_code, name="yuv422p10le_to_ycbcr444_kernel")
