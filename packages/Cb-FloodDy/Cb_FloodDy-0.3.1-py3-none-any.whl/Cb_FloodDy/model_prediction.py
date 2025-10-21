# ==========================================
# Flood Depth Prediction Model Evaluation
# Hurricane Harvey 2017
# ==========================================

# ------------------------------------------
# 1. Import Necessary Libraries
# ------------------------------------------
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import rasterio
import geopandas as gpd
from tensorflow.keras.models import Model
from tensorflow.keras.initializers import HeNormal, GlorotNormal
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import load_model
from rasterio.features import rasterize
from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
from tensorflow.keras.layers import (
    Conv2D, Multiply, Dense, Reshape, Flatten, Input, ConvLSTM2D, LSTM,
    Activation, LayerNormalization, Lambda, Add, Concatenate, GlobalAveragePooling2D,
    GlobalMaxPooling2D
)
from tensorflow.keras.regularizers import l2
import matplotlib.patches as patches

# ------------------------------------------
# 2. Setup and Configuration
# ------------------------------------------

# Seed for reproducibility
seed_value = 3
np.random.seed(seed_value)
tf.random.set_seed(seed_value)

# Check and configure GPU usage
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Enable mixed precision (if desired)
from tensorflow.keras.mixed_precision import set_global_policy
set_global_policy('float32')

# ------------------------------------------
# 3. Helper Functions
# ------------------------------------------

def load_tiff_images(data_dir):
    """
    Loads all TIFF images from a specified directory.

    Args:
        data_dir (str): Path to the directory containing TIFF files.

    Returns:
        Tuple[np.ndarray, List[str], Any, Any]: Loaded images array, filenames, CRS, and transform.
    """
    images = []
    filenames = []
    crs = None
    transform = None
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".tif"):
            filepath = os.path.join(data_dir, filename)
            with rasterio.open(filepath) as src:
                img = src.read(1)
                if crs is None:
                    crs = src.crs
                if transform is None:
                    transform = src.transform
                images.append(img)
            filenames.append(filename)
    print(f"Loaded {len(images)} TIFF images from {data_dir}")
    return np.array(images), filenames, crs, transform

def load_single_tiff_image(filepath):
    """
    Loads a single TIFF image.

    Args:
        filepath (str): Path to the TIFF file.

    Returns:
        Tuple[np.ndarray, Any, Any]: Loaded image array, CRS, and transform.
    """
    with rasterio.open(filepath) as src:
        img = src.read(1)
        crs = src.crs
        transform = src.transform
    print(f"Loaded single TIFF image from {filepath}")
    return img, crs, transform

def natural_sort(file_list):
    """
    Sorts a list of filenames in a natural, human-friendly order.
    
    Args:
        file_list (List[str]): List of filenames to sort.
    
    Returns:
        List[str]: Naturally sorted list of filenames.
    """
    def alphanum_key(key):
        # Split the key into a list of strings and integers
        return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', key)]
    
    return sorted(file_list, key=alphanum_key)

def load_water_level_data(data_dir):
    """
    Loads water level data from CSV files for each station, sorted naturally.

    Args:
        data_dir (str): Path to the directory containing water level CSV files.

    Returns:
        Tuple[np.ndarray, List[str]]: Water level data array and naturally sorted filenames.
    """
    water_level_data = []
    filenames = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    filenames = natural_sort(filenames)  # Apply natural sorting
    for filename in filenames:
        filepath = os.path.join(data_dir, filename)
        df = pd.read_csv(filepath)
        if 'water_level' in df.columns:
            water_level_data.append(df['water_level'].values)
        else:
            print(f"'water_level' column not found in {filepath}. Skipping.")
    print(f"Loaded water level data from {data_dir} with {len(water_level_data)} stations.")
    return np.array(water_level_data), filenames

def normalize_data_with_nan(data, min_val, max_val):
    """
    Normalizes data to the range [0.1, 1.0], handling NaN values.

    Args:
        data (np.ndarray): Input data array.
        min_val (float): Minimum value for normalization.
        max_val (float): Maximum value for normalization.

    Returns:
        np.ndarray: Normalized data array.
    """
    nan_mask = np.isnan(data)
    norm_data = 0.1 + 0.9 * (data - min_val) / (max_val - min_val)
    norm_data[nan_mask] = 0  # Set NaN cells to 0 after normalization
    return norm_data

def denormalize_data(norm_data, min_val, max_val):
    """
    Denormalizes data from the range [0.1, 1.0] back to original scale.

    Args:
        norm_data (np.ndarray): Normalized data array.
        min_val (float): Minimum value used during normalization.
        max_val (float): Maximum value used during normalization.

    Returns:
        np.ndarray: Denormalized data array.
    """
    return (norm_data - 0.1) / 0.9 * (max_val - min_val) + min_val

def apply_nan_mask(data, mask):
    """
    Applies a NaN mask to data.

    Args:
        data (np.ndarray): Data array.
        mask (np.ndarray): Boolean mask where True indicates NaN.

    Returns:
        np.ndarray: Data array with NaNs applied.
    """
    data = data.copy()  # Avoid modifying the original data
    data[mask] = np.nan
    return data

def save_tiff_image(data, output_path, reference_dataset):
    """
    Saves a data array as a TIFF image using a reference dataset for metadata.

    Args:
        data (np.ndarray): Data array to save.
        output_path (str): Output file path.
        reference_dataset (str): Path to a reference TIFF file for metadata.
    """
    with rasterio.open(reference_dataset) as src:
        out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": src.crs,
        "transform": src.transform
    })
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(data.astype(np.float32), 1)
    print(f"Saved TIFF image to {output_path}")

def verify_mask_distribution(mask):
    """
    Verifies the distribution of valid and invalid pixels in the mask.

    Args:
        mask (np.ndarray): Mask array with shape (num_sequences, sequence_length, height, width, 1).
    """
    total_pixels = mask.size
    valid_pixels = np.sum(mask == 1)
    invalid_pixels = np.sum(mask == 0)
    
    print(f"Total Pixels: {total_pixels}")
    print(f"Valid Pixels (1): {valid_pixels} ({(valid_pixels / total_pixels) * 100:.2f}%)")
    print(f"Invalid Pixels (0): {invalid_pixels} ({(invalid_pixels / total_pixels) * 100:.2f}%)")

def visualize_mask(mask, index=0, timestep=0):
    """
    Visualizes the mask to ensure correct inversion.

    Args:
        mask (np.ndarray): Mask array with shape (batch_size, sequence_length, height, width, 1).
        index (int): Sequence index to visualize.
        timestep (int): Timestep index to visualize.
    """
    # Verify mask dimensions
    if mask.ndim != 5:
        raise ValueError(f"Expected mask to be 5D, but got {mask.ndim}D.")

    batch_size, sequence_length, height, width, channels = mask.shape
    if channels != 1:
        raise ValueError(f"Expected mask to have 1 channel, but got {channels} channels.")

    # Extract the specific mask slice
    mask_sample = mask[index, timestep, :, :, 0]

    plt.figure(figsize=(6, 6))
    plt.title('Valid Mask (1=Valid, 0=Invalid)')
    plt.imshow(mask_sample, cmap='gray')
    plt.colorbar()
    plt.axis('off')
    plt.show()
    
import matplotlib.patches as patches

def visualize_spatial_attention_with_clusters(spatial_attention_map, polygons_gdf, transform, vmin=None, vmax=None):
    """
    Visualizes the spatial attention map with cluster polygons overlayed, masking invalid areas.
    
    Args:
        spatial_attention_map (np.ndarray): Spatial attention map array with shape (height, width).
        polygons_gdf (gpd.GeoDataFrame): GeoDataFrame containing cluster polygons.
        transform (Affine): Affine transform of the raster.
        vmin (float, optional): Minimum value for the color map.
        vmax (float, optional): Maximum value for the color map.
    """
    # Mask out values outside the valid range by setting them to NaN
    masked_attention_map = np.where((spatial_attention_map >= vmin) & (spatial_attention_map <= vmax), spatial_attention_map, np.nan)

    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the masked attention map
    im = ax.imshow(masked_attention_map, cmap='viridis', vmin=vmin, vmax=vmax)
    ax.set_title('Spatial Attention Map with Cluster Overlays')
    ax.axis('off')
    
    # Plot polygons
    for idx, polygon in polygons_gdf.geometry.items():
        if polygon.is_empty:
            continue
        polygon_pixels = []
        for coord in polygon.exterior.coords:
            col, row = ~transform * (coord[0], coord[1])
            polygon_pixels.append((col, row))
        polygon_pixels = np.array(polygon_pixels)
        ax.add_patch(patches.Polygon(polygon_pixels, linewidth=1, edgecolor='red', facecolor='none'))
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Normalized Attention Weight', rotation=270, labelpad=15)

    # Save and show the plot
    plt.savefig('spatial_attention_with_clusters_masked.png', dpi=300, bbox_inches='tight')
    plt.show()
    
# ==========================================
# 3. Custom Attention Mechanisms
# ==========================================

def masked_global_average_pooling2d(inputs, mask):
    masked_inputs = inputs * mask  # Shape: (batch, height, width, channels)
    sum_pool = tf.reduce_sum(masked_inputs, axis=[1, 2])  # Shape: (batch, channels)
    valid_pixels = tf.reduce_sum(mask, axis=[1, 2]) + tf.keras.backend.epsilon()  # Shape: (batch, 1)
    avg_pool = sum_pool / valid_pixels  # Shape: (batch, channels)
    return avg_pool

def masked_global_max_pooling2d(inputs, mask):
    masked_inputs = inputs * mask + (1.0 - mask) * (-1e9)  # Shape: (batch, height, width, channels)
    max_pool = tf.reduce_max(masked_inputs, axis=[1, 2])  # Shape: (batch, channels)
    return max_pool

class StandardCBAM(Layer):
    def __init__(self, ratio=8, kernel_size=7, return_attention=False, **kwargs):
        super(StandardCBAM, self).__init__(**kwargs)
        self.ratio = ratio
        self.kernel_size = kernel_size
        self.return_attention = return_attention

    def build(self, input_shape):
        if isinstance(input_shape, list):
            raise ValueError("StandardCBAM now expects a single concatenated input.")

        total_channels = input_shape[-1]
        self.feature_channels = total_channels - 1  # Last channel is assumed to be the mask

        # Channel Attention layers without fixed names
        self.shared_dense_one = Dense(
            self.feature_channels // self.ratio,
            activation='relu',
            kernel_initializer='he_normal',
            use_bias=True,
            bias_initializer='zeros'
        )
        self.shared_dense_two = Dense(
            self.feature_channels,
            activation='sigmoid',
            kernel_initializer='glorot_normal',
            use_bias=True,
            bias_initializer='zeros'
        )

        # Spatial Attention convolutional layer without fixed name
        self.conv_spatial = Conv2D(
            filters=1,
            kernel_size=self.kernel_size,
            strides=1,
            padding='same',
            activation='sigmoid',
            kernel_initializer='glorot_normal',
            use_bias=False
        )

        super(StandardCBAM, self).build(input_shape)

    def call(self, inputs, training=None):
        # Split feature and mask channels
        feature = inputs[..., :self.feature_channels]
        mask = inputs[..., self.feature_channels:]  # Shape: (batch, height, width, 1)

        # tf.print("Feature shape:", tf.shape(feature))
        # tf.print("Mask shape:", tf.shape(mask))

        # --- Channel Attention ---
        # Apply masked global average and max pooling
        avg_pool = masked_global_average_pooling2d(feature, mask)  # Shape: (batch, channels)
        # tf.print("Average Pool shape:", tf.shape(avg_pool))
        avg_pool = self.shared_dense_one(avg_pool)  # Shape: (batch, channels // ratio)
        avg_pool = self.shared_dense_two(avg_pool)  # Shape: (batch, channels)

        max_pool = masked_global_max_pooling2d(feature, mask)  # Shape: (batch, channels)
        # tf.print("Max Pool shape:", tf.shape(max_pool))
        max_pool = self.shared_dense_one(max_pool)  # Shape: (batch, channels // ratio)
        max_pool = self.shared_dense_two(max_pool)  # Shape: (batch, channels)

        # Combine average and max pooling
        channel_attention = Add()([avg_pool, max_pool])  # Shape: (batch, channels)
        channel_attention = Activation('sigmoid')(channel_attention)  # Shape: (batch, channels)

        # tf.print("Channel Attention shape:", tf.shape(channel_attention))

        # Reshape for broadcasting across spatial dimensions using Keras Reshape
        channel_attention = Reshape((1, 1, self.feature_channels))(channel_attention)
        # tf.print("Reshaped Channel Attention shape:", tf.shape(channel_attention))

        # Apply channel attention to the features
        refined_feature = Multiply()([feature, channel_attention])  # Shape: (batch, height, width, channels)
        # tf.print("Refined Feature shape:", tf.shape(refined_feature))

        # --- Spatial Attention ---
        # Generate spatial attention map using a convolutional layer
        spatial_attention = self.conv_spatial(refined_feature)  # Shape: (batch, height, width, 1)
        # tf.print("Spatial Attention shape:", tf.shape(spatial_attention))
        
        # Apply mask to ensure invalid cells are zeroed
        spatial_attention = Multiply()([spatial_attention, mask])  # Shape: (batch, height, width, 1)
        # tf.print("Masked Spatial Attention shape:", tf.shape(spatial_attention))

        # Apply spatial attention to the refined features
        refined_feature = Multiply()([refined_feature, spatial_attention])  # Shape: (batch, height, width, channels)
        # tf.print("Final Refined Feature shape:", tf.shape(refined_feature))

        # Return both refined feature and spatial attention map if requested
        if self.return_attention:
            return refined_feature, spatial_attention
        else:
            return refined_feature

    def compute_output_shape(self, input_shape):
        """
        Computes the output shape of the layer.

        Args:
            input_shape (tuple): Shape of the input tensor.

        Returns:
            tuple: Shape of the output tensor.
        """
        # Determine if the input is 4D or 5D
        if len(input_shape) == 5:
            # Input shape: (batch, time, height, width, channels +1)
            return (input_shape[0], input_shape[1], input_shape[2], input_shape[3], self.feature_channels)
        elif len(input_shape) == 4:
            # Input shape: (batch, height, width, channels +1)
            return (input_shape[0], input_shape[1], input_shape[2], self.feature_channels)
        else:
            raise ValueError(f"Unsupported input shape: {input_shape}")

    def get_config(self):
        config = super(StandardCBAM, self).get_config()
        config.update({
            "ratio": self.ratio,
            "kernel_size": self.kernel_size,
            "return_attention": self.return_attention
        })
        return config

class CustomAttentionLayer(Layer):
    def __init__(self, emphasis_factor=1.5, top_k_percent=0.2, **kwargs):
        super(CustomAttentionLayer, self).__init__(**kwargs)
        self.emphasis_factor = emphasis_factor
        self.top_k_percent = top_k_percent

    def get_config(self):
        config = super(CustomAttentionLayer, self).get_config()
        config.update({
            "emphasis_factor": self.emphasis_factor,
            "top_k_percent": self.top_k_percent
        })
        return config

    def build(self, input_shape):
        # Build as before
        self.W = self.add_weight(name='att_weight',
                                 shape=(input_shape[-1], 1),
                                 initializer=GlorotNormal(),
                                 trainable=True)
        self.b = self.add_weight(shape=(1,),
                                 initializer='zeros',
                                 trainable=True,
                                 name='bias')
        super(CustomAttentionLayer, self).build(input_shape)

    def call(self, x):
        # Compute attention weights
        e = K.tanh(K.dot(x, self.W) + self.b)  # (batch_size, timesteps, 1)
        a = K.softmax(e, axis=1)               # (batch_size, timesteps, 1)
        a = K.squeeze(a, axis=-1)              # (batch_size, timesteps)

        # Emphasize top-k attention weights
        k_value = tf.cast(tf.cast(tf.shape(a)[1], tf.float32) * self.top_k_percent, tf.int32)
        k_value = tf.maximum(k_value, 1)
        top_k_values, top_k_indices = tf.math.top_k(a, k=k_value)
        mask = tf.one_hot(top_k_indices, depth=tf.shape(a)[1])  # (batch_size, k, timesteps)
        mask = tf.reduce_max(mask, axis=1)                      # (batch_size, timesteps)
        mask = tf.cast(mask, tf.bool)
        emphasized_a = tf.where(mask, a * self.emphasis_factor, a)  # (batch_size, timesteps)

        # Compute the context vector
        output = x * tf.expand_dims(emphasized_a, axis=-1)  # (batch_size, timesteps, features)
        summed_output = K.sum(output, axis=1)               # (batch_size, features)

        # Return both the context vector and the attention weights
        return [summed_output, emphasized_a]

    def compute_output_shape(self, input_shape):
        context_shape = (input_shape[0], input_shape[-1])
        attention_shape = (input_shape[0], input_shape[1])
        return [context_shape, attention_shape]

