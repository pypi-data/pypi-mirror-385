"""
Global constants and default paths for ZACH-ViT preprocessing and training.
Edit these paths as needed for your environment.
"""

# Default directory locations
TALOS_PATH = "../Data/TALOS"
OUTPUT_DIR_ROI = "../Data/Processed_ROI"
OUTPUT_DIR_VIS = "../Data/VIS"
OUTPUT_DIR_0_SSDA = "../Data/0_SSDA"
OUTPUT_DIR_MAIN = "../Data/2_3_SSDA"
INPUT_ROOT = OUTPUT_DIR_ROI

# Dataset structure
NUM_POSITIONS = 4  # Four probe positions per patient

# Default seeds for semi-supervised ShuffleStrides augmentation
PRIME_SEEDS = [2, 3]

# Default patient range for demonstration (edit as needed)
PATIENT_RANGE = [100, 122]
