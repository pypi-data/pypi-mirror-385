import sys
import time

import cupy as cp
import numpy as np

import pixtreme as px
from pixtreme.transform.schema import INTER_AREA


def benchmark_resize_detailed(image, new_size, interpolation, num_iterations=10, warmup=3):
    """Detailed benchmark with individual iteration times"""
    # Warmup
    for _ in range(warmup):
        _ = px.resize(image, new_size, interpolation=interpolation)
    cp.cuda.Stream.null.synchronize()

    # Benchmark
    times = []
    for i in range(num_iterations):
        cp.cuda.Stream.null.synchronize()
        start = time.time()
        result = px.resize(image, new_size, interpolation=interpolation)
        cp.cuda.Stream.null.synchronize()
        elapsed = time.time() - start
        times.append(elapsed)
        if i < 5:  # Print first 5 iterations
            print(f"      Iter {i + 1}: {elapsed * 1000:.2f} ms")

    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)

    return avg_time, std_time, min_time, max_time


def test_ultra_high_res_workflow():
    """Test ultra high resolution workflow scenarios"""
    print("=== Ultra High Resolution Workflow Tests ===\n")

    # Test scenarios based on real workflows
    test_scenarios = [
        # (input_h, input_w, scale_factor, target_h, target_w, description)
        (6144, 3072, 4, 8192, 4096, "Standard 6K→8K workflow"),
        (8192, 4096, 4, 16384, 8192, "8K→16K workflow"),
        (12288, 6144, 2, 12288, 6144, "12K workflow (2x upscale)"),
        (16384, 8192, 2, 16384, 8192, "16K workflow (2x upscale)"),
        (24576, 12288, 1, 16384, 8192, "24K→16K (downscale only)"),
        (32768, 16384, 1, 16384, 8192, "32K→16K (extreme downscale)"),
    ]

    for input_h, input_w, scale_factor, target_h, target_w, desc in test_scenarios:
        print(f"\n{'=' * 70}")
        print(f"{desc}")
        print(f"Input: {input_h}x{input_w} → Upscale {scale_factor}x → Output: {target_h}x{target_w}")
        print(f"{'=' * 70}")

        try:
            # Step 1: Create input image
            print(f"\n1. Creating {input_h}x{input_w} input image...")
            start = time.time()
            input_image = cp.random.rand(input_h, input_w, 3).astype(cp.float32)
            cp.cuda.Stream.null.synchronize()
            create_time = time.time() - start
            print(f"   Time: {create_time * 1000:.2f} ms")
            print(f"   Size: {input_image.nbytes / 1024 / 1024:.1f} MB")

            # Step 2: Subsample (if scale_factor > 1)
            if scale_factor > 1:
                print(f"\n2. Subsampling with dim=2...")
                start = time.time()
                subsampled = px.subsample_image(input_image, dim=2)
                cp.cuda.Stream.null.synchronize()
                subsample_time = time.time() - start
                print(f"   Time: {subsample_time * 1000:.2f} ms")
                print(f"   Output: {len(subsampled)} images of {subsampled[0].shape}")

                # Step 3: Upscale
                print(f"\n3. Upscaling {scale_factor}x...")
                start = time.time()
                upscaled = []
                for img in subsampled:
                    # Simple repeat upscaling for testing
                    upscaled.append(cp.repeat(cp.repeat(img, scale_factor, axis=0), scale_factor, axis=1))
                cp.cuda.Stream.null.synchronize()
                upscale_time = time.time() - start
                print(f"   Time: {upscale_time * 1000:.2f} ms")

                # Step 4: Reconstruct
                print(f"\n4. Reconstructing...")
                start = time.time()
                reconstructed = px.subsample_image_back(upscaled, dim=2)
                cp.cuda.Stream.null.synchronize()
                reconstruct_time = time.time() - start
                print(f"   Time: {reconstruct_time * 1000:.2f} ms")
                print(f"   Output shape: {reconstructed.shape}")
            else:
                # No upscaling, just use input
                reconstructed = input_image
                subsample_time = upscale_time = reconstruct_time = 0

            # Step 5: Final resize comparison
            print(f"\n5. Final resize {reconstructed.shape[1]}x{reconstructed.shape[0]} → {target_w}x{target_h}:")

            # Clear GPU cache
            cp.get_default_memory_pool().free_all_blocks()

            # INTER_AREA
            print("\n   INTER_AREA:")
            avg_area, std_area, min_area, max_area = benchmark_resize_detailed(
                reconstructed, (target_w, target_h), px.INTER_AREA, num_iterations=10
            )
            print(f"   Average: {avg_area * 1000:.2f} ms (±{std_area * 1000:.2f} ms)")

            # INTER_LINEAR
            print("\n   INTER_LINEAR:")
            avg_area2, std_area2, min_area2, max_area2 = benchmark_resize_detailed(
                reconstructed, (target_w, target_h), px.INTER_LINEAR, num_iterations=10
            )
            print(f"   Average: {avg_area2 * 1000:.2f} ms (±{std_area2 * 1000:.2f} ms)")

            # Results
            speedup = avg_area / avg_area2
            print(f"\n   Speedup: {speedup:.2f}x")
            if speedup > 1.1:
                print("   🏆 INTER_LINEAR is significantly faster!")
            elif speedup < 0.9:
                print("   ❌ INTER_LINEAR is significantly slower")
            else:
                print("   ≈ Performance is similar")

            # Total workflow time
            if scale_factor > 1:
                total_area = subsample_time + upscale_time + reconstruct_time + avg_area
                total_area2 = subsample_time + upscale_time + reconstruct_time + avg_area2
            else:
                total_area = avg_area
                total_area2 = avg_area2

            print(f"\n   Total workflow time:")
            print(f"   - With INTER_AREA:  {total_area * 1000:.2f} ms")
            print(f"   - With INTER_AREA2: {total_area2 * 1000:.2f} ms")
            print(f"   - Time saved: {(total_area - total_area2) * 1000:.2f} ms")

            # Memory info
            mempool = cp.get_default_memory_pool()
            print(f"\n   GPU memory used: {mempool.used_bytes() / 1024 / 1024:.1f} MB")

            # Clean up
            del input_image, reconstructed
            if scale_factor > 1 and "subsampled" in locals():
                del subsampled
            if scale_factor > 1 and "upscaled" in locals():
                del upscaled
            cp.get_default_memory_pool().free_all_blocks()

        except cp.cuda.memory.OutOfMemoryError:
            print("\n   ❌ Out of GPU memory!")
        except Exception as e:
            print(f"\n   ❌ Error: {e}")


def test_specific_sizes():
    """Test specific size combinations that might show differences"""
    print("\n\n=== Specific Size Tests ===\n")

    # Specific sizes where differences might be more pronounced
    test_sizes = [
        # (height, width, new_height, new_width, description)
        (512, 512, 128, 128, "512*512 → 128*128 (1/4 downscale)"),
        (512, 512, 256, 256, "512*512 → 256*256 (1/2 downscale)"),
        (512, 512, 768, 768, "512*512 → 768*768 (1.5x upscale)"),
        (512, 512, 1024, 1024, "512*512 → 1024*1024 (2x upscale)"),
        (512, 512, 1536, 1536, "512*512 → 1536*1536 (3x upscale)"),
        (512, 512, 2048, 2048, "512*512 → 2048*2048 (4x upscale)"),
        (1024, 1024, 256, 256, "1K*1K → 256*256 (1/4 downscale)"),
        (1024, 1024, 512, 512, "1K*1K → 512*512 (1/2 downscale)"),
        (1024, 1024, 1536, 1536, "1K*1K → 1.5K*1.5K (1.5x upscale)"),
        (1024, 1024, 2048, 2048, "1K*1K → 2K*2K (2x upscale)"),
        (1024, 1024, 3072, 3072, "1K*1K → 3K*3K (3x upscale)"),
        (1024, 1024, 4096, 4096, "1K*1K → 4K*4K (4x upscale)"),
        (1920, 1080, 480, 270, "HD 16:9 → 480p (1/4 downscale)"),
        (1920, 1080, 960, 540, "HD 16:9 → 540p (1/2 downscale)"),
        (1920, 1080, 1280, 720, "HD 16:9 → HD (720p) (2/3 downscale)"),
        (1920, 1080, 2560, 1440, "HD 16:9 → QHD (1.33x upscale)"),
        (1920, 1080, 3840, 2160, "HD 16:9 → 4K (2x upscale)"),
        (1920, 1080, 5760, 3240, "HD 16:9 → 6K (3x upscale)"),
        (1920, 1080, 7680, 4320, "HD 16:9 → 8K (4x upscale)"),
        (3840, 2160, 960, 540, "4K → 540p (1/4 downscale)"),
        (3840, 2160, 1920, 1080, "4K → HD (1/2 downscale)"),
        (3840, 2160, 2560, 1440, "4K → QHD (2/3 downscale)"),
        (3840, 2160, 5120, 2880, "4K → 5K (1.33x upscale)"),
        (3840, 2160, 7680, 4320, "4K → 8K (2x upscale)"),
        (3840, 2160, 11520, 6480, "4K → 12K (3x upscale)"),
        (3840, 2160, 15360, 8640, "4K → 16K (4x upscale)"),
        (4096, 2048, 1024, 512, "4K*2K → 1K*512 (1/4 downscale)"),
        (4096, 2048, 2048, 1024, "4K*2K → 2K*1K (1/2 downscale)"),
        (4096, 2048, 3072, 1536, "4K*2K → 3K*1.5K (3/4 downscale)"),
        (4096, 2048, 6144, 3072, "4K*2K → 6K*3K (1.5x upscale)"),
        (4096, 2048, 8192, 4096, "4K*2K → 8K*4K (2x upscale)"),
        (4096, 2048, 12288, 6144, "4K*2K → 12K*6K (3x upscale)"),
        (4096, 2048, 16384, 8192, "4K*2K → 16K*8K (4x upscale)"),
        (7680, 4320, 1920, 1080, "8K → HD (1/4 downscale)"),
        (7680, 4320, 3840, 2160, "8K → 4K (1/2 downscale)"),
        (7680, 4320, 5120, 2880, "8K → 5K (2/3 downscale)"),
        (7680, 4320, 11520, 6480, "8K → 12K (1.33x upscale)"),
        (7680, 4320, 15360, 8640, "8K → 16K (2x upscale)"),
        (7680, 4320, 23040, 12960, "8K → 24K (3x upscale)"),
        (12288, 6144, 6144, 3072, "12K*6K → 6K*3K (1/2 downscale)"),
        (12288, 6144, 8192, 4096, "12K*6K → 8K*4K (2/3 downscale)"),
        (12288, 6144, 15360, 7680, "12K*6K → 15K*7.5K (1.25x upscale)"),
        (12288, 6144, 16384, 8192, "12K*6K → 16K*8K (1.33x upscale)"),
        (12288, 6144, 24576, 12288, "12K*6K → 24K*12K (2x upscale)"),
        (16384, 8192, 8192, 4096, "16K*8K → 8K*4K (1/2 downscale)"),
        (16384, 8192, 12288, 6144, "16K*8K → 12K*6K (3/4 downscale)"),
        (16384, 8192, 20480, 10240, "16K*8K → 20K*10K (1.25x upscale)"),
        (16384, 8192, 24576, 12288, "16K*8K → 24K*12K (1.5x upscale)"),
        (24576, 12288, 12288, 6144, "24K*12K → 12K*6K (1/2 downscale)"),
        (24576, 12288, 18432, 9216, "24K*12K → 18K*9K (3/4 downscale)"),
        (24576, 12288, 30720, 15360, "24K*12K → 30K*15K (1.25x upscale)"),
        (32768, 16384, 16384, 8192, "32K*16K → 16K*8K (1/2 downscale)"),
        (32768, 16384, 24576, 12288, "32K*16K → 24K*12K (3/4 downscale)"),
    ]

    for h_in, w_in, h_out, w_out, desc in test_sizes:
        print(f"\n{'=' * 60}")
        print(f"{desc}")
        print(f"Input: {h_in}x{w_in} ({h_in * w_in * 3 * 4 / 1024 / 1024 / 1024:.2f} GB)")
        print(f"Output: {h_out}x{w_out} ({h_out * w_out * 3 * 4 / 1024 / 1024 / 1024:.2f} GB)")
        print(f"{'=' * 60}")

        try:
            # Create test image
            print("\nCreating test image...")
            test_image = cp.random.rand(h_in, w_in, 3).astype(cp.float32)

            # Benchmark both methods
            print("\nBenchmarking (5 iterations):")

            # INTER_AREA
            print("\nINTER_AREA:")
            times_area = []
            for i in range(5):
                cp.cuda.Stream.null.synchronize()
                start = time.time()
                _ = px.resize(test_image, (w_out, h_out), interpolation=px.INTER_AREA)
                cp.cuda.Stream.null.synchronize()
                elapsed = time.time() - start
                times_area.append(elapsed)
                print(f"  Iter {i + 1}: {elapsed * 1000:.2f} ms")
            avg_area = np.mean(times_area)

            # INTER_AREA2
            print("\nINTER_AREA2:")
            times_area2 = []
            for i in range(5):
                cp.cuda.Stream.null.synchronize()
                start = time.time()
                _ = px.resize(test_image, (w_out, h_out), interpolation=px.INTER_LINEAR)
                cp.cuda.Stream.null.synchronize()
                elapsed = time.time() - start
                times_area2.append(elapsed)
                print(f"  Iter {i + 1}: {elapsed * 1000:.2f} ms")
            avg_area2 = np.mean(times_area2)

            # Results
            speedup = avg_area / avg_area2
            print(f"\nResults:")
            print(f"  INTER_AREA average:  {avg_area * 1000:.2f} ms")
            print(f"  INTER_LINEAR average: {avg_area2 * 1000:.2f} ms")
            print(f"  Speedup: {speedup:.2f}x")

            if speedup > 1.2:
                print("  🏆 INTER_LINEAR shows significant improvement!")

            # Clean up
            del test_image
            cp.get_default_memory_pool().free_all_blocks()

        except cp.cuda.memory.OutOfMemoryError:
            print("\n❌ Out of GPU memory!")
        except Exception as e:
            print(f"\n❌ Error: {e}")


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
    test_ultra_high_res_workflow()
    test_specific_sizes()
