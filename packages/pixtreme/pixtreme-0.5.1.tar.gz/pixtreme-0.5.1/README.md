# 🚀 pixtreme

> **Blazing-fast GPU-accelerated image processing for Python**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CUDA](https://img.shields.io/badge/CUDA-12.x-green.svg)](https://developer.nvidia.com/cuda-downloads)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pixtreme.svg)](https://pypi.org/project/pixtreme/)

## 🌟 Highlights

- **⚡ Lightning Fast**: CUDA-optimized kernels deliver real-time performance
- **🎨 Professional Color Pipeline**: Full ACES workflow, 3D LUTs, 10-bit precision
- **🧠 AI-Ready**: Seamless integration with ONNX, PyTorch, and TensorRT
- **🔗 Zero-Copy Interop**: DLPack support for PyTorch, TensorFlow, JAX
- **📊 Extensive Format Support**: OpenEXR, JPEG, PNG, TIFF, and more

## 📋 Table of Contents

- [Breaking Change (v0.5.1)](#️-breaking-change-v051)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Modules](#-core-modules)
- [Examples](#-examples)
- [API Reference](#-api-reference)
- [Performance](#-performance)
- [Changelog](CHANGELOG.md)
- [Contributing](#-contributing)
- [License](#-license)

## ⚠️ Breaking Change (v0.5.1)

**`_cp` functions have been removed** from the main pixtreme package in v0.5.1.

The following functions are now available only in the `pixtreme-legacy` package:
- `apply_lut_cp` → Use `apply_lut` instead
- `uyvy422_to_ycbcr444_cp` → Use `uyvy422_to_ycbcr444` instead
- `ndi_uyvy422_to_ycbcr444_cp` → Use `ndi_uyvy422_to_ycbcr444` instead
- `yuv420p_to_ycbcr444_cp` → Use `yuv420p_to_ycbcr444` instead
- `yuv422p10le_to_ycbcr444_cp` → Use `yuv422p10le_to_ycbcr444` instead

### Migration Path

**Option 1: Use pixtreme-legacy (Temporary)**:
```bash
pip install pixtreme-legacy
```

```python
from pixtreme_legacy import apply_lut_cp
result = apply_lut_cp(image, lut)  # Works without warnings
```

**Option 2: Migrate to standard functions (Recommended)**:
```python
from pixtreme import apply_lut
result = apply_lut(image, lut)  # No warning
```

### Legacy Support

If you need continued support for `_cp` functions, install `pixtreme-legacy`:
```bash
pip install pixtreme-legacy
```

See [CHANGELOG.md](CHANGELOG.md) for more details.

## ✨ Features

### 🎯 Image Processing
- **11 Interpolation Methods**: Nearest, Linear, Cubic, Area, Lanczos (2/3/4), Mitchell, B-Spline, Catmull-Rom
- **Advanced Transforms**: Affine transformations, tiling with overlap blending
- **Morphological Operations**: Erosion with custom kernels
- **GPU-Accelerated Filters**: Gaussian blur, custom convolutions

### 🎨 Color Science
- **Color Spaces**: BGR/RGB, HSV, YCbCr, YUV (4:2:0, 4:2:2), Grayscale
- **ACES Pipeline**: Complete Academy Color Encoding System workflow
- **3D LUT Processing**: Trilinear and tetrahedral interpolation
- **10-bit Precision**: Professional video color accuracy

### 🤖 Deep Learning
- **Multi-Backend Support**: ONNX Runtime, PyTorch, TensorRT
- **Super Resolution**: Built-in upscaling with various models
- **Batch Processing**: Efficient multi-image inference
- **Model Optimization**: Automatic conversion and optimization tools

### 🔧 Advanced Features
- **Memory I/O**: Encode/decode images in memory
- **Hardware Acceleration**: NVIDIA nvimgcodec support
- **Drawing Tools**: GPU-accelerated shapes and text rendering
- **Framework Integration**: Zero-copy tensor sharing via DLPack

## 🚀 Installation

### Requirements
- Python >= 3.10
- CUDA Toolkit 12.x
- NVIDIA GPU with compute capability >= 6.0

### Quick Install

```bash
# Standard installation with OpenCV
pip install pixtreme[opencv]

# With OpenCV contrib modules
pip install pixtreme[opencv-contrib]
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sync-dev-org/pixtreme.git
cd pixtreme

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup development environment
uv python pin 3.12
uv sync --extra dev --extra opencv
```

## 💡 Quick Start

```python
import pixtreme as px

# Read image directly to GPU as float32 (BGR format)
image = px.imread("photo.jpg")

# All operations work on GPU memory
image_rgb = px.bgr_to_rgb(image)
image_hsv = px.rgb_to_hsv(image_rgb)

# High-quality resize with 11 interpolation methods
image = px.resize(image, (1920, 1080), interpolation=px.INTER_LANCZOS4)

# Choose backend based on your needs
upscaler = px.OnnxUpscaler("models/realesrgan.onnx")     # Balanced
# upscaler = px.TrtUpscaler("models/realesrgan.trt")     # Fastest
# upscaler = px.TorchUpscaler("models/realesrgan.pth")   # Most flexible

# Upscale with single method call
upscaled = upscaler.get(image)

# Professional color grading with 3D LUT
lut = px.read_lut("cinematic_look.cube")
graded = px.apply_lut(image, lut, interpolation=1)  # Tetrahedral

# Save with format-specific options
px.imwrite("output.jpg", graded, param=95)
```

## 📖 API Reference

### 🎮 Device Management

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `get_device_id()` | - | `int` | Get current CUDA device ID |
| `get_device_count()` | - | `int` | Get number of available GPUs |
| `Device(id)` | `id: int` | Context manager | Context manager for device selection |

### 🎨 Color Module (`pixtreme.color`)

#### Basic Color Conversions
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `bgr_to_rgb(image)` | `image: np.ndarray or cp.ndarray` | `np.ndarray or cp.ndarray` | Convert BGR to RGB format |
| `rgb_to_bgr(image)` | `image: np.ndarray or cp.ndarray` | `np.ndarray or cp.ndarray` | Convert RGB to BGR format |
| `bgr_to_grayscale(image)` | `image: cp.ndarray` | `cp.ndarray` | Convert BGR to grayscale |
| `rgb_to_grayscale(image)` | `image: cp.ndarray` | `cp.ndarray` | Convert to grayscale (Rec.709) |
| `bgr_to_hsv(image)` | `image: cp.ndarray` | `cp.ndarray` | Convert BGR to HSV |
| `hsv_to_bgr(image)` | `image: cp.ndarray` | `cp.ndarray` | Convert HSV to BGR |
| `rgb_to_hsv(image)` | `image: cp.ndarray` | `cp.ndarray` | Convert RGB to HSV |
| `hsv_to_rgb(image)` | `image: cp.ndarray` | `cp.ndarray` | Convert HSV to RGB |

#### YCbCr/YUV Conversions
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `bgr_to_ycbcr(image)` | `image: cp.ndarray` | `cp.ndarray` | BGR to YCbCr (10-bit precision) |
| `rgb_to_ycbcr(image)` | `image: cp.ndarray` | `cp.ndarray` | RGB to YCbCr (10-bit precision) |
| `ycbcr_to_bgr(image)` | `image: cp.ndarray` | `cp.ndarray` | YCbCr to BGR conversion |
| `ycbcr_to_rgb(image)` | `image: cp.ndarray` | `cp.ndarray` | YCbCr to RGB conversion |
| `ycbcr_to_grayscale(image)` | `image: cp.ndarray` | `cp.ndarray` | Extract Y channel as grayscale |
| `ycbcr_full_to_legal(image)` | `image: cp.ndarray` | `cp.ndarray` | Full to Legal range conversion |
| `ycbcr_legal_to_full(image)` | `image: cp.ndarray` | `cp.ndarray` | Legal to Full range conversion |
| `yuv420p_to_ycbcr444(yuv420_data, width, height, interpolation)` | `yuv420_data: cp.ndarray, width: int, height: int, interpolation: int = 1` | `cp.ndarray` | YUV 4:2:0 to YCbCr 4:4:4 |
| `yuv420p_to_ycbcr444_cp(yuv420_data, width, height, interpolation)` | `yuv420_data: cp.ndarray, width: int, height: int, interpolation: int = 1` | `cp.ndarray` | YUV 4:2:0 to YCbCr 4:4:4 (CuPy native) |
| `yuv422p10le_to_ycbcr444(ycbcr422_data, width, height)` | `ycbcr422_data: cp.ndarray, width: int, height: int` | `cp.ndarray` | 10-bit YUV 4:2:2 to YCbCr 4:4:4 |
| `yuv422p10le_to_ycbcr444_cp(ycbcr422_data, width, height)` | `ycbcr422_data: cp.ndarray, width: int, height: int` | `cp.ndarray` | 10-bit YUV 4:2:2 to YCbCr 4:4:4 (CuPy) |
| `uyvy422_to_ycbcr444(uyvy_data, height, width)` | `uyvy_data: cp.ndarray, height: int, width: int` | `cp.ndarray` | UYVY 4:2:2 to YCbCr 4:4:4 |
| `uyvy422_to_ycbcr444_cp(uyvy_data, height, width)` | `uyvy_data: cp.ndarray, height: int, width: int` | `cp.ndarray` | UYVY 4:2:2 to YCbCr 4:4:4 (CuPy native) |
| `ndi_uyvy422_to_ycbcr444(uyvy_data)` | `uyvy_data: cp.ndarray` | `cp.ndarray` | NDI UYVY to YCbCr 4:4:4 |
| `ndi_uyvy422_to_ycbcr444_cp(uyvy_data)` | `uyvy_data: cp.ndarray` | `cp.ndarray` | NDI UYVY to YCbCr 4:4:4 (CuPy native) |

#### ACES Color Pipeline
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `rec709_to_aces2065_1(image, tonemap)` | `image: cp.ndarray \| np.ndarray, tonemap: bool = True` | `cp.ndarray \| np.ndarray` | Rec.709 to ACES2065-1 IDT. Preserves input type (NumPy/CuPy). OCIO ACES 1.2 compliant |
| `aces2065_1_to_rec709(image, tonemap)` | `image: cp.ndarray \| np.ndarray, tonemap: bool = True` | `cp.ndarray \| np.ndarray` | ACES2065-1 to Rec.709 ODT. Preserves input type (NumPy/CuPy). OCIO ACES 1.2 compliant |
| `aces2065_1_to_acescct(image)` | `image: cp.ndarray \| np.ndarray` | `cp.ndarray \| np.ndarray` | ACES2065-1 (AP0) to ACEScct (AP1 log-encoded). Preserves input type |
| `aces2065_1_to_acescg(image)` | `image: cp.ndarray \| np.ndarray` | `cp.ndarray \| np.ndarray` | ACES2065-1 (AP0) to ACEScg (AP1 linear). Preserves input type |
| `acescct_to_aces2065_1(image)` | `image: cp.ndarray \| np.ndarray` | `cp.ndarray \| np.ndarray` | ACEScct (AP1 log-encoded) to ACES2065-1 (AP0). Preserves input type |
| `acescg_to_aces2065_1(image)` | `image: cp.ndarray \| np.ndarray` | `cp.ndarray \| np.ndarray` | ACEScg (AP1 linear) to ACES2065-1 (AP0). Preserves input type |

#### 3D LUT Processing
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_lut(file_path, use_cache, cache_dir)` | `file_path: str, use_cache: bool = True, cache_dir: str = "cache"` | `cp.ndarray` | Read .cube format LUT files |
| `apply_lut(image, lut, interpolation)` | `image: cp.ndarray, lut: cp.ndarray, interpolation: int = 0` | `cp.ndarray` | Apply 3D LUT (0=trilinear, 1=tetrahedral) |
| `apply_lut_cp(image, lut, interpolation)` | `image: cp.ndarray, lut: cp.ndarray, interpolation: int = 0` | `cp.ndarray` | Apply 3D LUT (CuPy native implementation) |

### 🖼️ Draw Module (`pixtreme.draw`)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `circle(image, center_x, center_y, radius, color)` | `image: cp.ndarray, center_x: int, center_y: int, radius: int, color: tuple = (1.0, 1.0, 1.0)` | `cp.ndarray` | Draw filled circle |
| `rectangle(image, top_left_x, top_left_y, bottom_right_x, bottom_right_y, color)` | `image: cp.ndarray, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int, color: tuple = (1.0, 1.0, 1.0)` | `cp.ndarray` | Draw filled rectangle |
| `put_text(image, text, org, font_face, font_scale, color, thickness, line_type, density)` | `image: cp.ndarray, text: str, org: tuple[int, int], font_face: int = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float = 1.0, color: tuple = (1.0, 1.0, 1.0), thickness: int = 2, line_type: int = cv2.LINE_AA, density: float = 1.0` | `cp.ndarray` | Draw text with supersampling |
| `add_label(image, text, org, font_face, font_scale, color, thickness, line_type, label_size, label_color, label_align, density)` | `image: cp.ndarray, text: str, org: tuple = (0, 0), font_face: int = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float = 1.0, color: tuple = (1.0, 1.0, 1.0), thickness: int = 2, line_type: int = cv2.LINE_AA, label_size: int = 20, label_color: tuple = (0.0, 0.0, 0.0), label_align: str = "bottom", density: float = 1.0` | `cp.ndarray` | Add labeled banner |
| `create_rounded_mask(dsize, mask_offsets, radius_ratio, density, blur_size, sigma)` | `dsize: tuple = (512, 512), mask_offsets: tuple = (0.1, 0.1, 0.1, 0.1), radius_ratio: float = 0.1, density: int = 1, blur_size: int = 0, sigma: float = 1.0` | `cp.ndarray` | Create rounded rectangle mask |

### 🔨 Filter Module (`pixtreme.filter`)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `gaussian_blur(image, kernel_size, sigma, kernel)` | `image: cp.ndarray, kernel_size: int, sigma: float, kernel: cp.ndarray or None = None` | `cp.ndarray` | Apply Gaussian blur |
| `get_gaussian_kernel(ksize, sigma)` | `ksize: int, sigma: float` | `cp.ndarray` | Generate 1D Gaussian kernel |
| `GaussianBlur(kernel_size, sigma)` | Class - `kernel_size: int, sigma: float` | Class instance | Gaussian blur filter class |

### 🔄 Transform Module (`pixtreme.transform`)

#### Image Operations
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `resize(src, dsize, fx, fy, interpolation)` | `src: cp.ndarray, dsize: tuple[int, int] or None = None, fx: float or None = None, fy: float or None = None, interpolation: int = INTER_AUTO` | `cp.ndarray` | Resize image with 11 interpolation methods |
| `affine_transform(src, M, dsize, flags)` | `src: cp.ndarray, M: cp.ndarray, dsize: tuple, flags: int = INTER_AUTO` | `cp.ndarray` | Apply affine transformation matrix |
| `get_inverse_matrix(M)` | `M: cp.ndarray` | `cp.ndarray` | Calculate inverse transformation matrix |
| `crop_from_kps(image, kps, size)` | `image: cp.ndarray, kps: cp.ndarray, size: int = 512` | `tuple[cp.ndarray, cp.ndarray]` | Crop image based on keypoints |
| `erode(image, kernel_size, kernel, border_value)` | `image: cp.ndarray, kernel_size: int, kernel: cp.ndarray or None = None, border_value: float = 0.0` | `cp.ndarray` | Morphological erosion |
| `create_erode_kernel(kernel_size)` | `kernel_size: int` | `cp.ndarray` | Create erosion kernel |
| `stack_images(images, axis)` | `images: list[cp.ndarray], axis: int = 0` | `cp.ndarray` | Stack multiple images |
| `subsample_image(image, factor)` | `image: cp.ndarray, factor: int` | `cp.ndarray` | Fast downsampling |
| `subsample_image_back(image, original_shape, factor)` | `image: cp.ndarray, original_shape: tuple, factor: int` | `cp.ndarray` | Upsample back to original |
| `tile_image(input_image, tile_size, overlap)` | `input_image: cp.ndarray, tile_size: int = 128, overlap: int = 16` | `tuple[list[cp.ndarray], tuple]` | Split image into tiles |
| `merge_tiles(tiles, original_shape, padded_shape, scale, tile_size, overlap)` | `tiles: list[cp.ndarray], original_shape: tuple[int, int, int], padded_shape: tuple[int, int, int], scale: int, tile_size: int = 128, overlap: int = 16` | `cp.ndarray` | Merge tiles with blending |
| `add_padding(input_image, patch_size, overlap)` | `input_image: cp.ndarray, patch_size: int = 128, overlap: int = 16` | `cp.ndarray` | Add padding for tiling |
| `create_gaussian_weights(size, sigma)` | `size: int, sigma: int` | `cp.ndarray` | Create Gaussian weight map |

#### Interpolation Constants
- `INTER_NEAREST` = 0 - Nearest neighbor
- `INTER_LINEAR` = 1 - Bilinear
- `INTER_CUBIC` = 2 - Bicubic
- `INTER_AREA` = 3 - Area-based resampling
- `INTER_LANCZOS4` = 4 - Lanczos (8x8)
- `INTER_AUTO` = 5 - Auto-select
- `INTER_MITCHELL` = 6 - Mitchell-Netravali
- `INTER_B_SPLINE` = 7 - B-spline
- `INTER_CATMULL_ROM` = 8 - Catmull-Rom
- `INTER_LANCZOS2` = 9 - Lanczos (4x4)
- `INTER_LANCZOS3` = 10 - Lanczos (6x6)

### 📁 I/O Module (`pixtreme.io`)

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `imread(input_path, dtype, swap_rb, is_nvimgcodec)` | `input_path: str, dtype: str = "fp32", swap_rb: bool = False, is_nvimgcodec: bool = False` | `cp.ndarray` | Read image to GPU (defaults to float32) |
| `imwrite(output_path, image, param, swap_rb)` | `output_path: str, image: cp.ndarray or np.ndarray, param: int = -1, swap_rb: bool = False` | `None` | Write image with format-specific options |
| `imencode(image, ext, param, swap_rb)` | `image: cp.ndarray, ext: str = ".png", param: int = -1, swap_rb: bool = False` | `bytes` | Encode image to memory |
| `imdecode(src, dtype, swap_rb)` | `src: bytes, dtype: str = "fp32", swap_rb: bool = False` | `cp.ndarray` | Decode image from memory |
| `imshow(title, image, scale, is_rgb)` | `title: str, image: np.ndarray or cp.ndarray, scale: float = 1.0, is_rgb: bool = False` | `None` | Display image |
| `waitkey(delay)` | `delay: int` | `int` | Wait for keyboard input |
| `destroy_all_windows()` | - | `None` | Close all OpenCV windows |

### 🤖 Upscale Module (`pixtreme.upscale`)

| Class | Constructor Parameters | Method | Description |
|-------|------------------------|--------|-------------|
| `OnnxUpscaler` | `model_path: str or None = None, model_bytes: bytes or None = None, device_id: int = 0, provider_options: list or None = None` | `get(image: cp.ndarray) -> cp.ndarray` | ONNX Runtime upscaling |
| `TrtUpscaler` | `model_path: str or None = None, model_bytes: bytes or None = None, device_id: int = 0` | `get(image: cp.ndarray) -> cp.ndarray` | TensorRT optimized upscaling |
| `TorchUpscaler` | `model_path: str or None = None, model_bytes: bytes or None = None, device: str = "cuda"` | `get(image: cp.ndarray) -> cp.ndarray` | PyTorch native upscaling |

### 🔧 Utils Module (`pixtreme.utils`)

#### Type Conversions
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `to_uint8(image)` | `image: np.ndarray or cp.ndarray` | `np.ndarray or cp.ndarray` | Convert to 8-bit (0-255) |
| `to_uint16(image)` | `image: np.ndarray or cp.ndarray` | `np.ndarray or cp.ndarray` | Convert to 16-bit unsigned |
| `to_float16(image)` | `image: np.ndarray or cp.ndarray` | `np.ndarray or cp.ndarray` | Convert to 16-bit float |
| `to_float32(image, clip)` | `image: np.ndarray or cp.ndarray, clip: bool = True` | `np.ndarray or cp.ndarray` | Convert to 32-bit float. If clip=True, clamps to [0,1]. If clip=False, preserves values outside [0,1] for scene-referred workflows (ACES) |
| `to_float64(image)` | `image: np.ndarray or cp.ndarray` | `np.ndarray or cp.ndarray` | Convert to 64-bit float |
| `to_dtype(image, dtype)` | `image: np.ndarray or cp.ndarray, dtype: str` | `np.ndarray or cp.ndarray` | Convert to specified dtype |

#### Framework Interoperability
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `to_cupy(image)` | `image: np.ndarray or torch.Tensor or nvimgcodec.Image` | `cp.ndarray` | Convert to CuPy array |
| `to_numpy(image)` | `image: cp.ndarray or torch.Tensor or nvimgcodec.Image` | `np.ndarray` | Convert to NumPy array |
| `to_tensor(image, device)` | `image: np.ndarray or cp.ndarray, device: str or torch.device or None = None` | `torch.Tensor` | Convert to PyTorch tensor |

#### Batch Processing
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `guess_image_layout(image)` | `image: np.ndarray or cp.ndarray` | `str` | Detect image layout (HW, HWC, CHW, etc.) |
| `image_to_batch(image, size, scalefactor, mean, swap_rb, layout)` | `image: cp.ndarray, size: int or tuple[int, int] or None = None, scalefactor: float or None = None, mean: float or tuple or None = None, swap_rb: bool = True, layout: str = "HWC"` | `cp.ndarray` | Convert single image to batch |
| `images_to_batch(images, size, scalefactor, mean, swap_rb, layout)` | `images: list[cp.ndarray], size: int or tuple[int, int] or None = None, scalefactor: float or None = None, mean: float or tuple or None = None, swap_rb: bool = True, layout: str = "HWC"` | `cp.ndarray` | Convert images to batch format |
| `batch_to_images(batch, scalefactor, mean, swap_rb, layout)` | `batch: cp.ndarray, scalefactor: float or tuple or None = None, mean: float or tuple or None = None, swap_rb: bool = True, layout: str = "NCHW"` | `list[cp.ndarray]` | Convert batch to images |

#### Model Conversion
| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `check_torch_model(model_path)` | `model_path: str` | `bool` | Validate PyTorch model |
| `check_onnx_model(model_path)` | `model_path: str` | `bool` | Validate ONNX model |
| `torch_to_onnx(model_path, onnx_path, input_shape, opset_version, precision, dynamic_axes, device)` | `model_path: str, onnx_path: str, input_shape: tuple = (1,3,1080,1920), opset_version: int = 20, precision: str = "fp32", dynamic_axes: dict or None = None, device: str = "cuda"` | `None` | Convert PyTorch to ONNX |
| `onnx_to_onnx_dynamic(input_path, output_path, opset, irver)` | `input_path: str, output_path: str, opset: int or None = None, irver: int or None = None` | `None` | Add dynamic shape support |
| `onnx_to_trt(onnx_path, engine_path, precision, workspace)` | `onnx_path: str, engine_path: str, precision: str = "fp16", workspace: int = 1<<30` | `None` | Convert ONNX to TensorRT |
| `onnx_to_trt_dynamic_shape(onnx_path, engine_path, precision, workspace)` | `onnx_path: str, engine_path: str, precision: str = "fp16", workspace: int = 1<<30` | `None` | TensorRT with dynamic shapes |
| `onnx_to_trt_fixed_shape(onnx_path, engine_path, precision, workspace, input_shape)` | `onnx_path: str, engine_path: str, precision: str = "fp16", workspace: int = 1<<30, input_shape: tuple = (1,3,1080,1920)` | `None` | TensorRT with fixed shape |



## Performance Notes

- All color conversion operations use optimized CUDA kernels
- Supports both legal range (16-235) and full range (0-255) for video processing
- 10-bit precision support for professional video workflows
- Zero-copy tensor sharing via DLPack for framework interoperability
- Batch processing support for multiple images

## License

pixtreme is distributed under the MIT License (see [LICENSE](LICENSE)).

### Included Components

* **ACES LUTs**
  - © 2014 Academy of Motion Picture Arts and Sciences
  - Licensed under "License Terms for ACES Components"
  - See [third_party/aces/LICENSE_ACES.txt](third_party/aces/LICENSE_ACES.txt) for details

## Authors

minamik (@minamikik)

## Acknowledgments

sync.dev