class ClusterBasedApplication(Layer):
    def __init__(self, num_stations, height, width, **kwargs):
        super(ClusterBasedApplication, self).__init__(**kwargs)
        self.num_stations = num_stations
        self.height = height
        self.width = width

    def build(self, input_shape):
        # Define Dense layer to project context vectors to spatial dimensions
        self.dense_project = Dense(self.height * self.width,
                                   activation='relu',
                                   kernel_initializer='he_normal',
                                   kernel_regularizer=l2(1e-5),
                                   name='Dense_Project_Context')
        super(ClusterBasedApplication, self).build(input_shape)

    def call(self, inputs):
        attention_outputs, cluster_masks_tensor = inputs  # attention_outputs: (batch, num_stations, features)
        
        # Dynamically determine batch size
        batch_size = tf.shape(attention_outputs)[0]
        
        # Project context vectors to spatial dimensions
        reshaped_context = self.dense_project(attention_outputs)  # Shape: (batch, num_stations, height * width)
        reshaped_context = tf.reshape(reshaped_context, (batch_size, self.num_stations, self.height, self.width))  # Shape: (batch, num_stations, height, width)
        
        # Expand cluster masks to match batch size
        cluster_masks_expanded = tf.expand_dims(cluster_masks_tensor, axis=0)  # Shape: (1, num_stations, height, width)
        cluster_masks_expanded = tf.tile(cluster_masks_expanded, [batch_size, 1, 1, 1])  # Shape: (batch, num_stations, height, width)
        cluster_masks_expanded = tf.cast(cluster_masks_expanded, reshaped_context.dtype)
        
        # Apply cluster masks
        localized_context = reshaped_context * cluster_masks_expanded  # Shape: (batch, num_stations, height, width)
        
        # Compute cluster indices
        cluster_indices = tf.argmax(tf.cast(cluster_masks_tensor, tf.int32), axis=0)  # Shape: (height, width)
        
        # One-hot encode cluster indices
        cluster_indices_one_hot = tf.one_hot(cluster_indices, depth=self.num_stations)  # Shape: (height, width, num_stations)
        cluster_indices_one_hot = tf.transpose(cluster_indices_one_hot, perm=[2, 0, 1])  # Shape: (num_stations, height, width)
        cluster_indices_one_hot = tf.expand_dims(cluster_indices_one_hot, axis=0)  # Shape: (1, num_stations, height, width)
        cluster_indices_one_hot = tf.tile(cluster_indices_one_hot, [batch_size, 1, 1, 1])  # Shape: (batch, num_stations, height, width)
        
        # Select the correct context
        selected_context = tf.reduce_sum(localized_context * cluster_indices_one_hot, axis=1)  # Shape: (batch, height, width)
        
        # Expand dimensions to match spatial features
        combined_context = tf.expand_dims(selected_context, axis=-1)  # Shape: (batch, height, width, 1)
        
        return combined_context  # Shape: (batch, height, width, 1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], self.height, self.width, 1)

    def get_config(self):
        config = super(ClusterBasedApplication, self).get_config()
        config.update({
            "num_stations": self.num_stations,
            "height": self.height,
            "width": self.width
        })
        return config

# ==========================================
# 4. Loss Function
# ==========================================

def masked_mse(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    mask = tf.math.not_equal(y_true, 0.0)
    mask = tf.cast(mask, y_true.dtype)
    mse = tf.square(y_true - y_pred)
    mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
    return mse

# TrueLoss Metric Definition
class TrueLoss(tf.keras.metrics.Metric):
    def __init__(self, name='trueloss', **kwargs):
        super(TrueLoss, self).__init__(name=name, **kwargs)
        self.true_loss = self.add_weight(name='tl', initializer='zeros')
        self.count = self.add_weight(name='count', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        """
        Updates the state of the metric with the current batch's loss.

        Args:
            y_true (Tensor): Ground truth values.
            y_pred (Tensor): Predicted values.
            sample_weight (Tensor, optional): Sample weights.
        """
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        
        # Create mask: 1 for valid pixels, 0 otherwise
        mask = tf.math.not_equal(y_true, 0.0)
        mask = tf.cast(mask, y_true.dtype)
        
        # Compute squared errors
        mse = tf.square(y_true - y_pred)
        
        # Apply mask
        masked_mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
        
        # Update accumulators
        self.true_loss.assign_add(masked_mse)
        self.count.assign_add(1.0)
        pass

    def result(self):
        """
        Computes the average TrueLoss over all batches.

        Returns:
            Tensor: The average TrueLoss.
        """
        return self.true_loss / self.count
        pass

    def reset_state(self):
        """
        Resets the state of the metric.
        """
        self.true_loss.assign(0.0)
        self.count.assign(0.0)

# ------------------------------------------
# 6. Model Evaluation and Visualization Functions
# ------------------------------------------

def plot_and_compare_predictions(model, X_test, mask, water_level_data, y_test, y_test_nan_mask, filenames, num_images=2):
    """
    Plots and compares actual vs. predicted water depth images.

    Args:
        model (tf.keras.Model): Loaded TensorFlow model.
        X_test (np.ndarray): Normalized test input sequences.
        mask (np.ndarray): Cluster mask for the test data.
        water_level_data (np.ndarray): Normalized water level sequences.
        y_test (np.ndarray): Normalized ground truth water depth maps.
        y_test_nan_mask (np.ndarray): Mask indicating NaN values in y_test.
        filenames (List[str]): List of filenames corresponding to y_test.
        num_images (int): Number of images to plot for comparison.
    """
    mse_list, rmse_list, r2_list, mse_filenames = [], [], [], []
    for i in range(len(X_test)):
        X = X_test[i:i + 1]
        mask_sample = mask[i:i + 1]
        water_level = water_level_data[i:i + 1]
        y = y_test[i]

        # Make prediction
        preds = model.predict([X, mask_sample, water_level])

        # Ensure preds is squeezed to remove batch dimension
        preds_denorm = denormalize_data(preds[0], y_train_min, y_train_max)
        y_true = denormalize_data(y, y_train_min, y_train_max)

        # Apply NaN mask
        preds_denorm = apply_nan_mask(preds_denorm, y_test_nan_mask[i].squeeze())
        y_true = apply_nan_mask(y_true, y_test_nan_mask[i].squeeze())

        # Calculate MSE, RMSE, and R^2
        valid_mask = ~np.isnan(y_true)
        if np.any(valid_mask):
            mse = mean_squared_error(y_true[valid_mask], preds_denorm[valid_mask])
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true[valid_mask], preds_denorm[valid_mask])

            mse_list.append(mse)
            rmse_list.append(rmse)
            r2_list.append(r2)
            mse_filenames.append(filenames[i])

            if i < num_images:  # Only plot a specified number of images
                fig, axes = plt.subplots(1, 2, figsize=(12, 6))

                # Actual Water Depth
                im = axes[0].imshow(y_true, cmap='jet')
                axes[0].set_title(f'Actual Water Depth\n({filenames[i]})')
                axes[0].axis('off')
                plt.colorbar(im, ax=axes[0])

                # Predicted Water Depth
                im = axes[1].imshow(preds_denorm, cmap='jet')
                axes[1].set_title(f'Predicted Water Depth\n({filenames[i]})')
                axes[1].axis('off')
                plt.colorbar(im, ax=axes[1])

                plt.suptitle(f'MSE: {mse:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}')
                plt.tight_layout()
                plt.show()
        else:
            print(f"No valid data points for index {i}. Skipping...")

    if mse_list:
        avg_mse, avg_rmse, avg_r2 = np.mean(mse_list), np.mean(rmse_list), np.mean(r2_list)
        max_rmse_index = np.argmax(rmse_list)
        max_rmse = rmse_list[max_rmse_index]
        max_rmse_filename = mse_filenames[max_rmse_index]

        print(f'Average MSE: {avg_mse:.4f}, RMSE: {avg_rmse:.4f}, R²: {avg_r2:.4f}')
        print(f'Largest RMSE: {max_rmse:.4f}, Filename: {max_rmse_filename}')
    else:
        print("No valid predictions made.")

# ------------------------------------------
# 7. Main Execution Flow
# ------------------------------------------

def main():
    # --------------------------------------
    # A. Define Directories and Paths
    # --------------------------------------
    
    # Directories for testing data
    test_atm_pressure_dir = os.path.join(os.getcwd(), 'atm_pressure')
    test_wind_speed_dir = os.path.join(os.getcwd(), 'wind_speed')
    test_precipitation_dir = os.path.join(os.getcwd(), 'precipitation')
    test_river_discharge_dir = os.path.join(os.getcwd(), 'river_discharge')
    test_water_depth_dir = os.path.join(os.getcwd(), 'water_depth')
    test_dem_file = os.path.join(os.getcwd(), 'DEM/dem_idw.tif')
    test_water_level_dir = os.path.join(os.getcwd(), 'test_stations_harvey')
    
    # Define output directory in the current directory
    output_dir = os.path.join(os.getcwd(), 'predictionsharvey33')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define the checkpoint directory
    checkpoint_dir = '/home/samueldaramola/CNN/trainingcnn/checkpoints_cluster_33'
    
    # --------------------------------------
    # B. Load Normalization Parameters
    # --------------------------------------
    
    # Load normalization parameters
    normalization_params_path = os.path.join(checkpoint_dir, 'normalization_params.npy')
    if not os.path.exists(normalization_params_path):
        print(f"Normalization parameters not found at {normalization_params_path}. Exiting.")
        return
    normalization_params = np.load(normalization_params_path, allow_pickle=True).item()
    X_train_min_vals = normalization_params['X_train_min_vals']
    X_train_max_vals = normalization_params['X_train_max_vals']
    y_train_min = normalization_params['y_train_min']
    y_train_max = normalization_params['y_train_max']
    water_level_global_min = normalization_params.get('water_level_global_min', None)
    water_level_global_max = normalization_params.get('water_level_global_max', None)
    
    # --------------------------------------
    # C. Load Test Input Images
    # --------------------------------------
    
    # Load test input images
    test_atm_pressure_images, test_atm_filenames, crs, transform = load_tiff_images(test_atm_pressure_dir)
    test_wind_speed_images, test_wind_filenames, _, _ = load_tiff_images(test_wind_speed_dir)
    test_precipitation_images, test_precip_filenames, _, _ = load_tiff_images(test_precipitation_dir)
    test_river_discharge_images, test_river_discharge_filenames, _, _ = load_tiff_images(test_river_discharge_dir)
    
    # Load DEM image and replicate for all timesteps
    test_dem_image, _, _ = load_single_tiff_image(test_dem_file)
    num_test_timesteps = test_atm_pressure_images.shape[0]
    test_dem_images = np.tile(test_dem_image, (num_test_timesteps, 1, 1))
    
    # Stack input features (atm_pressure, wind_speed, DEM, precipitation, river discharge)
    X_test = np.stack((test_atm_pressure_images, test_wind_speed_images, test_dem_images, test_precipitation_images, test_river_discharge_images), axis=-1)
    
    # --------------------------------------
    # D. Define Sequence Length and Create Sequences
    # --------------------------------------
    
    # Define the sequence length (should match the training sequence length)
    sequence_length = 6
    
    # Create sequences for X_test
    X_test_sequences = []
    for i in range(len(X_test) - sequence_length + 1):
        X_test_sequences.append(X_test[i:i + sequence_length])
    X_test_sequences = np.array(X_test_sequences)
    
    # Load water depth data for testing
    y_test, y_test_filenames, _, _ = load_tiff_images(test_water_depth_dir)
    
    # Adjust y_test_sequences to align correctly
    y_test_sequences = y_test[sequence_length - 1:]
    X_test_sequences = X_test_sequences[:len(y_test_sequences)]
    
    # --------------------------------------
    # E. Normalize Input Features Using Training Min and Max Values
    # --------------------------------------
    
    X_test_norm_list = []
    for i in range(X_test_sequences.shape[-1]):
        min_val = X_train_min_vals[i]
        max_val = X_train_max_vals[i]
        norm_data = normalize_data_with_nan(X_test_sequences[..., i], min_val, max_val)
        X_test_norm_list.append(norm_data)
    X_test_norm = np.stack(X_test_norm_list, axis=-1)  # Shape: (num_sequences, sequence_length, height, width, channels)
    
    # --------------------------------------
    # F. Load and Normalize Water Level Data
    # --------------------------------------
    
    # Load water level data and create sequences
    test_water_level_data, test_water_level_filenames = load_water_level_data(test_water_level_dir)
    
    # Check if water_level_global_min and max exist
    if water_level_global_min is None or water_level_global_max is None:
        print("Global water level min and max not found in normalization parameters. Exiting.")
        return
    
    # Normalize test water level data globally
    test_water_level_data_norm = (test_water_level_data - water_level_global_min) / (water_level_global_max - water_level_global_min)
    
    # Create sequences for water level data
    test_water_level_data_sequences = []
    for i in range(test_water_level_data_norm.shape[1] - sequence_length + 1):
        test_water_level_data_sequences.append(test_water_level_data_norm[:, i:i + sequence_length])
    test_water_level_data_sequences = np.array(test_water_level_data_sequences)
    test_water_level_data_sequences = test_water_level_data_sequences.transpose(0, 2, 1)  # Shape: (num_samples, sequence_length, num_stations)
    
    # --------------------------------------
    # G. Ensure Sequence Alignment
    # --------------------------------------
    
    # Ensure that the number of sequences align across inputs and outputs
    min_sequences = min(X_test_norm.shape[0], test_water_level_data_sequences.shape[0], y_test_sequences.shape[0])
    X_test_norm = X_test_norm[:min_sequences]
    test_water_level_data_sequences = test_water_level_data_sequences[:min_sequences]
    y_test_sequences = y_test_sequences[:min_sequences]
    y_test_filenames = y_test_filenames[sequence_length - 1:sequence_length - 1 + min_sequences]
    
    print(f"X_test_norm.shape: {X_test_norm.shape}")
    print(f"test_water_level_data_sequences.shape: {test_water_level_data_sequences.shape}")
    print(f"y_test_sequences.shape: {y_test_sequences.shape}")
    
    # --------------------------------------
    # H. Normalize Output Data
    # --------------------------------------
    
    # Normalize output data using training min and max values
    y_test_nan_mask = np.isnan(y_test_sequences)
    y_test_norm = 0.1 + 0.9 * (y_test_sequences - y_train_min) / (y_train_max - y_train_min)
    y_test_norm[y_test_nan_mask] = 0  # Handle NaNs
    
    # --------------------------------------
    # I. Load the Trained Model with Custom Layers
    # --------------------------------------
    
    try:
        # Load the model with all custom objects
        model = load_model(
            os.path.join(checkpoint_dir, 'best_model.h5'),
            custom_objects={
                'StandardCBAM': StandardCBAM,
                'CustomAttentionLayer': CustomAttentionLayer,
                'ClusterBasedApplication': ClusterBasedApplication,
                'masked_mse': masked_mse,
                'TrueLoss': TrueLoss,
                # Include any other custom layers or functions here
            }
        )
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # --------------------------------------
    # J. Cluster Masks Loading and Validation
    # --------------------------------------
    
    # Define mask directory and shapefile path
    mask_dir = '/home/samueldaramola/CNN/trainingcnn'
    polygon_clusters_path = os.path.join(mask_dir, 'reordered_polygons.shp')
    
    def create_cluster_masks(polygon_shapefile, raster_shape, transform):
        """
        Creates mutually exclusive cluster masks by rasterizing polygons.

        Args:
            polygon_shapefile (str): Path to the shapefile containing cluster polygons.
            raster_shape (tuple): Shape of the raster as (height, width).
            transform (Affine): Affine transform of the raster.

        Returns:
            Tuple[np.ndarray, gpd.GeoDataFrame]: Array of cluster masks and the GeoDataFrame of polygons.
        """
        try:
            polygons_gdf = gpd.read_file(polygon_shapefile)
        except Exception as e:
            raise ValueError(f"Error loading shapefile {polygon_shapefile}: {e}")

        cluster_masks = []

        for i, polygon in enumerate(polygons_gdf.geometry):
            mask = rasterize(
                [(polygon, 1)],
                out_shape=raster_shape,
                transform=transform,
                fill=0,
                dtype='uint8'
            )
            cluster_masks.append(mask)

        cluster_masks = np.array(cluster_masks)
        print(f"Created {len(cluster_masks)} cluster masks from {polygon_shapefile}")

        # Ensure mutual exclusivity
        combined_mask = np.sum(cluster_masks.astype(int), axis=0)
        overlap = np.any(combined_mask > 1)

        if overlap:
            overlapping_pixels = np.sum(combined_mask > 1)
            raise ValueError(f"Overlap detected: {overlapping_pixels} pixels belong to multiple clusters!")
        else:
            print("Success: All pixels belong to at most one cluster.")

        return cluster_masks, polygons_gdf

    # Load cluster masks and polygons GeoDataFrame
    try:
        cluster_masks, polygons_gdf = create_cluster_masks(
            polygon_shapefile=polygon_clusters_path,
            raster_shape=(test_atm_pressure_images.shape[1], test_atm_pressure_images.shape[2]),
            transform=transform
        )
    except ValueError as ve:
        print(ve)
        print("Please ensure the shapefile exists at the specified path.")
        return

    # Number of clusters
    num_clusters = cluster_masks.shape[0]
    print(f"Number of clusters: {num_clusters}")

    # Verify the number of clusters and stations
    num_stations = len(test_water_level_filenames)
    if num_clusters != num_stations:
        print(f"\nMismatch detected: {num_clusters} clusters vs {num_stations} stations.")
        print("Please ensure that each cluster has a corresponding station.")
        # Optionally, handle the mismatch as per your requirements
    else:
        print(f"\nNumber of clusters ({num_clusters}) matches number of stations ({num_stations}).")

    # Print the first 5 clusters and their corresponding stations
    print("\nFirst 5 clusters and corresponding stations:")
    for i in range(min(5, num_clusters)):
        # Extract cluster name
        if 'name' in polygons_gdf.columns:
            cluster_name = polygons_gdf.iloc[i]['name']
        else:
            # If there's no 'name' column, use a default naming convention
            cluster_name = f"Cluster_{i+1}"
        
        # Extract station name
        station_name = test_water_level_filenames[i]
        
        print(f"Cluster {i+1}: {cluster_name} <-> Station {i+1}: {station_name}")

    # Convert cluster masks to tensor
    cluster_masks_tensor = tf.constant(cluster_masks, dtype=tf.float32)  # Shape: (num_clusters, height, width)

    # --------------------------------------
    # K. Ensure Mask Correctness
    # --------------------------------------
    
    # Reshape cluster masks for model input
    # The model expects (batch_size, sequence_length, height, width, 1)
    batch_size = X_test_norm.shape[0]
    sequence_length = X_test_norm.shape[1]
    
    # Combine cluster masks into a single mask by taking the maximum over clusters
    single_mask = np.max(cluster_masks, axis=0)  # Shape: (212, 230)
    print(f"After np.max: {single_mask.shape}")
    
    # Add a singleton dimension for the mask channel
    single_mask = single_mask[..., np.newaxis]    # Shape: (212, 230, 1)
    print(f"After adding channel dimension: {single_mask.shape}")
    
    # Expand dimensions to add batch and sequence dimensions
    single_mask = np.expand_dims(single_mask, axis=(0, 1))  # Shape: (1, 1, 212, 230, 1)
    print(f"After expanding batch and sequence dimensions: {single_mask.shape}")
    
    # Repeat the mask for each sample in the batch and each timestep
    single_mask = np.tile(single_mask, (batch_size, sequence_length, 1, 1, 1))  # Shape: (260, 6, 212, 230, 1)
    print(f"After tiling for batch and sequence: {single_mask.shape}")
    
    # Convert to Tensor
    mask_tensor = tf.constant(single_mask, dtype=tf.float32)  # Shape: (260, 6, 212, 230, 1)
    print(f"mask_tensor shape before visualization: {mask_tensor.shape}")  # Should print (260, 6, 212, 230, 1)
    
    # Verify mask distribution
    verify_mask_distribution(mask_tensor.numpy())
    
    # Visualize the first mask of the first sequence
    visualize_mask(mask_tensor.numpy(), index=0, timestep=0)

    # --------------------------------------
    # L. Define Function to Create Attention Model
    # --------------------------------------
    
    def create_attention_models(model):
        """
        Creates separate models to output temporal and spatial attention vectors.

        Args:
            model (tf.keras.Model): Trained model.

        Returns:
            Tuple[tf.keras.Model, tf.keras.Model]: Models that output temporal and spatial attention vectors.
        """
        temporal_attention_model = None
        spatial_attention_model = None

        try:
            # Access the Temporal_Attention layer
            if 'Temporal_Attention' in [layer.name for layer in model.layers]:
                temporal_attention_layer = model.get_layer('Temporal_Attention')
                temporal_attention_output = temporal_attention_layer.output[1]
                temporal_attention_model = Model(
                    inputs=model.inputs,
                    outputs=temporal_attention_output,
                    name='Temporal_Attention_Model'
                )
            else:
                print("Layer 'Temporal_Attention' not found in the model.")

            # Access the CBAM_3 layer
            if 'CBAM_3' in [layer.name for layer in model.layers]:
                cbam3_layer = model.get_layer('CBAM_3')
                # The outputs of CBAM_3 are (refined_feature, spatial_attention_map)
                _, spatial_attention_map = cbam3_layer.output
                spatial_attention_model = Model(
                    inputs=model.inputs,
                    outputs=spatial_attention_map,
                    name='Spatial_Attention_Model'
                )
            else:
                print("Layer 'CBAM_3' not found in the model.")

            return temporal_attention_model, spatial_attention_model

        except Exception as e:
            print(f"Error creating attention models: {e}")
            return temporal_attention_model, spatial_attention_model

    # Create separate models for temporal and spatial attention
    temporal_attention_model, spatial_attention_model = create_attention_models(model)

    # --------------------------------------
    # M. Perform Predictions and Save as TIFF Images
    # --------------------------------------
    
    for i in range(len(X_test_norm)):
        X = X_test_norm[i:i + 1]                           # Shape: (1, 6, 212, 230, 5)
        mask_sample = mask_tensor[i:i + 1]                 # Shape: (1, 6, 212, 230, 1)
        water_level = test_water_level_data_sequences[i:i + 1]  # Shape: (1, 6, 21)
    
        # Make prediction
        preds = model.predict([X, mask_sample, water_level])
    
        # Ensure preds is squeezed to remove batch dimension
        preds_denorm = denormalize_data(preds[0], y_train_min, y_train_max)
        preds_denorm = apply_nan_mask(preds_denorm, y_test_nan_mask[i].squeeze())
    
        # Save prediction as TIFF
        output_filename = y_test_filenames[i]
        output_path = os.path.join(output_dir, output_filename)
        reference_dataset = os.path.join(test_water_depth_dir, output_filename)
        if not os.path.exists(reference_dataset):
            print(f"Reference dataset {reference_dataset} not found. Skipping saving prediction {i}.")
            continue
        save_tiff_image(preds_denorm, output_path, reference_dataset)
        print(f"Saved prediction {i} to {output_path}")
    
    # --------------------------------------
    # N. Load Actual and Predicted Water Depth Data
    # --------------------------------------
    
    # Prepare time series data for valid areas
    actual_water_depth, actual_filenames, _, _ = load_tiff_images(test_water_depth_dir)
    predicted_water_depth, predicted_filenames, _, _ = load_tiff_images(output_dir)
    
    # Ensure filenames of actual and predicted data match
    common_filenames = sorted(list(set(actual_filenames) & set(predicted_filenames)))
    
    if not common_filenames:
        print("No matching filenames found between actual and predicted data. Please verify the filenames.")
        return  # Exit the main function or handle appropriately
    
    # Filter actual and predicted water depth based on matching filenames
    actual_filtered = []
    predicted_filtered = []
    
    for filename in common_filenames:
        actual_idx = actual_filenames.index(filename)
        predicted_idx = predicted_filenames.index(filename)
        
        actual_filtered.append(actual_water_depth[actual_idx])
        predicted_filtered.append(predicted_water_depth[predicted_idx])
    
    # Convert filtered data to numpy arrays
    actual_filtered = np.array(actual_filtered)
    predicted_filtered = np.array(predicted_filtered)
    
    # --------------------------------------
    # O. Time Series Analysis at Specific Locations
    # --------------------------------------
    
    # Define coordinates for the new areas
    area_coords = {
        'West University Place, TX': (29.715929, -95.432992),
        'Green Lake Oil Field, TX': (29.26667, -95.0088),
        'Moody National Wildlife Refuge, TX': (29.55, -94.66)
    }
    
    # Function to get row, col index for coordinates
    def get_index_from_coords(lat, lon, transform):
        """Convert latitude/longitude to row/col index in raster grid"""
        try:
            col, row = ~transform * (lon, lat)
            return int(row), int(col)
        except Exception as e:
            print(f"Error converting coordinates ({lat}, {lon}): {e}")
            return None, None
    
    # Prepare time series data for valid areas
    actual_ts_dict = {}
    predicted_ts_dict = {}
    valid_areas = []
    
    for area, coords in area_coords.items():
        # Get row, col for each area
        row, col = get_index_from_coords(coords[0], coords[1], transform)
        
        if row is None or col is None:
            print(f"Skipping {area} due to coordinate conversion error.")
            continue
    
        # Check if row and col are within the bounds of the raster grid
        if (0 <= row < actual_filtered.shape[1]) and (0 <= col < actual_filtered.shape[2]):
            # Extract actual water depth time series
            actual_ts = actual_filtered[:, row, col]
            predicted_ts = predicted_filtered[:, row, col]
    
            # Check if all values are NaN
            if np.isnan(actual_ts).all() and np.isnan(predicted_ts).all():
                print(f"All values are NaN for area {area}. Skipping...")
                continue
    
            actual_ts_dict[area] = actual_ts
            predicted_ts_dict[area] = predicted_ts
            valid_areas.append(area)
        else:
            print(f"Skipping {area}: coordinates fall outside the raster grid.")
    
    if not valid_areas:
        print("No valid areas found within the raster grid.")
        return
    
    # Collect all min and max values, ignoring NaNs
    y_min_values = []
    y_max_values = []
    
    for area in valid_areas:
        actual_vals = actual_ts_dict[area]
        predicted_vals = predicted_ts_dict[area]
    
        # Remove NaN values
        actual_vals = actual_vals[~np.isnan(actual_vals)]
        predicted_vals = predicted_vals[~np.isnan(predicted_vals)]
    
        # Append min and max values, if arrays are not empty
        if actual_vals.size > 0:
            y_min_values.append(actual_vals.min())
            y_max_values.append(actual_vals.max())
    
        if predicted_vals.size > 0:
            y_min_values.append(predicted_vals.min())
            y_max_values.append(predicted_vals.max())
    
    # Proceed if we have valid min and max values
    if y_min_values and y_max_values:
        y_min = min(y_min_values) - 0.05
        y_max = max(y_max_values) + 0.05
    else:
        print("No valid min or max values found. Exiting plotting.")
        return
    
    # Plot the comparison for valid areas in subplots
    fig, axes = plt.subplots(1, len(valid_areas), figsize=(12, 3), sharey=True)
    
    # Adjust axes handling when there's only one valid subplot
    if len(valid_areas) == 1:
        axes = [axes]  # Convert to list
    
    for i, area in enumerate(valid_areas):
        actual_vals = actual_ts_dict[area]
        predicted_vals = predicted_ts_dict[area]
    
        axes[i].plot(actual_vals, label='Actual Water Depth', color='blue', linestyle='-', marker='')
        axes[i].plot(predicted_vals, label='Predicted Water Depth', color='red', linestyle='-', marker='')
        axes[i].set_title(f'{area}')
        axes[i].set_xlabel('Timesteps')
        axes[i].set_ylim([y_min, y_max])  # Apply the y-axis limits
        axes[i].grid(False)
    
    # Shared y-axis label
    axes[0].set_ylabel('Water Depth (m)')
    
    # Adjust the position of the legend and the title
    fig.suptitle('Hurricane Harvey 2017', y=1.05)  # Title adjusted
    fig.legend(['Actual Water Depth', 'Predicted Water Depth'], loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.0))
    
    # Adjust layout to add space at the top and bottom
    plt.tight_layout(rect=[0, 0.05, 1, 0.85])  # Leave a gap at the bottom and top
    plt.subplots_adjust(top=0.8, bottom=0.1)  # Extra space at the top and bottom
    
    # Save the figure
    plt.savefig('harvey.png', dpi=300, bbox_inches='tight')
    
    plt.show()
            
    # --------------------------------------
    # Q. Final Completion Message
    # --------------------------------------
    
    print("Model evaluation and visualization completed successfully.")

