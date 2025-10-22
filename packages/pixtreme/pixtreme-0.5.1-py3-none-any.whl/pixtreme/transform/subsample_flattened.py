import cupy as cp
import numpy as np

# シンプルなコピーカーネル
simple_copy_kernel_code = r"""
extern "C" __global__ void simple_copy_kernel(
    const float* __restrict__ input,
    float* __restrict__ output,
    const int total_elements
) {
    const int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= total_elements) return;
    
    // 単純なメモリコピー
    output[tid] = input[tid];
}
"""

simple_copy_kernel = cp.RawKernel(simple_copy_kernel_code, "simple_copy_kernel")


def create_output_order_indices(batch_shape, dim):
    """出力順序に合わせたインデックスマップを作成"""
    N, C, H, W = batch_shape
    output_height = H * dim
    output_width = W * dim

    # 出力のHWC形式での各位置に対応する入力のインデックスを計算
    indices = np.zeros(output_height * output_width * C, dtype=np.int64)

    idx = 0
    for y in range(output_height):
        for x in range(output_width):
            for c in range(C):
                # 出力位置から入力位置を計算
                dy = y % dim
                dx = x % dim
                subsample_idx = dy * dim + dx
                y_in = y // dim
                x_in = x // dim

                # NCHW形式でのインデックス
                input_idx = subsample_idx * C * H * W + c * H * W + y_in * W + x_in

                indices[idx] = input_idx
                idx += 1

    return cp.asarray(indices)


# インデックスマップのキャッシュ
_index_cache = {}


def subsample_image_back_flattened(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """1次元化による最適化版のsubsample_image_back

    Args:
        subsampled_images: Batch tensor with shape (N, C, H, W) where N = dim*dim or a list of images[H, W, C].
        dim: Block size used in the original subsampling

    Returns:
        Reconstructed image with shape (H*dim, W*dim, C)
    """

    # バッチ形式に変換
    if isinstance(subsampled_images, list):
        first = subsampled_images[0]
        if first.ndim == 2:
            batch = cp.stack([img[cp.newaxis, :, :] for img in subsampled_images], axis=0)
        else:
            batch = cp.stack([img.transpose(2, 0, 1) for img in subsampled_images], axis=0)
    else:
        batch = subsampled_images

    if batch.ndim != 4:
        raise ValueError("Input must be 4D tensor in NCHW format")

    batch_size, channels, input_height, input_width = batch.shape

    if batch_size != dim * dim:
        raise ValueError(f"Batch size {batch_size} doesn't match dim*dim = {dim * dim}")

    # Ensure contiguous float32
    if batch.dtype != cp.float32:
        batch = batch.astype(cp.float32)
    batch = cp.ascontiguousarray(batch)

    # Output dimensions
    output_height = input_height * dim
    output_width = input_width * dim
    total_elements = output_height * output_width * channels

    # インデックスマップを取得（キャッシュから or 新規作成）
    cache_key = (batch_size, channels, input_height, input_width, dim)
    if cache_key not in _index_cache:
        indices = create_output_order_indices((batch_size, channels, input_height, input_width), dim)
        _index_cache[cache_key] = indices
    else:
        indices = _index_cache[cache_key]

    # 入力データを1次元化
    flattened_input = batch.ravel()

    # 出力順序に並べ替え
    reordered_input = flattened_input[indices]

    # 出力バッファを確保
    output = cp.empty(total_elements, dtype=cp.float32)

    # シンプルなコピーカーネルを実行
    block_size = 256
    grid_size = (total_elements + block_size - 1) // block_size

    simple_copy_kernel((grid_size,), (block_size,), (reordered_input, output, total_elements))

    # 適切な形状にreshape
    output = output.reshape(output_height, output_width, channels)

    # Return 2D if originally grayscale
    if channels == 1:
        return output.squeeze(axis=2)

    return output


# より高度な最適化版：gather操作を使用
gather_kernel_code = r"""
extern "C" __global__ void gather_kernel(
    const float* __restrict__ input,
    float* __restrict__ output,
    const long long* __restrict__ indices,
    const int total_elements
) {
    const int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= total_elements) return;
    
    // インデックスを使用してgather操作
    output[tid] = input[indices[tid]];
}
"""

gather_kernel = cp.RawKernel(gather_kernel_code, "gather_kernel")


def subsample_image_back_gather(subsampled_images: cp.ndarray | list[cp.ndarray], dim: int) -> cp.ndarray:
    """Gather操作を使用した最適化版

    インデックスの並べ替えをせず、直接gather操作でデータを収集
    """

    # バッチ形式に変換
    if isinstance(subsampled_images, list):
        first = subsampled_images[0]
        if first.ndim == 2:
            batch = cp.stack([img[cp.newaxis, :, :] for img in subsampled_images], axis=0)
        else:
            batch = cp.stack([img.transpose(2, 0, 1) for img in subsampled_images], axis=0)
    else:
        batch = subsampled_images

    if batch.ndim != 4:
        raise ValueError("Input must be 4D tensor in NCHW format")

    batch_size, channels, input_height, input_width = batch.shape

    if batch_size != dim * dim:
        raise ValueError(f"Batch size {batch_size} doesn't match dim*dim = {dim * dim}")

    # Ensure contiguous float32
    if batch.dtype != cp.float32:
        batch = batch.astype(cp.float32)
    batch = cp.ascontiguousarray(batch)

    # Output dimensions
    output_height = input_height * dim
    output_width = input_width * dim
    total_elements = output_height * output_width * channels

    # インデックスマップを取得
    cache_key = (batch_size, channels, input_height, input_width, dim)
    if cache_key not in _index_cache:
        indices = create_output_order_indices((batch_size, channels, input_height, input_width), dim)
        _index_cache[cache_key] = indices
    else:
        indices = _index_cache[cache_key]

    # 入力データを1次元化
    flattened_input = batch.ravel()

    # 出力バッファを確保
    output = cp.empty(total_elements, dtype=cp.float32)

    # Gather操作カーネルを実行
    block_size = 256
    grid_size = (total_elements + block_size - 1) // block_size

    gather_kernel((grid_size,), (block_size,), (flattened_input, output, indices, total_elements))

    # 適切な形状にreshape
    output = output.reshape(output_height, output_width, channels)

    # Return 2D if originally grayscale
    if channels == 1:
        return output.squeeze(axis=2)

    return output
