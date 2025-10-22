import sys
import time

import cupy as cp

from pixtreme.transform.subsample import subsample_image_back
from pixtreme.transform.subsample_flattened import subsample_image_back_flattened, subsample_image_back_gather
from pixtreme.transform.subsample_optimized_v2 import subsample_image_back_shared, subsample_image_back_vectorized


def benchmark_function(func, args, num_iterations=10):
    """Benchmark a function with warmup"""
    # Warmup
    for _ in range(2):
        func(*args)
    cp.cuda.Stream.null.synchronize()

    # Benchmark
    start = time.time()
    for _ in range(num_iterations):
        func(*args)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.time() - start

    return elapsed / num_iterations


def benchmark_ultra_high_resolution():
    """Benchmark for ultra high resolution images"""
    print("=== Ultra High Resolution Benchmark ===")
    print("Testing real-world use case: 8192x4096 -> 16384x8192\n")

    test_configs = [
        # (h, w, c, dim, iterations)
        (1024, 1024, 3, 2, 100),  # Medium - baseline
        (2048, 2048, 3, 2, 50),  # Large
        (4096, 4096, 3, 2, 20),  # Very large
        (8192, 4096, 3, 2, 10),  # Real input size
        (8192, 8192, 3, 2, 5),  # Ultra large
        (16384, 8192, 3, 2, 3),  # Real output size
    ]

    for h, w, c, dim, num_iter in test_configs:
        print(f"\n{'=' * 70}")
        print(f"Testing {h}x{w}x{c} image (dim={dim}), {num_iter} iterations:")
        print(f"Output size will be: {h}x{w} pixels")
        print(f"Memory required: {h * w * c * 4 / 1024 / 1024:.1f} MB")
        print(f"{'=' * 70}")

        # Create test input
        try:
            subsampled_list = []
            for i in range(dim * dim):
                img = cp.random.rand(h // dim, w // dim, c).astype(cp.float32)
                subsampled_list.append(img)

            # Benchmark original
            print("\nRunning benchmarks...")
            time_original = benchmark_function(subsample_image_back, (subsampled_list, dim), num_iterations=num_iter)
            print(f"✓ Original completed")

            # Benchmark flattened (only for smaller sizes due to memory)
            if h * w <= 8192 * 8192:
                time_flattened = benchmark_function(
                    subsample_image_back_flattened, (subsampled_list, dim), num_iterations=num_iter
                )
                print(f"✓ Flattened completed")

                time_gather = benchmark_function(subsample_image_back_gather, (subsampled_list, dim), num_iterations=num_iter)
                print(f"✓ Gather completed")
            else:
                time_flattened = float("inf")
                time_gather = float("inf")
                print(f"⚠ Skipping flattened/gather (too much memory)")

            # Benchmark shared memory
            time_shared = benchmark_function(subsample_image_back_shared, (subsampled_list, dim), num_iterations=num_iter)
            print(f"✓ Shared memory completed")

            # Benchmark vectorized
            time_vectorized = benchmark_function(
                subsample_image_back_vectorized, (subsampled_list, dim), num_iterations=num_iter
            )
            print(f"✓ Vectorized completed")

            # Calculate speedups
            speedup_flattened = time_original / time_flattened if time_flattened != float("inf") else 0
            speedup_gather = time_original / time_gather if time_gather != float("inf") else 0
            speedup_shared = time_original / time_shared
            speedup_vectorized = time_original / time_vectorized

            # Calculate memory bandwidth
            total_bytes = h * w * c * 4  # float32
            bw_original = total_bytes / time_original / 1e9

            # Print results
            print(f"\nPerformance Results:")
            print(f"Original:          {time_original:.4f}s ({time_original * 1000:.1f} ms) - 1.00x (baseline)")
            if time_flattened != float("inf"):
                print(f"Flattened (copy):  {time_flattened:.4f}s ({time_flattened * 1000:.1f} ms) - {speedup_flattened:.2f}x")
                print(f"Gather:            {time_gather:.4f}s ({time_gather * 1000:.1f} ms) - {speedup_gather:.2f}x")
            print(f"Shared memory:     {time_shared:.4f}s ({time_shared * 1000:.1f} ms) - {speedup_shared:.2f}x")
            print(f"Vectorized:        {time_vectorized:.4f}s ({time_vectorized * 1000:.1f} ms) - {speedup_vectorized:.2f}x")

            print(f"\nMemory bandwidth: {bw_original:.1f} GB/s")

            # Find best performer
            best_time = min(time_original, time_shared, time_vectorized)
            if time_flattened != float("inf"):
                best_time = min(best_time, time_flattened, time_gather)

            if best_time == time_original:
                best_method = "Original"
            elif best_time == time_shared:
                best_method = "Shared memory"
            elif best_time == time_vectorized:
                best_method = "Vectorized"
            elif best_time == time_flattened:
                best_method = "Flattened"
            else:
                best_method = "Gather"

            print(f"\n🏆 Best performer: {best_method}")

        except cp.cuda.memory.OutOfMemoryError:
            print(f"\n❌ Out of GPU memory for {h}x{w}x{c}")
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


def test_real_world_scenario():
    """Test the specific real-world scenario mentioned by the user"""
    print("\n\n=== Real World Scenario Test ===")
    print("4x 8192x4096 images -> 16384x8192 output\n")

    # Simulate the real scenario
    dim = 2
    input_h, input_w = 8192, 4096
    channels = 3

    print(f"Creating 4 input images of size {input_h}x{input_w}x{channels}")
    print(f"Expected output size: {input_h * dim}x{input_w * dim} = 16384x8192")
    print(f"Total memory required: {input_h * dim * input_w * dim * channels * 4 / 1024 / 1024 / 1024:.2f} GB\n")

    try:
        # Create test input (4 images for dim=2)
        subsampled_list = []
        for i in range(dim * dim):
            print(f"Creating input image {i + 1}/4...")
            img = cp.random.rand(input_h, input_w, channels).astype(cp.float32)
            subsampled_list.append(img)

        print("\nBenchmarking reconstruction methods (5 iterations each)...")

        # Benchmark original
        time_original = benchmark_function(subsample_image_back, (subsampled_list, dim), num_iterations=5)
        print(f"✓ Original: {time_original * 1000:.1f} ms/iter")

        # Benchmark shared memory
        time_shared = benchmark_function(subsample_image_back_shared, (subsampled_list, dim), num_iterations=5)
        print(f"✓ Shared memory: {time_shared * 1000:.1f} ms/iter ({time_original / time_shared:.2f}x)")

        # Benchmark vectorized
        time_vectorized = benchmark_function(subsample_image_back_vectorized, (subsampled_list, dim), num_iterations=5)
        print(f"✓ Vectorized: {time_vectorized * 1000:.1f} ms/iter ({time_original / time_vectorized:.2f}x)")

        # Memory bandwidth
        total_bytes = input_h * dim * input_w * dim * channels * 4
        bw = total_bytes / time_original / 1e9
        print(f"\nMemory bandwidth: {bw:.1f} GB/s")

        # FPS calculation
        fps_original = 1.0 / time_original
        fps_best = 1.0 / min(time_original, time_shared, time_vectorized)
        print(f"\nProcessing speed:")
        print(f"Original: {fps_original:.2f} FPS")
        print(f"Best method: {fps_best:.2f} FPS")

    except cp.cuda.memory.OutOfMemoryError:
        print("\n❌ Out of GPU memory!")
        print("Note: This test requires significant GPU memory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Get GPU info
    mempool = cp.get_default_memory_pool()
    print(f"GPU Memory Pool: {mempool.total_bytes() / 1024**3:.2f} GB allocated")

    # Run benchmarks
    benchmark_ultra_high_resolution()
    test_real_world_scenario()