if __name__ == "__main__":
    main()



















# ==========================================
# Flood Depth Prediction Model Evaluation
# Hurricane Nicolas 2021
# ==========================================

# ------------------------------------------
# 1. Import Necessary Libraries
# ------------------------------------------
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import rasterio
import geopandas as gpd
from tensorflow.keras.models import Model
from tensorflow.keras.initializers import HeNormal, GlorotNormal
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import load_model
from rasterio.features import rasterize
from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
from tensorflow.keras.layers import (
    Conv2D, Multiply, Dense, Reshape, Flatten, Input, ConvLSTM2D, LSTM,
    Activation, LayerNormalization, Lambda, Add, Concatenate, GlobalAveragePooling2D,
    GlobalMaxPooling2D
)
from tensorflow.keras.regularizers import l2
import matplotlib.patches as patches

# ------------------------------------------
# 2. Setup and Configuration
# ------------------------------------------

# Seed for reproducibility
seed_value = 3
np.random.seed(seed_value)
tf.random.set_seed(seed_value)

# Check and configure GPU usage
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Enable mixed precision (if desired)
from tensorflow.keras.mixed_precision import set_global_policy
set_global_policy('float32')

# ------------------------------------------
# 3. Helper Functions
# ------------------------------------------

def load_tiff_images(data_dir):
    """
    Loads all TIFF images from a specified directory.

    Args:
        data_dir (str): Path to the directory containing TIFF files.

    Returns:
        Tuple[np.ndarray, List[str], Any, Any]: Loaded images array, filenames, CRS, and transform.
    """
    images = []
    filenames = []
    crs = None
    transform = None
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".tif"):
            filepath = os.path.join(data_dir, filename)
            with rasterio.open(filepath) as src:
                img = src.read(1)
                if crs is None:
                    crs = src.crs
                if transform is None:
                    transform = src.transform
                images.append(img)
            filenames.append(filename)
    print(f"Loaded {len(images)} TIFF images from {data_dir}")
    return np.array(images), filenames, crs, transform

def load_single_tiff_image(filepath):
    """
    Loads a single TIFF image.

    Args:
        filepath (str): Path to the TIFF file.

    Returns:
        Tuple[np.ndarray, Any, Any]: Loaded image array, CRS, and transform.
    """
    with rasterio.open(filepath) as src:
        img = src.read(1)
        crs = src.crs
        transform = src.transform
    print(f"Loaded single TIFF image from {filepath}")
    return img, crs, transform

def natural_sort(file_list):
    """
    Sorts a list of filenames in a natural, human-friendly order.
    
    Args:
        file_list (List[str]): List of filenames to sort.
    
    Returns:
        List[str]: Naturally sorted list of filenames.
    """
    def alphanum_key(key):
        # Split the key into a list of strings and integers
        return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', key)]
    
    return sorted(file_list, key=alphanum_key)

def load_water_level_data(data_dir):
    """
    Loads water level data from CSV files for each station, sorted naturally.

    Args:
        data_dir (str): Path to the directory containing water level CSV files.

    Returns:
        Tuple[np.ndarray, List[str]]: Water level data array and naturally sorted filenames.
    """
    water_level_data = []
    filenames = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    filenames = natural_sort(filenames)  # Apply natural sorting
    for filename in filenames:
        filepath = os.path.join(data_dir, filename)
        df = pd.read_csv(filepath)
        if 'water_level' in df.columns:
            water_level_data.append(df['water_level'].values)
        else:
            print(f"'water_level' column not found in {filepath}. Skipping.")
    print(f"Loaded water level data from {data_dir} with {len(water_level_data)} stations.")
    return np.array(water_level_data), filenames

def normalize_data_with_nan(data, min_val, max_val):
    """
    Normalizes data to the range [0.1, 1.0], handling NaN values.

    Args:
        data (np.ndarray): Input data array.
        min_val (float): Minimum value for normalization.
        max_val (float): Maximum value for normalization.

    Returns:
        np.ndarray: Normalized data array.
    """
    nan_mask = np.isnan(data)
    norm_data = 0.1 + 0.9 * (data - min_val) / (max_val - min_val)
    norm_data[nan_mask] = 0  # Set NaN cells to 0 after normalization
    return norm_data

def denormalize_data(norm_data, min_val, max_val):
    """
    Denormalizes data from the range [0.1, 1.0] back to original scale.

    Args:
        norm_data (np.ndarray): Normalized data array.
        min_val (float): Minimum value used during normalization.
        max_val (float): Maximum value used during normalization.

    Returns:
        np.ndarray: Denormalized data array.
    """
    return (norm_data - 0.1) / 0.9 * (max_val - min_val) + min_val

def apply_nan_mask(data, mask):
    """
    Applies a NaN mask to data.

    Args:
        data (np.ndarray): Data array.
        mask (np.ndarray): Boolean mask where True indicates NaN.

    Returns:
        np.ndarray: Data array with NaNs applied.
    """
    data = data.copy()  # Avoid modifying the original data
    data[mask] = np.nan
    return data

def save_tiff_image(data, output_path, reference_dataset):
    """
    Saves a data array as a TIFF image using a reference dataset for metadata.

    Args:
        data (np.ndarray): Data array to save.
        output_path (str): Output file path.
        reference_dataset (str): Path to a reference TIFF file for metadata.
    """
    with rasterio.open(reference_dataset) as src:
        out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": src.crs,
        "transform": src.transform
    })
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(data.astype(np.float32), 1)
    print(f"Saved TIFF image to {output_path}")

