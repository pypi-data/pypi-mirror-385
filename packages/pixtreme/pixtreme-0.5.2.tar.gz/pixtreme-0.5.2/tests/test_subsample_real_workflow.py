import sys
import time

import cupy as cp
import numpy as np

from pixtreme.transform.subsample import subsample_image, subsample_image_back
from pixtreme.transform.subsample_optimized_v2 import subsample_image_back_shared, subsample_image_back_vectorized


def simulate_upscale_4x(image):
    """Simulate 4x upscaling (using simple bilinear for testing)"""
    h, w = image.shape[:2]
    if image.ndim == 2:
        # Grayscale
        return cp.repeat(cp.repeat(image, 4, axis=0), 4, axis=1)
    else:
        # Color
        return cp.repeat(cp.repeat(image, 4, axis=0), 4, axis=1)


def measure_with_sync(func, args):
    """Measure function execution time with proper GPU synchronization"""
    cp.cuda.Stream.null.synchronize()
    start = time.time()
    result = func(*args)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.time() - start
    return elapsed, result


def real_workflow_test():
    """Test the actual workflow: subsample -> upscale -> subsample_back"""
    print("=== Real Workflow Performance Test ===")
    print("Workflow: 6144x3072 → subsample(dim=2) → 4x3072x1536 → 4x upscale → 4x12288x6144 → subsample_back → 12288x6144\n")

    # Initial parameters
    input_h, input_w = 6144, 3072
    channels = 3
    dim = 2
    upscale_factor = 4

    # Create test input image
    print(f"1. Creating input image ({input_h}x{input_w}x{channels})...")
    start = time.time()
    input_image = cp.random.rand(input_h, input_w, channels).astype(cp.float32)
    cp.cuda.Stream.null.synchronize()
    print(f"   Time: {(time.time() - start) * 1000:.2f} ms")
    print(f"   Size: {input_image.nbytes / 1024 / 1024:.1f} MB")

    # Step 1: Subsample
    print(f"\n2. Subsampling with dim={dim}...")
    time_subsample, subsampled_images = measure_with_sync(subsample_image, (input_image, dim))
    print(f"   Time: {time_subsample * 1000:.2f} ms")
    print(f"   Output: {len(subsampled_images)} images of {subsampled_images[0].shape}")
    print(f"   Total size: {sum(img.nbytes for img in subsampled_images) / 1024 / 1024:.1f} MB")

    # Step 2: Upscale each subsampled image
    print(f"\n3. Upscaling each image by {upscale_factor}x...")
    upscaled_images = []
    total_upscale_time = 0

    for i, img in enumerate(subsampled_images):
        start = time.time()
        upscaled = simulate_upscale_4x(img)
        cp.cuda.Stream.null.synchronize()
        upscale_time = time.time() - start
        total_upscale_time += upscale_time
        upscaled_images.append(upscaled)
        print(f"   Image {i + 1}: {img.shape} → {upscaled.shape} ({upscale_time * 1000:.2f} ms)")

    print(f"   Total upscale time: {total_upscale_time * 1000:.2f} ms")
    print(f"   Total size after upscale: {sum(img.nbytes for img in upscaled_images) / 1024 / 1024:.1f} MB")

    # Step 3: Reconstruct with different implementations
    print(f"\n4. Reconstructing with subsample_image_back...")

    implementations = [
        ("Original", subsample_image_back),
        ("Shared Memory", subsample_image_back_shared),
        ("Vectorized", subsample_image_back_vectorized),
    ]

    results = {}

    for name, func in implementations:
        print(f"\n   {name} implementation:")

        # Warmup
        print("     Warming up...", end="", flush=True)
        for _ in range(3):
            _ = func(upscaled_images, dim)
        cp.cuda.Stream.null.synchronize()
        print(" done")

        # Measure multiple runs
        times = []
        output_shape = None
        output_nbytes = None
        print("     Running 10 iterations:")
        for i in range(10):
            time_taken, output = measure_with_sync(func, (upscaled_images, dim))
            times.append(time_taken)
            print(f"       Iteration {i + 1:2d}: {time_taken * 1000:8.2f} ms")

            # Save output info from first iteration
            if i == 0:
                output_shape = output.shape
                output_nbytes = output.nbytes

        # Statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_time = np.std(times)

        results[name] = {"avg": avg_time, "min": min_time, "max": max_time, "std": std_time, "output_shape": output_shape}

        # Performance metrics
        output_size_mb = output_nbytes / 1024 / 1024 if output_nbytes else 0
        bandwidth = output_nbytes / avg_time / 1e9 if output_nbytes else 0

        print(f"     Output shape: {output_shape}")
        print(f"     Output size: {output_size_mb:.1f} MB")
        print(f"     Average time: {avg_time * 1000:.2f} ms (±{std_time * 1000:.2f} ms)")
        print(f"     Min/Max: {min_time * 1000:.2f} / {max_time * 1000:.2f} ms")
        print(f"     Memory bandwidth: {bandwidth:.1f} GB/s")

    # Summary
    print(f"\n{'=' * 60}")
    print("PERFORMANCE SUMMARY")
    print(f"{'=' * 60}")

    # Total workflow time
    print("\nTotal workflow time (excluding upscale):")
    for name, data in results.items():
        total_time = time_subsample + data["avg"]
        fps = 1.0 / total_time
        print(f"  {name:15s}: {total_time * 1000:7.2f} ms ({fps:.2f} FPS)")

    # Reconstruction comparison
    print("\nReconstruction performance comparison:")
    baseline = results["Original"]["avg"]
    for name, data in results.items():
        speedup = baseline / data["avg"]
        print(f"  {name:15s}: {data['avg'] * 1000:7.2f} ms ({speedup:5.2f}x)")

    # Find winner
    winner = min(results.items(), key=lambda x: x[1]["avg"])[0]
    print(f"\n🏆 Best reconstruction: {winner} ({results[winner]['avg'] * 1000:.2f} ms)")

    # Memory usage
    mempool = cp.get_default_memory_pool()
    print(f"\nPeak GPU memory usage: {mempool.total_bytes() / 1024 / 1024:.1f} MB")


