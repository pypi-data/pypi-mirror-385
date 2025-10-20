"""
COCO Dataset Resizer and Filter

This script resizes images in a COCO dataset while maintaining aspect ratio and filtering
annotations based on size thresholds. It's designed for computer vision datasets where
you want to:

1. Resize images to a maximum dimension while preserving aspect ratio
2. Filter annotations based on minimum bounding box sizes
3. Optionally include only specific categories
4. Handle keypoint annotations by scaling coordinates
5. Generate a new COCO JSON with updated annotations

Key Features:
- Maintains aspect ratio during resizing
- Filters annotations by minimum bounding box dimensions
- Supports category-specific filtering
- Handles keypoint annotations (scales x,y coordinates)
- Optionally includes other categories in selected images
- Preserves original image metadata with updated dimensions

Usage:
    poetry run coco-resize \
        --input-coco-json ./tests/data/annotations/coco.json \
        --input-image-dir ./tests/data/images/ \
        --output-images-dir ./tmp/output/resized/images \
        --output-coco-json ./tmp/output/resized/annotations/coco.json \
        --max-size 1024 \
        --min-side-len 250 \
        --min-area-others 100 \
        --include-empty-images \
        --num-workers 8
"""

import argparse
import concurrent.futures
import json
import os
import time
from copy import deepcopy

import cv2
from tqdm import tqdm


def process_single_image(
    img_data,
    images_dir,
    output_images_dir,
    max_size,
    min_side_len,
    min_area_others,
    include_empty_images,
    category_ids_to_include,
    category_id_to_name,
    annotations_by_image,
):
    """
    Process a single image: load, resize, filter annotations, and save.
    Optimized for I/O-bound operations with minimal data transfer.

    Args:
        img_data: Image metadata from COCO JSON
        images_dir: Directory containing original images
        output_images_dir: Directory to save resized images
        max_size: Maximum dimension for resized images
        min_side_len: Minimum side length for qualifying included categories
        min_area_others: Minimum squared area for other categories
        include_empty_images: Whether to include images with no annotations
        category_ids_to_include: Set of category IDs to include (or None)
        category_id_to_name: Mapping from category ID to name
        annotations_by_image: Dictionary mapping image ID to annotations

    Returns:
        tuple: (new_img_meta, new_annotations) or None if image should be skipped
    """
    img = img_data

    # Get annotations for this image first to check if we need to process it
    anns = annotations_by_image.get(img["id"], [])

    # Pre-check if image qualifies to avoid loading unnecessary images
    qualified_ann_ids = set()
    if category_ids_to_include:
        for ann in anns:
            cat_id = ann["category_id"]
            if cat_id in category_ids_to_include:
                # Check if this annotation would meet the size threshold after scaling
                _, _, w, h = ann["bbox"]
                # We need to calculate scale first, so we'll load the image
                break
        else:
            # No qualifying categories found, check if we should skip
            if not include_empty_images and not anns:
                return None

    # Load the image
    img_path = os.path.join(images_dir, img["file_name"])
    image = cv2.imread(img_path)
    if image is None:
        print(f"Warning: Failed to load {img_path}")
        return None

    # Calculate resize scale to maintain aspect ratio
    height, width = image.shape[:2]
    scale = min(max_size / max(height, width), 1.0)  # Never upscale, only downscale
    new_w, new_h = round(width * scale), round(height * scale)

    # Now check qualification with actual scale
    qualified_ann_ids = set()
    if category_ids_to_include:
        for ann in anns:
            cat_id = ann["category_id"]
            if cat_id in category_ids_to_include:
                # Check if this annotation meets the size threshold
                _, _, w, h = ann["bbox"]
                w_scaled = w * scale
                h_scaled = h * scale
                if min(w_scaled, h_scaled) >= min_side_len:
                    qualified_ann_ids.add(ann["id"])

    # Image qualifies if it has qualifying annotations or no category filtering
    image_qualifies = bool(qualified_ann_ids) or not category_ids_to_include

    # Skip images that don't qualify (unless including empty images)
    if not image_qualifies and not include_empty_images:
        return None

    # Resize the image
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Save the resized image
    output_path = os.path.join(output_images_dir, img["file_name"])
    cv2.imwrite(output_path, resized_image)

    # Create new image metadata with updated dimensions
    new_img_meta = deepcopy(img)
    new_img_meta["width"] = new_w
    new_img_meta["height"] = new_h

    # Process annotations for this image
    new_anns = []
    for ann in anns:
        cat_id = ann["category_id"]
        x, y, w, h = ann["bbox"]

        # Scale bounding box coordinates
        w_scaled = w * scale
        h_scaled = h * scale
        min_side = min(w_scaled, h_scaled)
        area_scaled = w_scaled * h_scaled

        # Determine threshold for this annotation
        if category_ids_to_include:
            # Category filtering is enabled
            is_included_category = cat_id in category_ids_to_include
            if is_included_category:
                if ann["id"] in qualified_ann_ids:
                    threshold = (
                        min_side_len  # Use primary threshold for qualifying annotations
                    )
                elif image_qualifies:
                    threshold = 0  # Include all instances of included categories in selected images
                else:
                    threshold = min_side_len  # Use same threshold for non-qualifying included categories
            else:
                # Other categories in selected images - check area threshold
                if image_qualifies:
                    # Use area-based filtering for other categories in selected images
                    if area_scaled < min_area_others:
                        continue
                else:
                    threshold = min_side_len  # Use threshold for non-selected images
                    if min_side < threshold:
                        continue
        else:
            # No category filtering - include all annotations
            pass

        # Skip annotations that don't meet size threshold (only for included categories)
        if category_ids_to_include:
            is_included_category = cat_id in category_ids_to_include
            if is_included_category and min_side < threshold:
                continue

        # Create new annotation with scaled coordinates
        new_ann = deepcopy(ann)
        new_ann["bbox"] = [x * scale, y * scale, w_scaled, h_scaled]
        new_ann["area"] = w_scaled * h_scaled

        # Handle keypoint annotations if present
        if "keypoints" in new_ann:
            kps = new_ann["keypoints"]
            new_kps = []
            for i in range(0, len(kps), 3):
                kp_x = kps[i] * scale  # Scale x coordinate
                kp_y = kps[i + 1] * scale  # Scale y coordinate
                v = kps[i + 2]  # Keep visibility unchanged
                new_kps += [kp_x, kp_y, v]
            new_ann["keypoints"] = new_kps

        # Update annotation metadata (will be set properly in main function)
        new_ann["image_id"] = new_img_meta["id"]

        new_anns.append(new_ann)

    # Return results if we have annotations or should include empty images
    if new_anns or include_empty_images:
        return (new_img_meta, new_anns)
    else:
        return None


