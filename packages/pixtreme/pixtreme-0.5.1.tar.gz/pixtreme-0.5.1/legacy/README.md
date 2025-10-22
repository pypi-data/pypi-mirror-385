# pixtreme-legacy

**⚠️ DEPRECATED**: This package provides backward compatibility for deprecated `_cp` functions in pixtreme.

## Status

- **Current Version**: 0.5.0
- **Deprecation Notice**: All functions in this package are deprecated and will be removed in pixtreme v0.6.0
- **Recommendation**: Migrate to standard functions (without `_cp` suffix)

## Purpose

This package exists solely for backward compatibility. It re-exports the following deprecated functions from pixtreme:

- `apply_lut_cp` - Apply 3D LUT with CuPy implementation
- `uyvy422_to_ycbcr444_cp` - Convert UYVY422 to YCbCr444
- `ndi_uyvy422_to_ycbcr444_cp` - Convert NDI UYVY422 to YCbCr444
- `yuv420p_to_ycbcr444_cp` - Convert YUV420 to YCbCr444
- `yuv422p10le_to_ycbcr444_cp` - Convert YUV422p10le to YCbCr444

## Installation

```bash
pip install pixtreme-legacy
```

## Usage

```python
from pixtreme_legacy import apply_lut_cp

# This will trigger a DeprecationWarning
result = apply_lut_cp(image, lut)
```

## Migration Guide

Replace `_cp` functions with their standard equivalents:

### Before (deprecated)
```python
from pixtreme import apply_lut_cp
result = apply_lut_cp(image, lut, interpolation=0)
```

### After (recommended)
```python
from pixtreme import apply_lut
result = apply_lut(image, lut, interpolation=0)
```

## Why were _cp functions deprecated?

The `_cp` suffix originally indicated "CuPy native" implementations, as opposed to CUDA kernel implementations. However:

1. **Redundancy**: Both implementations exist in the main functions now
2. **Confusion**: Users don't need to choose between implementations
3. **Maintenance**: Duplicate APIs increase maintenance burden

The standard functions (without `_cp`) now automatically select the best implementation.

## Timeline

- **v0.4.0**: `_cp` functions available without warnings
- **v0.5.0**: `_cp` functions deprecated with warnings, `pixtreme-legacy` package created
- **v0.6.0**: `_cp` functions removed from main `pixtreme` package, only available in `pixtreme-legacy`

## License

MIT License (same as pixtreme)
