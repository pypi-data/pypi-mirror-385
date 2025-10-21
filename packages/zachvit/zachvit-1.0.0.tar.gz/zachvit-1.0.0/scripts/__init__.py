"""
ZACH-ViT: Zero-Token Adaptive Compact Hierarchical Vision Transformer
=====================================================================

Official implementation of ZACH-ViT and ShuffleStrides Data Augmentation (SSDA)
for robust and explainable classification of lung ultrasound videos.

Developed by:
    Athanasios Angelakis, 2025
    https://github.com/Bluesman79/ZACH-ViT

License:
    Apache License 2.0
"""

__version__ = "1.0.0"
__author__ = "Athanasios Angelakis"
__email__ = "ath.angelakis@gmail.com"
__license__ = "Apache 2.0"

# Expose key APIs
from .preprocessing_utils import run_full_preprocessing_pipeline
from .model_utils import run_zach_vit_time
