# SAM Mask CLI

A command-line tool for generating segmentation masks using SAM (Segment Anything Model). This tool takes an input image and a bounding box, then generates a binary mask where detected objects are white and the background is black.

## Features

- Generate segmentation masks using SAM 2.1
- Command-line interface for easy automation
- Support for various image formats (JPEG, PNG, WebP, etc.)
- Binary mask output (white for detected objects, black for background)
- Robust error handling and validation

## Installation

### Prerequisites

- Python 3.10 or higher
- CUDA-compatible GPU (recommended for better performance)

### Install from source

1. Clone the repository:
```bash
git clone <repository-url>
cd sam-mask-cli
```

2. Install the package:
```bash
pip install -e .
```

### Install dependencies only

If you just want to install the dependencies:
```bash
pip install -r requirements.txt
```

Or using uv:
```bash
uv pip install -e .
```

## Usage

The basic syntax is:
```bash
sam-mask-cli <image_path> <bounding_box> <output_path> <output_filename> [options]
```

### Parameters

- `image_path`: Path to the input image
- `bounding_box`: Bounding box coordinates in format `x_min,y_min,x_max,y_max`
- `output_path`: Directory where the mask will be saved
- `output_filename`: Name of the output mask file (e.g., `mask.png`)

### Options

- `--model`: Choose SAM model variant (sam2.1_t.pt, sam2.1_s.pt, sam2.1_b.pt, sam2.1_l.pt)
- `--draw-box`: Also save the original image with the bounding box drawn on it

### Examples

Generate a mask for an object in an image:
```bash
sam-mask-cli input.jpg "100,50,300,250" output/ mask.png
```

Process a WebP image with specific coordinates:
```bash
sam-mask-cli image.webp "981,57,1261,720" ./masks/ result.png
```

Save to a nested directory (will be created if it doesn't exist):
```bash
sam-mask-cli photo.png "200,100,400,300" results/masks/ person_mask.png
```

Use a faster model for quicker processing:
```bash
sam-mask-cli image.jpg "100,50,300,250" output/ mask.png --model sam2.1_b.pt
```

Generate mask and visualize the bounding box:
```bash
sam-mask-cli photo.png "200,100,400,300" output/ mask.png --draw-box
```

This creates two files:
- `mask.png` - The binary segmentation mask
- `mask_bbox.png` - Original image with green bounding box drawn on it

### Bounding Box Format

The bounding box should be specified as four comma-separated integers:
- `x_min`: Left edge of the box
- `y_min`: Top edge of the box  
- `x_max`: Right edge of the box
- `y_max`: Bottom edge of the box

Where (0,0) is the top-left corner of the image.

## Output

The tool generates a binary mask image with:
- **White pixels (255)**: Areas where SAM detected the segmented object
- **Black pixels (0)**: Background areas

The output mask has the same dimensions as the input image.

When using `--draw-box`, an additional image is created showing the original image with:
- **Green bounding box**: Rectangle outline showing the specified coordinates
- **Coordinate label**: Text showing the exact bounding box values

## SAM Model Options

The tool supports different SAM 2.1 model variants with different speed/accuracy tradeoffs:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `sam2.1_t.pt` | Smallest | Fastest | Lower | Quick prototyping, real-time applications |
| `sam2.1_s.pt` | Small | Fast | Good | Balanced performance |
| `sam2.1_b.pt` | Medium | Moderate | Better | Recommended for most use cases |
| `sam2.1_l.pt` | Large | Slowest | Best | High-accuracy requirements (default) |

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Error Handling

The tool provides clear error messages for common issues:

- Invalid image paths or unsupported formats
- Malformed bounding box coordinates
- Bounding boxes outside image boundaries
- Output directory creation failures

## Development

### Setting up development environment

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run code formatting:
```bash
black sam_mask_cli/
isort sam_mask_cli/
```

3. Run type checking:
```bash
mypy sam_mask_cli/
```

4. Run linting:
```bash
flake8 sam_mask_cli/
```

### Project Structure

```
sam-mask-cli/
├── sam_mask_cli/
│   ├── __init__.py
│   └── cli.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Model Requirements

This tool uses SAM 2.1 models which are automatically downloaded and cached on first use. Models are stored in `~/.cache/ultralytics/` (Linux/macOS) or `%USERPROFILE%\.cache\ultralytics\` (Windows) to avoid polluting your working directory.

**Model Cache Behavior:**
- ✅ Models download to system cache directory  
- ✅ Shared across all installations (pip, pipx, uvx)
- ✅ No files created in your current working directory
- ✅ Automatic cache management by ultralytics

The cache location is displayed when loading models for transparency.

## Performance Notes

- First run may be slower due to model downloading and initialization
- Models are cached globally - subsequent runs are faster
- GPU acceleration is recommended for better performance
- Larger images and complex scenes may require more processing time
- Use smaller models (`--model sam2.1_b.pt`) for faster inference

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

**Model download fails:**
- Ensure you have a stable internet connection
- Check that you have sufficient disk space in `~/.cache/ultralytics/`
- Try running the command again
- Models download to cache directory, not current working directory

**CUDA out of memory:**
- Try processing smaller images
- Close other GPU-intensive applications
- Consider using CPU-only mode (though slower)

**Invalid bounding box errors:**
- Verify coordinates are within image bounds
- Ensure x_min < x_max and y_min < y_max
- Check that coordinates are positive integers

**Permission errors:**
- Ensure you have write permissions to the output directory
- Try running with appropriate user permissions

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem