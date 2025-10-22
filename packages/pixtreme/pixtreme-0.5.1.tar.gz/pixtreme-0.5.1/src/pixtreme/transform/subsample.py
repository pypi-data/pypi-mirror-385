import cupy as cp


def subsample_image(image: cp.ndarray, dim: int) -> list[cp.ndarray]:
    """Perform interleaved subsampling of an image without for loops.

    Args:
        image: Input image (cp.ndarray) with shape (height, width) or (height, width, channels).
        dim: Block size for subsampling.

    Returns:
        List of interleaved subsampled images.
    """
    # Get image dimensions
    if image.ndim == 2:
        height, width = image.shape
        channels = None
    elif image.ndim == 3:
        height, width, channels = image.shape
    else:
        raise ValueError("Image must be 2D or 3D")

    # Check if dimensions are divisible by dim
    if height % dim != 0 or width % dim != 0:
        raise ValueError(f"Image size ({height}×{width}) must be divisible by dim ({dim})")

    # Calculate new dimensions
    new_height = height // dim
    new_width = width // dim

    if channels is None:
        # For grayscale images
        # Reshape image to (new_height, dim, new_width, dim)
        reshaped = image.reshape(new_height, dim, new_width, dim)
        # Transpose axes to (dim, dim, new_height, new_width)
        transposed = reshaped.transpose(1, 3, 0, 2)
        # Reshape to (dim*dim, new_height, new_width)
        flattened = transposed.reshape(dim * dim, new_height, new_width)
        # Convert to list
        result = [flattened[i] for i in range(dim * dim)]
    else:
        # For color images
        # Reshape image to (new_height, dim, new_width, dim, channels)
        reshaped = image.reshape(new_height, dim, new_width, dim, channels)
        # Transpose axes to (dim, dim, new_height, new_width, channels)
        transposed = reshaped.transpose(1, 3, 0, 2, 4)
        # Reshape to (dim*dim, new_height, new_width, channels)
        flattened = transposed.reshape(dim * dim, new_height, new_width, channels)
        # Convert to list
        result = [flattened[i] for i in range(dim * dim)]

    return result


# Reconstruction kernel optimized for memory coalescing
reconstruct_optimized_kernel_code = r"""
extern "C" __global__ void reconstruct_optimized_kernel(
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
    // Use 1D indexing for better performance
    const int tid = blockIdx.x * blockDim.x + threadIdx.x;
    const int total_elements = output_height * output_width * channels;
    
    if (tid >= total_elements) return;
    
    // Decode output position
    const int c = tid % channels;
    const int xy = tid / channels;
    const int x = xy % output_width;
    const int y = xy / output_width;
    
    // Calculate which subsample and position
    const int dy = y % dim;
    const int dx = x % dim;
    const int subsample_idx = dy * dim + dx;
    const int y_in = y / dim;
    const int x_in = x / dim;
    
    // Read from NCHW input
    const int idx_in = subsample_idx * channels * input_height * input_width +
                      c * input_height * input_width +
                      y_in * input_width + x_in;
    
    // Write to output
    output[tid] = input[idx_in];
}
"""

reconstruct_optimized_kernel = cp.RawKernel(reconstruct_optimized_kernel_code, "reconstruct_optimized_kernel")


def subsample_image_back(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """Ultra-optimized reconstruction using single-pass kernel.

    Args:
        subsampled_images: Batch tensor with shape (N, C, H, W) where N = dim*dim or a list of images[H, W, C].
        dim: Block size used in the original subsampling

    Returns:
        Reconstructed image with shape (H*dim, W*dim, C)
    """

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

    # Launch optimized kernel
    total_elements = output_height * output_width * channels
    block_size = 256
    grid_size = (total_elements + block_size - 1) // block_size

    reconstruct_optimized_kernel(
        (grid_size,),
        (block_size,),
        (batch, output, batch_size, channels, input_height, input_width, output_height, output_width, dim),
    )

    # Return 2D if originally grayscale
    if channels == 1:
        return output.squeeze(axis=2)

    return output
