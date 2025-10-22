import sys
import time

import cupy as cp

from pixtreme.transform.subsample import subsample_image_back
from pixtreme.transform.subsample_optimized_v2 import subsample_image_back_shared, subsample_image_back_vectorized


def benchmark_with_stats(func, args, num_iterations=10):
    """Benchmark with detailed statistics"""
    # Warmup
    for _ in range(3):
        func(*args)
    cp.cuda.Stream.null.synchronize()

    # Measure
    times = []
    for _ in range(num_iterations):
        cp.cuda.Stream.null.synchronize()
        start = time.time()
        func(*args)
        cp.cuda.Stream.null.synchronize()
        elapsed = time.time() - start
        times.append(elapsed)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    return avg_time, min_time, max_time


def final_comparison():
    """Final comparison of the viable implementations"""
    print("=== Final Performance Comparison ===")
    print("Testing Original vs Shared Memory vs Vectorized\n")

    test_configs = [
        # (height, width, channels, dim, iterations)
        (1024, 1024, 3, 2, 100),  # Small
        (2048, 2048, 3, 2, 50),  # Medium
        (4096, 4096, 3, 2, 20),  # Large
        (8192, 4096, 3, 2, 10),  # Real use case
        (8192, 8192, 3, 2, 5),  # Very large
        (16384, 8192, 3, 2, 3),  # Ultra large
    ]

    overall_results = {
        "Original": {"wins": 0, "total_speedup": 0},
        "Shared Memory": {"wins": 0, "total_speedup": 0},
        "Vectorized": {"wins": 0, "total_speedup": 0},
    }

    for h, w, c, dim, num_iter in test_configs:
        print(f"\n{'=' * 60}")
        print(f"{h}x{w}x{c} (dim={dim}) -> Output: {h * w * c * 4 / 1024 / 1024:.1f} MB")
        print(f"{'=' * 60}")

        # Create test input
        subsampled_list = []
        for i in range(dim * dim):
            img = cp.random.rand(h // dim, w // dim, c).astype(cp.float32)
            subsampled_list.append(img)

        # Benchmark implementations
        results = {}

        # Original
        avg, min_t, max_t = benchmark_with_stats(subsample_image_back, (subsampled_list, dim), num_iter)
        results["Original"] = avg
        bandwidth = h * w * c * 4 / avg / 1e9
        print(f"Original:      {avg * 1000:6.2f} ms (±{(max_t - min_t) * 1000:.2f} ms) | {bandwidth:6.1f} GB/s")

        # Shared Memory
        avg, min_t, max_t = benchmark_with_stats(subsample_image_back_shared, (subsampled_list, dim), num_iter)
        results["Shared Memory"] = avg
        bandwidth = h * w * c * 4 / avg / 1e9
        speedup = results["Original"] / avg
        print(
            f"Shared Memory: {avg * 1000:6.2f} ms (±{(max_t - min_t) * 1000:.2f} ms) | {bandwidth:6.1f} GB/s | {speedup:.2f}x"
        )

        # Vectorized
        avg, min_t, max_t = benchmark_with_stats(subsample_image_back_vectorized, (subsampled_list, dim), num_iter)
        results["Vectorized"] = avg
        bandwidth = h * w * c * 4 / avg / 1e9
        speedup = results["Original"] / avg
        print(
            f"Vectorized:    {avg * 1000:6.2f} ms (±{(max_t - min_t) * 1000:.2f} ms) | {bandwidth:6.1f} GB/s | {speedup:.2f}x"
        )

        # Find winner
        winner = min(results.items(), key=lambda x: x[1])[0]
        print(f"\n🏆 Winner: {winner}")
        overall_results[winner]["wins"] += 1

        # Calculate speedups for overall statistics
        for name, time in results.items():
            overall_results[name]["total_speedup"] += results["Original"] / time

        # Clear memory
        del subsampled_list
        cp.get_default_memory_pool().free_all_blocks()

    # Overall summary
    print(f"\n\n{'=' * 60}")
    print("OVERALL SUMMARY")
    print(f"{'=' * 60}")

    print("\nWin Count:")
    for name, data in overall_results.items():
        print(f"  {name:15s}: {data['wins']} wins")

    print("\nAverage Speedup vs Original:")
    num_tests = len(test_configs)
    for name, data in overall_results.items():
        avg_speedup = data["total_speedup"] / num_tests
        print(f"  {name:15s}: {avg_speedup:.3f}x")

    # Final verdict
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    if overall_results["Original"]["wins"] >= num_tests // 2:
        print("✅ Original implementation is the best overall choice!")
        print("   - Simplest code")
        print("   - Best or near-best performance in most cases")
        print("   - No additional complexity")
    else:
        winner = max(overall_results.items(), key=lambda x: x[1]["wins"])[0]
        print(f"✅ {winner} shows slight advantages in some cases")
        print("   But the improvement is marginal (<5% in most cases)")
    print("=" * 60)


def test_real_world_fps():
    """Test FPS for real-world scenario"""
    print("\n\n=== Real-World Scenario FPS Test ===")
    print("8192x4096 x4 -> 16384x8192 (1.5GB)\n")

    dim = 2
    input_h, input_w = 8192, 4096
    channels = 3

    # Create input
    subsampled_list = []
    for i in range(dim * dim):
        img = cp.random.rand(input_h, input_w, channels).astype(cp.float32)
        subsampled_list.append(img)

    # Test each implementation
    implementations = [
        ("Original", subsample_image_back),
        ("Shared Memory", subsample_image_back_shared),
        ("Vectorized", subsample_image_back_vectorized),
    ]

    print("Measuring FPS (10 frames)...")
    for name, func in implementations:
        # Warmup
        for _ in range(2):
            func(subsampled_list, dim)
        cp.cuda.Stream.null.synchronize()

        # Measure 10 frames
        start = time.time()
        for _ in range(10):
            func(subsampled_list, dim)
        cp.cuda.Stream.null.synchronize()
        elapsed = time.time() - start

        fps = 10 / elapsed
        ms_per_frame = elapsed / 10 * 1000

        print(f"{name:15s}: {fps:6.2f} FPS ({ms_per_frame:.2f} ms/frame)")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Get GPU info
    mempool = cp.get_default_memory_pool()
    pinned_mempool = cp.get_default_pinned_memory_pool()

    print("GPU Information:")
    print(f"  Device: {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}")
    print(f"  Memory: {cp.cuda.runtime.getDeviceProperties(0)['totalGlobalMem'] / 1024**3:.1f} GB")
    print()

    # Run final comparison
    final_comparison()
    test_real_world_fps()
