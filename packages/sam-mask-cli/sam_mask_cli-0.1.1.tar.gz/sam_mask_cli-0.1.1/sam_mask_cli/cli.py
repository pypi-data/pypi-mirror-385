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
from ultralytics.utils import LOGGER


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


def setup_model_cache() -> Path:
    """Set up and return the proper cache directory for SAM models.

    Returns:
        Path to the cache directory where models should be stored
    """
    # Use ultralytics default cache directory
    cache_dir = Path.home() / ".cache" / "ultralytics"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variable to ensure ultralytics uses this cache
    os.environ["ULTRALYTICS_CACHE_DIR"] = str(cache_dir)

    return cache_dir


def ensure_model_in_cache(model_name: str) -> Path:
    """Ensure the SAM model is downloaded to the cache directory, not CWD.

    Args:
        model_name: Name of the SAM model (e.g., 'sam2.1_l.pt')

    Returns:
        Path to the model file in cache
    """
    cache_dir = setup_model_cache()
    model_path = cache_dir / model_name

    # If model doesn't exist in cache, force download to cache
    if not model_path.exists():
        # Temporarily change to cache directory to force download there
        original_cwd = os.getcwd()
        try:
            os.chdir(cache_dir)
            print(f"📥 Downloading {model_name} to cache directory: {cache_dir}")
            # Create a temporary SAM instance to trigger download
            temp_model = SAM(model_name)
            del temp_model  # Clean up
        finally:
            os.chdir(original_cwd)

    return model_path


def generate_mask(
    image_path: Path,
    bounding_box: List[int],
    output_path: Path,
    model_name: str = "sam2.1_l.pt",
    draw_box: bool = False,
    box_output_path: Path = None,
) -> None:
    """Generate a segmentation mask using SAM and save it as a binary image.

    Args:
        image_path: Path to the input image
        bounding_box: List of 4 integers [x_min, y_min, x_max, y_max]
        output_path: Path where the mask image will be saved
        model_name: SAM model to use (default: sam2.1_l.pt)
        draw_box: Whether to save an image with the bounding box drawn
        box_output_path: Path where the bounding box image will be saved
    """
    try:
        # Ensure model is in cache directory, not CWD
        model_path = ensure_model_in_cache(model_name)
        cache_dir = setup_model_cache()
        print(f"📂 Loading SAM model: {model_name} from cache ({cache_dir})")

        # Load model from cache path
        model = SAM(str(model_path))

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
        print(f"Image dimensions: {width}x{height}")

        # Generate segmentation mask
        results = model(image_rgb, bboxes=[bounding_box])

        # Check if any masks were detected
        if results[0].masks is None or len(results[0].masks.data) == 0:
            print("\n❌ No masks detected in the specified bounding box!")
            print("\nPossible issues:")
            print(
                f"  • Bounding box [{x_min}, {y_min}, {x_max}, {y_max}] might not contain a clear object"
            )
            print("  • The object boundaries might be unclear or too complex")
            print("  • Try adjusting the bounding box coordinates")
            print(
                "  • Consider using a different SAM model (sam2.1_b.pt for faster inference)"
            )
            print("\nTroubleshooting tips:")
            print(f"  • Bounding box size: {x_max - x_min}x{y_max - y_min} pixels")
            print(
                f"  • Make sure coordinates are within image bounds (0-{width}, 0-{height})"
            )
            print("  • Try making the bounding box slightly larger")
            print("  • Ensure the object has clear edges and good contrast")
            print("\n⚠️  Creating an empty mask (all black pixels)...")

            # Create empty mask (all black)
            mask_image = np.zeros((height, width), dtype=np.uint8)
        else:
            print(f"✅ Successfully detected {len(results[0].masks.data)} mask(s)")

            # Extract the mask
            mask = results[0].masks.data[0].cpu().numpy()

            # Count pixels for feedback
            mask_pixels = np.sum(mask == 1)
            total_pixels = mask.shape[0] * mask.shape[1]
            percentage = (mask_pixels / total_pixels) * 100

            print(
                f"   Mask covers {mask_pixels:,} pixels ({percentage:.1f}% of bounding box area)"
            )

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

        # Draw bounding box on original image if requested
        if draw_box and box_output_path:
            print(f"Drawing bounding box on original image...")

            # Create a copy of the original image for drawing
            image_with_box = image_rgb.copy()

            # Draw bounding box rectangle
            cv2.rectangle(
                image_with_box,
                (x_min, y_min),
                (x_max, y_max),
                (0, 255, 0),  # Green color in RGB
                3,  # Line thickness
            )

            # Add text label with coordinates
            label_text = f"BBox: [{x_min},{y_min},{x_max},{y_max}]"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            text_color = (0, 255, 0)  # Green color in RGB

            # Get text size for background rectangle
            (text_width, text_height), baseline = cv2.getTextSize(
                label_text, font, font_scale, font_thickness
            )

            # Position text above the bounding box, or below if too close to top
            text_y = max(y_min - 10, text_height + 10)
            text_x = x_min

            # Draw background rectangle for text
            cv2.rectangle(
                image_with_box,
                (text_x - 5, text_y - text_height - 5),
                (text_x + text_width + 5, text_y + baseline + 5),
                (0, 0, 0),  # Black background
                -1,  # Fill rectangle
            )

            # Draw text
            cv2.putText(
                image_with_box,
                label_text,
                (text_x, text_y),
                font,
                font_scale,
                text_color,
                font_thickness,
            )

            # Convert back to BGR for saving
            image_with_box_bgr = cv2.cvtColor(image_with_box, cv2.COLOR_RGB2BGR)

            # Save the image with bounding box
            ensure_output_directory(box_output_path)
            box_success = cv2.imwrite(str(box_output_path), image_with_box_bgr)
            if not box_success:
                print(
                    f"Warning: Failed to save bounding box image to: {box_output_path}",
                    file=sys.stderr,
                )
            else:
                print(f"Bounding box image saved to: {box_output_path}")

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
  sam-mask-cli photo.png "200,100,400,300" ./ mask.png --model sam2.1_b.pt
  sam-mask-cli image.jpg "100,50,300,250" ./ mask.png --draw-box

