
"""
Bayesian Optimization (Optuna) for Flood Depth Prediction — Cb_FloodDy

Key features:
- CBAM-attended ConvLSTM backbone with TimeDistributed(CBAM) on sequence frames
- Masked loss/metrics using valid-pixel mask
- Station water-level attention branch fused into spatial stream
- Saves best model per trial + final best copy
- Import-safe (no top-level execution)

- Explicit multi-DEM control via `dem_files` + `dem_timesteps` (lengths per DEM, in order)
- Configurable seed & EarlyStopping from the workflow script
- Defensive handling of water-level CSVs with variable lengths (truncate to min length)
- Clear I/O and normalization artifact saving
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional

import os
import re
import gc
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import geopandas as gpd
import rasterio
from rasterio.features import rasterize

import optuna
from optuna import Trial
from optuna.samplers import TPESampler

from tensorflow.keras.layers import (
    TimeDistributed, Conv2D, Multiply, Dense, Reshape, Flatten, Input,
    ConvLSTM2D, LSTM, Dropout, Activation, LayerNormalization, Lambda,
    Add, Concatenate, Softmax
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import (EarlyStopping, ReduceLROnPlateau, ModelCheckpoint)

plt.rcParams["font.family"] = "Times New Roman"


# -----------------------------
# Utility loaders & helpers
# -----------------------------

def natural_sort(file_list: List[str]) -> List[str]:
    def alphanum_key(key):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', key)]
    return sorted(file_list, key=alphanum_key)

def load_tiff_images(data_dir: str):
    images, filenames = [], []
    crs, transform = None, None
    for filename in sorted(os.listdir(data_dir)):
        if filename.lower().endswith(".tif"):
            fp = os.path.join(data_dir, filename)
            with rasterio.open(fp) as src:
                img = src.read(1)
                if crs is None:
                    crs = src.crs
                if transform is None:
                    transform = src.transform
                images.append(img)
            filenames.append(filename)
    if not images:
        raise ValueError(f"No .tif images found in {data_dir}")
    return np.array(images), filenames, crs, transform

def load_single_tiff_image(filepath: str):
    with rasterio.open(filepath) as src:
        img = src.read(1)
        crs = src.crs
        transform = src.transform
    return img, crs, transform

def create_cluster_masks(polygon_shapefile: str, raster_shape, transform, raster_crs):
    try:
        polygons_gdf = gpd.read_file(polygon_shapefile)
    except Exception as e:
        raise ValueError(f"Error loading shapefile {polygon_shapefile}: {e}")

    if polygons_gdf.crs != raster_crs:
        polygons_gdf = polygons_gdf.to_crs(raster_crs)

    cluster_masks = []
    for polygon in polygons_gdf.geometry:
        mask = rasterize([(polygon, 1)], out_shape=raster_shape, transform=transform,
                         fill=0, dtype='uint8')
        cluster_masks.append(mask)

    cluster_masks = np.array(cluster_masks)

    combined_mask = np.sum(cluster_masks.astype(int), axis=0)
    if np.any(combined_mask > 1):
        overlapping_pixels = int(np.sum(combined_mask > 1))
        raise ValueError(f"Overlap detected: {overlapping_pixels} pixels belong to multiple clusters!")

    return cluster_masks, polygons_gdf

def load_water_level_data(data_dir: str):
    """Load per-station water-level series.

    Truncates all stations to the minimum length to keep array rectangular,
    matching original training semantics.
    """
    series_list = []
    filenames = [f for f in os.listdir(data_dir) if f.lower().endswith(".csv")]
    filenames = natural_sort(filenames)
    for filename in filenames:
        fp = os.path.join(data_dir, filename)
        df = pd.read_csv(fp)
        # Accept several common column names
        col = None
        for candidate in ["water_level", "level", "wl"]:
            if candidate in df.columns:
                col = candidate
                break
        if col is None:
            # fallback: first numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                col = numeric_cols[0]
            else:
                raise ValueError(f"No numeric water-level column found in {fp}. Columns={list(df.columns)}")
        series_list.append(df[col].values.astype(np.float32))

    if not series_list:
        raise ValueError(f"No water-level CSVs found in {data_dir}.")

    min_len = min(len(s) for s in series_list)
    if min_len <= 0:
        raise ValueError("Water-level series are empty.")
    # truncate to min length
    series_list = [s[:min_len] for s in series_list]
    wl = np.stack(series_list, axis=0)  # (stations, T)
    return wl, filenames

def normalize_data_with_nan(data: np.ndarray):
    nan_mask = np.isnan(data)
    min_val = np.nanmin(data)
    max_val = np.nanmax(data)
    if max_val == min_val:
        norm_data = np.zeros_like(data) + 0.1
    else:
        norm_data = 0.1 + 0.9 * (data - min_val) / (max_val - min_val)
    norm_data = np.clip(norm_data, 0.1, 1.0)
    norm_data[nan_mask] = 0
    return norm_data, float(min_val), float(max_val), nan_mask

def verify_mask(mask: np.ndarray):
    mask_sample = mask[0, 0, :, :, 0]
    valid_pixels = int(np.sum(mask_sample == 1))
    invalid_pixels = int(np.sum(mask_sample == 0))
    print(f"Valid Pixels (1): {valid_pixels} | Invalid Pixels (0): {invalid_pixels}")

def masked_global_average_pooling2d(inputs, mask):
    masked_inputs = inputs * mask
    sum_pool = tf.reduce_sum(masked_inputs, axis=[1, 2])
    valid_pixels = tf.reduce_sum(mask, axis=[1, 2]) + tf.keras.backend.epsilon()
    avg_pool = sum_pool / valid_pixels
    return avg_pool

def masked_global_max_pooling2d(inputs, mask):
    masked_inputs = inputs * mask + (1.0 - mask) * (-1e9)
    max_pool = tf.reduce_max(masked_inputs, axis=[1, 2])
    return max_pool


# -----------------------------
# Custom layers & loss
# -----------------------------

class StandardCBAM(Layer):
    """CBAM block that expects the last channel to be a 1-channel mask.

    Implements `compute_output_shape` so it can be wrapped by `TimeDistributed`.
    """
    def __init__(self, ratio=8, kernel_size=7, return_attention=False, **kwargs):
        super().__init__(**kwargs)
        self.ratio = ratio
        self.kernel_size = kernel_size
        self.return_attention = return_attention

    def build(self, input_shape):
        total_channels = int(input_shape[-1])
        self.feature_channels = total_channels - 1  # last is mask
        self.shared_dense_one = Dense(
            max(1, self.feature_channels // self.ratio),
            activation='relu', kernel_initializer='he_normal',
            use_bias=True, bias_initializer='zeros'
        )
        self.shared_dense_two = Dense(
            self.feature_channels, activation='sigmoid',
            kernel_initializer='glorot_normal', use_bias=True, bias_initializer='zeros'
        )
        self.conv_spatial = Conv2D(
            filters=1, kernel_size=self.kernel_size, strides=1, padding='same',
            activation='sigmoid', kernel_initializer='glorot_normal', use_bias=False
        )
        super().build(input_shape)

    def call(self, inputs, training=None):
        feature = inputs[..., :self.feature_channels]
        mask = inputs[..., self.feature_channels:]

        # Channel attention (masked GAP + GMP)
        avg_pool = masked_global_average_pooling2d(feature, mask)
        avg_pool = self.shared_dense_one(avg_pool)
        avg_pool = self.shared_dense_two(avg_pool)

        max_pool = masked_global_max_pooling2d(feature, mask)
        max_pool = self.shared_dense_one(max_pool)
        max_pool = self.shared_dense_two(max_pool)

        channel_attention = Add()([avg_pool, max_pool])
        channel_attention = Activation('sigmoid')(channel_attention)
        channel_attention = Reshape((1, 1, self.feature_channels))(channel_attention)

        refined_feature = Multiply()([feature, channel_attention])

        # Spatial attention (masked)
        spatial_attention = self.conv_spatial(refined_feature)
        spatial_attention = Multiply()([spatial_attention, mask])
        refined_feature = Multiply()([refined_feature, spatial_attention])

        if self.return_attention:
            return refined_feature, spatial_attention
        return refined_feature

    def compute_output_shape(self, input_shape):
        # Remove the mask channel from the output
        *prefix, channels = input_shape
        return tuple(prefix + [channels - 1])

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            "ratio": self.ratio,
            "kernel_size": self.kernel_size,
            "return_attention": self.return_attention,
        })
        return cfg


class TrueLoss(tf.keras.metrics.Metric):
    def __init__(self, name='trueloss', **kwargs):
        super().__init__(name=name, **kwargs)
        self.true_loss = self.add_weight(name='tl', initializer='zeros')
        self.count = self.add_weight(name='count', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        mask = tf.math.not_equal(y_true, 0.0)
        mask = tf.cast(mask, y_true.dtype)
        mse = tf.square(y_true - y_pred)
        masked_mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
        self.true_loss.assign_add(masked_mse)
        self.count.assign_add(1.0)

    def result(self):
        return self.true_loss / self.count

    def reset_state(self):
        self.true_loss.assign(0.0)
        self.count.assign(0.0)


def masked_mse(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    mask = tf.math.not_equal(y_true, 0.0)
    mask = tf.cast(mask, y_true.dtype)
    mse = tf.square(y_true - y_pred)
    masked_mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
    return masked_mse


# -----------------------------
# Model builder (consistent with original topology)
# -----------------------------

def build_model_with_cbam_weighted(
    trial: Trial,
    X_train_shape,
    sequence_length: int,
    num_stations: int,
    cluster_masks_tensor: tf.Tensor,
    hp_space: Dict
):
    spatial_input = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], X_train_shape[4]),
                          name='spatial_input')
    mask_input    = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], 1),
                          name='mask_input')
    water_input   = Input(shape=(sequence_length, num_stations), name='water_level_input')

    convlstm_1_filters = trial.suggest_categorical('convlstm_1_filters', hp_space.get('convlstm_filters', [16,32,48,64]))
    convlstm_2_filters = trial.suggest_categorical('convlstm_2_filters', hp_space.get('convlstm_filters', [16,32,48,64]))
    convlstm_3_filters = trial.suggest_categorical('convlstm_3_filters', hp_space.get('convlstm_filters', [16,32,48,64]))

    lstm_units_1 = trial.suggest_categorical('lstm_units_1', hp_space.get('lstm_units', [32,48,64]))
    lstm_units_2 = trial.suggest_categorical('lstm_units_2', hp_space.get('lstm_units', [32,48,64]))

    dense_1_units = trial.suggest_categorical('dense_1_units', hp_space.get('dense_units', [32,48,64]))

    l2_reg_min, l2_reg_max = hp_space.get('l2_reg_range', (1e-6, 1e-3))
    learning_rate_min, learning_rate_max = hp_space.get('lr_range', (1e-5, 1e-3))
    dropout_min, dropout_max = hp_space.get('dropout_range', (0.2, 0.5))

    l2_reg_val   = trial.suggest_float('l2_reg', l2_reg_min, l2_reg_max, log=True)
    learning_rate = trial.suggest_float('learning_rate', learning_rate_min, learning_rate_max, log=True)
    dropout_rate  = trial.suggest_float('dropout_rate', dropout_min, dropout_max)

    # --- Spatial stream ---
    x = ConvLSTM2D(filters=convlstm_1_filters, kernel_size=(3,3), padding='same', return_sequences=True,
                   kernel_initializer='glorot_normal', kernel_regularizer=l2(l2_reg_val), name='ConvLSTM_1')(spatial_input)
    x = LayerNormalization(name='LayerNorm_1')(x)

    x_concat = Concatenate(axis=-1, name='Concat_CBAM_1')([x, mask_input])
    x = TimeDistributed(StandardCBAM(name='CBAM_1'), name='TimeDistributed_CBAM_1')(x_concat)

    x = ConvLSTM2D(filters=convlstm_2_filters, kernel_size=(3,3), padding='same', return_sequences=True,
                   kernel_initializer='glorot_normal', kernel_regularizer=l2(l2_reg_val), name='ConvLSTM_2')(x)
    x = LayerNormalization(name='LayerNorm_2')(x)

    x_concat = Concatenate(axis=-1, name='Concat_CBAM_2')([x, mask_input])
    x = TimeDistributed(StandardCBAM(name='CBAM_2'), name='TimeDistributed_CBAM_2')(x_concat)

    conv_lstm_output = ConvLSTM2D(filters=convlstm_3_filters, kernel_size=(3,3), padding='same', return_sequences=False,
                                  kernel_initializer='glorot_normal', kernel_regularizer=l2(l2_reg_val), name='ConvLSTM_3')(x)
    x = LayerNormalization(name='LayerNorm_3')(conv_lstm_output)

    last_mask = Lambda(lambda t: t[:, -1, :, :, :], name='Extract_Last_Mask')(mask_input)
    x_concat = Concatenate(axis=-1, name='Concat_CBAM_3')([x, last_mask])
    conv_lstm_output = StandardCBAM(name='CBAM_3', return_attention=False)(x_concat)

    # --- Water-level attention (per-station, shared weights) ---
    reshaped_water = Lambda(lambda t: tf.reshape(t, (-1, sequence_length, 1)),
                            name='Reshape_Water')(water_input)
    shared_l1 = LSTM(lstm_units_1, return_sequences=True, kernel_initializer='glorot_normal',
                     kernel_regularizer=l2(l2_reg_val), name='Shared_LSTM_1')(reshaped_water)
    shared_l2 = LSTM(lstm_units_2, return_sequences=True, kernel_initializer='glorot_normal',
                     kernel_regularizer=l2(l2_reg_val), name='Shared_LSTM_2')(shared_l1)

    att_logits = Dense(1, activation='tanh', name='Att_Logits')(shared_l2)
    att_weights = Softmax(axis=1, name="att_softmax")(att_logits)

    # Use a Keras layer to do the weighted sum over time
    temporal_context = Lambda(
        lambda t: tf.reduce_sum(t[0] * t[1], axis=1),
        name="Temporal_Context"
    )([shared_l2, att_weights])

    # Match channels to ConvLSTM_3 output for element-wise Multiply
    C3 = convlstm_3_filters
    temporal_context = Dense(
        X_train_shape[2] * X_train_shape[3] * C3,
        activation='relu',
        name='Temporal_Project'
    )(temporal_context)
    temporal_context = Reshape((X_train_shape[2], X_train_shape[3], C3), name='Temporal_Map')(temporal_context)

    modulated_output = Multiply(name='Modulate_Spatial_With_Context')([temporal_context, conv_lstm_output])

    # --- Head ---
    z = Flatten(name='Flatten_Modulated_Output')(modulated_output)
    z = Dense(dense_1_units, activation='relu', kernel_initializer='he_normal',
              kernel_regularizer=l2(l2_reg_val), name='Dense_1')(z)
    z = Dropout(dropout_rate, name='Dropout_1')(z)

    z = Dense(X_train_shape[2] * X_train_shape[3], activation='linear', kernel_initializer='he_normal',
              kernel_regularizer=l2(l2_reg_val), name='Dense_Output')(z)
    output = Reshape((X_train_shape[2], X_train_shape[3]), name='Reshape_Output')(z)
    output = Lambda(lambda t: tf.cast(t, tf.float32), name='Cast_Output')(output)

    model = Model(inputs=[spatial_input, mask_input, water_input], outputs=output,
                  name='Flood_Prediction_Model')
    optimizer = Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss=masked_mse, metrics=['mae','mse', TrueLoss()])
    return model


# -----------------------------
# Main optimization entrypoint
# -----------------------------

def run_optimization(
    train_atm_pressure_dir: str,
    train_wind_speed_dir: str,
    train_precipitation_dir: str,
    train_water_depth_dir: str,
    train_river_discharge_dir: str,
    water_level_dir: str,
    polygon_clusters_path: str,
    sequence_length: int = 6,
    n_trials: int = 100,
    study_name: str = "Flood_Depth_Prediction_BO",
    checkpoint_dir_BO: str = "checkpoint_BO",
    seed_value: int = 3,
    convlstm_filters: List[int] = (16, 32, 48, 64),
    lstm_units: List[int] = (32, 48, 64),
    dense_units: List[int] = (32, 48, 64),
    l2_reg_range: Tuple[float, float] = (1e-6, 1e-3),
    lr_range: Tuple[float, float] = (1e-5, 1e-3),
    dropout_range: Tuple[float, float] = (0.2, 0.5),
    es_monitor: str = "val_loss",
    early_stopping: int = 10,
    es_restore_best: bool = True,
    epochs: int = 300,
    batch_size: int = 2,
    val_split: float = 0.2,
    # Dynamic multi-DEM control
    dem_files: List[str] = None,          # e.g. ['DEM/dem1.tif','DEM/dem2.tif',...]
    dem_timesteps: List[int] = None,      # e.g. [217, 100, 300, 151] must sum to total T
):
    if dem_files is None or dem_timesteps is None:
        raise ValueError("dem_files and dem_timesteps are required for dynamic DEM handling.")
    if len(dem_files) != len(dem_timesteps):
        raise ValueError("dem_files and dem_timesteps must have the same length.")

    # --- Seeds / GPU setup ---
    np.random.seed(seed_value)
    tf.random.set_seed(seed_value)
    print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print("GPU memory growth enabled.")
        except RuntimeError as e:
            print(e)
    from tensorflow.keras.mixed_precision import set_global_policy
    set_global_policy('float32')

    os.makedirs(checkpoint_dir_BO, exist_ok=True)

    # --- Load spatial inputs ---
    atm, _, crs, transform = load_tiff_images(train_atm_pressure_dir)
    wind, _, _, _ = load_tiff_images(train_wind_speed_dir)
    precip, _, _, _ = load_tiff_images(train_precipitation_dir)
    river, _, _, _ = load_tiff_images(train_river_discharge_dir)

    raster_shape = atm.shape[1:3]
    total_T = atm.shape[0]

    # --- Cluster masks from polygons ---
    cluster_masks, polygons_gdf = create_cluster_masks(
        polygon_shapefile=polygon_clusters_path,
        raster_shape=raster_shape, transform=transform, raster_crs=crs
    )

    # --- DEMs (dynamic N) ---
    dem_rasters = []
    for f in dem_files:
        img, _, _ = load_single_tiff_image(f)
        dem_rasters.append(img)

    if sum(dem_timesteps) != total_T:
        raise ValueError(f"dem_timesteps must sum to total timesteps ({total_T}). Got {sum(dem_timesteps)}.")
    if any(t <= 0 for t in dem_timesteps):
        raise ValueError("All entries in dem_timesteps must be positive integers.")

    dem_stacks = [np.tile(d, (t, 1, 1)) for d, t in zip(dem_rasters, dem_timesteps)]
    dem = np.concatenate(dem_stacks, axis=0)  # (T, H, W)
    assert dem.shape[0] == total_T

    # --- Compose channels ---
    X = np.stack((atm, wind, dem, precip, river), axis=-1)  # (T, H, W, C)

    # --- Build sequences ---
    X_seq = [X[i:i+sequence_length] for i in range(len(X) - sequence_length + 1)]
    X_seq = np.array(X_seq)  # (Nseq, seq, H, W, C)

    y, _, _, _ = load_tiff_images(train_water_depth_dir)
    y_seq = y[sequence_length - 1:]
    y_seq = y_seq[:, np.newaxis, :, :]  # (Nseq, 1, H, W)

    # --- Normalize & build mask ---
    X_norm_list, min_vals, max_vals, nan_masks_list = [], [], [], []
    for c in range(X_seq.shape[-1]):
        norm_c, mn, mx, nan_mask_c = normalize_data_with_nan(X_seq[..., c])
        X_norm_list.append(norm_c); min_vals.append(mn); max_vals.append(mx); nan_masks_list.append(nan_mask_c)
    X_norm = np.stack(X_norm_list, axis=-1)
    nan_masks_combined = np.any(np.stack(nan_masks_list, axis=-1), axis=-1).astype(float)
    valid_mask = 1.0 - nan_masks_combined
    nan_masks = np.expand_dims(valid_mask, axis=-1)  # (Nseq, seq, H, W, 1)
    verify_mask(nan_masks)

    y_norm, y_min, y_max, _ = normalize_data_with_nan(y_seq)

    # --- Water level sequences ---
    wl_data, _ = load_water_level_data(water_level_dir)  # (stations, T_wl)
    wl_global_min, wl_global_max = float(np.min(wl_data)), float(np.max(wl_data))
    wl_norm = (wl_data - wl_global_min) / (wl_global_max - wl_global_min + 1e-8)

    wl_seq = []
    for i in range(wl_norm.shape[1] - sequence_length + 1):
        wl_seq.append(wl_norm[:, i:i+sequence_length])
    wl_seq = np.array(wl_seq)  # (Nseq, stations, seq)
    wl_seq = np.transpose(wl_seq, (0, 2, 1))  # (Nseq, seq, stations)

    num_stations = wl_seq.shape[-1]
    assert cluster_masks.shape[0] == num_stations, "Number of clusters must match number of stations."
    assert wl_seq.shape[0] == X_norm.shape[0], "Mismatch in num sequences between water level and spatial data."

    # --- Save normalization params ---
    norm_params = {
        'X_train_min_vals': min_vals,
        'X_train_max_vals': max_vals,
        'y_train_min': y_min,
        'y_train_max': y_max,
        'water_level_global_min': wl_global_min,
        'water_level_global_max': wl_global_max
    }
    np.save(os.path.join(checkpoint_dir_BO, 'normalization_params.npy'), norm_params, allow_pickle=True)

    # --- HP space dict ---
    hp_space = dict(
        convlstm_filters=list(convlstm_filters),
        lstm_units=list(lstm_units),
        dense_units=list(dense_units),
        l2_reg_range=tuple(l2_reg_range),
        lr_range=tuple(lr_range),
        dropout_range=tuple(dropout_range),
    )

    def build_model(trial: Trial):
        return build_model_with_cbam_weighted(
            trial=trial,
            X_train_shape=X_norm.shape,
            sequence_length=sequence_length,
            num_stations=num_stations,
            cluster_masks_tensor=tf.constant(cluster_masks, dtype=tf.float32),
            hp_space=hp_space
        )

    def objective(trial: Trial):
        model = build_model(trial)
        ckpt_path = os.path.join(checkpoint_dir_BO, f"trial_{trial.number}_best.h5")
        ckpt = ModelCheckpoint(filepath=ckpt_path, monitor=es_monitor, mode='min',
                               save_best_only=True, verbose=1)
        early_stopping_cb = EarlyStopping(monitor=es_monitor, patience=early_stopping,
                                          restore_best_weights=es_restore_best, verbose=1)
        lr_scheduler_cb = ReduceLROnPlateau(monitor=es_monitor, factor=0.5, patience=5,
                                            min_lr=lr_range[0], verbose=1)

        history = model.fit(
            [X_norm, nan_masks, wl_seq],
            y_norm.squeeze(),
            epochs=epochs,
            batch_size=batch_size,
            validation_split=val_split,
            verbose=2,
            callbacks=[ckpt, early_stopping_cb, lr_scheduler_cb]
        )
        best_val = float(np.min(history.history.get('val_loss', [np.inf])))
        # cleanup
        del model
        gc.collect()
        tf.keras.backend.clear_session()
        return best_val

    storage_name = f"sqlite:///{os.path.join(checkpoint_dir_BO, 'study.db')}"
    sampler = TPESampler(seed=seed_value)
    try:
        study = optuna.load_study(study_name=study_name, storage=storage_name)
        print(f"Loaded existing study '{study_name}'.")
    except Exception:
        study = optuna.create_study(direction='minimize', sampler=sampler, study_name=study_name,
                                    storage=storage_name, load_if_exists=True)
        print(f"Created new study '{study_name}'.")

    study.optimize(objective, n_trials=n_trials, timeout=None)

    # Save study summary
    study.trials_dataframe().to_csv(os.path.join(checkpoint_dir_BO, 'study_summary.csv'), index=False)

    # Copy best model
    best = study.best_trial
    src_ckpt = os.path.join(checkpoint_dir_BO, f"trial_{best.number}_best.h5")
    final_ckpt = os.path.join(checkpoint_dir_BO, "best_model_optuna.h5")
    if os.path.exists(src_ckpt):
        shutil.copy2(src_ckpt, final_ckpt)

    # Save best params
    with open(os.path.join(checkpoint_dir_BO, 'best_params.txt'), 'w', encoding='utf-8') as f:
        for k, v in best.params.items():
            f.write(f"{k}: {v}\n")
        f.write(f"best_val_loss: {best.value}\n")

    return {
        "best_trial_number": best.number,
        "best_val_loss": float(best.value),
        "best_params": dict(best.params),
        "best_model_path": final_ckpt if os.path.exists(final_ckpt) else None,
        "study_csv": os.path.join(checkpoint_dir_BO, 'study_summary.csv')
    }
