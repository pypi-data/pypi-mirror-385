#!/usr/bin/env python3
"""
SAM Mask CLI - Command-line interface for generating segmentation masks using SAM.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from ultralytics import SAM


def parse_bounding_box(bbox_str: str) -> List[int]:
    """Parse bounding box string into list of integers.

    Args:
        bbox_str: Comma-separated string of 4 integers (x_min,y_min,x_max,y_max)

    Returns:
        List of 4 integers representing the bounding box

    Raises:
        ValueError: If the bounding box format is invalid
    """
    try:
        bbox = [int(x.strip()) for x in bbox_str.split(",")]
        if len(bbox) != 4:
            raise ValueError("Bounding box must have exactly 4 values")
        return bbox
    except ValueError as e:
        raise ValueError(f"Invalid bounding box format: {e}")


def validate_image_path(image_path: str) -> Path:
    """Validate that the image path exists and is readable.

    Args:
        image_path: Path to the input image

    Returns:
        Path object for the image

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the file is not a valid image format
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {image_path}")

    # Check if it's a supported image format
    supported_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    if path.suffix.lower() not in supported_extensions:
        raise ValueError(f"Unsupported image format: {path.suffix}")

    return path


def ensure_output_directory(output_path: Path) -> None:
    """Ensure the output directory exists.

    Args:
        output_path: Path to the output directory
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)


def generate_mask(image_path: Path, bounding_box: List[int], output_path: Path) -> None:
    """Generate a segmentation mask using SAM and save it as a binary image.

    Args:
        image_path: Path to the input image
        bounding_box: List of 4 integers [x_min, y_min, x_max, y_max]
        output_path: Path where the mask image will be saved
    """
    try:
        # Load SAM model (will auto-download to ~/.cache/ultralytics/ if needed)
        print("Loading SAM model...")
        model = SAM("sam2.1_l.pt")  # Use SAM 2.1 large model, auto-downloads to cache

        # Load and prepare the image
        print(f"Loading image: {image_path}")
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]

        # Validate bounding box coordinates
        x_min, y_min, x_max, y_max = bounding_box
        if x_min < 0 or y_min < 0 or x_max > width or y_max > height:
            raise ValueError(
                f"Bounding box coordinates are out of image bounds. "
                f"Image size: {width}x{height}, bbox: {bounding_box}"
            )

        if x_min >= x_max or y_min >= y_max:
            raise ValueError(f"Invalid bounding box: {bounding_box}")

        print(f"Generating mask for bounding box: {bounding_box}")

        # Generate segmentation mask
        results = model(image_rgb, bboxes=[bounding_box])

        # Extract the mask
        mask = results[0].masks.data[0].cpu().numpy()

        # Create binary mask image (white for mask, black for background)
        mask_image = np.zeros((height, width), dtype=np.uint8)
        mask_image[mask == 1] = 255

        # Ensure output directory exists
        ensure_output_directory(output_path)

        # Save the mask
        success = cv2.imwrite(str(output_path), mask_image)
        if not success:
            raise RuntimeError(f"Failed to save mask to: {output_path}")

        print(f"Mask saved successfully to: {output_path}")

    except Exception as e:
        print(f"Error generating mask: {e}", file=sys.stderr)
        raise


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate segmentation masks using SAM (Segment Anything Model)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sam-mask-cli input.jpg "100,50,300,250" output/ mask.png
  sam-mask-cli image.webp "981,57,1261,720" ./masks/ result.png

The bounding box format is: x_min,y_min,x_max,y_max
where (x_min, y_min) is the top-left corner and (x_max, y_max) is the bottom-right corner.
""",
    )

    parser.add_argument("image_path", help="Path to the input image")

    parser.add_argument(
        "bounding_box", help="Bounding box coordinates as 'x_min,y_min,x_max,y_max'"
    )

    parser.add_argument("output_path", help="Output directory path")

    parser.add_argument("output_filename", help="Output filename (e.g., 'mask.png')")

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    try:
        # Validate inputs
        image_path = validate_image_path(args.image_path)
        bounding_box = parse_bounding_box(args.bounding_box)

        # Construct full output path
        output_dir = Path(args.output_path)
        output_path = output_dir / args.output_filename

        # Generate and save the mask
        generate_mask(image_path, bounding_box, output_path)

        return 0

    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