The bounding box format is: x_min,y_min,x_max,y_max
where (x_min, y_min) is the top-left corner and (x_max, y_max) is the bottom-right corner.

Model options (from fastest to most accurate):
  sam2.1_t.pt  - Tiny model (fastest, least accurate)
  sam2.1_s.pt  - Small model
  sam2.1_b.pt  - Base model (good balance)
  sam2.1_l.pt  - Large model (slowest, most accurate) [default]
""",
    )

    parser.add_argument("image_path", help="Path to the input image")

    parser.add_argument(
        "bounding_box", help="Bounding box coordinates as 'x_min,y_min,x_max,y_max'"
    )

    parser.add_argument("output_path", help="Output directory path")

    parser.add_argument("output_filename", help="Output filename (e.g., 'mask.png')")

    parser.add_argument(
        "--model",
        default="sam2.1_l.pt",
        choices=["sam2.1_t.pt", "sam2.1_s.pt", "sam2.1_b.pt", "sam2.1_l.pt"],
        help="SAM model to use (default: sam2.1_l.pt). Smaller models are faster but less accurate.",
    )

    parser.add_argument(
        "--draw-box",
        action="store_true",
        help="Also save the original image with the bounding box drawn on it",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    try:
        # Validate inputs
        image_path = validate_image_path(args.image_path)
        bounding_box = parse_bounding_box(args.bounding_box)

        # Construct full output path
        output_dir = Path(args.output_path)
        output_path = output_dir / args.output_filename

        # Construct bounding box image path if draw-box is enabled
        box_output_path = None
        if args.draw_box:
            # Create filename by adding "_bbox" before the extension
            filename_parts = args.output_filename.rsplit(".", 1)
            if len(filename_parts) == 2:
                box_filename = f"{filename_parts[0]}_bbox.{filename_parts[1]}"
            else:
                box_filename = f"{args.output_filename}_bbox.png"
            box_output_path = output_dir / box_filename

        # Generate and save the mask
        generate_mask(
            image_path,
            bounding_box,
            output_path,
            args.model,
            args.draw_box,
            box_output_path,
        )

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
