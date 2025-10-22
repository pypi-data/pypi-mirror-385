import timeit

import cupy as cp

import pixtreme_source as px

itr = 100
dim = 4


def pixel_shift_inverse_vectorized(input_tensor, dim):
    """
    さらに効率的な方法: 完全にベクトル化
    input_tensor: (N, C, H, W) where N = dim²
    output: (1, C, H*dim, W*dim)
    """
    N, C, H, W = input_tensor.shape
    assert N == dim * dim

    # reshapeとtransposeを使用した効率的な実装
    # (N, C, H, W) -> (dim, dim, C, H, W)
    reshaped = input_tensor.reshape(dim, dim, C, H, W)

    # (dim, dim, C, H, W) -> (C, H, dim, W, dim)
    transposed = reshaped.transpose(2, 3, 0, 4, 1)

    # (C, H, dim, W, dim) -> (1, C, H*dim, W*dim)
    output = transposed.reshape(1, C, H * dim, W * dim)

    return output


def test_subsample_image(image_path: str):
    print(f"Testing subsample_image with dim={dim} on image: {image_path}")

    upscaler = px.TorchUpscaler(model_path="models/4xNomosUni_span_multijpg.pth")

    original_image = px.imread(image_path)
    original_image = px.to_float32(original_image)  # float32に変換

    print(f"Original image shape: {original_image.shape}")
    print(f"Original image dtype: {original_image.dtype}")
    px.imshow("Original Image", original_image)

    test_image = original_image.copy()  # Keep original for reconstruction
    test_image = px.resize(
        test_image, (test_image.shape[1] * upscaler.scale, test_image.shape[0] * upscaler.scale), interpolation=px.INTER_AUTO
    )

    print(f"Test image shape after resize: {test_image.shape}")
    print(f"Test image dtype after resize: {test_image.dtype}")
    px.imshow("Test Image", test_image)

    results = []

    start = timeit.default_timer()
    for _ in range(itr):
        results = px.subsample_image(test_image, dim=upscaler.scale)
    end = timeit.default_timer()
    print(f"Subsampled image (reshape) time: {end - start:.4f} seconds")
    print(f"Subsampled images time per iteration: {(end - start) / itr:.4f} seconds")

    print(f"Subsampled images count: {len(results)}")

    for i, subsampled in enumerate(results):
        print(f"Subsampled image {i} shape: {subsampled.shape}")
        print(f"Subsampled image {i} dtype: {subsampled.dtype}")
        # px.imshow(f"Subsampled Image{i}", subsampled)
        results[i] = upscaler.get(subsampled)

    reconstructed_image = None
    start = timeit.default_timer()
    for _ in range(itr):
        reconstructed_image = px.subsample_image_back(results, dim=upscaler.scale)
    end = timeit.default_timer()
    print(f"Reconstructed image time: {end - start:.4f} seconds")

    vec_reconstructed_batch = None
    results_batch = px.images_to_batch(results)
    start = timeit.default_timer()
    for _ in range(itr):
        vec_reconstructed_batch = pixel_shift_inverse_vectorized(results_batch, dim=upscaler.scale)
    end = timeit.default_timer()
    print(f"Vectorized reconstruction time: {end - start:.4f} seconds")

    vec_reconstructed_images = px.batch_to_images(vec_reconstructed_batch)

    assert reconstructed_image is not None, "Reconstruction failed"
    assert vec_reconstructed_images is not None, "Vectorized reconstruction failed"

    scaled_image = px.resize(
        reconstructed_image,
        (
            reconstructed_image.shape[1] // upscaler.scale,
            reconstructed_image.shape[0] // upscaler.scale,
        ),
        interpolation=px.INTER_LINEAR,
    )
    print(f"Scaled image shape: {scaled_image.shape}")
    print(f"Scaled image dtype: {scaled_image.dtype}")

    vec_reconstructed_image = vec_reconstructed_images[0]  # Assuming we want the first image from the batch
    vec_scaled_image = px.resize(
        vec_reconstructed_image,
        (
            vec_reconstructed_image.shape[1] // upscaler.scale,
            vec_reconstructed_image.shape[0] // upscaler.scale,
        ),
        interpolation=px.INTER_LINEAR,
    )

    px.imshow("Reconstructed Image", reconstructed_image)
    px.imshow("Reconstructed Scaled Image", scaled_image)
    px.imshow("Vectorized Reconstructed Image", vec_reconstructed_image)
    px.imshow("Vectorized Scaled Image", vec_scaled_image)

    px.waitkey(0)  # Wait for a key press to close the images
    px.destroy_all_windows()  # Close all image windows


if __name__ == "__main__":
    test_subsample_image("examples/example.png")
