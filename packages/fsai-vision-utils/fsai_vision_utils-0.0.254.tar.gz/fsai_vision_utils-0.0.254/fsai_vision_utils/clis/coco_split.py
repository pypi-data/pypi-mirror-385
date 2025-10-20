import argparse
import json
import os
from collections import defaultdict
from itertools import chain

import numpy as np
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit


def parse_args():
    p = argparse.ArgumentParser(
        description="Split COCO dataset into train/val/test with optional background mixing (fast)"
    )
    p.add_argument("--input-coco-json", type=str, required=True)
    p.add_argument("--output-coco-dir", type=str, required=True)
    p.add_argument("--train-ratio", type=float, default=0.7)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--test-ratio", type=float, default=0.15)
    p.add_argument("--bg-train-frac", type=float, default=0.2)
    p.add_argument("--bg-val-frac", type=float, default=0.1)
    p.add_argument("--bg-test-frac", type=float, default=0.1)
    p.add_argument("--random-seed", type=int, default=42)
    p.add_argument("--min-train-per-class", type=int, default=5)
    # Optional: skip the (potentially expensive) min-per-class enforcement
    p.add_argument("--skip-min-train-enforce", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    rng = np.random.RandomState(args.random_seed)

    # --- Load COCO ---
    with open(args.input_coco_json, "r") as f:
        data = json.load(f)

    images = data["images"]
    annotations = data["annotations"]
    categories = data["categories"]

    id_to_image = {img["id"]: img for img in images}
    all_image_ids = set(id_to_image.keys())

    # image -> set(categories) for positives
    image_to_labels = defaultdict(set)
    for ann in annotations:
        image_to_labels[ann["image_id"]].add(ann["category_id"])

    positive_image_ids = np.fromiter(
        (iid for iid, labs in image_to_labels.items() if labs),
        dtype=np.int64,
        count=len(image_to_labels),
    )
    positive_image_ids = positive_image_ids[positive_image_ids != 0]  # guard if count overestimated
    positive_image_ids.sort()

    background_image_ids = np.array(sorted(all_image_ids - set(positive_image_ids)), dtype=np.int64)

    # Build Y (multi-hot) for positives only
    cat_id_to_index = {cat["id"]: idx for idx, cat in enumerate(categories)}
    n_pos = len(positive_image_ids)
    n_cls = len(categories)
    Y_pos = np.zeros((n_pos, n_cls), dtype=np.int8)
    for i, img_id in enumerate(positive_image_ids):
        for cid in image_to_labels[img_id]:
            Y_pos[i, cat_id_to_index[cid]] = 1

    # Ratios (for POSITIVES)
    tr, vr, te = args.train_ratio, args.val_ratio, args.test_ratio
    if not np.isclose(tr + vr + te, 1.0):
        raise ValueError("train_ratio + val_ratio + test_ratio must sum to 1.")

    # --- FAST stratified splits on positives only ---
    # Pass a dummy X to avoid carrying heavy dicts
    X_dummy = np.zeros((n_pos, 1), dtype=np.int8)

    sss1 = MultilabelStratifiedShuffleSplit(
        n_splits=1, test_size=(1 - tr), random_state=args.random_seed
    )
    train_pos_idx, temp_pos_idx = next(sss1.split(X_dummy, Y_pos))

    if te > 0:
        val_size = vr / (vr + te)
        sss2 = MultilabelStratifiedShuffleSplit(
            n_splits=1, test_size=(1 - val_size), random_state=args.random_seed
        )
        val_local_idx, test_local_idx = next(sss2.split(X_dummy[temp_pos_idx], Y_pos[temp_pos_idx]))
        val_pos_idx = temp_pos_idx[val_local_idx]
        test_pos_idx = temp_pos_idx[test_local_idx]
    else:
        val_pos_idx = temp_pos_idx
        test_pos_idx = np.array([], dtype=np.int64)

    # Work as sets for O(1) membership & edits
    train_pos_set = set(train_pos_idx.tolist())
    val_pos_set = set(val_pos_idx.tolist())
    test_pos_set = set(test_pos_idx.tolist())

    # --- Ensure min per-class (positives only) ---
    if not args.skip_min_train_enforce and args.min_train_per_class > 0:
        min_needed = args.min_train_per_class
        class_counts = Y_pos[list(train_pos_set)].sum(axis=0)

        # Precompute per-class positive indices to avoid repeated np.where
        pos_indices_by_class = [set(np.nonzero(Y_pos[:, c])[0].tolist()) for c in range(n_cls)]

        for c in range(n_cls):
            deficit = int(min_needed - class_counts[c])
            if deficit <= 0:
                continue

            # candidates not already in train
            candidates = list((pos_indices_by_class[c] - train_pos_set))
            rng.shuffle(candidates)

            # Prefer pulling from val, then test
            moved = 0
            for pool_set in (val_pos_set, test_pos_set):
                if moved >= deficit:
                    break
                # Select from intersection (fast set ops)
                pickable = [idx for idx in candidates if idx in pool_set]
                take = pickable[: (deficit - moved)]
                for idx in take:
                    pool_set.remove(idx)
                    train_pos_set.add(idx)
                moved += len(take)

            # Update counts for this class only (cheap)
            class_counts[c] = Y_pos[list(train_pos_set), c].sum()

    # Final positive image ids per split
    train_pos_img_ids = positive_image_ids[list(train_pos_set)]
    val_pos_img_ids = positive_image_ids[list(val_pos_set)]
    test_pos_img_ids = positive_image_ids[list(test_pos_set)]

    # --- Background sampling (single shuffle, slice) ---
    rng.shuffle(background_image_ids)
    n_bg_train = int(round(args.bg_train_frac * len(train_pos_img_ids)))
    n_bg_val = int(round(args.bg_val_frac * len(val_pos_img_ids)))
    n_bg_test = int(round(args.bg_test_frac * len(test_pos_img_ids))) if te > 0 else 0

    # Allocate sequentially from the shuffled pool (no overlap by construction)
    start = 0
    train_bg_ids = background_image_ids[start : start + n_bg_train]
    start += n_bg_train
    val_bg_ids = background_image_ids[start : start + n_bg_val]
    start += n_bg_val
    test_bg_ids = background_image_ids[start : start + n_bg_test] if te > 0 else np.array([], dtype=np.int64)

    # --- Build final splits (ids only) ---
    train_ids = np.concatenate([train_pos_img_ids, train_bg_ids])
    val_ids = np.concatenate([val_pos_img_ids, val_bg_ids])
    test_ids = np.concatenate([test_pos_img_ids, test_bg_ids]) if te > 0 else np.array([], dtype=np.int64)

    # --- Preindex annotations by image_id for fast gather ---
    anns_by_image = defaultdict(list)
    for ann in annotations:
        anns_by_image[ann["image_id"]].append(ann)

    def make_split(ids_np):
        # COCO expects dicts for images
        imgs = [id_to_image[int(iid)] for iid in ids_np]
        # Only positives have anns; backgrounds produce none
        anns_iter = (anns_by_image.get(int(iid), []) for iid in ids_np)
        anns = list(chain.from_iterable(anns_iter))
        return {"images": imgs, "annotations": anns, "categories": categories}

    os.makedirs(args.output_coco_dir, exist_ok=True)

    def save_json(name, payload):
        out = os.path.join(args.output_coco_dir, f"{name}.json")
        print(f"Writing {name} -> {out} (images={len(payload['images'])}, anns={len(payload['annotations'])})")
        # compact separators speeds dumping a bit and reduces file size
        with open(out, "w") as f:
            json.dump(payload, f, separators=(",", ":"))

    save_json("train", make_split(train_ids))
    save_json("val", make_split(val_ids))
    if te > 0:
        save_json("test", make_split(test_ids))
    else:
        print("No test split to save (test_ratio = 0)")

    # Summary
    print("\nSummary:")
    print(f"Positives: train={len(train_pos_img_ids)} val={len(val_pos_img_ids)} test={len(test_pos_img_ids)}")
    print(f"Backgrounds: train={len(train_bg_ids)} val={len(val_bg_ids)} test={len(test_bg_ids)}")
    print(f"Totals: train={len(train_ids)} val={len(val_ids)} test={len(test_ids)}")


if __name__ == "__main__":
    main()
