# Puhu Module Architecture

## Visual Structure

```
┌─────────────────────────────────────────────────────────────┐
│                         lib.rs                              │
│                   (Main Entry Point)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────────────────────┐
                            │                                 │
┌───────────────────────────▼──────┐           ┌──────────────▼────────────┐
│         image.rs                 │           │       errors.rs           │
│    (PyO3 Python Bindings)        │           │    (Error Types)          │
│                                  │           │                           │
│  • PyImage struct                │           │  • PuhuError              │
│  • LazyImage enum                │           │  • Custom exceptions      │
│  • Python API methods            │           │                           │
│  • I/O operations                │           └───────────────────────────┘
└──────────────┬───────────────────┘
               │
               │ delegates to
               │
   ┌───────────┴───────────┬─────────────────┬──────────────────┐
   │                       │                 │                  │
┌──▼──────────┐    ┌──────▼────────┐  ┌────▼────────┐  ┌─────▼──────┐
│ conversions │    │   palette     │  │   utils     │  │  formats   │
│    .rs      │    │     .rs       │  │    .rs      │  │    .rs     │
└─────────────┘    └───────────────┘  └─────────────┘  └────────────┘
│ Matrix conv │    │ Web palette   │  │ Color type  │  │ Format     │
│ Bilevel     │    │ Adaptive pal  │  │ conversion  │  │ parsing    │
│ Parallel    │    │ Quantization  │  │ utilities   │  │            │
│ processing  │    │ Dithering     │  │             │  │            │
└─────────────┘    └───────────────┘  └─────────────┘  └────────────┘
```

## Module Dependency Graph

```
        lib.rs
          │
    ┌─────┴─────┬─────────┬────────┬─────────┐
    │           │         │        │         │
  errors    formats   operations │      image.rs
    │           │         │        │         │
    │           │         │        │    ┌────┴─────┬─────────┐
    │           │         │        │    │          │         │
    │           │         │        │  utils   conversions  palette
    │           │         │        │    │          │         │
    │           │         │        └────┴──────────┴─────────┘
    │           │         │
    └───────────┴─────────┘
```

## Responsibility Matrix

| Module | Responsibility | Public Functions | Lines | Dependencies |
|--------|---------------|------------------|-------|--------------|
| **lib.rs** | Module registration & PyO3 setup | `_core()` | 23 | All modules |
| **image.rs** | Python API & I/O | 15+ PyO3 methods | 438 | utils, conversions, palette |
| **conversions.rs** | Color transformations | `convert_with_matrix()`<br>`convert_to_bilevel()` | 84 | image crate, rayon |
| **palette.rs** | Palette & quantization | `generate_web_palette()`<br>`generate_adaptive_palette()`<br>`convert_to_palette()` | 174 | image, color_quant |
| **utils.rs** | Shared utilities | `color_type_to_mode_string()` | 18 | image crate |
| **errors.rs** | Error handling | `PuhuError` enum | 35 | thiserror, PyO3 |
| **formats.rs** | Format parsing | `parse_format()` | 23 | image crate |
| **operations.rs** | Resampling filters | `parse_resample_filter()` | 15 | image crate |

## Data Flow

### Image Conversion Flow
```
Python: img.convert("P", palette="ADAPTIVE", colors=128)
   │
   ▼
image.rs: PyImage::convert()
   │
   ├─ utils::color_type_to_mode_string() ──► Get current mode
   │
   ├─ validate parameters
   │
   └─ match mode:
       │
       ├─ "L", "RGB", "RGBA" ──► Direct conversion
       │
       ├─ "1" ──► conversions::convert_to_bilevel()
       │               │
       │               └─ Floyd-Steinberg dithering
       │
       ├─ Matrix provided ──► conversions::convert_with_matrix()
       │                           │
       │                           └─ Parallel processing with Rayon
       │
       └─ "P" ──► palette::convert_to_palette()
                       │
                       ├─ palette::generate_web_palette() or
                       ├─ palette::generate_adaptive_palette()
                       │       │
                       │       └─ NeuQuant quantization
                       │
                       └─ palette::apply_floyd_steinberg_dithering()
```

### Module Communication

