import sys
import time

import cupy as cp

from pixtreme.transform.subsample import subsample_image_back
from pixtreme.transform.subsample_flattened import subsample_image_back_gather
from pixtreme.transform.subsample_optimized_v2 import subsample_image_back_shared, subsample_image_back_vectorized


def measure_single_execution(func, args):
    """Measure a single execution with proper synchronization"""
    cp.cuda.Stream.null.synchronize()
    start = time.time()
    result = func(*args)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.time() - start
    return elapsed, result


def benchmark_with_warmup(func, args, num_iterations=10, warmup_iterations=2):
    """Benchmark with warmup and detailed timing"""
    # Warmup
    print(f"      Warming up ({warmup_iterations} iterations)...", end="", flush=True)
    for _ in range(warmup_iterations):
        func(*args)
        cp.cuda.Stream.null.synchronize()
    print(" done")

    # Measure individual iterations
    times = []
    for i in range(num_iterations):
        cp.cuda.Stream.null.synchronize()
        start = time.time()
        func(*args)
        cp.cuda.Stream.null.synchronize()
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"      Iteration {i + 1:2d}: {elapsed * 1000:8.2f} ms", end="")
        if i == 0:
            print(" (first run)")
        else:
            print()

    # Statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    return avg_time, min_time, max_time, times


def detailed_high_res_benchmark():
    """Detailed benchmark for high resolution images"""
    print("=== High Resolution Detailed Benchmark ===\n")

    test_configs = [
        # (height, width, channels, dim, iterations)
        (2048, 2048, 3, 2, 20),  # 48MB output
        (4096, 4096, 3, 2, 10),  # 192MB output
        (8192, 4096, 3, 2, 5),  # 384MB output (real use case)
        (8192, 8192, 3, 2, 3),  # 768MB output
        (16384, 8192, 3, 2, 2),  # 1.5GB output
    ]

    for h, w, c, dim, num_iter in test_configs:
        print(f"\n{'=' * 80}")
        print(f"Testing {h}x{w}x{c} image reconstruction (dim={dim})")
        print(f"Input: {dim} images of {h // dim}x{w // dim}x{c} each")
        print(f"Output: {h}x{w}x{c} ({h * w * c * 4 / 1024 / 1024:.1f} MB)")
        print(f"{'=' * 80}")

        # Create test input
        print("\nCreating input data...", end="", flush=True)
        start = time.time()
        subsampled_list = []
        for i in range(dim * dim):
            img = cp.random.rand(h // dim, w // dim, c).astype(cp.float32)
            subsampled_list.append(img)
        cp.cuda.Stream.null.synchronize()
        print(f" done ({(time.time() - start) * 1000:.1f} ms)")

        # Memory info
        mempool = cp.get_default_memory_pool()
        print(f"GPU memory allocated: {mempool.total_bytes() / 1024 / 1024:.1f} MB")

        # Test each implementation
        implementations = [
            ("Original", subsample_image_back),
            ("Gather", subsample_image_back_gather),
            ("Shared Memory", subsample_image_back_shared),
            ("Vectorized", subsample_image_back_vectorized),
        ]

        results = {}

        for name, func in implementations:
            print(f"\n{name} implementation:")

            try:
                # First run (cold)
                print("   First run (cold):")
                cold_time, result = measure_single_execution(func, (subsampled_list, dim))
                print(f"      Time: {cold_time * 1000:.2f} ms")

                # Benchmark with multiple runs
                print(f"   Benchmarking ({num_iter} iterations):")
                avg_time, min_time, max_time, times = benchmark_with_warmup(
                    func, (subsampled_list, dim), num_iterations=num_iter
                )

                # Store results
                results[name] = {"cold": cold_time, "avg": avg_time, "min": min_time, "max": max_time, "times": times}

                # Calculate statistics
                print(f"      Average: {avg_time * 1000:8.2f} ms")
                print(f"      Min:     {min_time * 1000:8.2f} ms")
                print(f"      Max:     {max_time * 1000:8.2f} ms")

                # Memory bandwidth
                total_bytes = h * w * c * 4  # float32
                bandwidth = total_bytes / avg_time / 1e9
                print(f"      Bandwidth: {bandwidth:.1f} GB/s")

                # Clear result to free memory
                del result

            except Exception as e:
                print(f"   ERROR: {str(e)}")
                results[name] = None

        # Summary comparison
        if results.get("Original"):
            print("\n--- Performance Summary ---")
            baseline_avg = results["Original"]["avg"]

            for name, data in results.items():
                if data is None:
                    continue
                speedup = baseline_avg / data["avg"]
                print(f"{name:15s}: {data['avg'] * 1000:7.2f} ms avg ({speedup:5.2f}x)")

            # Find best performer
            best_name = min([k for k, v in results.items() if v is not None], key=lambda k: results[k]["avg"])
            print(f"\n🏆 Best: {best_name} ({results[best_name]['avg'] * 1000:.2f} ms)")

        # Clear memory
        del subsampled_list
        mempool.free_all_blocks()
        print(f"\nMemory freed. Current allocation: {mempool.total_bytes() / 1024 / 1024:.1f} MB")


def test_real_world_scenario():
    """Test the specific real-world scenario with detailed timing"""
    print("\n\n=== Real World Scenario Detailed Test ===")
    print("4x 8192x4096 images -> 16384x8192 output\n")

    dim = 2
    input_h, input_w = 8192, 4096
    channels = 3

    print(f"Creating {dim * dim} input images of size {input_h}x{input_w}x{channels}")
    print(f"Expected output: {input_h * dim}x{input_w * dim} = 16384x8192")
    print(f"Total output size: {input_h * dim * input_w * dim * channels * 4 / 1024 / 1024 / 1024:.2f} GB\n")

    # Create input
    print("Creating input images:")
    subsampled_list = []
    for i in range(dim * dim):
        print(f"  Image {i + 1}/{dim * dim}...", end="", flush=True)
        start = time.time()
        img = cp.random.rand(input_h, input_w, channels).astype(cp.float32)
        subsampled_list.append(img)
        cp.cuda.Stream.null.synchronize()
        print(f" done ({(time.time() - start) * 1000:.1f} ms)")

    # Test each implementation with single execution
    print("\nTesting implementations (single execution):")

    implementations = [
        ("Original", subsample_image_back),
        ("Gather", subsample_image_back_gather),
        ("Shared Memory", subsample_image_back_shared),
        ("Vectorized", subsample_image_back_vectorized),
    ]

    for name, func in implementations:
        print(f"\n{name}:")
        try:
            # Measure
            time_taken, result = measure_single_execution(func, (subsampled_list, dim))
            print(f"  Time: {time_taken * 1000:.2f} ms")
            print(f"  FPS: {1.0 / time_taken:.2f}")

            # Memory bandwidth
            total_bytes = input_h * dim * input_w * dim * channels * 4
            bandwidth = total_bytes / time_taken / 1e9
            print(f"  Bandwidth: {bandwidth:.1f} GB/s")

            # Verify result shape
            print(f"  Output shape: {result.shape}")

            del result

        except Exception as e:
            print(f"  ERROR: {str(e)}")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Run benchmarks
    detailed_high_res_benchmark()
    test_real_world_scenario()
