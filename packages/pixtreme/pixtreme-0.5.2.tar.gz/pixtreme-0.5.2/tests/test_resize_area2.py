import sys
import time

import cupy as cp
import numpy as np

import pixtreme as px
from pixtreme.transform.schema import INTER_AREA2


def benchmark_resize(image, new_size, interpolation, num_iterations=10, warmup=3):
    """Benchmark resize operation"""
    # Warmup
    for _ in range(warmup):
        _ = px.resize(image, new_size, interpolation=interpolation)
    cp.cuda.Stream.null.synchronize()

    # Benchmark
    times = []
    result = None
    for _ in range(num_iterations):
        cp.cuda.Stream.null.synchronize()
        start = time.time()
        result = px.resize(image, new_size, interpolation=interpolation)
        cp.cuda.Stream.null.synchronize()
        elapsed = time.time() - start
        times.append(elapsed)

    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)

    return avg_time, std_time, min_time, max_time, result


def test_area2_correctness():
    """Test that INTER_AREA2 produces correct results"""
    print("=== Testing INTER_AREA2 Correctness ===\n")

    # Test image sizes
    test_cases = [
        (1024, 512, 512, 256),  # 2x downsampling
        (1536, 768, 1024, 512),  # 1.5x downsampling
        (3072, 1536, 2048, 1024),  # 1.5x downsampling
    ]

    for h_in, w_in, h_out, w_out in test_cases:
        print(f"Testing {h_in}x{w_in} → {h_out}x{w_out}")

        # Create test image
        test_image = cp.random.rand(h_in, w_in, 3).astype(cp.float32)

        # Test both methods
        result_area = px.resize(test_image, (w_out, h_out), interpolation=px.INTER_AREA)
        result_area2 = px.resize(test_image, (w_out, h_out), interpolation=INTER_AREA2)

        # Compare results
        diff = cp.abs(result_area - result_area2)
        max_diff = cp.max(diff).get()
        mean_diff = cp.mean(diff).get()

        print(f"  Max difference: {max_diff:.6f}")
        print(f"  Mean difference: {mean_diff:.6f}")

        if max_diff < 0.001:
            print("  ✓ Results match (within tolerance)")
        else:
            print("  ✗ Results differ significantly!")
        print()


def benchmark_performance():
    """Benchmark INTER_AREA vs INTER_AREA2"""
    print("\n=== Performance Benchmark ===\n")

    test_configs = [
        # (height, width, new_height, new_width, description)
        (2048, 4096, 1024, 2048, "2K→1K (2x downsampling)"),
        (3072, 6144, 2048, 4096, "3K→2K (1.5x downsampling)"),
        (6144, 12288, 4096, 8192, "6K→4K (1.5x downsampling)"),
        (12288, 6144, 8192, 4096, "12Kx6K→8Kx4K (Real use case)"),
    ]

    for h_in, w_in, h_out, w_out, desc in test_configs:
        print(f"{'=' * 60}")
        print(f"{desc}: {h_in}x{w_in} → {h_out}x{w_out}")
        print(f"Input size: {h_in * w_in * 3 * 4 / 1024 / 1024:.1f} MB")
        print(f"Output size: {h_out * w_out * 3 * 4 / 1024 / 1024:.1f} MB")
        print(f"{'=' * 60}")

        # Create test image
        test_image = cp.random.rand(h_in, w_in, 3).astype(cp.float32)

        # Benchmark INTER_AREA
        avg_area, std_area, min_area, max_area, _ = benchmark_resize(
            test_image, (w_out, h_out), px.INTER_AREA, num_iterations=100
        )

        # Benchmark INTER_AREA2
        avg_area2, std_area2, min_area2, max_area2, _ = benchmark_resize(
            test_image, (w_out, h_out), INTER_AREA2, num_iterations=100
        )

        # Calculate speedup
        speedup = avg_area / avg_area2

        # Calculate memory bandwidth
        total_bytes_read = h_in * w_in * 3 * 4  # Input
        total_bytes_write = h_out * w_out * 3 * 4  # Output
        total_bytes = total_bytes_read + total_bytes_write

        bandwidth_area = total_bytes / avg_area / 1e9
        bandwidth_area2 = total_bytes / avg_area2 / 1e9

        # Print results
        print(f"\nINTER_AREA:")
        print(f"  Average: {avg_area * 1000:.2f} ms (±{std_area * 1000:.2f} ms)")
        print(f"  Min/Max: {min_area * 1000:.2f} / {max_area * 1000:.2f} ms")
        print(f"  Bandwidth: {bandwidth_area:.1f} GB/s")

        print(f"\nINTER_AREA2:")
        print(f"  Average: {avg_area2 * 1000:.2f} ms (±{std_area2 * 1000:.2f} ms)")
        print(f"  Min/Max: {min_area2 * 1000:.2f} / {max_area2 * 1000:.2f} ms")
        print(f"  Bandwidth: {bandwidth_area2:.1f} GB/s")

        print(f"\nSpeedup: {speedup:.2f}x")

        if speedup > 1.1:
            print("🏆 INTER_AREA2 is faster!")
        elif speedup < 0.9:
            print("❌ INTER_AREA2 is slower")
        else:
            print("≈ Performance is similar")

        print()

        # Clear memory
        del test_image
        cp.get_default_memory_pool().free_all_blocks()