def resize_coco_dataset(
    coco_json_path,
    images_dir,
    output_images_dir,
    output_json_path,
    max_size=1024,
    min_side_len=4,
    min_area_others=100,
    include_empty_images=True,
    include_categories=None,
    num_workers=8,
):
    """
    Resize COCO dataset images and filter annotations based on size criteria using parallel processing.

    Uses ThreadPoolExecutor for optimal I/O-bound performance (image loading/saving).

    Args:
        coco_json_path (str): Path to input COCO JSON annotation file
        images_dir (str): Directory containing original images
        output_images_dir (str): Directory to save resized images
        output_json_path (str): Path to save new COCO JSON with updated annotations
        max_size (int): Maximum dimension (width or height) for resized images
        min_side_len (float): Minimum side length for qualifying included categories
        min_area_others (float): Minimum squared area for other categories in selected images
        include_empty_images (bool): Whether to include images with no annotations
        include_categories (list): List of category names to include (case-insensitive)
        num_workers (int): Number of parallel workers for processing images (optimal: 8-16 for I/O)

    Returns:
        None: Saves resized images and updated COCO JSON to specified paths
    """
    # Load the COCO annotation file
    with open(coco_json_path, "r") as f:
        coco = json.load(f)

    # Create output directory for resized images
    os.makedirs(output_images_dir, exist_ok=True)

    # Group annotations by image_id for efficient lookup
    annotations_by_image = {}
    for ann in coco["annotations"]:
        annotations_by_image.setdefault(ann["image_id"], []).append(ann)

    # Create mappings for category lookups
    category_id_to_name = {cat["id"]: cat["name"] for cat in coco["categories"]}
    name_to_id = {cat["name"].lower(): cat["id"] for cat in coco["categories"]}
    category_counts = {}

    # Process category filtering if specified
    if include_categories:
        # Convert category names to lowercase for case-insensitive matching
        include_categories = [cat.strip().lower() for cat in include_categories]
        category_ids_to_include = {
            name_to_id[name] for name in include_categories if name in name_to_id
        }

        print("🔍 Mapped include_categories:")
        for name in include_categories:
            cid = name_to_id.get(name)
            print(f"  {name} → {cid if cid is not None else '❌ Not Found'}")
    else:
        category_ids_to_include = None

    # Initialize lists for new dataset
    new_images = []
    new_annotations = []
    new_ann_id = 1

    # Process images in parallel using ThreadPoolExecutor (better for I/O-bound tasks)
    print(f"🚀 Processing {len(coco['images'])} images using {num_workers} workers...")

    start_time = time.time()
    processed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all image processing tasks
        futures = {
            executor.submit(
                process_single_image,
                img,
                images_dir,
                output_images_dir,
                max_size,
                min_side_len,
                min_area_others,
                include_empty_images,
                category_ids_to_include,
                category_id_to_name,
                annotations_by_image,
            ): img
            for img in coco["images"]
        }

        # Collect results as they complete
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(futures),
            desc="Processing images",
        ):
            result = future.result()
            processed_count += 1

            if result is not None:
                new_img_meta, new_anns = result

                # Update annotation IDs and collect category counts
                for new_ann in new_anns:
                    new_ann["id"] = new_ann_id
                    new_ann_id += 1
                    category_counts[new_ann["category_id"]] = (
                        category_counts.get(new_ann["category_id"], 0) + 1
                    )

                # Add to final dataset
                new_images.append(new_img_meta)
                new_annotations.extend(new_anns)

            # Log progress every 50 images
            if processed_count % 50 == 0:
                elapsed = time.time() - start_time
                rate = processed_count / elapsed if elapsed > 0 else 0
                print(
                    f"⚡ Processed {processed_count}/{len(coco['images'])} images at {rate:.1f} imgs/sec"
                )

    # Final timing info
    total_time = time.time() - start_time
    final_rate = len(coco["images"]) / total_time if total_time > 0 else 0
    print(f"⏱️  Total processing time: {total_time:.2f}s ({final_rate:.1f} imgs/sec)")

    # Create new COCO dataset structure
    new_coco = {
        "images": new_images,
        "annotations": new_annotations,
        "categories": coco["categories"],  # Keep original categories unchanged
    }

    # Save the new COCO JSON file
    with open(output_json_path, "w") as f:
        json.dump(new_coco, f, indent=2)

    print(f"\n✅ Done! Saved resized dataset to: {output_json_path}")

    # Print category statistics
    if category_counts:
        print("\n📊 Category counts after filtering:")
        for cat_id, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            cat_name = category_id_to_name.get(cat_id, f"ID {cat_id}")
            print(f"{cat_name:<25} → {count} annotations")
    else:
        print("\n⚠️ No annotations passed the filter criteria.")


