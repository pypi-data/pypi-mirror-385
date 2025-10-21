#!/usr/bin/env python3
# ================================================================
# ZACH-ViT: CLI Trainer
# ================================================================
# Trains and evaluates the ZACH-ViT model directly from the terminal.
# Usage:
#   zachvit-train --base_dir ../Data --epochs 23 --batch_size 16 --threshold 53
# ================================================================

import argparse
from zachvit.zachvit_model_utils import run_zach_vit_time


def main():
    parser = argparse.ArgumentParser(
        description="Train and evaluate the ZACH-ViT model."
    )
    parser.add_argument(
        "--base_dir", required=True,
        help="Base directory containing the train/val/test subdirectories."
    )
    parser.add_argument(
        "--epochs", type=int, default=23,
        help="Number of training epochs (default: 23)."
    )
    parser.add_argument(
        "--batch_size", type=int, default=16,
        help="Batch size for training and evaluation (default: 16)."
    )
    parser.add_argument(
        "--threshold", type=int, default=53,
        help="Pixel intensity threshold for preprocessing (default: 53)."
    )
    parser.add_argument(
        "--class_weights", type=float, nargs=2, default=None,
        help="Optional class weights (e.g. --class_weights 1.0 1.5)"
    )

    args = parser.parse_args()

    print("🚀 Starting ZACH-ViT training...")
    print(f"Base directory: {args.base_dir}")
    print(f"Epochs: {args.epochs}, Batch size: {args.batch_size}, Threshold: {args.threshold}")

    # Convert class weights if provided
    class_weights = None
    if args.class_weights:
        class_weights = {0: args.class_weights[0], 1: args.class_weights[1]}
        print(f"Using class weights: {class_weights}")

    # Run training
    model, val_df, test_df = run_zach_vit_time(
        batch_size=args.batch_size,
        epochs=args.epochs,
        threshold=args.threshold,
        class_weights=class_weights,
        base_dir=args.base_dir,
    )

    print("✅ Training completed successfully!")
    print(f"Validation samples: {len(val_df)}, Test samples: {len(test_df)}")


if __name__ == "__main__":
    main()
