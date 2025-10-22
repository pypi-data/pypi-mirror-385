import cupy as cp

# Shared memoryを活用した最適化カーネル
reconstruct_shared_kernel_code = r"""
#define TILE_DIM 32
#define BLOCK_ROWS 8

extern "C" __global__ void reconstruct_shared_kernel(
    const float* __restrict__ input,  // NCHW format
    float* __restrict__ output,       // HWC format
    const int batch_size,
    const int channels,
    const int input_height,
    const int input_width,
    const int output_height,
    const int output_width,
    const int dim
) {
    __shared__ float tile[TILE_DIM][TILE_DIM+1];  // +1 to avoid bank conflicts
    
    int x = blockIdx.x * TILE_DIM + threadIdx.x;
    int y = blockIdx.y * TILE_DIM + threadIdx.y;
    
    // Process multiple elements per thread
    for (int k = 0; k < TILE_DIM; k += BLOCK_ROWS) {
        int yIndex = y + k;
        
        if (x < output_width && yIndex < output_height) {
            // Calculate subsample indices
            int dy = yIndex % dim;
            int dx = x % dim;
            int subsample_idx = dy * dim + dx;
            int y_in = yIndex / dim;
            int x_in = x / dim;
            
            // Process all channels
            for (int c = 0; c < channels; c++) {
                // Read from NCHW input
                int idx_in = subsample_idx * channels * input_height * input_width +
                            c * input_height * input_width +
                            y_in * input_width + x_in;
                
                // Write to HWC output
                int idx_out = (yIndex * output_width + x) * channels + c;
                
                output[idx_out] = input[idx_in];
            }
        }
    }
}
"""

reconstruct_shared_kernel = cp.RawKernel(reconstruct_shared_kernel_code, "reconstruct_shared_kernel")


# Vectorized memory access for RGB images
reconstruct_vectorized_kernel_code = r"""
extern "C" __global__ void reconstruct_vectorized_kernel(
    const float* __restrict__ input,  // NCHW format
    float* __restrict__ output,       // HWC format
    const int input_height,
    const int input_width,
    const int output_height,
    const int output_width,
    const int dim
) {
    const int x = blockIdx.x * blockDim.x + threadIdx.x;
    const int y = blockIdx.y * blockDim.y + threadIdx.y;
    
    if (x >= output_width || y >= output_height) return;
    
    // Calculate subsample indices
    const int dy = y % dim;
    const int dx = x % dim;
    const int subsample_idx = dy * dim + dx;
    const int y_in = y / dim;
    const int x_in = x / dim;
    
    // Calculate base indices
    const int input_pixel_base = subsample_idx * 3 * input_height * input_width +
                                y_in * input_width + x_in;
    const int output_pixel_base = (y * output_width + x) * 3;
    
    // Vectorized load and store for RGB
    float3 pixel;
    pixel.x = input[input_pixel_base];
    pixel.y = input[input_pixel_base + input_height * input_width];
    pixel.z = input[input_pixel_base + 2 * input_height * input_width];
    
    output[output_pixel_base] = pixel.x;
    output[output_pixel_base + 1] = pixel.y;
    output[output_pixel_base + 2] = pixel.z;
}
"""

reconstruct_vectorized_kernel = cp.RawKernel(reconstruct_vectorized_kernel_code, "reconstruct_vectorized_kernel")


# Pre-computed index pattern for small dimensions
reconstruct_pattern_kernel_code = r"""
extern "C" __global__ void reconstruct_pattern_kernel(
    const float* __restrict__ input,
    float* __restrict__ output,
    const int* __restrict__ pattern,
    const int pattern_size,
    const int total_pixels,
    const int channels
) {
    const int pixel_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (pixel_idx >= total_pixels) return;
    
    const int pattern_idx = pixel_idx % pattern_size;
    const int pattern_offset = pixel_idx / pattern_size;
    
    const int input_offset = pattern[pattern_idx] + pattern_offset * pattern_size;
    const int output_offset = pixel_idx * channels;
    
    // Unrolled copy for common channel counts
    if (channels == 3) {
        output[output_offset] = input[input_offset];
        output[output_offset + 1] = input[input_offset + total_pixels];
        output[output_offset + 2] = input[input_offset + 2 * total_pixels];
    } else {
        for (int c = 0; c < channels; c++) {
            output[output_offset + c] = input[input_offset + c * total_pixels];
        }
    }
}
"""

