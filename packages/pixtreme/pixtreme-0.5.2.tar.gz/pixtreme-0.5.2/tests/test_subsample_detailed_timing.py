import sys
import time

import cupy as cp

from pixtreme.transform.subsample import subsample_image_back
from pixtreme.transform.subsample_flattened import subsample_image_back_flattened, subsample_image_back_gather
from pixtreme.transform.subsample_optimized_v2 import subsample_image_back_shared, subsample_image_back_vectorized


def detailed_timing_test():
    """Detailed timing analysis for each step"""
    print("=== Detailed Timing Analysis ===\n")

    test_sizes = [
        (1024, 1024, 3, 2),
        (2048, 2048, 3, 2),
        (4096, 4096, 3, 2),
        (8192, 4096, 3, 2),
    ]

    for h, w, c, dim in test_sizes:
        print(f"\n{'=' * 60}")
        print(f"Testing {h}x{w}x{c} image (dim={dim})")
        print(f"Output size: {h}x{w} pixels ({h * w * c * 4 / 1024 / 1024:.1f} MB)")
        print(f"{'=' * 60}")

        # Create test input
        print("\n1. Creating input data...")
        start = time.time()
        subsampled_list = []
        for i in range(dim * dim):
            img = cp.random.rand(h // dim, w // dim, c).astype(cp.float32)
            subsampled_list.append(img)
        cp.cuda.Stream.null.synchronize()
        input_time = time.time() - start
        print(f"   Input creation time: {input_time * 1000:.1f} ms")

        # Test Original
        print("\n2. Testing Original implementation:")
        start = time.time()
        result_original = subsample_image_back(subsampled_list, dim)
        cp.cuda.Stream.null.synchronize()
        original_time = time.time() - start
        print(f"   Total time: {original_time * 1000:.1f} ms")

        # Test Flattened - with detailed breakdown
        print("\n3. Testing Flattened implementation:")
        print("   (This includes index array creation)")

        # Skip cache clearing as it's not accessible

        # First call (includes index creation)
        start_total = time.time()

        # Simulate what happens inside the function
        print("   - Converting input...")
        start_step = time.time()
        if isinstance(subsampled_list, list):
            first = subsampled_list[0]
            if first.ndim == 2:
                batch = cp.stack([img[cp.newaxis, :, :] for img in subsampled_list], axis=0)
            else:
                batch = cp.stack([img.transpose(2, 0, 1) for img in subsampled_list], axis=0)
        else:
            batch = subsampled_list

        if batch.dtype != cp.float32:
            batch = batch.astype(cp.float32)
        batch = cp.ascontiguousarray(batch)
        convert_time = time.time() - start_step
        print(f"     Conversion time: {convert_time * 1000:.1f} ms")

        # Index creation (the bottleneck)
        print("   - Creating index array...")
        start_step = time.time()

        batch_size, channels, input_height, input_width = batch.shape
        output_height = input_height * dim
        output_width = input_width * dim
        total_output_pixels = output_height * output_width

        # This is the expensive operation
        indices = cp.empty(total_output_pixels, dtype=cp.int32)

        # Calculate indices (this is very slow for large arrays)
        output_indices = cp.arange(total_output_pixels)
        y_out = output_indices // output_width
        x_out = output_indices % output_width

        dy = y_out % dim
        dx = x_out % dim
        subsample_idx = dy * dim + dx
        y_in = y_out // dim
        x_in = x_out // dim

        # This multiplication is expensive for large arrays
        indices[:] = subsample_idx * channels * input_height * input_width + y_in * input_width + x_in

        cp.cuda.Stream.null.synchronize()
        index_time = time.time() - start_step
        print(f"     Index creation time: {index_time * 1000:.1f} ms")
        print(f"     Index array size: {indices.nbytes / 1024 / 1024:.1f} MB")

        # Clear memory
        del indices, output_indices, y_out, x_out, dy, dx, subsample_idx, y_in, x_in

        # Actually call the function
        print("   - Calling flattened function...")
        start_step = time.time()
        result_flattened = subsample_image_back_flattened(subsampled_list, dim)
        cp.cuda.Stream.null.synchronize()
        func_time = time.time() - start_step

        total_flattened_time = time.time() - start_total
        print(f"     Function call time: {func_time * 1000:.1f} ms")
        print(f"   Total flattened time: {total_flattened_time * 1000:.1f} ms")
        print(f"   Slowdown vs original: {total_flattened_time / original_time:.1f}x slower")

        # Memory usage
        mempool = cp.get_default_memory_pool()
        used_bytes = mempool.used_bytes()
        total_bytes = mempool.total_bytes()
        print(f"\n   GPU Memory: {used_bytes / 1024 / 1024:.1f} MB used / {total_bytes / 1024 / 1024:.1f} MB allocated")

        # Clear memory
        del result_original, result_flattened, batch
        mempool.free_all_blocks()


def analyze_index_creation_scaling():
    """Analyze how index creation time scales with image size"""
    print("\n\n=== Index Creation Scaling Analysis ===\n")

    sizes = [512, 1024, 2048, 4096, 8192]
    dim = 2

    print("Size    | Output Pixels | Index Array | Index Creation Time")
    print("--------|---------------|-------------|--------------------")

    for size in sizes:
        h = w = size
        output_pixels = h * w
        index_size_mb = output_pixels * 4 / 1024 / 1024  # int32

        # Time just the index creation
        start = time.time()

        # Create indices
        indices = cp.arange(output_pixels)
        y_out = indices // w
        x_out = indices % w

        dy = y_out % dim
        dx = x_out % dim
        subsample_idx = dy * dim + dx
        y_in = y_out // dim
        x_in = x_out // dim

        # The expensive calculation
        final_indices = subsample_idx * 3 * (h // dim) * (w // dim) + y_in * (w // dim) + x_in

        cp.cuda.Stream.null.synchronize()
        elapsed = time.time() - start

        print(f"{size:4d}x{size:<4d} | {output_pixels / 1e6:11.1f}M | {index_size_mb:9.1f} MB | {elapsed * 1000:15.1f} ms")

        # Clear memory
        del indices, y_out, x_out, dy, dx, subsample_idx, y_in, x_in, final_indices
        cp.get_default_memory_pool().free_all_blocks()


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Run detailed timing analysis
    detailed_timing_test()
    analyze_index_creation_scaling()