def detailed_timing_breakdown():
    """Detailed timing breakdown for each step"""
    print("\n\n=== Detailed Timing Breakdown ===")

    # Test with multiple runs for stability
    num_runs = 5

    input_h, input_w = 6144, 3072
    channels = 3
    dim = 2

    print(f"Averaging over {num_runs} runs...")

    # Store timing for each run
    subsample_times = []
    reconstruction_times = {"Original": [], "Shared Memory": [], "Vectorized": []}

    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}:")

        # Create input
        input_image = cp.random.rand(input_h, input_w, channels).astype(cp.float32)

        # Subsample
        time_sub, subsampled = measure_with_sync(subsample_image, (input_image, dim))
        subsample_times.append(time_sub)
        print(f"  Subsample: {time_sub * 1000:.2f} ms")

        # Upscale
        upscaled = [simulate_upscale_4x(img) for img in subsampled]

        # Reconstruction
        for name, func in [
            ("Original", subsample_image_back),
            ("Shared Memory", subsample_image_back_shared),
            ("Vectorized", subsample_image_back_vectorized),
        ]:
            time_recon, _ = measure_with_sync(func, (upscaled, dim))
            reconstruction_times[name].append(time_recon)
            print(f"  {name}: {time_recon * 1000:.2f} ms")

    # Calculate averages
    print(f"\n{'=' * 50}")
    print("AVERAGE TIMING BREAKDOWN")
    print(f"{'=' * 50}")

    avg_subsample = np.mean(subsample_times)
    print(f"\nSubsample (dim={dim}): {avg_subsample * 1000:.2f} ± {np.std(subsample_times) * 1000:.2f} ms")

    print("\nReconstruction (subsample_back):")
    for name, times in reconstruction_times.items():
        avg = np.mean(times)
        std = np.std(times)
        print(f"  {name:15s}: {avg * 1000:.2f} ± {std * 1000:.2f} ms")

    # Best overall workflow
    print("\nBest workflow combination:")
    avg_times = {name: float(np.mean(times)) for name, times in reconstruction_times.items()}
    best_recon_name = min(avg_times, key=lambda k: avg_times[k])
    best_recon_time = avg_times[best_recon_name]
    total_time = avg_subsample + best_recon_time
    fps = 1.0 / total_time

    print(f"  Subsample + {best_recon_name}: {total_time * 1000:.2f} ms total")
    print(f"  Achievable FPS: {fps:.2f}")


if __name__ == "__main__":
    # Set GPU device
    cp.cuda.Device(0).use()

    # Get GPU info
    print("GPU Information:")
    props = cp.cuda.runtime.getDeviceProperties(0)
    print(f"  Device: {props['name'].decode()}")
    print(f"  Memory: {props['totalGlobalMem'] / 1024**3:.1f} GB")
    print(f"  Compute Capability: {props['major']}.{props['minor']}")
    print()

    # Run tests
    real_workflow_test()
    detailed_timing_breakdown()
