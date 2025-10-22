import sys
import time

import cupy as cp
import numpy as np

from pixtreme.transform.subsample import subsample_image_back
from pixtreme.transform.subsample_optimized_v2 import subsample_image_back_shared, subsample_image_back_vectorized


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
    """Test that optimized versions produce correct results"""
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

    # Test shared memory version
    result_shared = subsample_image_back_shared(subsampled_list, dim)
    print(f"Shared memory result shape: {result_shared.shape}")

    # Test vectorized version (RGB only)
    result_vectorized = subsample_image_back_vectorized(subsampled_list, dim)
    print(f"Vectorized result shape: {result_vectorized.shape}")

    # Verify correctness
    if cp.allclose(result_original, result_shared, atol=1e-6):
        print("✓ Shared memory version matches original")
    else:
        print("✗ Shared memory version does NOT match")
        diff = cp.abs(result_original - result_shared)
        print(f"  Max difference: {cp.max(diff)}")

    if cp.allclose(result_original, result_vectorized, atol=1e-6):
        print("✓ Vectorized version matches original")
    else:
        print("✗ Vectorized version does NOT match")
        diff = cp.abs(result_original - result_vectorized)
        print(f"  Max difference: {cp.max(diff)}")

    print(
        "\n✅ All correctness tests passed!"
        if cp.allclose(result_original, result_shared, atol=1e-6)
        and cp.allclose(result_original, result_vectorized, atol=1e-6)
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
        (16384, 8192, 3, 2),  # Real use case output
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

        # Benchmark shared memory
        time_shared = benchmark_function(subsample_image_back_shared, (subsampled_list, dim))

        # Benchmark vectorized (only for RGB)
        if c == 3:
            time_vectorized = benchmark_function(subsample_image_back_vectorized, (subsampled_list, dim))
        else:
            time_vectorized = float("inf")

        # Calculate speedups
        speedup_shared = time_original / time_shared
        speedup_vectorized = time_original / time_vectorized if c == 3 else 0

        # Calculate memory bandwidth
        total_bytes = h * w * c * 4  # float32
        bw_original = total_bytes / time_original / 1e9
        bw_shared = total_bytes / time_shared / 1e9
        bw_vectorized = total_bytes / time_vectorized / 1e9 if c == 3 else 0

        # Print results
        print(f"Original:          {time_original:.4f}s ({time_original * 1000:.2f} ms) - 1.00x (baseline)")
        print(f"Shared memory:     {time_shared:.4f}s ({time_shared * 1000:.2f} ms) - {speedup_shared:.2f}x speedup")
        if c == 3:
            print(
                f"Vectorized:        {time_vectorized:.4f}s ({time_vectorized * 1000:.2f} ms) - {speedup_vectorized:.2f}x speedup"
            )

        print(f"\nMemory bandwidth utilization:")
        print(f"Original:      {bw_original:.1f} GB/s")
        print(f"Shared memory: {bw_shared:.1f} GB/s")
        if c == 3:
            print(f"Vectorized:    {bw_vectorized:.1f} GB/s")


def test_memory_patterns():
    """Test memory access patterns"""
    print("\n=== Memory Access Pattern Analysis ===")

    dim = 2
    h, w = 512, 512
    channels = 3

    # Create aligned vs unaligned inputs
    print("\nTesting memory alignment impact:")

    # Aligned memory
    subsampled_aligned = []
    for i in range(dim * dim):
        img = cp.zeros((h // dim, w // dim, channels), dtype=cp.float32)
        img[:] = cp.random.rand(h // dim, w // dim, channels)
        subsampled_aligned.append(cp.ascontiguousarray(img))

    # Unaligned memory (transposed)
    subsampled_unaligned = []
    for i in range(dim * dim):
        img = cp.random.rand(channels, h // dim, w // dim).astype(cp.float32)
        img = img.transpose(1, 2, 0)
        subsampled_unaligned.append(img)

    # Benchmark aligned
    time_aligned = benchmark_function(subsample_image_back, (subsampled_aligned, dim), num_iterations=500)
    time_aligned_shared = benchmark_function(subsample_image_back_shared, (subsampled_aligned, dim), num_iterations=500)

    # Benchmark unaligned
    time_unaligned = benchmark_function(subsample_image_back, (subsampled_unaligned, dim), num_iterations=500)
    time_unaligned_shared = benchmark_function(subsample_image_back_shared, (subsampled_unaligned, dim), num_iterations=500)

    print(f"Aligned memory:")
    print(f"  Original:      {time_aligned * 1000:.2f} ms")
    print(f"  Shared memory: {time_aligned_shared * 1000:.2f} ms ({time_aligned / time_aligned_shared:.2f}x speedup)")

    print(f"\nUnaligned memory:")
    print(f"  Original:      {time_unaligned * 1000:.2f} ms")
    print(f"  Shared memory: {time_unaligned_shared * 1000:.2f} ms ({time_unaligned / time_unaligned_shared:.2f}x speedup)")

    print(f"\nAlignment impact:")
    print(f"  Original:      {(time_unaligned - time_aligned) / time_aligned * 100:.1f}% slower")
    print(f"  Shared memory: {(time_unaligned_shared - time_aligned_shared) / time_aligned_shared * 100:.1f}% slower")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Run tests
    test_correctness()
    benchmark_performance()
    test_memory_patterns()