def verify_mask_distribution(mask):
    """
    Verifies the distribution of valid and invalid pixels in the mask.

    Args:
        mask (np.ndarray): Mask array with shape (num_sequences, sequence_length, height, width, 1).
    """
    total_pixels = mask.size
    valid_pixels = np.sum(mask == 1)
    invalid_pixels = np.sum(mask == 0)
    
    print(f"Total Pixels: {total_pixels}")
    print(f"Valid Pixels (1): {valid_pixels} ({(valid_pixels / total_pixels) * 100:.2f}%)")
    print(f"Invalid Pixels (0): {invalid_pixels} ({(invalid_pixels / total_pixels) * 100:.2f}%)")

def visualize_mask(mask, index=0, timestep=0):
    """
    Visualizes the mask to ensure correct inversion.

    Args:
        mask (np.ndarray): Mask array with shape (batch_size, sequence_length, height, width, 1).
        index (int): Sequence index to visualize.
        timestep (int): Timestep index to visualize.
    """
    # Verify mask dimensions
    if mask.ndim != 5:
        raise ValueError(f"Expected mask to be 5D, but got {mask.ndim}D.")

    batch_size, sequence_length, height, width, channels = mask.shape
    if channels != 1:
        raise ValueError(f"Expected mask to have 1 channel, but got {channels} channels.")

    # Extract the specific mask slice
    mask_sample = mask[index, timestep, :, :, 0]

    plt.figure(figsize=(6, 6))
    plt.title('Valid Mask (1=Valid, 0=Invalid)')
    plt.imshow(mask_sample, cmap='gray')
    plt.colorbar()
    plt.axis('off')
    plt.show()
    
import matplotlib.patches as patches

def visualize_spatial_attention_with_clusters(spatial_attention_map, polygons_gdf, transform, vmin=None, vmax=None):
    """
    Visualizes the spatial attention map with cluster polygons overlayed, masking invalid areas.
    
    Args:
        spatial_attention_map (np.ndarray): Spatial attention map array with shape (height, width).
        polygons_gdf (gpd.GeoDataFrame): GeoDataFrame containing cluster polygons.
        transform (Affine): Affine transform of the raster.
        vmin (float, optional): Minimum value for the color map.
        vmax (float, optional): Maximum value for the color map.
    """
    # Mask out values outside the valid range by setting them to NaN
    masked_attention_map = np.where((spatial_attention_map >= vmin) & (spatial_attention_map <= vmax), spatial_attention_map, np.nan)

    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the masked attention map
    im = ax.imshow(masked_attention_map, cmap='viridis', vmin=vmin, vmax=vmax)
    ax.set_title('Spatial Attention Map with Cluster Overlays')
    ax.axis('off')
    
    # Plot polygons
    for idx, polygon in polygons_gdf.geometry.items():
        if polygon.is_empty:
            continue
        polygon_pixels = []
        for coord in polygon.exterior.coords:
            col, row = ~transform * (coord[0], coord[1])
            polygon_pixels.append((col, row))
        polygon_pixels = np.array(polygon_pixels)
        ax.add_patch(patches.Polygon(polygon_pixels, linewidth=1, edgecolor='red', facecolor='none'))
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Normalized Attention Weight', rotation=270, labelpad=15)

    # Save and show the plot
    plt.savefig('spatial_attention_with_clusters_masked.png', dpi=300, bbox_inches='tight')
    plt.show()
    
# ==========================================
# 3. Custom Attention Mechanisms
# ==========================================

def masked_global_average_pooling2d(inputs, mask):
    masked_inputs = inputs * mask  # Shape: (batch, height, width, channels)
    sum_pool = tf.reduce_sum(masked_inputs, axis=[1, 2])  # Shape: (batch, channels)
    valid_pixels = tf.reduce_sum(mask, axis=[1, 2]) + tf.keras.backend.epsilon()  # Shape: (batch, 1)
    avg_pool = sum_pool / valid_pixels  # Shape: (batch, channels)
    return avg_pool

def masked_global_max_pooling2d(inputs, mask):
    masked_inputs = inputs * mask + (1.0 - mask) * (-1e9)  # Shape: (batch, height, width, channels)
    max_pool = tf.reduce_max(masked_inputs, axis=[1, 2])  # Shape: (batch, channels)
    return max_pool

class StandardCBAM(Layer):
    def __init__(self, ratio=8, kernel_size=7, return_attention=False, **kwargs):
        super(StandardCBAM, self).__init__(**kwargs)
        self.ratio = ratio
        self.kernel_size = kernel_size
        self.return_attention = return_attention

    def build(self, input_shape):
        if isinstance(input_shape, list):
            raise ValueError("StandardCBAM now expects a single concatenated input.")

        total_channels = input_shape[-1]
        self.feature_channels = total_channels - 1  # Last channel is assumed to be the mask

        # Channel Attention layers without fixed names
        self.shared_dense_one = Dense(
            self.feature_channels // self.ratio,
            activation='relu',
            kernel_initializer='he_normal',
            use_bias=True,
            bias_initializer='zeros'
        )
        self.shared_dense_two = Dense(
            self.feature_channels,
            activation='sigmoid',
            kernel_initializer='glorot_normal',
            use_bias=True,
            bias_initializer='zeros'
        )

        # Spatial Attention convolutional layer without fixed name
        self.conv_spatial = Conv2D(
            filters=1,
            kernel_size=self.kernel_size,
            strides=1,
            padding='same',
            activation='sigmoid',
            kernel_initializer='glorot_normal',
            use_bias=False
        )

        super(StandardCBAM, self).build(input_shape)

    def call(self, inputs, training=None):
        # Split feature and mask channels
        feature = inputs[..., :self.feature_channels]
        mask = inputs[..., self.feature_channels:]  # Shape: (batch, height, width, 1)

        # tf.print("Feature shape:", tf.shape(feature))
        # tf.print("Mask shape:", tf.shape(mask))

        # --- Channel Attention ---
        # Apply masked global average and max pooling
        avg_pool = masked_global_average_pooling2d(feature, mask)  # Shape: (batch, channels)
        # tf.print("Average Pool shape:", tf.shape(avg_pool))
        avg_pool = self.shared_dense_one(avg_pool)  # Shape: (batch, channels // ratio)
        avg_pool = self.shared_dense_two(avg_pool)  # Shape: (batch, channels)

        max_pool = masked_global_max_pooling2d(feature, mask)  # Shape: (batch, channels)
        # tf.print("Max Pool shape:", tf.shape(max_pool))
        max_pool = self.shared_dense_one(max_pool)  # Shape: (batch, channels // ratio)
        max_pool = self.shared_dense_two(max_pool)  # Shape: (batch, channels)

        # Combine average and max pooling
        channel_attention = Add()([avg_pool, max_pool])  # Shape: (batch, channels)
        channel_attention = Activation('sigmoid')(channel_attention)  # Shape: (batch, channels)

        # tf.print("Channel Attention shape:", tf.shape(channel_attention))

        # Reshape for broadcasting across spatial dimensions using Keras Reshape
        channel_attention = Reshape((1, 1, self.feature_channels))(channel_attention)
        # tf.print("Reshaped Channel Attention shape:", tf.shape(channel_attention))

        # Apply channel attention to the features
        refined_feature = Multiply()([feature, channel_attention])  # Shape: (batch, height, width, channels)
        # tf.print("Refined Feature shape:", tf.shape(refined_feature))

        # --- Spatial Attention ---
        # Generate spatial attention map using a convolutional layer
        spatial_attention = self.conv_spatial(refined_feature)  # Shape: (batch, height, width, 1)
        # tf.print("Spatial Attention shape:", tf.shape(spatial_attention))
        
        # Apply mask to ensure invalid cells are zeroed
        spatial_attention = Multiply()([spatial_attention, mask])  # Shape: (batch, height, width, 1)
        # tf.print("Masked Spatial Attention shape:", tf.shape(spatial_attention))

        # Apply spatial attention to the refined features
        refined_feature = Multiply()([refined_feature, spatial_attention])  # Shape: (batch, height, width, channels)
        # tf.print("Final Refined Feature shape:", tf.shape(refined_feature))

        # Return both refined feature and spatial attention map if requested
        if self.return_attention:
            return refined_feature, spatial_attention
        else:
            return refined_feature

    def compute_output_shape(self, input_shape):
        """
        Computes the output shape of the layer.

        Args:
            input_shape (tuple): Shape of the input tensor.

        Returns:
            tuple: Shape of the output tensor.
        """
        # Determine if the input is 4D or 5D
        if len(input_shape) == 5:
            # Input shape: (batch, time, height, width, channels +1)
            return (input_shape[0], input_shape[1], input_shape[2], input_shape[3], self.feature_channels)
        elif len(input_shape) == 4:
            # Input shape: (batch, height, width, channels +1)
            return (input_shape[0], input_shape[1], input_shape[2], self.feature_channels)
        else:
            raise ValueError(f"Unsupported input shape: {input_shape}")

    def get_config(self):
        config = super(StandardCBAM, self).get_config()
        config.update({
            "ratio": self.ratio,
            "kernel_size": self.kernel_size,
            "return_attention": self.return_attention
        })
        return config

class CustomAttentionLayer(Layer):
    def __init__(self, emphasis_factor=1.5, top_k_percent=0.2, **kwargs):
        super(CustomAttentionLayer, self).__init__(**kwargs)
        self.emphasis_factor = emphasis_factor
        self.top_k_percent = top_k_percent

    def get_config(self):
        config = super(CustomAttentionLayer, self).get_config()
        config.update({
            "emphasis_factor": self.emphasis_factor,
            "top_k_percent": self.top_k_percent
        })
        return config

    def build(self, input_shape):
        # Build as before
        self.W = self.add_weight(name='att_weight',
                                 shape=(input_shape[-1], 1),
                                 initializer=GlorotNormal(),
                                 trainable=True)
        self.b = self.add_weight(shape=(1,),
                                 initializer='zeros',
                                 trainable=True,
                                 name='bias')
        super(CustomAttentionLayer, self).build(input_shape)

    def call(self, x):
        # Compute attention weights
        e = K.tanh(K.dot(x, self.W) + self.b)  # (batch_size, timesteps, 1)
        a = K.softmax(e, axis=1)               # (batch_size, timesteps, 1)
        a = K.squeeze(a, axis=-1)              # (batch_size, timesteps)

        # Emphasize top-k attention weights
        k_value = tf.cast(tf.cast(tf.shape(a)[1], tf.float32) * self.top_k_percent, tf.int32)
        k_value = tf.maximum(k_value, 1)
        top_k_values, top_k_indices = tf.math.top_k(a, k=k_value)
        mask = tf.one_hot(top_k_indices, depth=tf.shape(a)[1])  # (batch_size, k, timesteps)
        mask = tf.reduce_max(mask, axis=1)                      # (batch_size, timesteps)
        mask = tf.cast(mask, tf.bool)
        emphasized_a = tf.where(mask, a * self.emphasis_factor, a)  # (batch_size, timesteps)

        # Compute the context vector
        output = x * tf.expand_dims(emphasized_a, axis=-1)  # (batch_size, timesteps, features)
        summed_output = K.sum(output, axis=1)               # (batch_size, features)

        # Return both the context vector and the attention weights
        return [summed_output, emphasized_a]

    def compute_output_shape(self, input_shape):
        context_shape = (input_shape[0], input_shape[-1])
        attention_shape = (input_shape[0], input_shape[1])
        return [context_shape, attention_shape]

class ClusterBasedApplication(Layer):
    def __init__(self, num_stations, height, width, **kwargs):
        super(ClusterBasedApplication, self).__init__(**kwargs)
        self.num_stations = num_stations
        self.height = height
        self.width = width

    def build(self, input_shape):
        # Define Dense layer to project context vectors to spatial dimensions
        self.dense_project = Dense(self.height * self.width,
                                   activation='relu',
                                   kernel_initializer='he_normal',
                                   kernel_regularizer=l2(1e-5),
                                   name='Dense_Project_Context')
        super(ClusterBasedApplication, self).build(input_shape)

    def call(self, inputs):
        attention_outputs, cluster_masks_tensor = inputs  # attention_outputs: (batch, num_stations, features)
        
        # Dynamically determine batch size
        batch_size = tf.shape(attention_outputs)[0]
        
        # Project context vectors to spatial dimensions
        reshaped_context = self.dense_project(attention_outputs)  # Shape: (batch, num_stations, height * width)
        reshaped_context = tf.reshape(reshaped_context, (batch_size, self.num_stations, self.height, self.width))  # Shape: (batch, num_stations, height, width)
        
        # Expand cluster masks to match batch size
        cluster_masks_expanded = tf.expand_dims(cluster_masks_tensor, axis=0)  # Shape: (1, num_stations, height, width)
        cluster_masks_expanded = tf.tile(cluster_masks_expanded, [batch_size, 1, 1, 1])  # Shape: (batch, num_stations, height, width)
        cluster_masks_expanded = tf.cast(cluster_masks_expanded, reshaped_context.dtype)
        
        # Apply cluster masks
        localized_context = reshaped_context * cluster_masks_expanded  # Shape: (batch, num_stations, height, width)
        
        # Compute cluster indices
        cluster_indices = tf.argmax(tf.cast(cluster_masks_tensor, tf.int32), axis=0)  # Shape: (height, width)
        
        # One-hot encode cluster indices
        cluster_indices_one_hot = tf.one_hot(cluster_indices, depth=self.num_stations)  # Shape: (height, width, num_stations)
        cluster_indices_one_hot = tf.transpose(cluster_indices_one_hot, perm=[2, 0, 1])  # Shape: (num_stations, height, width)
        cluster_indices_one_hot = tf.expand_dims(cluster_indices_one_hot, axis=0)  # Shape: (1, num_stations, height, width)
        cluster_indices_one_hot = tf.tile(cluster_indices_one_hot, [batch_size, 1, 1, 1])  # Shape: (batch, num_stations, height, width)
        
        # Select the correct context
        selected_context = tf.reduce_sum(localized_context * cluster_indices_one_hot, axis=1)  # Shape: (batch, height, width)
        
        # Expand dimensions to match spatial features
        combined_context = tf.expand_dims(selected_context, axis=-1)  # Shape: (batch, height, width, 1)
        
        return combined_context  # Shape: (batch, height, width, 1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], self.height, self.width, 1)

    def get_config(self):
        config = super(ClusterBasedApplication, self).get_config()
        config.update({
            "num_stations": self.num_stations,
            "height": self.height,
            "width": self.width
        })
        return config

# ==========================================
# 4. Loss Function
# ==========================================

