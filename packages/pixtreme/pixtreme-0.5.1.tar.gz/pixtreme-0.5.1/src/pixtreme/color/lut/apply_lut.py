import cupy as cp

from ...utils.dtypes import to_float32


def apply_lut(image: cp.ndarray, lut: cp.ndarray, interpolation: int = 0) -> cp.ndarray:
    """
    Apply a 3D LUT to an image with trilinear interpolation.

    Parameters:
    ----------
    image : cp.ndarray
        Input image. Shape 3D array (height, width, 3) in RGB format.
    lut : cp.ndarray
        3D LUT. Shape 3D array (N, N, N, 3) in RGB format.
    interpolation : int
        Interpolation method. 0 for trilinear, 1 for tetrahedral.

    Returns
    -------
    result : cp.ndarray
        Output image. Shape 3D array (height, width, 3) in RGB format.
    """
    image_rgb: cp.ndarray = to_float32(image)

    height, width, channels = image_rgb.shape
    N = lut.shape[0]
    result = cp.zeros_like(image_rgb)
    block_size = (32, 32)
    grid_size = ((width + block_size[0] - 1) // block_size[0], (height + block_size[1] - 1) // block_size[1])

    if interpolation == 0:
        # Flatten the LUT for trilinear interpolation
        lut_flat = lut.reshape(-1)
        lut_trilinear_kernel(grid_size, block_size, (image_rgb, lut_flat, result, height, width, N))
    elif interpolation == 1:
        lut_tetrahedral_kernel(grid_size, block_size, (image_rgb, result, lut, height, width, N, N * N))

    return result


lut_trilinear_kernel_code = """
extern "C" __global__
void lut_trilinear_kernel(const float* frame_rgb, const float* lut, float* result, int height, int width, int N) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int idy = blockIdx.y * blockDim.y + threadIdx.y;
    if (idx >= width || idy >= height) return;

    int frame_rgb_index = (idy * width + idx) * 3;
    float r = frame_rgb[frame_rgb_index] * (N - 1);
    float g = frame_rgb[frame_rgb_index + 1] * (N - 1);
    float b = frame_rgb[frame_rgb_index + 2] * (N - 1);

    int r_low = max(0, min(int(r), N - 2));
    int g_low = max(0, min(int(g), N - 2));
    int b_low = max(0, min(int(b), N - 2));
    int r_high = r_low + 1;
    int g_high = g_low + 1;
    int b_high = b_low + 1;

    float r_ratio = r - r_low;
    float g_ratio = g - g_low;
    float b_ratio = b - b_low;

    for (int channel = 0; channel < 3; channel++) {
        float c000 = lut[((r_low * N + g_low) * N + b_low) * 3 + channel];
        float c001 = lut[((r_low * N + g_low) * N + b_high) * 3 + channel];
        float c010 = lut[((r_low * N + g_high) * N + b_low) * 3 + channel];
        float c011 = lut[((r_low * N + g_high) * N + b_high) * 3 + channel];
        float c100 = lut[((r_high * N + g_low) * N + b_low) * 3 + channel];
        float c101 = lut[((r_high * N + g_low) * N + b_high) * 3 + channel];
        float c110 = lut[((r_high * N + g_high) * N + b_low) * 3 + channel];
        float c111 = lut[((r_high * N + g_high) * N + b_high) * 3 + channel];

        float c00 = c000 * (1 - r_ratio) + c100 * r_ratio;
        float c01 = c001 * (1 - r_ratio) + c101 * r_ratio;
        float c10 = c010 * (1 - r_ratio) + c110 * r_ratio;
        float c11 = c011 * (1 - r_ratio) + c111 * r_ratio;

        float c0 = c00 * (1 - g_ratio) + c10 * g_ratio;
        float c1 = c01 * (1 - g_ratio) + c11 * g_ratio;

        float c = c0 * (1 - b_ratio) + c1 * b_ratio;

        result[frame_rgb_index + channel] = c;
    }
}

"""

lut_trilinear_kernel = cp.RawKernel(lut_trilinear_kernel_code, "lut_trilinear_kernel")


lut_tetrahedral_kernel_code = """
__device__ float3 get_lut_value(const float *lut, int x, int y, int z, int lutSize, int lutSizeSquared) {
    int index = (x * lutSizeSquared + y * lutSize + z) * 3;
    return {lut[index], lut[index + 1], lut[index + 2]};
}

extern "C" __global__
void lut_tetrahedral_kernel(const float *frame_rgb, float *output, const float *lut, int height, int width, int lutSize, int lutSizeSquared) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x >= width || y >= height) return;

    int idx = (y * width + x) * 3;

    float r = frame_rgb[idx] * (lutSize - 1);
    float g = frame_rgb[idx + 1] * (lutSize - 1);
    float b = frame_rgb[idx + 2] * (lutSize - 1);

    int x0 = static_cast<int>(r);
    int x1 = min(x0 + 1, lutSize - 1);
    int y0 = static_cast<int>(g);
    int y1 = min(y0 + 1, lutSize - 1);
    int z0 = static_cast<int>(b);
    int z1 = min(z0 + 1, lutSize - 1);

    float dx = r - x0;
    float dy = g - y0;
    float dz = b - z0;

    float3 c000 = get_lut_value(lut, x0, y0, z0, lutSize, lutSizeSquared);
    float3 c111 = get_lut_value(lut, x1, y1, z1, lutSize, lutSizeSquared);
    float3 cA, cB;
    float s0, s1, s2, s3;

    if (dx > dy) {
        if (dy > dz) { // dx > dy > dz
            cA = get_lut_value(lut, x1, y0, z0, lutSize, lutSizeSquared);
            cB = get_lut_value(lut, x1, y1, z0, lutSize, lutSizeSquared);
            s0 = 1.0 - dx;
            s1 = dx - dy;
            s2 = dy - dz;
            s3 = dz;
        } else if (dx > dz) { // dx > dz > dy
            cA = get_lut_value(lut, x1, y0, z0, lutSize, lutSizeSquared);
            cB = get_lut_value(lut, x1, y0, z1, lutSize, lutSizeSquared);
            s0 = 1.0 - dx;
            s1 = dx - dz;
            s2 = dz - dy;
            s3 = dy;
        } else { // dz > dx > dy
            cA = get_lut_value(lut, x0, y0, z1, lutSize, lutSizeSquared);
            cB = get_lut_value(lut, x1, y0, z1, lutSize, lutSizeSquared);
            s0 = 1.0 - dz;
            s1 = dz - dx;
            s2 = dx - dy;
            s3 = dy;
        }
    } else {
        if (dz > dy) { // dz > dy > dx
            cA = get_lut_value(lut, x0, y0, z1, lutSize, lutSizeSquared);
            cB = get_lut_value(lut, x0, y1, z1, lutSize, lutSizeSquared);
            s0 = 1.0 - dz;
            s1 = dz - dy;
            s2 = dy - dx;
            s3 = dx;
        } else if (dz > dx) { // dy > dz > dx
            cA = get_lut_value(lut, x0, y1, z0, lutSize, lutSizeSquared);
            cB = get_lut_value(lut, x0, y1, z1, lutSize, lutSizeSquared);
            s0 = 1.0 - dy;
            s1 = dy - dz;
            s2 = dz - dx;
            s3 = dx;
        } else { // dy > dx > dz
            cA = get_lut_value(lut, x0, y1, z0, lutSize, lutSizeSquared);
            cB = get_lut_value(lut, x1, y1, z0, lutSize, lutSizeSquared);
            s0 = 1.0 - dy;
            s1 = dy - dx;
            s2 = dx - dz;
            s3 = dz;
        }
    }

    output[idx] = s0 * c000.x + s1 * cA.x + s2 * cB.x + s3 * c111.x;
    output[idx + 1] = s0 * c000.y + s1 * cA.y + s2 * cB.y + s3 * c111.y;
    output[idx + 2] = s0 * c000.z + s1 * cA.z + s2 * cB.z + s3 * c111.z;
}
"""
lut_tetrahedral_kernel = cp.RawKernel(lut_tetrahedral_kernel_code, "lut_tetrahedral_kernel")
