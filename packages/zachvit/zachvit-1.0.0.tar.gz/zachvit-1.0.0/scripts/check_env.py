# ==============================================================
# ZACH-ViT: Zero-token Adaptive Compact Hierarchical Vision Transformer for Lung Ultrasound
# VIS, 0-SSDA and SSDA_p
# Paper:   https://arxiv.org/abs/2510.17650
# Code:    https://github.com/Bluesman79/ZACH-ViT
# License: Apache License 2.0
# Author:  Athanasios Angelakis
# ==============================================================
"""
check_environment.py
--------------------
Comprehensive environment inspection script for ZACH-ViT.
Prints versions of all required libraries, OS details, Python info, 
TensorFlow GPU configuration, and CUDA/cuDNN status.
"""

import os
import sys
import platform
import importlib
import multiprocessing
import datetime

# ==============================================================
# Collect System Info
# ==============================================================
print("=" * 70)
print("🔍  ZACH-ViT Environment Inspection")
print("=" * 70)
print(f"Run time:      {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python:        {sys.version.split()[0]}")
print(f"Platform:      {platform.system()} {platform.release()} ({platform.machine()})")
print(f"CPU cores:     {multiprocessing.cpu_count()}")
print(f"Processor:     {platform.processor() or 'N/A'}")
print("-" * 70)

# ==============================================================
# TensorFlow and GPU Information
# ==============================================================
try:
    import tensorflow as tf
    print(f"TensorFlow:    {tf.__version__}")
    print(f"Keras:         {tf.keras.__version__}")
    
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"GPU detected:  ✅ {len(gpus)} device(s)")
        for i, gpu in enumerate(gpus):
            details = tf.config.experimental.get_device_details(gpu)
            name = details.get('device_name', 'Unknown GPU')
            print(f"  - GPU {i}: {name}")
        print(f"Built with CUDA:   {tf.test.is_built_with_cuda()}")
        print(f"Built with cuDNN:  {tf.test.is_built_with_cudnn()}")
    else:
        print("GPU detected:  ⚠️ None (CPU-only mode)")
except Exception as e:
    print(f"TensorFlow GPU check error: {e}")

print("-" * 70)

# ==============================================================
# Core Dependencies (used in preprocessing and model)
# ==============================================================
modules = {
    "numpy": "np",
    "pandas": "pd",
    "matplotlib": "plt",
    "pydicom": None,
    "skimage": None,
    "PIL": None,
    "tensorflow": "tf",
    "scikit-learn": "sklearn",
    "IPython": None
}

def get_version(name):
    try:
        if name == "PIL":
            import PIL
            return PIL.__version__
        elif name == "skimage":
            import skimage
            return skimage.__version__
        elif name == "scikit-learn":
            import sklearn
            return sklearn.__version__
        else:
            mod = importlib.import_module(name)
            return getattr(mod, "__version__", "unknown")
    except ImportError:
        return "not installed"

rows = []
for m in modules:
    rows.append((m, get_version(m)))

max_len = max(len(r[0]) for r in rows)
for pkg, ver in rows:
    print(f"{pkg.ljust(max_len+2)}: {ver}")

print("-" * 70)

# ==============================================================
# Optional: Save report
# ==============================================================
SAVE_REPORT = True
if SAVE_REPORT:
    report_path = "environment_report.txt"
    with open(report_path, "w") as f:
        f.write("ZACH-ViT Environment Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Run time: {datetime.datetime.now()}\n")
        f.write(f"Python: {sys.version.split()[0]}\n")
        f.write(f"Platform: {platform.system()} {platform.release()} ({platform.machine()})\n")
        f.write(f"CPU cores: {multiprocessing.cpu_count()}\n")
        f.write(f"Processor: {platform.processor()}\n\n")
        f.write(f"TensorFlow: {tf.__version__}\n")
        f.write(f"Keras: {tf.keras.__version__}\n")
        f.write("GPU info:\n")
        if gpus:
            for i, gpu in enumerate(gpus):
                details = tf.config.experimental.get_device_details(gpu)
                name = details.get('device_name', 'Unknown GPU')
                f.write(f"  GPU {i}: {name}\n")
        else:
            f.write("  None detected\n")
        f.write("\nPackage versions:\n")
        for pkg, ver in rows:
            f.write(f"{pkg}: {ver}\n")
    print(f"✅ Environment report saved to: {report_path}")

print("=" * 70)
print("✅ ZACH-ViT environment inspection completed successfully.")
print("=" * 70)