def masked_mse(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    mask = tf.math.not_equal(y_true, 0.0)
    mask = tf.cast(mask, y_true.dtype)
    mse = tf.square(y_true - y_pred)
    mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
    return mse

# TrueLoss Metric Definition
class TrueLoss(tf.keras.metrics.Metric):
    def __init__(self, name='trueloss', **kwargs):
        super(TrueLoss, self).__init__(name=name, **kwargs)
        self.true_loss = self.add_weight(name='tl', initializer='zeros')
        self.count = self.add_weight(name='count', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        """
        Updates the state of the metric with the current batch's loss.

        Args:
            y_true (Tensor): Ground truth values.
            y_pred (Tensor): Predicted values.
            sample_weight (Tensor, optional): Sample weights.
        """
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        
        # Create mask: 1 for valid pixels, 0 otherwise
        mask = tf.math.not_equal(y_true, 0.0)
        mask = tf.cast(mask, y_true.dtype)
        
        # Compute squared errors
        mse = tf.square(y_true - y_pred)
        
        # Apply mask
        masked_mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
        
        # Update accumulators
        self.true_loss.assign_add(masked_mse)
        self.count.assign_add(1.0)
        pass

    def result(self):
        """
        Computes the average TrueLoss over all batches.

        Returns:
            Tensor: The average TrueLoss.
        """
        return self.true_loss / self.count
        pass

    def reset_state(self):
        """
        Resets the state of the metric.
        """
        self.true_loss.assign(0.0)
        self.count.assign(0.0)

# ------------------------------------------
# 6. Model Evaluation and Visualization Functions
# ------------------------------------------

def plot_and_compare_predictions(model, X_test, mask, water_level_data, y_test, y_test_nan_mask, filenames, num_images=2):
    """
    Plots and compares actual vs. predicted water depth images.

    Args:
        model (tf.keras.Model): Loaded TensorFlow model.
        X_test (np.ndarray): Normalized test input sequences.
        mask (np.ndarray): Cluster mask for the test data.
        water_level_data (np.ndarray): Normalized water level sequences.
        y_test (np.ndarray): Normalized ground truth water depth maps.
        y_test_nan_mask (np.ndarray): Mask indicating NaN values in y_test.
        filenames (List[str]): List of filenames corresponding to y_test.
        num_images (int): Number of images to plot for comparison.
    """
    mse_list, rmse_list, r2_list, mse_filenames = [], [], [], []
    for i in range(len(X_test)):
        X = X_test[i:i + 1]
        mask_sample = mask[i:i + 1]
        water_level = water_level_data[i:i + 1]
        y = y_test[i]

        # Make prediction
        preds = model.predict([X, mask_sample, water_level])

        # Ensure preds is squeezed to remove batch dimension
        preds_denorm = denormalize_data(preds[0], y_train_min, y_train_max)
        y_true = denormalize_data(y, y_train_min, y_train_max)

        # Apply NaN mask
        preds_denorm = apply_nan_mask(preds_denorm, y_test_nan_mask[i].squeeze())
        y_true = apply_nan_mask(y_true, y_test_nan_mask[i].squeeze())

        # Calculate MSE, RMSE, and R^2
        valid_mask = ~np.isnan(y_true)
        if np.any(valid_mask):
            mse = mean_squared_error(y_true[valid_mask], preds_denorm[valid_mask])
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true[valid_mask], preds_denorm[valid_mask])

            mse_list.append(mse)
            rmse_list.append(rmse)
            r2_list.append(r2)
            mse_filenames.append(filenames[i])

            if i < num_images:  # Only plot a specified number of images
                fig, axes = plt.subplots(1, 2, figsize=(12, 6))

                # Actual Water Depth
                im = axes[0].imshow(y_true, cmap='jet')
                axes[0].set_title(f'Actual Water Depth\n({filenames[i]})')
                axes[0].axis('off')
                plt.colorbar(im, ax=axes[0])

                # Predicted Water Depth
                im = axes[1].imshow(preds_denorm, cmap='jet')
                axes[1].set_title(f'Predicted Water Depth\n({filenames[i]})')
                axes[1].axis('off')
                plt.colorbar(im, ax=axes[1])

                plt.suptitle(f'MSE: {mse:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}')
                plt.tight_layout()
                plt.show()
        else:
            print(f"No valid data points for index {i}. Skipping...")

    if mse_list:
        avg_mse, avg_rmse, avg_r2 = np.mean(mse_list), np.mean(rmse_list), np.mean(r2_list)
        max_rmse_index = np.argmax(rmse_list)
        max_rmse = rmse_list[max_rmse_index]
        max_rmse_filename = mse_filenames[max_rmse_index]

        print(f'Average MSE: {avg_mse:.4f}, RMSE: {avg_rmse:.4f}, R²: {avg_r2:.4f}')
        print(f'Largest RMSE: {max_rmse:.4f}, Filename: {max_rmse_filename}')
    else:
        print("No valid predictions made.")

# ------------------------------------------
# 7. Main Execution Flow
# ------------------------------------------

def main():
    # --------------------------------------
    # A. Define Directories and Paths
    # --------------------------------------
    
    # Directories for testing data
    test_atm_pressure_dir = os.path.join(os.getcwd(), 'atm_pressure')
    test_wind_speed_dir = os.path.join(os.getcwd(), 'wind_speed')
    test_precipitation_dir = os.path.join(os.getcwd(), 'precipitation')
    test_river_discharge_dir = os.path.join(os.getcwd(), 'river_discharge')
    test_water_depth_dir = os.path.join(os.getcwd(), 'water_depth')
    test_dem_file = os.path.join(os.getcwd(), 'DEM/dem_idw.tif')
    test_water_level_dir = os.path.join(os.getcwd(), 'test_stations_nicolas')
    
    # Define output directory in the current directory
    output_dir = os.path.join(os.getcwd(), 'predictionsnicolas48')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define the checkpoint directory
    checkpoint_dir = '/home/samueldaramola/CNN/trainingcnn/checkpoints_cluster_48'
    
    # --------------------------------------
    # B. Load Normalization Parameters
    # --------------------------------------
    
    # Load normalization parameters
    normalization_params_path = os.path.join(checkpoint_dir, 'normalization_params.npy')
    if not os.path.exists(normalization_params_path):
        print(f"Normalization parameters not found at {normalization_params_path}. Exiting.")
        return
    normalization_params = np.load(normalization_params_path, allow_pickle=True).item()
    X_train_min_vals = normalization_params['X_train_min_vals']
    X_train_max_vals = normalization_params['X_train_max_vals']
    y_train_min = normalization_params['y_train_min']
    y_train_max = normalization_params['y_train_max']
    water_level_global_min = normalization_params.get('water_level_global_min', None)
    water_level_global_max = normalization_params.get('water_level_global_max', None)
    
    # --------------------------------------
    # C. Load Test Input Images
    # --------------------------------------
    
    # Load test input images
    test_atm_pressure_images, test_atm_filenames, crs, transform = load_tiff_images(test_atm_pressure_dir)
    test_wind_speed_images, test_wind_filenames, _, _ = load_tiff_images(test_wind_speed_dir)
    test_precipitation_images, test_precip_filenames, _, _ = load_tiff_images(test_precipitation_dir)
    test_river_discharge_images, test_river_discharge_filenames, _, _ = load_tiff_images(test_river_discharge_dir)
    
    # Load DEM image and replicate for all timesteps
    test_dem_image, _, _ = load_single_tiff_image(test_dem_file)
    num_test_timesteps = test_atm_pressure_images.shape[0]
    test_dem_images = np.tile(test_dem_image, (num_test_timesteps, 1, 1))
    
    # Stack input features (atm_pressure, wind_speed, DEM, precipitation, river discharge)
    X_test = np.stack((test_atm_pressure_images, test_wind_speed_images, test_dem_images, test_precipitation_images, test_river_discharge_images), axis=-1)
    
    # --------------------------------------
    # D. Define Sequence Length and Create Sequences
    # --------------------------------------
    
    # Define the sequence length (should match the training sequence length)
    sequence_length = 6
    
    # Create sequences for X_test
    X_test_sequences = []
    for i in range(len(X_test) - sequence_length + 1):
        X_test_sequences.append(X_test[i:i + sequence_length])
    X_test_sequences = np.array(X_test_sequences)
    
    # Load water depth data for testing
    y_test, y_test_filenames, _, _ = load_tiff_images(test_water_depth_dir)
    
    # Adjust y_test_sequences to align correctly
    y_test_sequences = y_test[sequence_length - 1:]
    X_test_sequences = X_test_sequences[:len(y_test_sequences)]
    
    # --------------------------------------
    # E. Normalize Input Features Using Training Min and Max Values
    # --------------------------------------
    
    X_test_norm_list = []
    for i in range(X_test_sequences.shape[-1]):
        min_val = X_train_min_vals[i]
        max_val = X_train_max_vals[i]
        norm_data = normalize_data_with_nan(X_test_sequences[..., i], min_val, max_val)
        X_test_norm_list.append(norm_data)
    X_test_norm = np.stack(X_test_norm_list, axis=-1)  # Shape: (num_sequences, sequence_length, height, width, channels)
    
    # --------------------------------------
    # F. Load and Normalize Water Level Data
    # --------------------------------------
    
    # Load water level data and create sequences
    test_water_level_data, test_water_level_filenames = load_water_level_data(test_water_level_dir)
    
    # Check if water_level_global_min and max exist
    if water_level_global_min is None or water_level_global_max is None:
        print("Global water level min and max not found in normalization parameters. Exiting.")
        return
    
    # Normalize test water level data globally
    test_water_level_data_norm = (test_water_level_data - water_level_global_min) / (water_level_global_max - water_level_global_min)
    
    # Create sequences for water level data
    test_water_level_data_sequences = []
    for i in range(test_water_level_data_norm.shape[1] - sequence_length + 1):
        test_water_level_data_sequences.append(test_water_level_data_norm[:, i:i + sequence_length])
    test_water_level_data_sequences = np.array(test_water_level_data_sequences)
    test_water_level_data_sequences = test_water_level_data_sequences.transpose(0, 2, 1)  # Shape: (num_samples, sequence_length, num_stations)
    
    # --------------------------------------
    # G. Ensure Sequence Alignment
    # --------------------------------------
    
    # Ensure that the number of sequences align across inputs and outputs
    min_sequences = min(X_test_norm.shape[0], test_water_level_data_sequences.shape[0], y_test_sequences.shape[0])
    X_test_norm = X_test_norm[:min_sequences]
    test_water_level_data_sequences = test_water_level_data_sequences[:min_sequences]
    y_test_sequences = y_test_sequences[:min_sequences]
    y_test_filenames = y_test_filenames[sequence_length - 1:sequence_length - 1 + min_sequences]
    
    print(f"X_test_norm.shape: {X_test_norm.shape}")
    print(f"test_water_level_data_sequences.shape: {test_water_level_data_sequences.shape}")
    print(f"y_test_sequences.shape: {y_test_sequences.shape}")
    
    # --------------------------------------
    # H. Normalize Output Data
    # --------------------------------------
    
    # Normalize output data using training min and max values
    y_test_nan_mask = np.isnan(y_test_sequences)
    y_test_norm = 0.1 + 0.9 * (y_test_sequences - y_train_min) / (y_train_max - y_train_min)
    y_test_norm[y_test_nan_mask] = 0  # Handle NaNs
    
    # --------------------------------------
    # I. Load the Trained Model with Custom Layers
    # --------------------------------------
    
    try:
        # Load the model with all custom objects
        model = load_model(
            os.path.join(checkpoint_dir, 'best_model.h5'),
            custom_objects={
                'StandardCBAM': StandardCBAM,
                'CustomAttentionLayer': CustomAttentionLayer,
                'ClusterBasedApplication': ClusterBasedApplication,
                'masked_mse': masked_mse,
                'TrueLoss': TrueLoss,
                # Include any other custom layers or functions here
            }
        )
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # --------------------------------------
    # J. Cluster Masks Loading and Validation
    # --------------------------------------
    
    # Define mask directory and shapefile path
    mask_dir = '/home/samueldaramola/CNN/trainingcnn'
    polygon_clusters_path = os.path.join(mask_dir, 'reordered_polygons.shp')
    
    def create_cluster_masks(polygon_shapefile, raster_shape, transform):
        """
        Creates mutually exclusive cluster masks by rasterizing polygons.

        Args:
            polygon_shapefile (str): Path to the shapefile containing cluster polygons.
            raster_shape (tuple): Shape of the raster as (height, width).
            transform (Affine): Affine transform of the raster.

        Returns:
            Tuple[np.ndarray, gpd.GeoDataFrame]: Array of cluster masks and the GeoDataFrame of polygons.
        """
        try:
            polygons_gdf = gpd.read_file(polygon_shapefile)
        except Exception as e:
            raise ValueError(f"Error loading shapefile {polygon_shapefile}: {e}")

        cluster_masks = []

        for i, polygon in enumerate(polygons_gdf.geometry):
            mask = rasterize(
                [(polygon, 1)],
                out_shape=raster_shape,
                transform=transform,
                fill=0,
                dtype='uint8'
            )
            cluster_masks.append(mask)

        cluster_masks = np.array(cluster_masks)
        print(f"Created {len(cluster_masks)} cluster masks from {polygon_shapefile}")

        # Ensure mutual exclusivity
        combined_mask = np.sum(cluster_masks.astype(int), axis=0)
        overlap = np.any(combined_mask > 1)

        if overlap:
            overlapping_pixels = np.sum(combined_mask > 1)
            raise ValueError(f"Overlap detected: {overlapping_pixels} pixels belong to multiple clusters!")
        else:
            print("Success: All pixels belong to at most one cluster.")

        return cluster_masks, polygons_gdf

    # Load cluster masks and polygons GeoDataFrame
    try:
        cluster_masks, polygons_gdf = create_cluster_masks(
            polygon_shapefile=polygon_clusters_path,
            raster_shape=(test_atm_pressure_images.shape[1], test_atm_pressure_images.shape[2]),
            transform=transform
        )
    except ValueError as ve:
        print(ve)
        print("Please ensure the shapefile exists at the specified path.")
        return

    # Number of clusters
    num_clusters = cluster_masks.shape[0]
    print(f"Number of clusters: {num_clusters}")

    # Verify the number of clusters and stations
    num_stations = len(test_water_level_filenames)
    if num_clusters != num_stations:
        print(f"\nMismatch detected: {num_clusters} clusters vs {num_stations} stations.")
        print("Please ensure that each cluster has a corresponding station.")
        # Optionally, handle the mismatch as per your requirements
    else:
        print(f"\nNumber of clusters ({num_clusters}) matches number of stations ({num_stations}).")

    # Print the first 5 clusters and their corresponding stations
    print("\nFirst 5 clusters and corresponding stations:")
    for i in range(min(5, num_clusters)):
        # Extract cluster name
        if 'name' in polygons_gdf.columns:
            cluster_name = polygons_gdf.iloc[i]['name']
        else:
            # If there's no 'name' column, use a default naming convention
            cluster_name = f"Cluster_{i+1}"
        
        # Extract station name
        station_name = test_water_level_filenames[i]
        
        print(f"Cluster {i+1}: {cluster_name} <-> Station {i+1}: {station_name}")

    # Convert cluster masks to tensor
    cluster_masks_tensor = tf.constant(cluster_masks, dtype=tf.float32)  # Shape: (num_clusters, height, width)

    # --------------------------------------
    # K. Ensure Mask Correctness
    # --------------------------------------
    
    # Reshape cluster masks for model input
    # The model expects (batch_size, sequence_length, height, width, 1)
    batch_size = X_test_norm.shape[0]
    sequence_length = X_test_norm.shape[1]
    
    # Combine cluster masks into a single mask by taking the maximum over clusters
    single_mask = np.max(cluster_masks, axis=0)  # Shape: (212, 230)
    print(f"After np.max: {single_mask.shape}")
    
    # Add a singleton dimension for the mask channel
    single_mask = single_mask[..., np.newaxis]    # Shape: (212, 230, 1)
    print(f"After adding channel dimension: {single_mask.shape}")
    
    # Expand dimensions to add batch and sequence dimensions
    single_mask = np.expand_dims(single_mask, axis=(0, 1))  # Shape: (1, 1, 212, 230, 1)
    print(f"After expanding batch and sequence dimensions: {single_mask.shape}")
    
    # Repeat the mask for each sample in the batch and each timestep
    single_mask = np.tile(single_mask, (batch_size, sequence_length, 1, 1, 1))  # Shape: (260, 6, 212, 230, 1)
    print(f"After tiling for batch and sequence: {single_mask.shape}")
    
    # Convert to Tensor
    mask_tensor = tf.constant(single_mask, dtype=tf.float32)  # Shape: (260, 6, 212, 230, 1)
    print(f"mask_tensor shape before visualization: {mask_tensor.shape}")  # Should print (260, 6, 212, 230, 1)
    
    # Verify mask distribution
    verify_mask_distribution(mask_tensor.numpy())
    
    # Visualize the first mask of the first sequence
    visualize_mask(mask_tensor.numpy(), index=0, timestep=0)

    # --------------------------------------
    # L. Define Function to Create Attention Model
    # --------------------------------------
    
    def create_attention_models(model):
        """
        Creates separate models to output temporal and spatial attention vectors.

        Args:
            model (tf.keras.Model): Trained model.

        Returns:
            Tuple[tf.keras.Model, tf.keras.Model]: Models that output temporal and spatial attention vectors.
        """
        temporal_attention_model = None
        spatial_attention_model = None

        try:
            # Access the Temporal_Attention layer
            if 'Temporal_Attention' in [layer.name for layer in model.layers]:
                temporal_attention_layer = model.get_layer('Temporal_Attention')
                temporal_attention_output = temporal_attention_layer.output[1]
                temporal_attention_model = Model(
                    inputs=model.inputs,
                    outputs=temporal_attention_output,
                    name='Temporal_Attention_Model'
                )
            else:
                print("Layer 'Temporal_Attention' not found in the model.")

            # Access the CBAM_3 layer
            if 'CBAM_3' in [layer.name for layer in model.layers]:
                cbam3_layer = model.get_layer('CBAM_3')
                # The outputs of CBAM_3 are (refined_feature, spatial_attention_map)
                _, spatial_attention_map = cbam3_layer.output
                spatial_attention_model = Model(
                    inputs=model.inputs,
                    outputs=spatial_attention_map,
                    name='Spatial_Attention_Model'
                )
            else:
                print("Layer 'CBAM_3' not found in the model.")

            return temporal_attention_model, spatial_attention_model

        except Exception as e:
            print(f"Error creating attention models: {e}")
            return temporal_attention_model, spatial_attention_model

    # Create separate models for temporal and spatial attention
    temporal_attention_model, spatial_attention_model = create_attention_models(model)

    # --------------------------------------
    # M. Perform Predictions and Save as TIFF Images
    # --------------------------------------
    
    for i in range(len(X_test_norm)):
        X = X_test_norm[i:i + 1]                           # Shape: (1, 6, 212, 230, 5)
        mask_sample = mask_tensor[i:i + 1]                 # Shape: (1, 6, 212, 230, 1)
        water_level = test_water_level_data_sequences[i:i + 1]  # Shape: (1, 6, 21)
    
        # Make prediction
        preds = model.predict([X, mask_sample, water_level])
    
        # Ensure preds is squeezed to remove batch dimension
        preds_denorm = denormalize_data(preds[0], y_train_min, y_train_max)
        preds_denorm = apply_nan_mask(preds_denorm, y_test_nan_mask[i].squeeze())
    
        # Save prediction as TIFF
        output_filename = y_test_filenames[i]
        output_path = os.path.join(output_dir, output_filename)
        reference_dataset = os.path.join(test_water_depth_dir, output_filename)
        if not os.path.exists(reference_dataset):
            print(f"Reference dataset {reference_dataset} not found. Skipping saving prediction {i}.")
            continue
        save_tiff_image(preds_denorm, output_path, reference_dataset)
        print(f"Saved prediction {i} to {output_path}")
    
    # --------------------------------------
    # N. Load Actual and Predicted Water Depth Data
    # --------------------------------------
    
    # Prepare time series data for valid areas
    actual_water_depth, actual_filenames, _, _ = load_tiff_images(test_water_depth_dir)
    predicted_water_depth, predicted_filenames, _, _ = load_tiff_images(output_dir)
    
    # Ensure filenames of actual and predicted data match
    common_filenames = sorted(list(set(actual_filenames) & set(predicted_filenames)))
    
    if not common_filenames:
        print("No matching filenames found between actual and predicted data. Please verify the filenames.")
        return  # Exit the main function or handle appropriately
    
    # Filter actual and predicted water depth based on matching filenames
    actual_filtered = []
    predicted_filtered = []
    
    for filename in common_filenames:
        actual_idx = actual_filenames.index(filename)
        predicted_idx = predicted_filenames.index(filename)
        
        actual_filtered.append(actual_water_depth[actual_idx])
        predicted_filtered.append(predicted_water_depth[predicted_idx])
    
    # Convert filtered data to numpy arrays
    actual_filtered = np.array(actual_filtered)
    predicted_filtered = np.array(predicted_filtered)
    
    # --------------------------------------
    # O. Time Series Analysis at Specific Locations
    # --------------------------------------
    
    # Define coordinates for the new areas
    area_coords = {
        'West University Place, TX': (29.715929, -95.432992),
        'Green Lake Oil Field, TX': (29.26667, -95.0088),
        'Moody National Wildlife Refuge, TX': (29.55, -94.66)
    }
    
    # Function to get row, col index for coordinates
    def get_index_from_coords(lat, lon, transform):
        """Convert latitude/longitude to row/col index in raster grid"""
        try:
            col, row = ~transform * (lon, lat)
            return int(row), int(col)
        except Exception as e:
            print(f"Error converting coordinates ({lat}, {lon}): {e}")
            return None, None
    
    # Prepare time series data for valid areas
    actual_ts_dict = {}
    predicted_ts_dict = {}
    valid_areas = []
    
    for area, coords in area_coords.items():
        # Get row, col for each area
        row, col = get_index_from_coords(coords[0], coords[1], transform)
        
        if row is None or col is None:
            print(f"Skipping {area} due to coordinate conversion error.")
            continue
    
        # Check if row and col are within the bounds of the raster grid
        if (0 <= row < actual_filtered.shape[1]) and (0 <= col < actual_filtered.shape[2]):
            # Extract actual water depth time series
            actual_ts = actual_filtered[:, row, col]
            predicted_ts = predicted_filtered[:, row, col]
    
            # Check if all values are NaN
            if np.isnan(actual_ts).all() and np.isnan(predicted_ts).all():
                print(f"All values are NaN for area {area}. Skipping...")
                continue
    
            actual_ts_dict[area] = actual_ts
            predicted_ts_dict[area] = predicted_ts
            valid_areas.append(area)
        else:
            print(f"Skipping {area}: coordinates fall outside the raster grid.")
    
    if not valid_areas:
        print("No valid areas found within the raster grid.")
        return
    
    # Collect all min and max values, ignoring NaNs
    y_min_values = []
    y_max_values = []
    
    for area in valid_areas:
        actual_vals = actual_ts_dict[area]
        predicted_vals = predicted_ts_dict[area]
    
        # Remove NaN values
        actual_vals = actual_vals[~np.isnan(actual_vals)]
        predicted_vals = predicted_vals[~np.isnan(predicted_vals)]
    
        # Append min and max values, if arrays are not empty
        if actual_vals.size > 0:
            y_min_values.append(actual_vals.min())
            y_max_values.append(actual_vals.max())
    
        if predicted_vals.size > 0:
            y_min_values.append(predicted_vals.min())
            y_max_values.append(predicted_vals.max())
    
    # Proceed if we have valid min and max values
    if y_min_values and y_max_values:
        y_min = min(y_min_values) - 0.05
        y_max = max(y_max_values) + 0.05
    else:
        print("No valid min or max values found. Exiting plotting.")
        return
    
    # Plot the comparison for valid areas in subplots
    fig, axes = plt.subplots(1, len(valid_areas), figsize=(12, 3), sharey=True)
    
    # Adjust axes handling when there's only one valid subplot
    if len(valid_areas) == 1:
        axes = [axes]  # Convert to list
    
    for i, area in enumerate(valid_areas):
        actual_vals = actual_ts_dict[area]
        predicted_vals = predicted_ts_dict[area]
    
        axes[i].plot(actual_vals, label='Actual Water Depth', color='blue', linestyle='-', marker='')
        axes[i].plot(predicted_vals, label='Predicted Water Depth', color='red', linestyle='-', marker='')
        axes[i].set_title(f'{area}')
        axes[i].set_xlabel('Timesteps')
        axes[i].set_ylim([y_min, y_max])  # Apply the y-axis limits
        axes[i].grid(False)
    
    # Shared y-axis label
    axes[0].set_ylabel('Water Depth (m)')
    
    # Adjust the position of the legend and the title
    fig.suptitle('Hurricane Nicolas 2021', y=1.05)  # Title adjusted
    fig.legend(['Actual Water Depth', 'Predicted Water Depth'], loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.0))
    
    # Adjust layout to add space at the top and bottom
    plt.tight_layout(rect=[0, 0.05, 1, 0.85])  # Leave a gap at the bottom and top
    plt.subplots_adjust(top=0.8, bottom=0.1)  # Extra space at the top and bottom
    
    # Save the figure
    plt.savefig('nicolas.png', dpi=300, bbox_inches='tight')
    
    plt.show()
            
    # --------------------------------------
    # Q. Final Completion Message
    # --------------------------------------
    
    print("Model evaluation and visualization completed successfully.")