```
┌────────────┐
│   Python   │
└─────┬──────┘
      │ PyO3
      ▼
┌────────────────────────────────────────┐
│            image.rs                    │
│  ┌──────────────────────────────────┐ │
│  │  LazyImage (enum)                │ │
│  │  • Loaded(DynamicImage)          │ │
│  │  • Path { path }                 │ │
│  │  • Bytes { data }                │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  PyImage (struct)                │ │
│  │  • lazy_image: LazyImage         │ │
│  │  • format: Option<ImageFormat>   │ │
│  └──────────────────────────────────┘ │
└──────────┬─────────────────────────────┘
           │
           ├──────────► conversions::convert_with_matrix()
           │            • Input: &DynamicImage, mode, matrix
           │            • Output: Result<DynamicImage>
           │            • Uses: Rayon for parallelization
           │
           ├──────────► conversions::convert_to_bilevel()
           │            • Input: &DynamicImage, dither flag
           │            • Output: Result<DynamicImage>
           │            • Uses: image::imageops::colorops
           │
           ├──────────► palette::convert_to_palette()
           │            • Input: &DynamicImage, type, colors, dither
           │            • Output: Result<DynamicImage>
           │            • Uses: color_quant::NeuQuant
           │
           └──────────► utils::color_type_to_mode_string()
                        • Input: ColorType
                        • Output: String (PIL mode)
```

## API Boundaries

### Public API (Exposed to Python)
```rust
// image.rs
#[pyclass(name = "Image")]
pub struct PyImage { ... }

#[pymethods]
impl PyImage {
    fn open(...) -> PyResult<Self>
    fn save(...) -> PyResult<()>
    fn convert(...) -> PyResult<Self>
    fn resize(...) -> PyResult<Self>
    fn crop(...) -> PyResult<Self>
    // ... more methods
}
```

### Internal API (Module boundaries)
```rust
// conversions.rs
pub fn convert_with_matrix(...) -> Result<DynamicImage, PuhuError>
pub fn convert_to_bilevel(...) -> Result<DynamicImage, PuhuError>

// palette.rs
pub fn generate_web_palette() -> Vec<u8>
pub fn generate_adaptive_palette(...) -> Vec<u8>
pub fn convert_to_palette(...) -> Result<DynamicImage, PuhuError>
pub fn find_nearest_palette_color(...) -> (u8, (u8, u8, u8))

// utils.rs
pub fn color_type_to_mode_string(...) -> String
```

### Private Implementation
```rust
// palette.rs (private)
fn apply_floyd_steinberg_dithering(...) -> Vec<u8>
// Only used internally, not exposed
```

## Code Organization Benefits

### 1. **Clear Ownership**
- **image.rs**: Owns Python integration
- **conversions.rs**: Owns transformation algorithms
- **palette.rs**: Owns quantization logic
- **utils.rs**: Shared utilities

### 2. **Easy Navigation**
```
Need to modify matrix conversion? → conversions.rs
Need to add new palette? → palette.rs
Need to change Python API? → image.rs
Need a utility function? → utils.rs
```

### 3. **Independent Testing**
```rust
// Can test conversions without PyO3
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_matrix_conversion() {
        let img = DynamicImage::new_rgb8(10, 10);
        let result = convert_with_matrix(&img, "RGB", &[1.0, 0.0, 0.0, 0.0, ...]);
        assert!(result.is_ok());
    }
}
```

### 4. **Parallel Development**
- Developer A: Work on `palette.rs` (new quantization algorithm)
- Developer B: Work on `conversions.rs` (new color space)
- Developer C: Work on `image.rs` (new Python method)
- Minimal merge conflicts!

## Future Extensions

### Adding New Conversion
```rust
// 1. Add function to conversions.rs
pub fn convert_to_cmyk(image: &DynamicImage) -> Result<DynamicImage, PuhuError> {
    // Implementation
}

// 2. Update image.rs
fn convert(...) {
    match mode {
        "CMYK" => conversions::convert_to_cmyk(image)?,
        // ... existing cases
    }
}
```

### Adding New Palette Type
```rust
// 1. Add function to palette.rs
pub fn generate_octree_palette(image: &DynamicImage, colors: u32) -> Vec<u8> {
    // Octree quantization implementation
}

// 2. Update palette.rs::convert_to_palette()
match palette_type {
    "OCTREE" => generate_octree_palette(image, num_colors),
    // ... existing cases
}
```

## Summary

The modular architecture provides:

✅ **Clear separation** of concerns  
✅ **Easy maintenance** and navigation  
✅ **Independent testing** of modules  
✅ **Parallel development** capability  
✅ **Clean dependencies** between modules  
✅ **Future-proof** design for extensions  

Each module has a single, well-defined purpose and communicates through clean interfaces.
