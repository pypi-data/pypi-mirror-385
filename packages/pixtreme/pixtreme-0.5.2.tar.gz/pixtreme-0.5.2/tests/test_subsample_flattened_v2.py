import sys
import time

import cupy as cp

from pixtreme.transform.subsample import subsample_image_back
from pixtreme.transform.subsample_flattened import subsample_image_back_flattened, subsample_image_back_gather


def benchmark_function(func, args, num_iterations=1000):
    """Benchmark a function with warmup"""
    # Warmup
    for _ in range(10):
        func(*args)
    cp.cuda.Stream.null.synchronize()

    # Benchmark
    start = time.time()
    for _ in range(num_iterations):
        func(*args)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.time() - start

    return elapsed / num_iterations


def test_correctness():
    """Test that flattened versions produce correct results"""
    print("=== Testing Correctness ===")

    # Test parameters
    dim = 2
    h, w = 128, 128
    channels = 3

    # Create test input
    subsampled_list = []
    for i in range(dim * dim):
        img = cp.random.rand(h, w, channels).astype(cp.float32)
        subsampled_list.append(img)

    # Test original
    result_original = subsample_image_back(subsampled_list, dim)
    print(f"Original result shape: {result_original.shape}")

    # Test flattened
    result_flattened = subsample_image_back_flattened(subsampled_list, dim)
    print(f"Flattened result shape: {result_flattened.shape}")

    # Test gather
    result_gather = subsample_image_back_gather(subsampled_list, dim)
    print(f"Gather result shape: {result_gather.shape}")

    # Verify correctness
    if cp.allclose(result_original, result_flattened, atol=1e-6):
        print("✓ Flattened version matches original")
    else:
        print("✗ Flattened version does NOT match")
        diff = cp.abs(result_original - result_flattened)
        print(f"  Max difference: {cp.max(diff)}")

    if cp.allclose(result_original, result_gather, atol=1e-6):
        print("✓ Gather version matches original")
    else:
        print("✗ Gather version does NOT match")
        diff = cp.abs(result_original - result_gather)
        print(f"  Max difference: {cp.max(diff)}")

    print(
        "\n✅ All correctness tests passed!"
        if cp.allclose(result_original, result_flattened, atol=1e-6) and cp.allclose(result_original, result_gather, atol=1e-6)
        else "\n❌ Some tests failed!"
    )


def benchmark_performance():
    """Benchmark different implementations"""
    print("\n=== Performance Benchmark ===")

    test_sizes = [
        (512, 512, 3, 2),  # Small
        (1024, 1024, 3, 2),  # Medium
        (2048, 2048, 3, 2),  # Large
        (4096, 4096, 3, 2),  # Very large
        (8192, 8192, 3, 2),  # Ultra large
        (16384, 8192, 3, 2),  # Real use case
        (8192, 4096, 3, 2),  # Real input size
    ]

    for h, w, c, dim in test_sizes:
        print(f"\n{'=' * 60}")
        print(f"Testing {h}x{w}x{c} image (dim={dim}):")
        print(f"{'=' * 60}")

        # Create test input
        subsampled_list = []
        for i in range(dim * dim):
            img = cp.random.rand(h // dim, w // dim, c).astype(cp.float32)
            subsampled_list.append(img)

        # Benchmark original
        time_original = benchmark_function(subsample_image_back, (subsampled_list, dim))

        # Benchmark flattened
        time_flattened = benchmark_function(subsample_image_back_flattened, (subsampled_list, dim))

        # Benchmark gather
        time_gather = benchmark_function(subsample_image_back_gather, (subsampled_list, dim))

        # Calculate speedups
        speedup_flattened = time_original / time_flattened
        speedup_gather = time_original / time_gather

        # Calculate memory bandwidth
        total_bytes = h * w * c * 4  # float32
        bw_original = total_bytes / time_original / 1e9
        bw_flattened = total_bytes / time_flattened / 1e9
        bw_gather = total_bytes / time_gather / 1e9

        # Print results
        print(f"Original:          {time_original:.4f}s ({time_original * 1000:.2f} ms) - 1.00x (baseline)")
        print(f"Flattened (copy):  {time_flattened:.4f}s ({time_flattened * 1000:.2f} ms) - {speedup_flattened:.2f}x speedup")
        print(f"Gather:            {time_gather:.4f}s ({time_gather * 1000:.2f} ms) - {speedup_gather:.2f}x speedup")

        print(f"\nMemory bandwidth utilization:")
        print(f"Original:   {bw_original:.1f} GB/s")
        print(f"Flattened:  {bw_flattened:.1f} GB/s")
        print(f"Gather:     {bw_gather:.1f} GB/s")


def test_cache_efficiency():
    """Test cache efficiency for repeated operations"""
    print("\n\n=== Cache Efficiency Test ===")

    for h, w in [(512, 512), (1024, 1024)]:
        print(f"\nTesting cache for {h}x{w}x3:")

        dim = 2
        c = 3

        # Create test input
        subsampled_list = []
        for i in range(dim * dim):
            img = cp.random.rand(h // dim, w // dim, c).astype(cp.float32)
            subsampled_list.append(img)

        # First call (creates indices)
        start = time.time()
        result = subsample_image_back_flattened(subsampled_list, dim)
        cp.cuda.Stream.null.synchronize()
        first_time = (time.time() - start) * 1000

        # Cached call
        time_cached = benchmark_function(subsample_image_back_flattened, (subsampled_list, dim), num_iterations=100)

        print(f"First call (with index creation): {first_time:.2f} ms")
        print(f"Cached call: {time_cached * 1000:.2f} ms")
        print(f"Cache speedup: {first_time / (time_cached * 1000):.2f}x")


def test_batch_input():
    """Test with batch input format"""
    print("\n\n=== Batch Input Test ===")

    dim = 2
    h, w = 256, 256
    c = 3

    # Create batch input (NCHW format)
    batch = cp.random.rand(dim * dim, c, h // dim, w // dim).astype(cp.float32)
    print(f"Batch shape: {batch.shape}")

    # Benchmark original
    time_original = benchmark_function(subsample_image_back, (batch, dim), num_iterations=100)

    # Benchmark flattened
    time_flattened = benchmark_function(subsample_image_back_flattened, (batch, dim), num_iterations=100)

    print(f"Original:   {time_original:.4f}s ({time_original * 1000:.2f} ms)")
    print(f"Flattened:  {time_flattened:.4f}s ({time_flattened * 1000:.2f} ms)")
    print(f"Speedup:    {time_original / time_flattened:.2f}x")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Run tests
    test_correctness()
    benchmark_performance()
    test_cache_efficiency()
    test_batch_input()