if __name__ == "__main__":
    main()



















# ==========================================
# Flood Depth Prediction Model Evaluation
# Hurricane Beryl 2024
# ==========================================

# ------------------------------------------
# 1. Import Necessary Libraries
# ------------------------------------------
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import rasterio
import geopandas as gpd
from tensorflow.keras.models import Model
from tensorflow.keras.initializers import HeNormal, GlorotNormal
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import load_model
from rasterio.features import rasterize
from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
from tensorflow.keras.layers import (
    Conv2D, Multiply, Dense, Reshape, Flatten, Input, ConvLSTM2D, LSTM,
    Activation, LayerNormalization, Lambda, Add, Concatenate, GlobalAveragePooling2D,
    GlobalMaxPooling2D
)
from tensorflow.keras.regularizers import l2
import matplotlib.patches as patches

# ------------------------------------------
# 2. Setup and Configuration
# ------------------------------------------

# Seed for reproducibility
seed_value = 3
np.random.seed(seed_value)
tf.random.set_seed(seed_value)

# Check and configure GPU usage
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Enable mixed precision (if desired)
from tensorflow.keras.mixed_precision import set_global_policy
set_global_policy('float32')

# ------------------------------------------
# 3. Helper Functions
# ------------------------------------------

def load_tiff_images(data_dir):
    """
    Loads all TIFF images from a specified directory.

    Args:
        data_dir (str): Path to the directory containing TIFF files.

    Returns:
        Tuple[np.ndarray, List[str], Any, Any]: Loaded images array, filenames, CRS, and transform.
    """
    images = []
    filenames = []
    crs = None
    transform = None
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".tif"):
            filepath = os.path.join(data_dir, filename)
            with rasterio.open(filepath) as src:
                img = src.read(1)
                if crs is None:
                    crs = src.crs
                if transform is None:
                    transform = src.transform
                images.append(img)
            filenames.append(filename)
    print(f"Loaded {len(images)} TIFF images from {data_dir}")
    return np.array(images), filenames, crs, transform

def load_single_tiff_image(filepath):
    """
    Loads a single TIFF image.

    Args:
        filepath (str): Path to the TIFF file.

    Returns:
        Tuple[np.ndarray, Any, Any]: Loaded image array, CRS, and transform.
    """
    with rasterio.open(filepath) as src:
        img = src.read(1)
        crs = src.crs
        transform = src.transform
    print(f"Loaded single TIFF image from {filepath}")
    return img, crs, transform

def natural_sort(file_list):
    """
    Sorts a list of filenames in a natural, human-friendly order.
    
    Args:
        file_list (List[str]): List of filenames to sort.
    
    Returns:
        List[str]: Naturally sorted list of filenames.
    """
    def alphanum_key(key):
        # Split the key into a list of strings and integers
        return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', key)]
    
    return sorted(file_list, key=alphanum_key)

def load_water_level_data(data_dir):
    """
    Loads water level data from CSV files for each station, sorted naturally.

    Args:
        data_dir (str): Path to the directory containing water level CSV files.

    Returns:
        Tuple[np.ndarray, List[str]]: Water level data array and naturally sorted filenames.
    """
    water_level_data = []
    filenames = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    filenames = natural_sort(filenames)  # Apply natural sorting
    for filename in filenames:
        filepath = os.path.join(data_dir, filename)
        df = pd.read_csv(filepath)
        if 'water_level' in df.columns:
            water_level_data.append(df['water_level'].values)
        else:
            print(f"'water_level' column not found in {filepath}. Skipping.")
    print(f"Loaded water level data from {data_dir} with {len(water_level_data)} stations.")
    return np.array(water_level_data), filenames

def normalize_data_with_nan(data, min_val, max_val):
    """
    Normalizes data to the range [0.1, 1.0], handling NaN values.

    Args:
        data (np.ndarray): Input data array.
        min_val (float): Minimum value for normalization.
        max_val (float): Maximum value for normalization.

    Returns:
        np.ndarray: Normalized data array.
    """
    nan_mask = np.isnan(data)
    norm_data = 0.1 + 0.9 * (data - min_val) / (max_val - min_val)
    norm_data[nan_mask] = 0  # Set NaN cells to 0 after normalization
    return norm_data

def denormalize_data(norm_data, min_val, max_val):
    """
    Denormalizes data from the range [0.1, 1.0] back to original scale.

    Args:
        norm_data (np.ndarray): Normalized data array.
        min_val (float): Minimum value used during normalization.
        max_val (float): Maximum value used during normalization.

    Returns:
        np.ndarray: Denormalized data array.
    """
    return (norm_data - 0.1) / 0.9 * (max_val - min_val) + min_val

def apply_nan_mask(data, mask):
    """
    Applies a NaN mask to data.

    Args:
        data (np.ndarray): Data array.
        mask (np.ndarray): Boolean mask where True indicates NaN.

    Returns:
        np.ndarray: Data array with NaNs applied.
    """
    data = data.copy()  # Avoid modifying the original data
    data[mask] = np.nan
    return data

def save_tiff_image(data, output_path, reference_dataset):
    """
    Saves a data array as a TIFF image using a reference dataset for metadata.

    Args:
        data (np.ndarray): Data array to save.
        output_path (str): Output file path.
        reference_dataset (str): Path to a reference TIFF file for metadata.
    """
    with rasterio.open(reference_dataset) as src:
        out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": src.crs,
        "transform": src.transform
    })
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(data.astype(np.float32), 1)
    print(f"Saved TIFF image to {output_path}")

def verify_mask_distribution(mask):
    """
    Verifies the distribution of valid and invalid pixels in the mask.

    Args:
        mask (np.ndarray): Mask array with shape (num_sequences, sequence_length, height, width, 1).
    """
    total_pixels = mask.size
    valid_pixels = np.sum(mask == 1)
    invalid_pixels = np.sum(mask == 0)
    
    print(f"Total Pixels: {total_pixels}")
    print(f"Valid Pixels (1): {valid_pixels} ({(valid_pixels / total_pixels) * 100:.2f}%)")
    print(f"Invalid Pixels (0): {invalid_pixels} ({(invalid_pixels / total_pixels) * 100:.2f}%)")

def visualize_mask(mask, index=0, timestep=0):
    """
    Visualizes the mask to ensure correct inversion.

    Args:
        mask (np.ndarray): Mask array with shape (batch_size, sequence_length, height, width, 1).
        index (int): Sequence index to visualize.
        timestep (int): Timestep index to visualize.
    """
    # Verify mask dimensions
    if mask.ndim != 5:
        raise ValueError(f"Expected mask to be 5D, but got {mask.ndim}D.")

    batch_size, sequence_length, height, width, channels = mask.shape
    if channels != 1:
        raise ValueError(f"Expected mask to have 1 channel, but got {channels} channels.")

    # Extract the specific mask slice
    mask_sample = mask[index, timestep, :, :, 0]

    plt.figure(figsize=(6, 6))
    plt.title('Valid Mask (1=Valid, 0=Invalid)')
    plt.imshow(mask_sample, cmap='gray')
    plt.colorbar()
    plt.axis('off')
    plt.show()
    
import matplotlib.patches as patches

def visualize_spatial_attention_with_clusters(spatial_attention_map, polygons_gdf, transform, vmin=None, vmax=None):
    """
    Visualizes the spatial attention map with cluster polygons overlayed, masking invalid areas.
    
    Args:
        spatial_attention_map (np.ndarray): Spatial attention map array with shape (height, width).
        polygons_gdf (gpd.GeoDataFrame): GeoDataFrame containing cluster polygons.
        transform (Affine): Affine transform of the raster.
        vmin (float, optional): Minimum value for the color map.
        vmax (float, optional): Maximum value for the color map.
    """
    # Mask out values outside the valid range by setting them to NaN
    masked_attention_map = np.where((spatial_attention_map >= vmin) & (spatial_attention_map <= vmax), spatial_attention_map, np.nan)

    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the masked attention map
    im = ax.imshow(masked_attention_map, cmap='viridis', vmin=vmin, vmax=vmax)
    ax.set_title('Spatial Attention Map with Cluster Overlays')
    ax.axis('off')
    
    # Plot polygons
    for idx, polygon in polygons_gdf.geometry.items():
        if polygon.is_empty:
            continue
        polygon_pixels = []
        for coord in polygon.exterior.coords:
            col, row = ~transform * (coord[0], coord[1])
            polygon_pixels.append((col, row))
        polygon_pixels = np.array(polygon_pixels)
        ax.add_patch(patches.Polygon(polygon_pixels, linewidth=1, edgecolor='red', facecolor='none'))
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Normalized Attention Weight', rotation=270, labelpad=15)

    # Save and show the plot
    plt.savefig('spatial_attention_with_clusters_masked.png', dpi=300, bbox_inches='tight')
    plt.show()
    
# ==========================================
# 3. Custom Attention Mechanisms
# ==========================================

def masked_global_average_pooling2d(inputs, mask):
    masked_inputs = inputs * mask  # Shape: (batch, height, width, channels)
    sum_pool = tf.reduce_sum(masked_inputs, axis=[1, 2])  # Shape: (batch, channels)
    valid_pixels = tf.reduce_sum(mask, axis=[1, 2]) + tf.keras.backend.epsilon()  # Shape: (batch, 1)
    avg_pool = sum_pool / valid_pixels  # Shape: (batch, channels)
    return avg_pool

def masked_global_max_pooling2d(inputs, mask):
    masked_inputs = inputs * mask + (1.0 - mask) * (-1e9)  # Shape: (batch, height, width, channels)
    max_pool = tf.reduce_max(masked_inputs, axis=[1, 2])  # Shape: (batch, channels)
    return max_pool

