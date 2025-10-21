[![arXiv](https://img.shields.io/badge/arXiv-2510.17650-b31b1b.svg)](https://arxiv.org/abs/2510.17650)
[![DOI](https://img.shields.io/badge/DOI-10.48550%2FarXiv.2510.17650-blue)](https://doi.org/10.48550/arXiv.2510.17650)

# 🧩 ZACH-ViT: Zero-Token Adaptive Compact Hierarchical Vision Transformer with ShuffleStrides Data Augmentation (SSDA)

Official implementation of **ZACH-ViT**, a lightweight Vision Transformer for robust classification of lung ultrasound videos, and the **ShuffleStrides Data Augmentation (SSDA)** algorithm.  

Introduced in *Angelakis et al., "ZACH-ViT: A Zero-Token Vision Transformer with ShuffleStrides Data Augmentation for Robust Lung Ultrasound Classification", (arXiv:2510.17650)*.

---

## 📘 Overview

**ZACH-ViT** redefines Vision Transformer design for small, heterogeneous medical datasets.

- ❌ **No positional embeddings or class tokens** — zero-token paradigm for order-agnostic feature extraction  
- ⚙️ **Adaptive hierarchical residuals** for stable feature learning  
- 🌍 **Global pooling** for invariant image-level representations  
- 🔄 **ShuffleStrides Data Augmentation (SSDA)** — permutation-based semi-supervised augmentation preserving clinical plausibility  

---

## 🧠 Full Pipeline

This repository provides a fully reproducible pipeline for **preprocessing**, **training**, and **evaluation**, available as both **Jupyter notebooks** and **pure Python scripts**:

1. **ROI extraction** from raw TALOS DICOM ultrasound recordings  
2. **VIS (Video Image Sequence)** creation per patient, concatenating frame strides from all probe positions  
3. **ShuffleStrides semi-supervised data augmentation (0-SSDA)** for robust domain generalization  
4. **ShuffleStrides semi-supervised data augmentation (SSDA_p)** for permutation-based learning enhancement  
5. **ZACH-ViT** training, validation, and testing with automatic time and metric reporting    

---

## 📂 Data Directory Structure

The `../Data` directory evolves from raw patient data to fully structured training datasets.

### 🧩 Before Preprocessing
```bash
../Data/
├── TALOS100/
└── TALOS122/
```

**Description:**
- Each folder contains the raw ultrasound recordings (`.dcm` format) for one patient across the four transducer positions
- Data is stored in DICOM format, which is standard for medical imaging

### 🔄 After Preprocessing
```bash
../Data/
├── 0_SSDA/             # Dataset with all 4! stride permutations (first SSDA regime)
├── 2_3_SSDA/           # Second-level SSDA with partial stride reordering
├── imgs/               # Auto-saved training and validation plots (timestamped)
├── Processed_ROI/      # Extracted pleural ROI frames per position
├── TALOS100/           # Original raw DICOMs (kept for reference)
├── TALOS122/           # Original raw DICOMs (kept for reference)
├── VIS/                # Generated VIS images per patient (concatenated stride representation)
├── train/
│   ├── 0/              # Non-CPE
│   └── 1/              # CPE
├── val/
│   ├── 0/
│   └── 1/
└── test/
    ├── 0/
    └── 1/
```

### 🧠 Notes

- **VIS** images represent one patient by vertically stacking the four position-specific stride sequences.
- **SSDA** folders contain automatically generated semi-supervised augmentations.
- **train**, **val**, and **test** directories follow the standard Keras `ImageDataGenerator` convention with subfolders `0` and `1` for binary classes.
- All training curves from the ZACH-ViT notebook are automatically saved in `../Data/imgs/` with a date-time prefix (e.g., `ZACH_ViT_training_20251014_183502.png`).
---

## ⚙️ Installation

ZACH-ViT provides both Jupyter notebook and Command-Line Interface (CLI) execution for full reproducibility.

## 📓 Using Jupyter Notebooks
1. Run Preprocessing
   Open and run the notebook: `Preprocessing_ROI_VIS_0_SSDA_SSDA_p`.

   This will:
   *  Extract and crop the DICOM ROIs
   *  Generate VIS images
   *  Create 0-SSDA and SSDA_p datasets
   *  
2. Train and evaluate ZACH-ViT
   Open and run the notebook: `ZACH-ViT`.

   This will:
   * Train the model
   * Report training/inference times
   * Save learning curves automatically in `../Data/imgs/`

## 💻 Using CLI
```bash
# Clone the repository
git clone https://github.com/Bluesman79/ZACH-ViT.git
cd ZACH-ViT

# (Optional) Create a clean virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install in editable/development mode
pip install -e .

# Verify installation
python -c 'import zachvit; print("✅ ZACH-ViT installed successfully!")'
```

This installs two CLI tools globally in the environment:
* `zachvit-preprocess`: runs the entire preprocessing and data augmentation pipeline
* `zachvit-train`: runs training and evaluation of the ZACH-ViT model


## 🧩 CLI Usage
### 🧠 Preprocessing Pipeline

The preprocessing CLI `zachvit-preprocess` automatically runs all four modules:

1. ROI extraction and height compression
2. VIS (Video Image Sequence) creation
3. 0-SSDA (stride permutation augmentation)
4. SSDAₚ (semi-supervised prime-based augmentation)
   
**Example**
```bash
zachvit-preprocess \
  --talos_path ../Data/TALOS \
  --output_dir ../Data \
  --patient_start 100 \
  --patient_end 122 \
  --primes 2 3
```

| Argument          | Description                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| `--talos_path`    | Path to folder containing raw TALOS DICOM patient directories (`TALOS100/`, `TALOS122/`, etc.) |
| `--output_dir`    | Base directory where all processed data will be saved (`../Data/`)                             |
| `--patient_start` | Starting patient ID (inclusive)                                                                |
| `--patient_end`   | Ending patient ID (inclusive)                                                                  |
| `--primes`        | (Optional) Prime numbers for SSDAₚ augmentation seeds — default: `2 3`                         |

The CLI will automatically generate:
```bash
../Data/
├── Processed_ROI/
├── VIS/
├── 0_SSDA/
├── 2_3_SSDA/
└── imgs/           # Training curves and logs
```

### 🧩 Training ZACH-ViT

The training CLI `zachvit-train` runs end-to-end training, validation, and testing of ZACH-ViT on the prepared datasets.
It also reports total training time, mean inference time per batch, and saves ROC-AUC/accuracy curves automatically.

**Example**
```bash
zachvit-train \
  --base_dir ../Data \
  --epochs 23 \
  --batch_size 16 \
  --threshold 53
  --class_weights 1.0 2.5
```

| Argument          | Description                                                                |
| ----------------- | -------------------------------------------------------------------------- |
| `--base_dir`      | Root data directory containing `train/`, `val/`, and `test/`               |
| `--epochs`        | Number of training epochs (default: 23)                                    |
| `--batch_size`    | Batch size for training (default: 16)                                      |
| `--threshold`     | Intensity threshold (0–255) for background removal (default: 53)           |
| `--class_weights` | Optional class weights for labels 0 and 1 (e.g. `--class_weights 1.0 2.5`) |

### 📊 Output

After training:

* All performance plots (loss, accuracy, AUC) are saved in ../Data/imgs/
* Model metrics (AUC, sensitivity, specificity, F1-score) are printed at the end
* Inference time (validation/test) and average epoch duration are reported

### 💡 Example Workflow
```bash
# Step 1: Run preprocessing
zachvit-preprocess --talos_path ../Data/TALOS --output_dir ../Data --patient_start 100 --patient_end 122 --primes 2 3

# Step 2: Train and evaluate ZACH-ViT
zachvit-train --base_dir ../Data --epochs 23 --batch_size 16 --threshold 53 --class_weights 1.0 2.5

```

Both scripts mirror the logic of the notebooks and save identical output structures.

## 🔁 Data Flow Overview
```bash
TALOS DICOM
   │
   ▼
ROI Extraction
   │
   ▼
VIS Image Generation
   │
   ▼
ShuffleStrides Data Augmentation (SSDA)
   │
   ▼
Train / Val / Test Sets
   │
   ▼
ZACH-ViT Training and Evaluation
```

## 🧾 Citation
If you use this work, please cite:

```bibtex
@article{angelakis2025zachvit,
  author    = {Angelakis, A. et al.},
  title     = {ZACH-ViT: A Zero-Token Vision Transformer with ShuffleStrides Data Augmentation for Robust Lung Ultrasound Classification},
  journal   = {arXiv preprint arXiv:2510.17650},
  year      = {2025},
  doi       = {https://doi.org/10.48550/arXiv.2510.17650},
  url       = {https://arxiv.org/abs/2510.17650}
}
```