def test_real_world_workflow():
    """Test the real-world workflow with INTER_AREA2"""
    print("\n=== Real World Workflow Test ===")
    print("Simulating: subsample → upscale → subsample_back → resize\n")

    # Create 6144x3072 input
    input_h, input_w = 6144, 3072
    input_image = cp.random.rand(input_h, input_w, 3).astype(cp.float32)

    # Step 1: Subsample
    start = time.time()
    subsampled = px.subsample_image(input_image, dim=2)
    cp.cuda.Stream.null.synchronize()
    subsample_time = time.time() - start
    print(f"1. Subsample: {subsample_time * 1000:.2f} ms")

    # Step 2: Simulate 4x upscale (simple repeat for testing)
    start = time.time()
    upscaled = []
    for img in subsampled:
        upscaled.append(cp.repeat(cp.repeat(img, 4, axis=0), 4, axis=1))
    cp.cuda.Stream.null.synchronize()
    upscale_time = time.time() - start
    print(f"2. Upscale 4x: {upscale_time * 1000:.2f} ms")

    # Step 3: Reconstruct
    start = time.time()
    reconstructed = px.subsample_image_back(upscaled, dim=2)
    cp.cuda.Stream.null.synchronize()
    reconstruct_time = time.time() - start
    print(f"3. Reconstruct: {reconstruct_time * 1000:.2f} ms")
    print(f"   Output shape: {reconstructed.shape}")

    # Step 4: Resize with both methods
    target_size = (8192, 4096)

    # INTER_AREA
    start = time.time()
    final_area = px.resize(reconstructed, target_size, interpolation=px.INTER_AREA)
    cp.cuda.Stream.null.synchronize()
    resize_area_time = time.time() - start

    # INTER_AREA2
    start = time.time()
    final_area2 = px.resize(reconstructed, target_size, interpolation=INTER_AREA2)
    cp.cuda.Stream.null.synchronize()
    resize_area2_time = time.time() - start

    print(f"\n4. Resize {reconstructed.shape[1]}x{reconstructed.shape[0]} → {target_size[0]}x{target_size[1]}:")
    print(f"   INTER_AREA:  {resize_area_time * 1000:.2f} ms")
    print(f"   INTER_AREA2: {resize_area2_time * 1000:.2f} ms")
    print(f"   Speedup: {resize_area_time / resize_area2_time:.2f}x")

    # Total time comparison
    total_area = subsample_time + upscale_time + reconstruct_time + resize_area_time
    total_area2 = subsample_time + upscale_time + reconstruct_time + resize_area2_time

    print(f"\nTotal workflow time:")
    print(f"  With INTER_AREA:  {total_area:.2f} s")
    print(f"  With INTER_AREA2: {total_area2:.2f} s")
    print(f"  Time saved: {(total_area - total_area2) * 1000:.1f} ms")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Get GPU info
    print("GPU Information:")
    props = cp.cuda.runtime.getDeviceProperties(0)
    print(f"  Device: {props['name'].decode()}")
    print(f"  Memory: {props['totalGlobalMem'] / 1024**3:.1f} GB")
    print()

    # Run tests
    test_area2_correctness()
    benchmark_performance()
    test_real_world_workflow()