class StandardCBAM(Layer):
    def __init__(self, ratio=8, kernel_size=7, return_attention=False, **kwargs):
        super(StandardCBAM, self).__init__(**kwargs)
        self.ratio = ratio
        self.kernel_size = kernel_size
        self.return_attention = return_attention

    def build(self, input_shape):
        if isinstance(input_shape, list):
            raise ValueError("StandardCBAM now expects a single concatenated input.")

        total_channels = input_shape[-1]
        self.feature_channels = total_channels - 1  # Last channel is assumed to be the mask

        # Channel Attention layers without fixed names
        self.shared_dense_one = Dense(
            self.feature_channels // self.ratio,
            activation='relu',
            kernel_initializer='he_normal',
            use_bias=True,
            bias_initializer='zeros'
        )
        self.shared_dense_two = Dense(
            self.feature_channels,
            activation='sigmoid',
            kernel_initializer='glorot_normal',
            use_bias=True,
            bias_initializer='zeros'
        )

        # Spatial Attention convolutional layer without fixed name
        self.conv_spatial = Conv2D(
            filters=1,
            kernel_size=self.kernel_size,
            strides=1,
            padding='same',
            activation='sigmoid',
            kernel_initializer='glorot_normal',
            use_bias=False
        )

        super(StandardCBAM, self).build(input_shape)

    def call(self, inputs, training=None):
        # Split feature and mask channels
        feature = inputs[..., :self.feature_channels]
        mask = inputs[..., self.feature_channels:]  # Shape: (batch, height, width, 1)

        # tf.print("Feature shape:", tf.shape(feature))
        # tf.print("Mask shape:", tf.shape(mask))

        # --- Channel Attention ---
        # Apply masked global average and max pooling
        avg_pool = masked_global_average_pooling2d(feature, mask)  # Shape: (batch, channels)
        # tf.print("Average Pool shape:", tf.shape(avg_pool))
        avg_pool = self.shared_dense_one(avg_pool)  # Shape: (batch, channels // ratio)
        avg_pool = self.shared_dense_two(avg_pool)  # Shape: (batch, channels)

        max_pool = masked_global_max_pooling2d(feature, mask)  # Shape: (batch, channels)
        # tf.print("Max Pool shape:", tf.shape(max_pool))
        max_pool = self.shared_dense_one(max_pool)  # Shape: (batch, channels // ratio)
        max_pool = self.shared_dense_two(max_pool)  # Shape: (batch, channels)

        # Combine average and max pooling
        channel_attention = Add()([avg_pool, max_pool])  # Shape: (batch, channels)
        channel_attention = Activation('sigmoid')(channel_attention)  # Shape: (batch, channels)

        # tf.print("Channel Attention shape:", tf.shape(channel_attention))

        # Reshape for broadcasting across spatial dimensions using Keras Reshape
        channel_attention = Reshape((1, 1, self.feature_channels))(channel_attention)
        # tf.print("Reshaped Channel Attention shape:", tf.shape(channel_attention))

        # Apply channel attention to the features
        refined_feature = Multiply()([feature, channel_attention])  # Shape: (batch, height, width, channels)
        # tf.print("Refined Feature shape:", tf.shape(refined_feature))

        # --- Spatial Attention ---
        # Generate spatial attention map using a convolutional layer
        spatial_attention = self.conv_spatial(refined_feature)  # Shape: (batch, height, width, 1)
        # tf.print("Spatial Attention shape:", tf.shape(spatial_attention))
        
        # Apply mask to ensure invalid cells are zeroed
        spatial_attention = Multiply()([spatial_attention, mask])  # Shape: (batch, height, width, 1)
        # tf.print("Masked Spatial Attention shape:", tf.shape(spatial_attention))

        # Apply spatial attention to the refined features
        refined_feature = Multiply()([refined_feature, spatial_attention])  # Shape: (batch, height, width, channels)
        # tf.print("Final Refined Feature shape:", tf.shape(refined_feature))

        # Return both refined feature and spatial attention map if requested
        if self.return_attention:
            return refined_feature, spatial_attention
        else:
            return refined_feature

    def compute_output_shape(self, input_shape):
        """
        Computes the output shape of the layer.

        Args:
            input_shape (tuple): Shape of the input tensor.

        Returns:
            tuple: Shape of the output tensor.
        """
        # Determine if the input is 4D or 5D
        if len(input_shape) == 5:
            # Input shape: (batch, time, height, width, channels +1)
            return (input_shape[0], input_shape[1], input_shape[2], input_shape[3], self.feature_channels)
        elif len(input_shape) == 4:
            # Input shape: (batch, height, width, channels +1)
            return (input_shape[0], input_shape[1], input_shape[2], self.feature_channels)
        else:
            raise ValueError(f"Unsupported input shape: {input_shape}")

    def get_config(self):
        config = super(StandardCBAM, self).get_config()
        config.update({
            "ratio": self.ratio,
            "kernel_size": self.kernel_size,
            "return_attention": self.return_attention
        })
        return config

class CustomAttentionLayer(Layer):
    def __init__(self, emphasis_factor=1.5, top_k_percent=0.2, **kwargs):
        super(CustomAttentionLayer, self).__init__(**kwargs)
        self.emphasis_factor = emphasis_factor
        self.top_k_percent = top_k_percent

    def get_config(self):
        config = super(CustomAttentionLayer, self).get_config()
        config.update({
            "emphasis_factor": self.emphasis_factor,
            "top_k_percent": self.top_k_percent
        })
        return config

    def build(self, input_shape):
        # Build as before
        self.W = self.add_weight(name='att_weight',
                                 shape=(input_shape[-1], 1),
                                 initializer=GlorotNormal(),
                                 trainable=True)
        self.b = self.add_weight(shape=(1,),
                                 initializer='zeros',
                                 trainable=True,
                                 name='bias')
        super(CustomAttentionLayer, self).build(input_shape)

    def call(self, x):
        # Compute attention weights
        e = K.tanh(K.dot(x, self.W) + self.b)  # (batch_size, timesteps, 1)
        a = K.softmax(e, axis=1)               # (batch_size, timesteps, 1)
        a = K.squeeze(a, axis=-1)              # (batch_size, timesteps)

        # Emphasize top-k attention weights
        k_value = tf.cast(tf.cast(tf.shape(a)[1], tf.float32) * self.top_k_percent, tf.int32)
        k_value = tf.maximum(k_value, 1)
        top_k_values, top_k_indices = tf.math.top_k(a, k=k_value)
        mask = tf.one_hot(top_k_indices, depth=tf.shape(a)[1])  # (batch_size, k, timesteps)
        mask = tf.reduce_max(mask, axis=1)                      # (batch_size, timesteps)
        mask = tf.cast(mask, tf.bool)
        emphasized_a = tf.where(mask, a * self.emphasis_factor, a)  # (batch_size, timesteps)

        # Compute the context vector
        output = x * tf.expand_dims(emphasized_a, axis=-1)  # (batch_size, timesteps, features)
        summed_output = K.sum(output, axis=1)               # (batch_size, features)

        # Return both the context vector and the attention weights
        return [summed_output, emphasized_a]

    def compute_output_shape(self, input_shape):
        context_shape = (input_shape[0], input_shape[-1])
        attention_shape = (input_shape[0], input_shape[1])
        return [context_shape, attention_shape]

class ClusterBasedApplication(Layer):
    def __init__(self, num_stations, height, width, **kwargs):
        super(ClusterBasedApplication, self).__init__(**kwargs)
        self.num_stations = num_stations
        self.height = height
        self.width = width

    def build(self, input_shape):
        # Define Dense layer to project context vectors to spatial dimensions
        self.dense_project = Dense(self.height * self.width,
                                   activation='relu',
                                   kernel_initializer='he_normal',
                                   kernel_regularizer=l2(1e-5),
                                   name='Dense_Project_Context')
        super(ClusterBasedApplication, self).build(input_shape)

    def call(self, inputs):
        attention_outputs, cluster_masks_tensor = inputs  # attention_outputs: (batch, num_stations, features)
        
        # Dynamically determine batch size
        batch_size = tf.shape(attention_outputs)[0]
        
        # Project context vectors to spatial dimensions
        reshaped_context = self.dense_project(attention_outputs)  # Shape: (batch, num_stations, height * width)
        reshaped_context = tf.reshape(reshaped_context, (batch_size, self.num_stations, self.height, self.width))  # Shape: (batch, num_stations, height, width)
        
        # Expand cluster masks to match batch size
        cluster_masks_expanded = tf.expand_dims(cluster_masks_tensor, axis=0)  # Shape: (1, num_stations, height, width)
        cluster_masks_expanded = tf.tile(cluster_masks_expanded, [batch_size, 1, 1, 1])  # Shape: (batch, num_stations, height, width)
        cluster_masks_expanded = tf.cast(cluster_masks_expanded, reshaped_context.dtype)
        
        # Apply cluster masks
        localized_context = reshaped_context * cluster_masks_expanded  # Shape: (batch, num_stations, height, width)
        
        # Compute cluster indices
        cluster_indices = tf.argmax(tf.cast(cluster_masks_tensor, tf.int32), axis=0)  # Shape: (height, width)
        
        # One-hot encode cluster indices
        cluster_indices_one_hot = tf.one_hot(cluster_indices, depth=self.num_stations)  # Shape: (height, width, num_stations)
        cluster_indices_one_hot = tf.transpose(cluster_indices_one_hot, perm=[2, 0, 1])  # Shape: (num_stations, height, width)
        cluster_indices_one_hot = tf.expand_dims(cluster_indices_one_hot, axis=0)  # Shape: (1, num_stations, height, width)
        cluster_indices_one_hot = tf.tile(cluster_indices_one_hot, [batch_size, 1, 1, 1])  # Shape: (batch, num_stations, height, width)
        
        # Select the correct context
        selected_context = tf.reduce_sum(localized_context * cluster_indices_one_hot, axis=1)  # Shape: (batch, height, width)
        
        # Expand dimensions to match spatial features
        combined_context = tf.expand_dims(selected_context, axis=-1)  # Shape: (batch, height, width, 1)
        
        return combined_context  # Shape: (batch, height, width, 1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], self.height, self.width, 1)

    def get_config(self):
        config = super(ClusterBasedApplication, self).get_config()
        config.update({
            "num_stations": self.num_stations,
            "height": self.height,
            "width": self.width
        })
        return config

# ==========================================
# 4. Loss Function
# ==========================================

def masked_mse(y_true, y_pred):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    mask = tf.math.not_equal(y_true, 0.0)
    mask = tf.cast(mask, y_true.dtype)
    mse = tf.square(y_true - y_pred)
    mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
    return mse

# TrueLoss Metric Definition
class TrueLoss(tf.keras.metrics.Metric):
    def __init__(self, name='trueloss', **kwargs):
        super(TrueLoss, self).__init__(name=name, **kwargs)
        self.true_loss = self.add_weight(name='tl', initializer='zeros')
        self.count = self.add_weight(name='count', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        """
        Updates the state of the metric with the current batch's loss.

        Args:
            y_true (Tensor): Ground truth values.
            y_pred (Tensor): Predicted values.
            sample_weight (Tensor, optional): Sample weights.
        """
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        
        # Create mask: 1 for valid pixels, 0 otherwise
        mask = tf.math.not_equal(y_true, 0.0)
        mask = tf.cast(mask, y_true.dtype)
        
        # Compute squared errors
        mse = tf.square(y_true - y_pred)
        
        # Apply mask
        masked_mse = tf.reduce_sum(mse * mask) / (tf.reduce_sum(mask) + 1e-8)
        
        # Update accumulators
        self.true_loss.assign_add(masked_mse)
        self.count.assign_add(1.0)
        pass

    def result(self):
        """
        Computes the average TrueLoss over all batches.

        Returns:
            Tensor: The average TrueLoss.
        """
        return self.true_loss / self.count
        pass

    def reset_state(self):
        """
        Resets the state of the metric.
        """
        self.true_loss.assign(0.0)
        self.count.assign(0.0)

# ------------------------------------------
# 6. Model Evaluation and Visualization Functions
# ------------------------------------------

def plot_and_compare_predictions(model, X_test, mask, water_level_data, y_test, y_test_nan_mask, filenames, num_images=2):
    """
    Plots and compares actual vs. predicted water depth images.

    Args:
        model (tf.keras.Model): Loaded TensorFlow model.
        X_test (np.ndarray): Normalized test input sequences.
        mask (np.ndarray): Cluster mask for the test data.
        water_level_data (np.ndarray): Normalized water level sequences.
        y_test (np.ndarray): Normalized ground truth water depth maps.
        y_test_nan_mask (np.ndarray): Mask indicating NaN values in y_test.
        filenames (List[str]): List of filenames corresponding to y_test.
        num_images (int): Number of images to plot for comparison.
    """
    mse_list, rmse_list, r2_list, mse_filenames = [], [], [], []
    for i in range(len(X_test)):
        X = X_test[i:i + 1]
        mask_sample = mask[i:i + 1]
        water_level = water_level_data[i:i + 1]
        y = y_test[i]

        # Make prediction
        preds = model.predict([X, mask_sample, water_level])

        # Ensure preds is squeezed to remove batch dimension
        preds_denorm = denormalize_data(preds[0], y_train_min, y_train_max)
        y_true = denormalize_data(y, y_train_min, y_train_max)

        # Apply NaN mask
        preds_denorm = apply_nan_mask(preds_denorm, y_test_nan_mask[i].squeeze())
        y_true = apply_nan_mask(y_true, y_test_nan_mask[i].squeeze())

        # Calculate MSE, RMSE, and R^2
        valid_mask = ~np.isnan(y_true)
        if np.any(valid_mask):
            mse = mean_squared_error(y_true[valid_mask], preds_denorm[valid_mask])
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true[valid_mask], preds_denorm[valid_mask])

            mse_list.append(mse)
            rmse_list.append(rmse)
            r2_list.append(r2)
            mse_filenames.append(filenames[i])

            if i < num_images:  # Only plot a specified number of images
                fig, axes = plt.subplots(1, 2, figsize=(12, 6))

                # Actual Water Depth
                im = axes[0].imshow(y_true, cmap='jet')
                axes[0].set_title(f'Actual Water Depth\n({filenames[i]})')
                axes[0].axis('off')
                plt.colorbar(im, ax=axes[0])

                # Predicted Water Depth
                im = axes[1].imshow(preds_denorm, cmap='jet')
                axes[1].set_title(f'Predicted Water Depth\n({filenames[i]})')
                axes[1].axis('off')
                plt.colorbar(im, ax=axes[1])

                plt.suptitle(f'MSE: {mse:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}')
                plt.tight_layout()
                plt.show()
        else:
            print(f"No valid data points for index {i}. Skipping...")

    if mse_list:
        avg_mse, avg_rmse, avg_r2 = np.mean(mse_list), np.mean(rmse_list), np.mean(r2_list)
        max_rmse_index = np.argmax(rmse_list)
        max_rmse = rmse_list[max_rmse_index]
        max_rmse_filename = mse_filenames[max_rmse_index]

        print(f'Average MSE: {avg_mse:.4f}, RMSE: {avg_rmse:.4f}, R²: {avg_r2:.4f}')
        print(f'Largest RMSE: {max_rmse:.4f}, Filename: {max_rmse_filename}')
    else:
        print("No valid predictions made.")

# ------------------------------------------
# 7. Main Execution Flow
# ------------------------------------------