def parse_args():
    """Parse command line arguments for the COCO resizing script."""
    parser = argparse.ArgumentParser(description="Resize COCO images and annotations")
    parser.add_argument(
        "--input-coco-json", required=True, help="Path to COCO JSON file"
    )
    parser.add_argument(
        "--input-image-dir", required=True, help="Directory with original images"
    )
    parser.add_argument(
        "--output-images-dir", required=True, help="Directory to save resized images"
    )
    parser.add_argument(
        "--output-coco-json", required=True, help="Path to save new COCO JSON"
    )
    parser.add_argument(
        "--max-size", type=int, default=1024, help="Max dimension (width/height)"
    )
    parser.add_argument(
        "--min-side-len",
        type=float,
        default=4,
        help="Minimum side length (px) for qualifying included categories",
    )
    parser.add_argument(
        "--min-area-others",
        type=float,
        default=100,
        help="Minimum squared area (px²) for other categories in selected images",
    )
    parser.add_argument(
        "--include-empty-images",
        action="store_true",
        help="Include images with no annotations",
    )
    parser.add_argument(
        "--include-categories",
        type=str,
        default=None,
        help="Comma-separated list of category names to include (e.g., 'person,car,dog')",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=8,
        help="Number of parallel workers for processing images (default: 8, optimal for I/O-bound tasks)",
    )
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_args()
    include_categories = (
        getattr(args, "include_categories", None).split(",")
        if getattr(args, "include_categories", None)
        else None
    )

    # Execute the resizing process
    resize_coco_dataset(
        coco_json_path=args.input_coco_json,
        images_dir=getattr(args, "input_image_dir"),
        output_images_dir=getattr(args, "output_images_dir"),
        output_json_path=getattr(args, "output_coco_json"),
        max_size=getattr(args, "max_size"),
        min_side_len=getattr(args, "min_side_len"),
        min_area_others=getattr(args, "min_area_others"),
        include_empty_images=getattr(args, "include_empty_images"),
        include_categories=include_categories,
        num_workers=getattr(args, "num_workers"),
    )


if __name__ == "__main__":
    main()
