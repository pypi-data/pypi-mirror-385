import time

import cupy as cp
import numpy as np

import pixtreme as px
from pixtreme.transform.subsample import subsample_image, subsample_image_back
from pixtreme.transform.subsample_flattened import subsample_image_back_flattened, subsample_image_back_gather


def test_correctness():
    """Test that flattened versions produce correct results."""
    print("=== Testing Correctness ===")

    # Test image
    test_image = px.imread("examples/example.png")
    test_image = px.to_float32(test_image)
    test_image = test_image[:256, :256]

    dim = 2

    # Subsample the image
    subsampled = subsample_image(test_image, dim)

    # Test all three reconstruction methods
    result_original = subsample_image_back(subsampled, dim)
    result_flattened = subsample_image_back_flattened(subsampled, dim)
    result_gather = subsample_image_back_gather(subsampled, dim)

    print(f"Original result shape: {result_original.shape}")
    print(f"Flattened result shape: {result_flattened.shape}")
    print(f"Gather result shape: {result_gather.shape}")

    # Check if results match
    if cp.allclose(result_original, result_flattened, rtol=1e-5, atol=1e-7):
        print("✓ Flattened version matches original")
    else:
        print("✗ Flattened version differs!")
        diff = cp.abs(result_original - result_flattened)
        print(f"  Max difference: {cp.max(diff)}")

    if cp.allclose(result_original, result_gather, rtol=1e-5, atol=1e-7):
        print("✓ Gather version matches original")
    else:
        print("✗ Gather version differs!")
        diff = cp.abs(result_original - result_gather)
        print(f"  Max difference: {cp.max(diff)}")

    return cp.allclose(result_original, result_flattened) and cp.allclose(result_original, result_gather)


def benchmark_performance():
    """Benchmark performance of different implementations."""
    print("\n=== Performance Benchmark ===")

    test_sizes = [(256, 256, 3), (512, 512, 3), (1024, 1024, 3), (2048, 2048, 3), (4096, 4096, 3)]

    dim = 2
    iterations = 50

    for height, width, channels in test_sizes:
        print(f"\n{'=' * 60}")
        print(f"Testing {height}x{width}x{channels} image (dim={dim}):")
        print(f"{'=' * 60}")

        # Create test image
        test_image = cp.random.rand(height, width, channels).astype(cp.float32)

        # Subsample the image
        subsampled = subsample_image(test_image, dim)

        # Warm up all implementations
        _ = subsample_image_back(subsampled, dim)
        _ = subsample_image_back_flattened(subsampled, dim)
        _ = subsample_image_back_gather(subsampled, dim)
        cp.cuda.Stream.null.synchronize()

        # Benchmark original
        start = time.perf_counter()
        for _ in range(iterations):
            _ = subsample_image_back(subsampled, dim)
        cp.cuda.Stream.null.synchronize()
        time_original = time.perf_counter() - start

        # Benchmark flattened version
        start = time.perf_counter()
        for _ in range(iterations):
            _ = subsample_image_back_flattened(subsampled, dim)
        cp.cuda.Stream.null.synchronize()
        time_flattened = time.perf_counter() - start

        # Benchmark gather version
        start = time.perf_counter()
        for _ in range(iterations):
            _ = subsample_image_back_gather(subsampled, dim)
        cp.cuda.Stream.null.synchronize()
        time_gather = time.perf_counter() - start

        print(f"Original:          {time_original:.4f}s ({time_original / iterations * 1000:.2f} ms/iter) - 1.00x (baseline)")
        print(
            f"Flattened (copy):  {time_flattened:.4f}s ({time_flattened / iterations * 1000:.2f} ms/iter) - {time_original / time_flattened:.2f}x speedup"
        )
        print(
            f"Gather:            {time_gather:.4f}s ({time_gather / iterations * 1000:.2f} ms/iter) - {time_original / time_gather:.2f}x speedup"
        )

        # Calculate efficiency
        total_elements = height * width * channels
        bandwidth_original = total_elements * 4 * iterations / time_original / 1e9  # GB/s
        bandwidth_flattened = total_elements * 4 * iterations / time_flattened / 1e9
        bandwidth_gather = total_elements * 4 * iterations / time_gather / 1e9

        print(f"\nMemory bandwidth utilization:")
        print(f"Original:   {bandwidth_original:.1f} GB/s")
        print(f"Flattened:  {bandwidth_flattened:.1f} GB/s")
        print(f"Gather:     {bandwidth_gather:.1f} GB/s")


def test_cache_efficiency():
    """Test the efficiency of index caching."""
    print("\n\n=== Cache Efficiency Test ===")

    dim = 2
    test_sizes = [(512, 512, 3), (1024, 1024, 3)]

    for size in test_sizes:
        height, width, channels = size
        print(f"\nTesting cache for {height}x{width}x{channels}:")

        test_image = cp.random.rand(height, width, channels).astype(cp.float32)
        subsampled = subsample_image(test_image, dim)

        # First call - should create cache
        start = time.perf_counter()
        _ = subsample_image_back_flattened(subsampled, dim)
        cp.cuda.Stream.null.synchronize()
        time_first_call = time.perf_counter() - start

        # Second call - should use cache
        start = time.perf_counter()
        _ = subsample_image_back_flattened(subsampled, dim)
        cp.cuda.Stream.null.synchronize()
        time_cached_call = time.perf_counter() - start

        print(f"First call (with index creation): {time_first_call * 1000:.2f} ms")
        print(f"Cached call: {time_cached_call * 1000:.2f} ms")
        print(f"Cache speedup: {time_first_call / time_cached_call:.2f}x")


def test_with_batch_input():
    """Test with batch input (NCHW format)."""
    print("\n\n=== Batch Input Test ===")

    dim = 2
    height, width = 512, 512
    channels = 3

    # Create test image
    test_image = cp.random.rand(height, width, channels).astype(cp.float32)

    # Subsample
    subsampled_list = subsample_image(test_image, dim)

    # Convert to batch format (NCHW)
    batch = cp.stack([img.transpose(2, 0, 1) for img in subsampled_list], axis=0)

    print(f"Batch shape: {batch.shape}")

    # Benchmark with batch input
    iterations = 100

    # Original
    start = time.perf_counter()
    for _ in range(iterations):
        _ = subsample_image_back(batch, dim)
    cp.cuda.Stream.null.synchronize()
    time_original = time.perf_counter() - start

    # Flattened
    start = time.perf_counter()
    for _ in range(iterations):
        _ = subsample_image_back_flattened(batch, dim)
    cp.cuda.Stream.null.synchronize()
    time_flattened = time.perf_counter() - start

    print(f"Original:   {time_original:.4f}s ({time_original / iterations * 1000:.2f} ms/iter)")
    print(f"Flattened:  {time_flattened:.4f}s ({time_flattened / iterations * 1000:.2f} ms/iter)")
    print(f"Speedup:    {time_original / time_flattened:.2f}x")


if __name__ == "__main__":
    # Test correctness first
    if test_correctness():
        print("\n✅ All correctness tests passed!")
    else:
        print("\n❌ Some correctness tests failed!")
        exit(1)

    # Run performance benchmarks
    benchmark_performance()

    # Test cache efficiency
    test_cache_efficiency()

    # Test with batch input
    test_with_batch_input()