def main():
    # --------------------------------------
    # A. Define Directories and Paths
    # --------------------------------------
    
    # Directories for testing data
    test_atm_pressure_dir = os.path.join(os.getcwd(), 'atm_pressure')
    test_wind_speed_dir = os.path.join(os.getcwd(), 'wind_speed')
    test_precipitation_dir = os.path.join(os.getcwd(), 'precipitation')
    test_river_discharge_dir = os.path.join(os.getcwd(), 'river_discharge')
    test_water_depth_dir = os.path.join(os.getcwd(), 'water_depth')
    test_dem_file = os.path.join(os.getcwd(), 'DEM/dem_idw.tif')
    test_water_level_dir = os.path.join(os.getcwd(), 'test_stations_beryl')
    
    # Define output directory in the current directory
    output_dir = os.path.join(os.getcwd(), 'predictionsberyl48')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define the checkpoint directory
    checkpoint_dir = '/home/samueldaramola/CNN/trainingcnn/checkpoints_cluster_48'
    
    # --------------------------------------
    # B. Load Normalization Parameters
    # --------------------------------------
    
    # Load normalization parameters
    normalization_params_path = os.path.join(checkpoint_dir, 'normalization_params.npy')
    if not os.path.exists(normalization_params_path):
        print(f"Normalization parameters not found at {normalization_params_path}. Exiting.")
        return
    normalization_params = np.load(normalization_params_path, allow_pickle=True).item()
    X_train_min_vals = normalization_params['X_train_min_vals']
    X_train_max_vals = normalization_params['X_train_max_vals']
    y_train_min = normalization_params['y_train_min']
    y_train_max = normalization_params['y_train_max']
    water_level_global_min = normalization_params.get('water_level_global_min', None)
    water_level_global_max = normalization_params.get('water_level_global_max', None)
    
    # --------------------------------------
    # C. Load Test Input Images
    # --------------------------------------
    
    # Load test input images
    test_atm_pressure_images, test_atm_filenames, crs, transform = load_tiff_images(test_atm_pressure_dir)
    test_wind_speed_images, test_wind_filenames, _, _ = load_tiff_images(test_wind_speed_dir)
    test_precipitation_images, test_precip_filenames, _, _ = load_tiff_images(test_precipitation_dir)
    test_river_discharge_images, test_river_discharge_filenames, _, _ = load_tiff_images(test_river_discharge_dir)
    
    # Load DEM image and replicate for all timesteps
    test_dem_image, _, _ = load_single_tiff_image(test_dem_file)
    num_test_timesteps = test_atm_pressure_images.shape[0]
    test_dem_images = np.tile(test_dem_image, (num_test_timesteps, 1, 1))
    
    # Stack input features (atm_pressure, wind_speed, DEM, precipitation, river discharge)
    X_test = np.stack((test_atm_pressure_images, test_wind_speed_images, test_dem_images, test_precipitation_images, test_river_discharge_images), axis=-1)
    
    # --------------------------------------
    # D. Define Sequence Length and Create Sequences
    # --------------------------------------
    
    # Define the sequence length (should match the training sequence length)
    sequence_length = 6
    
    # Create sequences for X_test
    X_test_sequences = []
    for i in range(len(X_test) - sequence_length + 1):
        X_test_sequences.append(X_test[i:i + sequence_length])
    X_test_sequences = np.array(X_test_sequences)
    
    # Load water depth data for testing
    y_test, y_test_filenames, _, _ = load_tiff_images(test_water_depth_dir)
    
    # Adjust y_test_sequences to align correctly
    y_test_sequences = y_test[sequence_length - 1:]
    X_test_sequences = X_test_sequences[:len(y_test_sequences)]
    
    # --------------------------------------
    # E. Normalize Input Features Using Training Min and Max Values
    # --------------------------------------
    
    X_test_norm_list = []
    for i in range(X_test_sequences.shape[-1]):
        min_val = X_train_min_vals[i]
        max_val = X_train_max_vals[i]
        norm_data = normalize_data_with_nan(X_test_sequences[..., i], min_val, max_val)
        X_test_norm_list.append(norm_data)
    X_test_norm = np.stack(X_test_norm_list, axis=-1)  # Shape: (num_sequences, sequence_length, height, width, channels)
    
    # --------------------------------------
    # F. Load and Normalize Water Level Data
    # --------------------------------------
    
    # Load water level data and create sequences
    test_water_level_data, test_water_level_filenames = load_water_level_data(test_water_level_dir)
    
    # Check if water_level_global_min and max exist
    if water_level_global_min is None or water_level_global_max is None:
        print("Global water level min and max not found in normalization parameters. Exiting.")
        return
    
    # Normalize test water level data globally
    test_water_level_data_norm = (test_water_level_data - water_level_global_min) / (water_level_global_max - water_level_global_min)
    
    # Create sequences for water level data
    test_water_level_data_sequences = []
    for i in range(test_water_level_data_norm.shape[1] - sequence_length + 1):
        test_water_level_data_sequences.append(test_water_level_data_norm[:, i:i + sequence_length])
    test_water_level_data_sequences = np.array(test_water_level_data_sequences)
    test_water_level_data_sequences = test_water_level_data_sequences.transpose(0, 2, 1)  # Shape: (num_samples, sequence_length, num_stations)
    
    # --------------------------------------
    # G. Ensure Sequence Alignment
    # --------------------------------------
    
    # Ensure that the number of sequences align across inputs and outputs
    min_sequences = min(X_test_norm.shape[0], test_water_level_data_sequences.shape[0], y_test_sequences.shape[0])
    X_test_norm = X_test_norm[:min_sequences]
    test_water_level_data_sequences = test_water_level_data_sequences[:min_sequences]
    y_test_sequences = y_test_sequences[:min_sequences]
    y_test_filenames = y_test_filenames[sequence_length - 1:sequence_length - 1 + min_sequences]
    
    print(f"X_test_norm.shape: {X_test_norm.shape}")
    print(f"test_water_level_data_sequences.shape: {test_water_level_data_sequences.shape}")
    print(f"y_test_sequences.shape: {y_test_sequences.shape}")
    
    # --------------------------------------
    # H. Normalize Output Data
    # --------------------------------------
    
    # Normalize output data using training min and max values
    y_test_nan_mask = np.isnan(y_test_sequences)
    y_test_norm = 0.1 + 0.9 * (y_test_sequences - y_train_min) / (y_train_max - y_train_min)
    y_test_norm[y_test_nan_mask] = 0  # Handle NaNs
    
    # --------------------------------------
    # I. Load the Trained Model with Custom Layers
    # --------------------------------------
    
    try:
        # Load the model with all custom objects
        model = load_model(
            os.path.join(checkpoint_dir, 'best_model.h5'),
            custom_objects={
                'StandardCBAM': StandardCBAM,
                'CustomAttentionLayer': CustomAttentionLayer,
                'ClusterBasedApplication': ClusterBasedApplication,
                'masked_mse': masked_mse,
                'TrueLoss': TrueLoss,
                # Include any other custom layers or functions here
            }
        )
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # --------------------------------------
    # J. Cluster Masks Loading and Validation
    # --------------------------------------
    
    # Define mask directory and shapefile path
    mask_dir = '/home/samueldaramola/CNN/trainingcnn'
    polygon_clusters_path = os.path.join(mask_dir, 'reordered_polygons.shp')
    
    def create_cluster_masks(polygon_shapefile, raster_shape, transform):
        """
        Creates mutually exclusive cluster masks by rasterizing polygons.

        Args:
            polygon_shapefile (str): Path to the shapefile containing cluster polygons.
            raster_shape (tuple): Shape of the raster as (height, width).
            transform (Affine): Affine transform of the raster.

        Returns:
            Tuple[np.ndarray, gpd.GeoDataFrame]: Array of cluster masks and the GeoDataFrame of polygons.
        """
        try:
            polygons_gdf = gpd.read_file(polygon_shapefile)
        except Exception as e:
            raise ValueError(f"Error loading shapefile {polygon_shapefile}: {e}")

        cluster_masks = []

        for i, polygon in enumerate(polygons_gdf.geometry):
            mask = rasterize(
                [(polygon, 1)],
                out_shape=raster_shape,
                transform=transform,
                fill=0,
                dtype='uint8'
            )
            cluster_masks.append(mask)

        cluster_masks = np.array(cluster_masks)
        print(f"Created {len(cluster_masks)} cluster masks from {polygon_shapefile}")

        # Ensure mutual exclusivity
        combined_mask = np.sum(cluster_masks.astype(int), axis=0)
        overlap = np.any(combined_mask > 1)

        if overlap:
            overlapping_pixels = np.sum(combined_mask > 1)
            raise ValueError(f"Overlap detected: {overlapping_pixels} pixels belong to multiple clusters!")
        else:
            print("Success: All pixels belong to at most one cluster.")

        return cluster_masks, polygons_gdf

    # Load cluster masks and polygons GeoDataFrame
    try:
        cluster_masks, polygons_gdf = create_cluster_masks(
            polygon_shapefile=polygon_clusters_path,
            raster_shape=(test_atm_pressure_images.shape[1], test_atm_pressure_images.shape[2]),
            transform=transform
        )
    except ValueError as ve:
        print(ve)
        print("Please ensure the shapefile exists at the specified path.")
        return

    # Number of clusters
    num_clusters = cluster_masks.shape[0]
    print(f"Number of clusters: {num_clusters}")

    # Verify the number of clusters and stations
    num_stations = len(test_water_level_filenames)
    if num_clusters != num_stations:
        print(f"\nMismatch detected: {num_clusters} clusters vs {num_stations} stations.")
        print("Please ensure that each cluster has a corresponding station.")
        # Optionally, handle the mismatch as per your requirements
    else:
        print(f"\nNumber of clusters ({num_clusters}) matches number of stations ({num_stations}).")

    # Print the first 5 clusters and their corresponding stations
    print("\nFirst 5 clusters and corresponding stations:")
    for i in range(min(5, num_clusters)):
        # Extract cluster name
        if 'name' in polygons_gdf.columns:
            cluster_name = polygons_gdf.iloc[i]['name']
        else:
            # If there's no 'name' column, use a default naming convention
            cluster_name = f"Cluster_{i+1}"
        
        # Extract station name
        station_name = test_water_level_filenames[i]
        
        print(f"Cluster {i+1}: {cluster_name} <-> Station {i+1}: {station_name}")

    # Convert cluster masks to tensor
    cluster_masks_tensor = tf.constant(cluster_masks, dtype=tf.float32)  # Shape: (num_clusters, height, width)

    # --------------------------------------
    # K. Ensure Mask Correctness
    # --------------------------------------
    
    # Reshape cluster masks for model input
    # The model expects (batch_size, sequence_length, height, width, 1)
    batch_size = X_test_norm.shape[0]
    sequence_length = X_test_norm.shape[1]
    
    # Combine cluster masks into a single mask by taking the maximum over clusters
    single_mask = np.max(cluster_masks, axis=0)  # Shape: (212, 230)
    print(f"After np.max: {single_mask.shape}")
    
    # Add a singleton dimension for the mask channel
    single_mask = single_mask[..., np.newaxis]    # Shape: (212, 230, 1)
    print(f"After adding channel dimension: {single_mask.shape}")
    
    # Expand dimensions to add batch and sequence dimensions
    single_mask = np.expand_dims(single_mask, axis=(0, 1))  # Shape: (1, 1, 212, 230, 1)
    print(f"After expanding batch and sequence dimensions: {single_mask.shape}")
    
    # Repeat the mask for each sample in the batch and each timestep
    single_mask = np.tile(single_mask, (batch_size, sequence_length, 1, 1, 1))  # Shape: (260, 6, 212, 230, 1)
    print(f"After tiling for batch and sequence: {single_mask.shape}")
    
    # Convert to Tensor
    mask_tensor = tf.constant(single_mask, dtype=tf.float32)  # Shape: (260, 6, 212, 230, 1)
    print(f"mask_tensor shape before visualization: {mask_tensor.shape}")  # Should print (260, 6, 212, 230, 1)
    
    # Verify mask distribution
    verify_mask_distribution(mask_tensor.numpy())
    
    # Visualize the first mask of the first sequence
    visualize_mask(mask_tensor.numpy(), index=0, timestep=0)

    # --------------------------------------
    # L. Define Function to Create Attention Model
    # --------------------------------------
    
    def create_attention_models(model):
        """
        Creates separate models to output temporal and spatial attention vectors.

        Args:
            model (tf.keras.Model): Trained model.

        Returns:
            Tuple[tf.keras.Model, tf.keras.Model]: Models that output temporal and spatial attention vectors.
        """
        temporal_attention_model = None
        spatial_attention_model = None

        try:
            # Access the Temporal_Attention layer
            if 'Temporal_Attention' in [layer.name for layer in model.layers]:
                temporal_attention_layer = model.get_layer('Temporal_Attention')
                temporal_attention_output = temporal_attention_layer.output[1]
                temporal_attention_model = Model(
                    inputs=model.inputs,
                    outputs=temporal_attention_output,
                    name='Temporal_Attention_Model'
                )
            else:
                print("Layer 'Temporal_Attention' not found in the model.")

            # Access the CBAM_3 layer
            if 'CBAM_3' in [layer.name for layer in model.layers]:
                cbam3_layer = model.get_layer('CBAM_3')
                # The outputs of CBAM_3 are (refined_feature, spatial_attention_map)
                _, spatial_attention_map = cbam3_layer.output
                spatial_attention_model = Model(
                    inputs=model.inputs,
                    outputs=spatial_attention_map,
                    name='Spatial_Attention_Model'
                )
            else:
                print("Layer 'CBAM_3' not found in the model.")

            return temporal_attention_model, spatial_attention_model

        except Exception as e:
            print(f"Error creating attention models: {e}")
            return temporal_attention_model, spatial_attention_model

    # Create separate models for temporal and spatial attention
    temporal_attention_model, spatial_attention_model = create_attention_models(model)

    # --------------------------------------
    # M. Perform Predictions and Save as TIFF Images
    # --------------------------------------
    
    for i in range(len(X_test_norm)):
        X = X_test_norm[i:i + 1]                           # Shape: (1, 6, 212, 230, 5)
        mask_sample = mask_tensor[i:i + 1]                 # Shape: (1, 6, 212, 230, 1)
        water_level = test_water_level_data_sequences[i:i + 1]  # Shape: (1, 6, 21)
    
        # Make prediction
        preds = model.predict([X, mask_sample, water_level])
    
        # Ensure preds is squeezed to remove batch dimension
        preds_denorm = denormalize_data(preds[0], y_train_min, y_train_max)
        preds_denorm = apply_nan_mask(preds_denorm, y_test_nan_mask[i].squeeze())
    
        # Save prediction as TIFF
        output_filename = y_test_filenames[i]
        output_path = os.path.join(output_dir, output_filename)
        reference_dataset = os.path.join(test_water_depth_dir, output_filename)
        if not os.path.exists(reference_dataset):
            print(f"Reference dataset {reference_dataset} not found. Skipping saving prediction {i}.")
            continue
        save_tiff_image(preds_denorm, output_path, reference_dataset)
        print(f"Saved prediction {i} to {output_path}")
    
    # --------------------------------------
    # N. Load Actual and Predicted Water Depth Data
    # --------------------------------------
    
    # Prepare time series data for valid areas
    actual_water_depth, actual_filenames, _, _ = load_tiff_images(test_water_depth_dir)
    predicted_water_depth, predicted_filenames, _, _ = load_tiff_images(output_dir)
    
    # Ensure filenames of actual and predicted data match
    common_filenames = sorted(list(set(actual_filenames) & set(predicted_filenames)))
    
    if not common_filenames:
        print("No matching filenames found between actual and predicted data. Please verify the filenames.")
        return  # Exit the main function or handle appropriately
    
    # Filter actual and predicted water depth based on matching filenames
    actual_filtered = []
    predicted_filtered = []
    
    for filename in common_filenames:
        actual_idx = actual_filenames.index(filename)
        predicted_idx = predicted_filenames.index(filename)
        
        actual_filtered.append(actual_water_depth[actual_idx])
        predicted_filtered.append(predicted_water_depth[predicted_idx])
    
    # Convert filtered data to numpy arrays
    actual_filtered = np.array(actual_filtered)
    predicted_filtered = np.array(predicted_filtered)
    
    # --------------------------------------
    # O. Time Series Analysis at Specific Locations
    # --------------------------------------
    
    # Define coordinates for the new areas
    area_coords = {
        'Pasadena, TX': (29.691063, -95.209099),
        'Green Lake Oil Field, TX': (29.26667, -95.0088),
        'Wallisville, TX': (29.79746, -94.7342),
        'Moody National Wildlife Refuge, TX': (29.55, -94.66) 
    }
    
    # Function to get row, col index for coordinates
    def get_index_from_coords(lat, lon, transform):
        """Convert latitude/longitude to row/col index in raster grid"""
        try:
            col, row = ~transform * (lon, lat)
            return int(row), int(col)
        except Exception as e:
            print(f"Error converting coordinates ({lat}, {lon}): {e}")
            return None, None
    
    # Prepare time series data for valid areas
    actual_ts_dict = {}
    predicted_ts_dict = {}
    valid_areas = []
    
    for area, coords in area_coords.items():
        # Get row, col for each area
        row, col = get_index_from_coords(coords[0], coords[1], transform)
        
        if row is None or col is None:
            print(f"Skipping {area} due to coordinate conversion error.")
            continue
    
        # Check if row and col are within the bounds of the raster grid
        if (0 <= row < actual_filtered.shape[1]) and (0 <= col < actual_filtered.shape[2]):
            # Extract actual water depth time series
            actual_ts = actual_filtered[:, row, col]
            predicted_ts = predicted_filtered[:, row, col]
    
            # Check if all values are NaN
            if np.isnan(actual_ts).all() and np.isnan(predicted_ts).all():
                print(f"All values are NaN for area {area}. Skipping...")
                continue
    
            actual_ts_dict[area] = actual_ts
            predicted_ts_dict[area] = predicted_ts
            valid_areas.append(area)
        else:
            print(f"Skipping {area}: coordinates fall outside the raster grid.")
    
    if not valid_areas:
        print("No valid areas found within the raster grid.")
        return
    
    # Collect all min and max values, ignoring NaNs
    y_min_values = []
    y_max_values = []
    
    for area in valid_areas:
        actual_vals = actual_ts_dict[area]
        predicted_vals = predicted_ts_dict[area]
    
        # Remove NaN values
        actual_vals = actual_vals[~np.isnan(actual_vals)]
        predicted_vals = predicted_vals[~np.isnan(predicted_vals)]
    
        # Append min and max values, if arrays are not empty
        if actual_vals.size > 0:
            y_min_values.append(actual_vals.min())
            y_max_values.append(actual_vals.max())
    
        if predicted_vals.size > 0:
            y_min_values.append(predicted_vals.min())
            y_max_values.append(predicted_vals.max())
    
    # Proceed if we have valid min and max values
    if y_min_values and y_max_values:
        y_min = min(y_min_values) - 0.05
        y_max = max(y_max_values) + 0.05
    else:
        print("No valid min or max values found. Exiting plotting.")
        return
    
    # Plot the comparison for valid areas in subplots
    fig, axes = plt.subplots(1, len(valid_areas), figsize=(12, 3), sharey=True)
    
    # Adjust axes handling when there's only one valid subplot
    if len(valid_areas) == 1:
        axes = [axes]  # Convert to list
    
    for i, area in enumerate(valid_areas):
        actual_vals = actual_ts_dict[area]
        predicted_vals = predicted_ts_dict[area]
    
        axes[i].plot(actual_vals, label='Actual Water Depth', color='blue', linestyle='-', marker='')
        axes[i].plot(predicted_vals, label='Predicted Water Depth', color='red', linestyle='-', marker='')
        axes[i].set_title(f'{area}')
        axes[i].set_xlabel('Timesteps')
        axes[i].set_ylim([y_min, y_max])  # Apply the y-axis limits
        axes[i].grid(False)
    
    # Shared y-axis label
    axes[0].set_ylabel('Water Depth (m)')
    
    # Adjust the position of the legend and the title
    fig.suptitle('Hurricane Beryl 2024', y=1.05)  # Title adjusted
    fig.legend(['Actual Water Depth', 'Predicted Water Depth'], loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.0))
    
    # Adjust layout to add space at the top and bottom
    plt.tight_layout(rect=[0, 0.05, 1, 0.85])  # Leave a gap at the bottom and top
    plt.subplots_adjust(top=0.8, bottom=0.1)  # Extra space at the top and bottom
    
    # Save the figure
    plt.savefig('beryl.png', dpi=300, bbox_inches='tight')
    
    plt.show()
            
    # --------------------------------------
    # Q. Final Completion Message
    # --------------------------------------
    
    print("Model evaluation and visualization completed successfully.")

if __name__ == "__main__":
    main()

