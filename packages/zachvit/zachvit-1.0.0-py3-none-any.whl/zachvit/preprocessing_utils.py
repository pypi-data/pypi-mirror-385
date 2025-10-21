"""
Preprocessing utilities for the ZACH-ViT pipeline.
Includes DICOM reading, ROI cropping, VIS generation, and ShuffleStrides augmentations.
Author: Athanasios Angelakis
"""

import os, itertools, random, numpy as np, matplotlib.pyplot as plt
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
from skimage.transform import resize
from PIL import Image

from zachvit.constants import TALOS_PATH, OUTPUT_DIR_ROI, OUTPUT_DIR_VIS, OUTPUT_DIR_0_SSDA, OUTPUT_DIR_MAIN, INPUT_ROOT, NUM_POSITIONS, PRIME_SEEDS


# -----------------------------------------
# Basic utilities
# -----------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def crop_roi(image, x_start=285, x_end=395, y_start=65, y_end=400):
    """Crop predefined pleural ROI (adjust coordinates per dataset)."""
    return image[y_start:y_end, x_start:x_end]

def compress_height(image, factor=0.5):
    """Reduce height by given factor (default: 50%)."""
    new_height = int(image.shape[0] * factor)
    return resize(image, (new_height, image.shape[1]), anti_aliasing=True)

def save_cropped_image(path, image, base_name, frame_idx):
    ensure_dir(path)
    out_path = os.path.join(path, f"{base_name}_frame{frame_idx:03d}.png")
    plt.imsave(out_path, image, cmap="gray", vmin=0, vmax=1)


# -----------------------------------------
# DICOM frame extraction
# -----------------------------------------
def process_dicom(patient_id, probe_idx):
    fname = f"{TALOS_PATH}{patient_id}/TALOS{patient_id}_{probe_idx}.dcm"
    base_name = f"TALOS{patient_id}_{probe_idx}"
    output_path = os.path.join(OUTPUT_DIR_ROI, f"TALOS{patient_id}", f"pos_{probe_idx}")
    ensure_dir(output_path)

    ds = dcmread(fname)
    pixel_array = ds.pixel_array.astype(np.float32)

    if "ModalityLUTSequence" in ds:
        pixel_array = apply_modality_lut(pixel_array, ds)
    if "VOILUTSequence" in ds:
        pixel_array = apply_voi_lut(pixel_array, ds)
    pixel_array /= np.max(pixel_array)

    for k in range(len(pixel_array)):
        frame = pixel_array[k] if pixel_array.ndim > 2 else pixel_array
        if frame.ndim == 3:
            frame = np.mean(frame, axis=-1)
        cropped = crop_roi(frame)
        compressed = compress_height(cropped)
        save_cropped_image(output_path, compressed, base_name, k)


# -----------------------------------------
# VIS Construction
# -----------------------------------------
def load_frames_from_position(path):
    if not os.path.exists(path):
        return None
    files = sorted([f for f in os.listdir(path) if f.endswith(".png")])
    frames = [np.array(Image.open(os.path.join(path, f)).convert("L")) / 255.0 for f in files]
    return frames if frames else None

def concatenate_frames_horizontally(frames):
    return np.concatenate(frames, axis=1) if frames else None

def zero_pad_to_width(image, target_width):
    h, w = image.shape
    if w < target_width:
        pad = target_width - w
        image = np.pad(image, ((0, 0), (0, pad)), mode='constant', constant_values=0)
    return image

def save_vis_image(patient_id, vis):
    vis_path = os.path.join(OUTPUT_DIR_VIS, f"TALOS{patient_id}_VIS.png")
    Image.fromarray((vis * 255).astype(np.uint8)).save(vis_path)
    print(f"Saved VIS for TALOS{patient_id} at {vis_path}")

def construct_vis_for_patient(patient_id):
    all_strides = []
    for pos in range(1, NUM_POSITIONS + 1):
        pos_path = os.path.join(INPUT_ROOT, f"TALOS{patient_id}", f"pos_{pos}")
        frames = load_frames_from_position(pos_path)
        if frames:
            stride = concatenate_frames_horizontally(frames)
            all_strides.append(stride)

    if not all_strides:
        print(f"Skipping {patient_id}: no valid positions.")
        return None

    max_w = max(s.shape[1] for s in all_strides)
    padded = [zero_pad_to_width(s, max_w) for s in all_strides]
    vis = np.concatenate(padded, axis=0)
    vis /= np.max(vis)
    save_vis_image(patient_id, vis)
    return vis


# -----------------------------------------
# 0-SSDA and SSDA_p Generation
# -----------------------------------------
def create_permuted_vis(patient_id):
    from zachvit.constants import NUM_POSITIONS
    strides = []
    for pos in range(1, NUM_POSITIONS + 1):
        path = os.path.join(INPUT_ROOT, f"TALOS{patient_id}", f"pos_{pos}")
        frames = load_frames_from_position(path)
        if frames is None:
            return []
        stride = concatenate_frames_horizontally(frames)
        strides.append(stride)
    max_w = max(s.shape[1] for s in strides)
    padded = [zero_pad_to_width(s, max_w) for s in strides]
    perms = list(itertools.permutations(range(NUM_POSITIONS)))

    for idx, perm in enumerate(perms):
        ordered = [padded[i] for i in perm]
        vis = np.concatenate(ordered, axis=0)
        vis /= np.max(vis)
        Image.fromarray((vis * 255).astype(np.uint8)).save(
            os.path.join(OUTPUT_DIR_0_SSDA, f"TALOS{patient_id}_perm_{idx:02d}.png")
        )