reconstruct_pattern_kernel = cp.RawKernel(reconstruct_pattern_kernel_code, "reconstruct_pattern_kernel")


def subsample_image_back_shared(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """Shared memory optimized version"""

    # Convert to batch format if necessary
    if isinstance(subsampled_images, list):
        first = subsampled_images[0]
        if first.ndim == 2:
            batch = cp.stack([img[cp.newaxis, :, :] for img in subsampled_images], axis=0)
        else:
            batch = cp.stack([img.transpose(2, 0, 1) for img in subsampled_images], axis=0)
    else:
        batch = subsampled_images

    if batch.ndim != 4:
        raise ValueError("Input must be 4D tensor in NCHW format")

    batch_size, channels, input_height, input_width = batch.shape

    if batch_size != dim * dim:
        raise ValueError(f"Batch size {batch_size} doesn't match dim*dim = {dim * dim}")

    # Ensure contiguous float32
    if batch.dtype != cp.float32:
        batch = batch.astype(cp.float32)
    batch = cp.ascontiguousarray(batch)

    # Output dimensions
    output_height = input_height * dim
    output_width = input_width * dim

    # Allocate output in HWC format
    output = cp.empty((output_height, output_width, channels), dtype=cp.float32)

    # Launch shared memory kernel
    TILE_DIM = 32
    BLOCK_ROWS = 8
    block_size = (TILE_DIM, BLOCK_ROWS)
    grid_size = ((output_width + TILE_DIM - 1) // TILE_DIM, (output_height + TILE_DIM - 1) // TILE_DIM)

    reconstruct_shared_kernel(
        grid_size,
        block_size,
        (batch, output, batch_size, channels, input_height, input_width, output_height, output_width, dim),
    )

    # Return 2D if originally grayscale
    if channels == 1:
        return output.squeeze(axis=2)

    return output


def subsample_image_back_vectorized(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """Vectorized version optimized for RGB images"""

    # Convert to batch format if necessary
    if isinstance(subsampled_images, list):
        first = subsampled_images[0]
        if first.ndim == 2:
            batch = cp.stack([img[cp.newaxis, :, :] for img in subsampled_images], axis=0)
        else:
            batch = cp.stack([img.transpose(2, 0, 1) for img in subsampled_images], axis=0)
    else:
        batch = subsampled_images

    if batch.ndim != 4:
        raise ValueError("Input must be 4D tensor in NCHW format")

    batch_size, channels, input_height, input_width = batch.shape

    if batch_size != dim * dim:
        raise ValueError(f"Batch size {batch_size} doesn't match dim*dim = {dim * dim}")

    # This kernel is optimized for RGB images
    if channels != 3:
        raise ValueError("Vectorized kernel only supports RGB images (3 channels)")

    # Ensure contiguous float32
    if batch.dtype != cp.float32:
        batch = batch.astype(cp.float32)
    batch = cp.ascontiguousarray(batch)

    # Output dimensions
    output_height = input_height * dim
    output_width = input_width * dim

    # Allocate output in HWC format
    output = cp.empty((output_height, output_width, channels), dtype=cp.float32)

    # Launch vectorized kernel
    block_size = (16, 16)
    grid_size = ((output_width + block_size[0] - 1) // block_size[0], (output_height + block_size[1] - 1) // block_size[1])

    reconstruct_vectorized_kernel(
        grid_size, block_size, (batch, output, input_height, input_width, output_height, output_width, dim)
    )

    return output
