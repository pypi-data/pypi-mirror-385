#!/usr/bin/env python3
"""
Command-line interface for running the full ZACH-ViT preprocessing pipeline.

Example:
---------
zachvit-preprocess \
  --talos_path ../Data/TALOS \
  --output_dir ../Data \
  --patient_start 100 \
  --patient_end 122 \
  --primes 2 3
"""

import argparse
import os
import time

from zachvit import constants as C
from zachvit.preprocessing_utils import (
    process_dicom,
    construct_vis_for_patient,
    create_permuted_vis,
    create_permuted_vis_with_frame_shuffling
)

def run_full_preprocessing_pipeline():
    """Run the complete 4-stage preprocessing pipeline."""
    print(f"🚀 Starting ZACH-ViT preprocessing for patients {C.PATIENT_RANGE}...\n")
    total_start = time.time()

    # ------------------------------
    # 1️⃣ ROI Extraction
    # ------------------------------
    print("📍 1st Module: ROI Extraction")
    os.makedirs(C.OUTPUT_DIR_ROI, exist_ok=True)
    t1 = time.time()
    for pid in C.PATIENT_RANGE:
        for pos in range(1, C.NUM_POSITIONS + 1):
            try:
                process_dicom(pid, pos)
            except Exception as e:
                print(f"⚠️ Skipping patient {pid}, position {pos}: {e}")
    print(f"✅ ROI Extraction completed in {round(time.time() - t1, 2)} s.\n")

    # ------------------------------
    # 2️⃣ VIS Construction
    # ------------------------------
    print("🖼️ 2nd Module: VIS Construction")
    os.makedirs(C.OUTPUT_DIR_VIS, exist_ok=True)
    t2 = time.time()
    for pid in C.PATIENT_RANGE:
        construct_vis_for_patient(pid)
    print(f"✅ VIS Construction completed in {round(time.time() - t2, 2)} s.\n")

    # ------------------------------
    # 3️⃣ 0-SSDA (Stride Permutations)
    # ------------------------------
    print("🔄 3rd Module: ShuffleStrides 0-SSDA")
    os.makedirs(C.OUTPUT_DIR_0_SSDA, exist_ok=True)
    t3 = time.time()
    for pid in C.PATIENT_RANGE:
        create_permuted_vis(pid)
    print(f"✅ 0-SSDA completed in {round(time.time() - t3, 2)} s.\n")

    # ------------------------------
    # 4️⃣ SSDA_p (Semi-supervised)
    # ------------------------------
    print("🧮 4th Module: Semi-supervised SSDA_p")
    os.makedirs(C.OUTPUT_DIR_MAIN, exist_ok=True)
    for p in C.PRIME_SEEDS:
        os.makedirs(os.path.join(C.OUTPUT_DIR_MAIN, f"p{p}"), exist_ok=True)

    t4 = time.time()
    for pid in C.PATIENT_RANGE:
        create_permuted_vis_with_frame_shuffling(pid)
    print(f"✅ SSDA_p completed in {round(time.time() - t4, 2)} s.\n")

    total_end = time.time()
    print(f"🎯 Total preprocessing time: {round(total_end - total_start, 2)} seconds.")
    print("✅ All preprocessing steps completed successfully!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run the full ZACH-ViT preprocessing pipeline."
    )

    parser.add_argument("--talos_path", type=str, required=True,
                        help="Path to the folder containing TALOS patient DICOM directories.")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Base directory where processed data will be saved.")
    parser.add_argument("--patient_start", type=int, required=True,
                        help="Starting patient ID (inclusive).")
    parser.add_argument("--patient_end", type=int, required=True,
                        help="Ending patient ID (inclusive).")
    parser.add_argument("--primes", type=int, nargs="+", default=[2, 3],
                        help="Prime numbers to use as random seeds for SSDA_p augmentation (default: 2 3).")

    args = parser.parse_args()

    # Dynamically override constants
    C.TALOS_PATH = os.path.abspath(args.talos_path)
    C.OUTPUT_DIR_ROI = os.path.join(args.output_dir, "Processed_ROI")
    C.OUTPUT_DIR_VIS = os.path.join(args.output_dir, "VIS")
    C.OUTPUT_DIR_0_SSDA = os.path.join(args.output_dir, "0_SSDA")
    C.OUTPUT_DIR_MAIN = os.path.join(args.output_dir, "_".join(str(p) for p in args.primes) + "_SSDA")
    C.INPUT_ROOT = C.OUTPUT_DIR_ROI
    C.PRIME_SEEDS = args.primes
    C.PATIENT_RANGE = list(range(args.patient_start, args.patient_end + 1))

    # Run pipeline
    run_full_preprocessing_pipeline()


if __name__ == "__main__":
    main()