def create_permuted_vis_with_frame_shuffling(patient_id):
    from zachvit.constants import PRIME_SEEDS, NUM_POSITIONS
    for prime in PRIME_SEEDS:
        all_strides = []
        for pos in range(1, NUM_POSITIONS + 1):
            frames = load_frames_from_position(os.path.join(INPUT_ROOT, f"TALOS{patient_id}", f"pos_{pos}"))
            if frames is None:
                continue
            random.seed(prime)
            random.shuffle(frames)
            stride = concatenate_frames_horizontally(frames)
            all_strides.append(stride)
        if not all_strides:
            continue
        max_w = max(s.shape[1] for s in all_strides)
        padded = [zero_pad_to_width(s, max_w) for s in all_strides]
        perms = list(itertools.permutations(range(NUM_POSITIONS)))
        for idx, perm in enumerate(perms):
            vis = np.concatenate([padded[i] for i in perm], axis=0)
            vis /= np.max(vis)
            prime_dir = os.path.join(OUTPUT_DIR_MAIN, f"p{prime}")
            ensure_dir(prime_dir)
            Image.fromarray((vis * 255).astype(np.uint8)).save(
                os.path.join(prime_dir, f"TALOS{patient_id}_perm_{idx:02d}_p{prime}.png")
            )


def run_full_preprocessing_pipeline():
    """Convenience wrapper for CLI."""
    for pid in [100, 122]:  # Example
        for probe in range(1, 5):
            process_dicom(pid, probe)
        construct_vis_for_patient(pid)
        create_permuted_vis(pid)
        create_permuted_vis_with_frame_shuffling(pid)


# ================================================================
# Wrapper: full preprocessing pipeline
# ================================================================
def run_full_preprocessing_pipeline(
    talos_path="../Data/TALOS",
    output_dir_roi="../Data/Processed_ROI",
    output_dir_vis="../Data/VIS",
    output_dir_0_ssda="../Data/0_SSDA",
    prime_seeds=[2, 3],
    patient_range=(100, 122),
    num_positions=4
):
    """
    Runs all four preprocessing modules sequentially:
    1. ROI extraction
    2. VIS construction
    3. 0-SSDA
    4. SSDA_p (prime-seeded)
    """
    import time, os
    global TALOS_PATH, OUTPUT_DIR_ROI, OUTPUT_DIR_VIS, OUTPUT_DIR_0_SSDA, OUTPUT_DIR_MAIN
    global INPUT_ROOT, PRIME_SEEDS, NUM_POSITIONS, PATIENT_RANGE

    TALOS_PATH = talos_path if talos_path.endswith("/") else talos_path + "/"
    OUTPUT_DIR_ROI = output_dir_roi
    OUTPUT_DIR_VIS = output_dir_vis
    OUTPUT_DIR_0_SSDA = output_dir_0_ssda
    PRIME_SEEDS = prime_seeds
    PATIENT_RANGE = range(patient_range[0], patient_range[1] + 1)
    NUM_POSITIONS = num_positions

    os.makedirs(OUTPUT_DIR_ROI, exist_ok=True)
    os.makedirs(OUTPUT_DIR_VIS, exist_ok=True)
    os.makedirs(OUTPUT_DIR_0_SSDA, exist_ok=True)

    print(f"\n🩺 ZACH-ViT Preprocessing for {len(PATIENT_RANGE)} patients\n")

    # ------------------------------
    # 1️⃣ ROI Extraction
    # ------------------------------
    print("=== 1st Module: ROI Extraction ===")
    ts1 = time.time()
    for pid in PATIENT_RANGE:
        for pos in range(1, NUM_POSITIONS + 1):
            try:
                process_dicom(pid, pos)
            except Exception as e:
                print(f"⚠️ Skipping patient {pid}, position {pos}: {e}")
    te1 = time.time()
    print(f"Time for ROI Extraction: {round(te1 - ts1, 2)}s\n")

    time.sleep(3)

    # ------------------------------
    # 2️⃣ VIS Construction
    # ------------------------------
    print("=== 2nd Module: VIS Construction ===")
    INPUT_ROOT = OUTPUT_DIR_ROI
    ts2 = time.time()
    for pid in PATIENT_RANGE:
        construct_vis_for_patient(pid)
    te2 = time.time()
    print(f"Time for VIS: {round(te2 - ts2, 2)}s\n")

    time.sleep(3)

    # ------------------------------
    # 3️⃣ 0-SSDA
    # ------------------------------
    print("=== 3rd Module: ShuffleStrides (0-SSDA) ===")
    INPUT_ROOT = OUTPUT_DIR_ROI
    ts3 = time.time()
    for pid in PATIENT_RANGE:
        create_permuted_vis(pid)
    te3 = time.time()
    print(f"Time for 0-SSDA: {round(te3 - ts3, 2)}s\n")

    time.sleep(3)

    # ------------------------------
    # 4️⃣ SSDA_p (Prime-seeded)
    # ------------------------------
    print("=== 4th Module: SSDA_p ===")
    INPUT_ROOT = OUTPUT_DIR_ROI
    OUTPUT_DIR_MAIN = os.path.join("../Data", "_".join(str(p) for p in PRIME_SEEDS) + "_SSDA")
    os.makedirs(OUTPUT_DIR_MAIN, exist_ok=True)
    for prime in PRIME_SEEDS:
        os.makedirs(os.path.join(OUTPUT_DIR_MAIN, f"p{prime}"), exist_ok=True)
    ts4 = time.time()
    for pid in PATIENT_RANGE:
        create_permuted_vis_with_frame_shuffling(pid)
    te4 = time.time()

    print(f"Time for SSDA_p: {round(te4 - ts4, 2)}s")
    print(f"✅ Total preprocessing time: {round(te4 - ts1, 2)}s\n")
