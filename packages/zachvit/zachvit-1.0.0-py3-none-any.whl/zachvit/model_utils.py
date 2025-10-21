"""
ZACH-ViT: Zero-Token Adaptive Compact Hierarchical Vision Transformer
with ShuffleStrides Data Augmentation (SSDA)
Author: Athanasios Angelakis
License: Apache 2.0
Date: 2025-10-21
Paper: https://arxiv.org/abs/2510.17650
"""

import os, time, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.layers import (
    Lambda, Reshape, Dense, Dropout, LayerNormalization,
    MultiHeadAttention, GlobalAveragePooling1D, Input
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.metrics import AUC
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, roc_auc_score, f1_score, accuracy_score
from IPython.display import clear_output
from datetime import datetime


# ==============================================================
# Environment setup for deterministic and reproducible runs
# ==============================================================
os.environ.pop("TF_DETERMINISTIC_OPS", None)
os.environ["TF_XLA_FLAGS"] = "--tf_xla_enable_xla_devices=false --tf_xla_auto_jit=0"
os.environ.pop("TF_CUDNN_DETERMINISTIC", None)
tf.config.optimizer.set_jit(False)
try:
    tf.config.experimental.enable_op_determinism(False)
except Exception:
    pass

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except Exception as e:
        print("Memory growth setup error:", e)

# Reproducibility
np.random.seed(7)
tf.random.set_seed(7)
tf.keras.utils.set_random_seed(7)
warnings.filterwarnings("ignore")


# ==============================================================
# Visualization Callbacks
# ==============================================================
class PlotTrainingHistory(tf.keras.callbacks.Callback):
    """Callback to visualize and save training metrics."""
    def __init__(self, save_dir="../Data/imgs"):
        super().__init__()
        self.history = {'loss': [], 'val_loss': [], 'accuracy': [], 'val_accuracy': [], 'auc': [], 'val_auc': []}
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        for key in self.history.keys():
            self.history[key].append(logs.get(key))
        clear_output(wait=True)
        plt.figure(figsize=(18, 5))

        plt.subplot(1, 3, 1)
        plt.plot(self.history['loss'], label='Train')
        plt.plot(self.history['val_loss'], label='Val')
        plt.legend(); plt.title("Loss")

        plt.subplot(1, 3, 2)
        plt.plot(self.history['accuracy'], label='Train')
        plt.plot(self.history['val_accuracy'], label='Val')
        plt.legend(); plt.title("Accuracy")

        plt.subplot(1, 3, 3)
        plt.plot(self.history['auc'], label='Train')
        plt.plot(self.history['val_auc'], label='Val')
        plt.legend(); plt.title("ROC-AUC")

        plt.tight_layout()
        plt.show()

    def on_train_end(self, logs=None):
        """Save the training curves with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ZACH_ViT_training_{timestamp}.png"
        save_path = os.path.join(self.save_dir, filename)

        plt.figure(figsize=(18, 5))
        for i, (title, key1, key2) in enumerate([
            ("Loss", "loss", "val_loss"),
            ("Accuracy", "accuracy", "val_accuracy"),
            ("ROC-AUC", "auc", "val_auc")
        ]):
            plt.subplot(1, 3, i + 1)
            plt.plot(self.history[key1], label='Train')
            plt.plot(self.history[key2], label='Val')
            plt.legend(); plt.title(title)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📈 Training curves saved at: {save_path}")


class EpochTimeLogger(tf.keras.callbacks.Callback):
    """Callback to log per-epoch training time."""
    def on_train_begin(self, logs=None):
        self.epoch_times = []

    def on_epoch_begin(self, epoch, logs=None):
        self.start_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        duration = time.time() - self.start_time
        self.epoch_times.append(duration)
        print(f"Epoch {epoch + 1} took {duration:.2f} seconds")

    def on_train_end(self, logs=None):
        mean_time, std_time = np.mean(self.epoch_times), np.std(self.epoch_times)
        print(f"\nAverage epoch time: {mean_time:.2f} ± {std_time:.2f} seconds "
              f"over {len(self.epoch_times)} epochs\n")


# ==============================================================
# Data pipeline
# ==============================================================
def create_data_generators(base_dir, batch_size=128, target_size=(224, 224), threshold=53):
    """Create standardized ImageDataGenerators for train/val/test."""
    def thresholding(image):
        image = image.copy()
        image[image < (threshold / 255.0)] = 0
        return image

    train_gen = ImageDataGenerator(rescale=1./255, preprocessing_function=thresholding).flow_from_directory(
        os.path.join(base_dir, "train"), target_size=target_size, batch_size=batch_size,
        class_mode="binary", seed=7)
    val_gen = ImageDataGenerator(rescale=1./255, preprocessing_function=thresholding).flow_from_directory(
        os.path.join(base_dir, "val"), target_size=target_size, batch_size=batch_size,
        class_mode="binary", shuffle=False, seed=7)
    test_gen = ImageDataGenerator(rescale=1./255, preprocessing_function=thresholding).flow_from_directory(
        os.path.join(base_dir, "test"), target_size=target_size, batch_size=batch_size,
        class_mode="binary", shuffle=False, seed=7)

    return train_gen, val_gen, test_gen


# ==============================================================
# Metrics and Evaluation
# ==============================================================
def evaluate_model_and_create_dfs(model, val_gen, test_gen):
    def predict_df(gen):
        preds = model.predict(gen, verbose=0).ravel()
        return pd.DataFrame({
            "Filename": gen.filenames,
            "True Label": gen.classes,
            "Pred Label": (preds > 0.5).astype(int),
            "Pred Proba": preds
        })
    return predict_df(val_gen), predict_df(test_gen)


def print_metrics(df, name="Validation"):
    auc = roc_auc_score(df["True Label"], df["Pred Proba"])
    f1 = f1_score(df["True Label"], df["Pred Label"])
    acc = accuracy_score(df["True Label"], df["Pred Label"])
    tn, fp, fn, tp = confusion_matrix(df["True Label"], df["Pred Label"]).ravel()
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    print(f"{name} - AUC: {auc:.3f}, Acc: {acc:.3f}, Sens: {sens:.3f}, Spec: {spec:.3f}, F1: {f1:.3f}")


# ==============================================================
# ZACH-ViT Architecture
# ==============================================================
def build_custom_vit_model(input_shape=(224, 224, 3), patch_size=16, num_heads=8,
                           transformer_units=[128, 64], mlp_head_units=[128, 64]):
    """Build the ZACH-ViT architecture."""
    inputs = Input(shape=input_shape)
    n_h, n_w = input_shape[0] // patch_size, input_shape[1] // patch_size
    num_patches, patch_dims = n_h * n_w, patch_size * patch_size * input_shape[-1]

    patches = Lambda(lambda imgs: tf.image.extract_patches(
        images=imgs, sizes=[1, patch_size, patch_size, 1],
        strides=[1, patch_size, patch_size, 1],
        rates=[1, 1, 1, 1], padding="VALID"))(inputs)
    patches = Reshape((num_patches, patch_dims))(patches)
    x = Dense(units=transformer_units[0], activation="relu")(patches)

    for units in transformer_units:
        key_dim = max(1, units // num_heads)
        y = LayerNormalization(epsilon=1e-6)(x)
        y = MultiHeadAttention(num_heads=num_heads, key_dim=key_dim, dropout=0.1)(y, y)
        y = Dropout(0.1)(y)
        if x.shape[-1] != y.shape[-1]:
            x = Dense(y.shape[-1])(x)
        x = x + y

        y = LayerNormalization(epsilon=1e-6)(x)
        y = Dense(units, activation="relu")(y)
        y = Dropout(0.1)(y)
        if x.shape[-1] != y.shape[-1]:
            x = Dense(y.shape[-1])(x)
        x = x + y

    rep = GlobalAveragePooling1D()(x)
    for u in mlp_head_units:
        rep = Dense(u, activation="relu")(rep)
        rep = Dropout(0.1)(rep)
    logits = Dense(1, activation="sigmoid")(rep)

    model = Model(inputs, logits, name="ZACH-ViT")
    model.compile(optimizer=Adam(1e-4), loss="binary_crossentropy",
                  metrics=["accuracy", AUC()], jit_compile=False)
    return model


# ==============================================================
# Training Wrappers
# ==============================================================
def run_zach_vit(batch_size=128, epochs=23, class_weights=None, threshold=53, base_dir="../Data/"):
    """Train and evaluate ZACH-ViT (standard mode)."""
    train_gen, val_gen, test_gen = create_data_generators(base_dir, batch_size, threshold=threshold)
    model = build_custom_vit_model()
    print("=== ZACH-ViT Model Summary ===")
    model.summary()
    print(f"Total parameters: {model.count_params():,}")

    model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        callbacks=[EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
                   PlotTrainingHistory(), EpochTimeLogger()],
        class_weight=class_weights,
        verbose=1
    )

    val_df, test_df = evaluate_model_and_create_dfs(model, val_gen, test_gen)
    print_metrics(val_df, "Validation")
    print_metrics(test_df, "Test")
    return model, val_df, test_df


def run_zach_vit_time(batch_size=128, epochs=23, class_weights=None, threshold=53, base_dir="../Data/"):
    """Train and evaluate ZACH-ViT with timing of training and inference."""
    train_gen, val_gen, test_gen = create_data_generators(base_dir, batch_size, threshold=threshold)
    model = build_custom_vit_model()
    print("=== ZACH-ViT Model Summary ===")
    model.summary()
    print(f"Total parameters: {model.count_params():,}")

    start_train = time.time()
    model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        callbacks=[EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
                   PlotTrainingHistory(), EpochTimeLogger()],
        class_weight=class_weights,
        verbose=1
    )
    total_train_time = time.time() - start_train

    start_val = time.time()
    val_preds = model.predict(val_gen, verbose=0)
    val_time = time.time() - start_val

    start_test = time.time()
    test_preds = model.predict(test_gen, verbose=0)
    test_time = time.time() - start_test

    val_df = pd.DataFrame({
        "Filename": val_gen.filenames,
        "True Label": val_gen.classes,
        "Pred Label": (val_preds > 0.5).astype(int).ravel(),
        "Pred Proba": val_preds.ravel()
    })
    test_df = pd.DataFrame({
        "Filename": test_gen.filenames,
        "True Label": test_gen.classes,
        "Pred Label": (test_preds > 0.5).astype(int).ravel(),
        "Pred Proba": test_preds.ravel()
    })

    print("\n=== Final Performance ===")
    print_metrics(val_df, "Validation")
    print_metrics(test_df, "Test")

    print(f"\nSummary:")
    print(f" - Training time: {total_train_time/60:.2f} min")
    print(f" - Validation inference time: {val_time:.2f}s")
    print(f" - Test inference time: {test_time:.2f}s\n")

    return model, val_df, test_df
