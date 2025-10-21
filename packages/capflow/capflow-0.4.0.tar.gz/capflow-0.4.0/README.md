# capflow

A multi-model image captioning library that combines Florence2, WD14, and Vision Language Models for comprehensive image analysis.

## Features

- **Florence2**: Detailed image captions with conservative generation parameters
- **WD14**: Danbooru-style tagging with ONNX Runtime (fast GPU inference, clean dependencies)
- **VLM**: Async-first verification layer that resolves contradictions between models
- **EXIF extraction**: Camera, lens, and capture settings metadata
- **Auto-resize**: Automatically optimizes large images to model-specific resolutions
- Cross-platform support (CUDA, MPS, CPU)
- Direct numpy array processing (no PIL conversion required)
- Optimized prompts for AI image generation (Stable Diffusion, Midjourney, FLUX)

## Installation

```bash
pip install capflow
```

Or with uv:

```bash
uv add capflow
```

**GPU Support**: capflow installs `onnxruntime-gpu` by default for CUDA acceleration. CPU-only users can manually install `onnxruntime` instead of `onnxruntime-gpu` after installation.

## Quick Start

**Note:** All models expect images as `numpy.ndarray` (OpenCV format: HxWx3, BGR).

### Async (Recommended)

```python
import os
import cv2
import capflow as cf

# Initialize models (API key required for VLM)
florence2 = cf.Florence2()
wd14 = cf.WD14()
vlm = cf.VLM(api_key=os.getenv("OPENAI_API_KEY"))

# Load image with OpenCV
image = cv2.imread("your_image.jpg")

# Florence2: Detailed caption (sync)
caption = florence2.generate_caption(image, task="more_detailed_caption")

# WD14: Danbooru-style tags (sync)
tags = wd14.generate_tags(image)

# VLM: Verified and enhanced description (async)
description = await vlm.generate_caption(
    image,
    context=f"Florence2: {caption}\nWD14 Tags: {', '.join(tags)}"
)

# Extract EXIF metadata (sync, requires file path)
exif_data = cf.extract_exif("your_image.jpg")
camera_info = cf.get_camera_info(exif_data)
settings = cf.get_capture_settings(exif_data)
```

### Synchronous

```python
import os
import cv2
import capflow as cf

# Initialize models
florence2 = cf.Florence2()
wd14 = cf.WD14()
vlm = cf.VLM(api_key=os.getenv("OPENAI_API_KEY"))

# Load image with OpenCV
image = cv2.imread("your_image.jpg")

# All synchronous calls
caption = florence2.generate_caption(image, task="more_detailed_caption")
tags = wd14.generate_tags(image)

# Use _sync methods for VLM
description = vlm.generate_caption_sync(
    image,
    context=f"Florence2: {caption}\nWD14 Tags: {', '.join(tags)}"
)
```

## API Keys

API keys must be passed explicitly from your application:

```python
import os
import capflow as cf

# Pass API key from environment variable
vlm = cf.VLM(api_key=os.getenv("OPENAI_API_KEY"))

# Or pass directly (not recommended for production)
vlm = cf.VLM(api_key="your-api-key")
```

## VLM Async/Sync Methods

VLM provides both async (primary) and sync methods:

```python
# Async methods (recommended)
await vlm.generate_caption(image)
await vlm.generate_caption_with_tags(image, tags)
await vlm.refine_caption(image, draft)

# Sync methods (works even from async context)
vlm.generate_caption_sync(image)
vlm.generate_caption_with_tags_sync(image, tags)
vlm.refine_caption_sync(image, draft)
```

The `_sync` methods automatically detect if they're running in an async context and handle it correctly, so they won't raise "event loop already running" errors.

## Automatic Image Resizing

All models automatically resize images larger than their optimal size to improve performance and memory efficiency:

- **Florence2**: Resizes to 768×768px (with padding to preserve aspect ratio)
- **WD14**: Resizes to 448×448px (with padding to preserve aspect ratio)
- **VLM**: Resizes to max 2048px on longest edge (no padding, aspect ratio preserved)

Auto-resize is enabled by default but can be disabled:

```python
# Disable auto-resize
florence2 = cf.Florence2(auto_resize=False)
wd14 = cf.WD14(auto_resize=False)
vlm = cf.VLM(auto_resize=False)

# Custom target sizes
florence2 = cf.Florence2(target_size=1024)  # Use 1024 instead of 768
wd14 = cf.WD14(target_size=512)              # Use 512 instead of 448
vlm = cf.VLM(max_size=4096)                  # Use 4096 instead of 2048
```

## How It Works

capflow uses a three-stage pipeline:

1. **WD14**: Generates high-confidence tags (e.g., `1girl`, `solo`, `outdoors`)
2. **Florence2**: Creates detailed natural language captions
3. **VLM**: Examines the image directly and resolves contradictions between WD14 and Florence2, converting tags to natural English

### Example

**Input**: Image of a girl jumping outdoors

**WD14 Output**:
```
1girl, solo, dress, outdoors, jumping, motion_blur
```

**Florence2 Output**:
```
A young woman in an orange dress jumping in the air. There are a few people walking around.
```

**VLM Final Output**:
```
A photograph of a single woman mid-air, jumping in a rust-orange dress, barefoot with curly auburn hair,
dynamic extended-arms pose captured with slight motion blur, main subject left-of-center, low-angle wide shot,
foreground white marble steps, manicured hedges and formal garden behind her, large historic white stone
cathedral in the midground, overcast cloudy sky, natural daylight, joyful carefree atmosphere.
```

Note: VLM correctly identified "solo" from WD14 and ignored Florence2's hallucinated "a few people walking around".

## License

MIT
