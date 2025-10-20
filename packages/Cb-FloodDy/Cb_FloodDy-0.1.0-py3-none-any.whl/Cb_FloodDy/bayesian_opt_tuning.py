# ==========================================
# Flood Depth Prediction Model with Bayesian Optimization
# ==========================================

# Import necessary libraries
import os
import re
import gc
import rasterio
from rasterio.features import rasterize
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import geopandas as gpd
import optuna
from optuna import Trial
from optuna.samplers import TPESampler
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.initializers import HeNormal, GlorotNormal
from tensorflow.keras.callbacks import Callback, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import (
    Conv2D, Multiply, Dense, Reshape, Flatten, Input, ConvLSTM2D, LSTM, Dropout,
    Activation, LayerNormalization, Lambda, Add, Concatenate, GlobalAveragePooling2D,
    GlobalMaxPooling2D
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
from datetime import datetime
import matplotlib.patches as mpatches

# Set matplotlib font
plt.rcParams["font.family"] = "Times New Roman"

# ==========================================
# 1. Setup and Configuration
# ==========================================

# Set random seeds for reproducibility
seed_value = 3
np.random.seed(seed_value)
tf.random.set_seed(seed_value)

# Check if TensorFlow is using the GPU
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU memory growth enabled.")
    except RuntimeError as e:
        print(e)

# Enable mixed precision for faster computation
from tensorflow.keras.mixed_precision import set_global_policy
set_global_policy('float32')  # Use 'float32' instead of 'mixed_float16'
print("Mixed precision enabled.")

# ==========================================
# 2. Helper Functions
# ==========================================

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
            try:
                with rasterio.open(filepath) as src:
                    img = src.read(1)
                    if crs is None:
                        crs = src.crs
                    if transform is None:
                        transform = src.transform
                    images.append(img)
                filenames.append(filename)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
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
    try:
        with rasterio.open(filepath) as src:
            img = src.read(1)
            crs = src.crs
            transform = src.transform
        print(f"Loaded TIFF image from {filepath}")
        return img, crs, transform
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None, None, None

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

    # Ensure the CRS matches between the raster and vector data
    if polygons_gdf.crs != crs:
        print("CRS mismatch between raster and shapefile. Reprojecting shapefile to match raster CRS.")
        polygons_gdf = polygons_gdf.to_crs(crs)

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

def normalize_data_with_nan(data):
    """
    Normalizes data to the range [0.1, 1.0], handling NaN values by setting them to 0.

    Args:
        data (np.ndarray): Input data array.

    Returns:
        Tuple[np.ndarray, float, float, np.ndarray]: Normalized data, min, max, and NaN mask.
    """
    nan_mask = np.isnan(data)
    min_val = np.nanmin(data)
    max_val = np.nanmax(data)
    # Prevent division by zero
    if max_val == min_val:
        norm_data = np.zeros_like(data) + 0.1
    else:
        norm_data = 0.1 + 0.9 * (data - min_val) / (max_val - min_val)
    norm_data = np.clip(norm_data, 0.1, 1.0)
    norm_data[nan_mask] = 0
    return norm_data, min_val, max_val, nan_mask

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
    Loads water level data from CSV files for each station with natural sorting.
    
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
        try:
            df = pd.read_csv(filepath)
            if 'water_level' in df.columns:
                water_level_data.append(df['water_level'].values)
            else:
                print(f"'water_level' column not found in {filepath}. Skipping.")
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    if not water_level_data:
        raise ValueError(f"No valid water level data found in {data_dir}.")
    print(f"Loaded water level data from {data_dir}")
    return np.array(water_level_data), filenames

def verify_mask(mask):
    """
    Verifies that the mask is correctly inverted.

    Args:
        mask (np.ndarray): Mask array with shape (sequence_length, height, width, 1).
    """
    # Take the first sequence and first timestep
    mask_sample = mask[0, 0, :, :, 0]

    # Count number of valid and invalid pixels
    valid_pixels = np.sum(mask_sample == 1)
    invalid_pixels = np.sum(mask_sample == 0)

    print(f"Valid Pixels (1): {valid_pixels}")
    print(f"Invalid Pixels (0): {invalid_pixels}")

def visualize_valid_mask(mask):
    """
    Visualizes the inverted mask.

    Args:
        mask (np.ndarray): Mask array with shape (sequence_length, height, width, 1).
    """
    # Select the first sequence and first timestep
    mask_sample = mask[0, 0, :, :, 0]

    plt.figure(figsize=(6, 6))
    plt.title('Valid Mask (1=Valid, 0=Invalid)')
    plt.imshow(mask_sample, cmap='gray')
    plt.colorbar()
    plt.axis('off')
    plt.savefig('valid_mask.png', dpi=300, bbox_inches='tight')
    plt.show()

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
                                  kernel_regularizer=l2(l2_reg),
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

    def result(self):
        """
        Computes the average TrueLoss over all batches.

        Returns:
            Tensor: The average TrueLoss.
        """
        return self.true_loss / self.count

    def reset_state(self):
        """
        Resets the state of the metric.
        """
        self.true_loss.assign(0.0)
        self.count.assign(0.0)

# ==========================================
# 5. Data Loading and Preprocessing
# ==========================================

# Define data directories
train_atm_pressure_dir = os.path.join(os.getcwd(), 'atm_pressure')
train_wind_speed_dir = os.path.join(os.getcwd(), 'wind_speed')
train_precipitation_dir = os.path.join(os.getcwd(), 'precipitation')
train_water_depth_dir = os.path.join(os.getcwd(), 'water_depth')
train_river_discharge_dir = os.path.join(os.getcwd(), 'river_discharge')
train_dem_file1 = os.path.join(os.getcwd(), 'DEM/dem_idw.tif')
train_dem_file2 = os.path.join(os.getcwd(), 'DEM/dem_idw2.tif')
polygon_clusters_path = os.path.join(os.getcwd(), 'reordered_polygons.shp')

# Load spatial input images
train_atm_pressure_images, train_atm_filenames, crs, transform = load_tiff_images(train_atm_pressure_dir)
train_wind_speed_images, train_wind_filenames, _, _ = load_tiff_images(train_wind_speed_dir)
train_precipitation_images, train_precip_filenames, _, _ = load_tiff_images(train_precipitation_dir)
train_river_discharge_images, train_river_discharge_filenames, _, _ = load_tiff_images(train_river_discharge_dir)

# Use the shape and transform from one of your raster datasets (e.g., atmospheric pressure)
raster_shape = train_atm_pressure_images.shape[1:3]  # (height, width)

# Create cluster masks
try:
    cluster_masks, polygons_gdf = create_cluster_masks(
        polygon_shapefile=polygon_clusters_path,
        raster_shape=raster_shape,  # Use the shape from your raster data
        transform=transform  # Use the transform from your raster data
    )
except Exception as e:
    raise ValueError(f"Error creating cluster masks: {e}")

# Load DEM images and replicate across timesteps
train_dem_image1, _, _ = load_single_tiff_image(train_dem_file1)
train_dem_image2, _, _ = load_single_tiff_image(train_dem_file2)

if train_dem_image1 is None or train_dem_image2 is None:
    raise ValueError("DEM images could not be loaded. Please check the file paths and formats.")

# Define the number of timesteps for each DEM image
num_timesteps1 = 217
num_timesteps2 = train_atm_pressure_images.shape[0] - num_timesteps1

# Replicate DEM images
train_dem_images1 = np.tile(train_dem_image1, (num_timesteps1, 1, 1))
train_dem_images2 = np.tile(train_dem_image2, (num_timesteps2, 1, 1))

# Concatenate DEM images to match timesteps
train_dem_images = np.concatenate((train_dem_images1, train_dem_images2), axis=0)

# Ensure DEM images match the number of timesteps
assert train_dem_images.shape[0] == train_atm_pressure_images.shape[0], \
    "Mismatch between DEM images and timesteps."

# Stack spatial input features: atmospheric pressure, wind speed, DEM, precipitation, and river discharge
X_train = np.stack((
    train_atm_pressure_images,
    train_wind_speed_images,
    train_dem_images,
    train_precipitation_images,
    train_river_discharge_images
), axis=-1)  # Shape: (timesteps, height, width, channels)

# Define sequence length for temporal data
sequence_length = 6

# Create sequences for spatial data
X_train_sequences = []
for i in range(len(X_train) - sequence_length + 1):
    X_train_sequences.append(X_train[i:i + sequence_length])
X_train_sequences = np.array(X_train_sequences)  # Shape: (num_sequences, sequence_length, height, width, channels)

# Load training output images (water depth)
y_train, y_train_filenames, _, _ = load_tiff_images(train_water_depth_dir)

# Align y_train with X_train sequences
y_train_sequences = y_train[sequence_length - 1:]  # Shape: (num_sequences, height, width)

# Add channel dimension to y_train
y_train_sequences = y_train_sequences[:, np.newaxis, :, :]  # Shape: (num_sequences, 1, height, width)

# Normalize spatial input features, handling NaNs and collect masks
X_train_norm_list, min_vals, max_vals, nan_masks_list = [], [], [], []
for i in range(X_train_sequences.shape[-1]):
    norm_data, min_val, max_val, nan_mask = normalize_data_with_nan(X_train_sequences[..., i])
    X_train_norm_list.append(norm_data)
    min_vals.append(min_val)
    max_vals.append(max_val)
    nan_masks_list.append(nan_mask)

X_train_norm = np.stack(X_train_norm_list, axis=-1)  # Shape: (num_sequences, sequence_length, height, width, channels)

# Combine nan masks across channels to create a single mask
nan_masks_combined = np.any(np.stack(nan_masks_list, axis=-1), axis=-1).astype(float)  # Shape: (num_sequences, sequence_length, height, width)

# Invert the mask: 1 for valid areas, 0 for invalid areas
valid_mask = 1.0 - nan_masks_combined

# Expand dims to match input shape for the model
nan_masks = np.expand_dims(valid_mask, axis=-1)  # Shape: (num_sequences, sequence_length, height, width, 1)

# Verify the mask
verify_mask(nan_masks)  

# Visualize the inverted mask
visualize_valid_mask(nan_masks)  

# Normalize y_train, handling NaNs
y_train_norm, y_train_min, y_train_max, _ = normalize_data_with_nan(y_train_sequences)

# Ensure 'checkpoint_BO' directory exists
checkpoint_dir_BO = 'checkpoint_BO'
if not os.path.exists(checkpoint_dir_BO):
    os.makedirs(checkpoint_dir_BO)

# Load water level data for each station
water_level_dir = os.path.join(os.getcwd(), 'training_water_level')
water_level_data, water_level_filenames = load_water_level_data(water_level_dir)

# Normalize water level data across all stations and timesteps
global_min = np.min(water_level_data)
global_max = np.max(water_level_data)

# Normalize globally
water_level_data_norm = (water_level_data - global_min) / (global_max - global_min)

# Save normalization parameters for future reference
normalization_params = {
    'X_train_min_vals': min_vals,
    'X_train_max_vals': max_vals,
    'y_train_min': y_train_min,
    'y_train_max': y_train_max,
    'water_level_global_min': global_min,
    'water_level_global_max': global_max
}
np.save(os.path.join(checkpoint_dir_BO, 'normalization_params.npy'), normalization_params)
print(f"Normalization parameters saved to '{checkpoint_dir_BO}/normalization_params.npy'")

# Create sequences for water level data
water_level_data_sequences = []
for i in range(water_level_data_norm.shape[1] - sequence_length + 1):
    water_level_data_sequences.append(water_level_data_norm[:, i:i + sequence_length])
water_level_data_sequences = np.array(water_level_data_sequences)  # Shape: (num_sequences, num_stations, sequence_length)

# Transpose to match expected shape: (num_sequences, sequence_length, num_stations)
water_level_data_sequences = np.transpose(water_level_data_sequences, (0, 2, 1))  # Shape: (num_sequences, sequence_length, num_stations)

# Automatically infer the number of stations
num_stations = water_level_data_sequences.shape[-1]
print(f"Number of clusters: {cluster_masks.shape[0]}")
print(f"Number of stations: {num_stations}")

# Ensure that the number of clusters matches the number of stations
assert cluster_masks.shape[0] == num_stations, \
    f"Number of clusters ({cluster_masks.shape[0]}) does not match number of stations ({num_stations}). Please ensure a one-to-one mapping."

# Verify the order alignment between clusters and stations
print("First 5 clusters and corresponding stations:")
for i in range(min(5, cluster_masks.shape[0])):
    cluster_name = polygons_gdf.iloc[i]['name'] if 'name' in polygons_gdf.columns else f"Cluster_{i+1}"
    station_name = water_level_filenames[i]
    print(f"Cluster {i+1}: {cluster_name} <-> Station {i+1}: {station_name}")

# Ensure the number of sequences matches between spatial and temporal data
assert water_level_data_sequences.shape[0] == X_train_norm.shape[0], \
    "Mismatch in number of sequences between water level data and spatial data."

# After combining the masks and before training
print(f"X_train_norm shape: {X_train_norm.shape}")       
print(f"nan_masks shape: {nan_masks.shape}")       
print(f"water_level_data_sequences shape: {water_level_data_sequences.shape}") 
print(f"y_train_norm shape: {y_train_norm.squeeze().shape}")  

# ==========================================
# 6. Model Construction with Hyperparameter Tuning
# ==========================================

def build_model_with_cbam_weighted(trial: Trial, X_train_shape, sequence_length, num_stations, cluster_masks_tensor):
    """
    Builds the flood depth prediction model with spatial and temporal branches, integrating CBAM and attention mechanisms.
    Hyperparameters are sampled from the given ranges.

    Args:
        trial (Trial): Optuna trial object.
        X_train_shape (tuple): Shape of the normalized spatial input data.
        sequence_length (int): Length of the input sequences.
        num_stations (int): Number of water level stations.
        cluster_masks_tensor (tf.Tensor): Tensor of cluster masks.

    Returns:
        tensorflow.keras.Model: Compiled Keras model.
    """
    # ---------------------------
    # 1. Define Inputs
    # ---------------------------

    # Input for spatial data: (batch_size, sequence_length, height, width, channels)
    spatial_input = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], X_train_shape[4]),
                          name='spatial_input')

    # Input for NaN masks: (batch_size, sequence_length, height, width, 1)
    mask_input = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], 1),
                      name='mask_input')

    # Input for temporal water level data: (batch_size, sequence_length, num_stations)
    water_level_input = Input(shape=(sequence_length, num_stations), name='water_level_input')

    # ---------------------------
    # 2. Hyperparameter Sampling
    # ---------------------------

    # Sample hyperparameters
    convlstm_1_filters = trial.suggest_categorical('convlstm_1_filters', [16, 32, 48, 64])
    convlstm_2_filters = trial.suggest_categorical('convlstm_2_filters', [16, 32, 48, 64])
    convlstm_3_filters = trial.suggest_categorical('convlstm_3_filters', [16, 32, 48, 64])

    lstm_units_1 = trial.suggest_categorical('lstm_units_1', [32, 48, 64])
    lstm_units_2 = trial.suggest_categorical('lstm_units_2', [32, 48, 64])

    dense_1_units = trial.suggest_categorical('dense_1_units', [32, 48, 64])
    # dense_2_units = trial.suggest_categorical('dense_2_units', [32, 48, 64])

    l2_reg = trial.suggest_loguniform('l2_reg', l2_reg, 1e-3)
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-3)

    dropout_rate = trial.suggest_uniform('dropout_rate', 0.2, 0.5)

    # ---------------------------
    # 3. Spatial Branch with CBAM
    # ---------------------------

    # First ConvLSTM2D Layer
    x = ConvLSTM2D(filters=convlstm_1_filters,
                  kernel_size=(3, 3),
                #   dilation_rate=(2, 2),
                  padding='same',
                  return_sequences=True,
                  kernel_initializer='glorot_normal',
                  kernel_regularizer=l2(l2_reg),
                  name='ConvLSTM_1')(spatial_input)
    x = LayerNormalization(name='LayerNorm_1')(x)

    # Concatenate feature and mask along channels
    x_concat = Concatenate(axis=-1, name='Concat_CBAM_1')([x, mask_input])

    # Apply TimeDistributed CBAM
    x = TimeDistributed(StandardCBAM(name='CBAM_1'),
                        name='TimeDistributed_CBAM_1')(x_concat)

    # Second ConvLSTM2D Layer
    x = ConvLSTM2D(filters=convlstm_2_filters,
                  kernel_size=(3, 3),
                #   dilation_rate=(2, 2),
                  padding='same',
                  return_sequences=True,
                  kernel_initializer='glorot_normal',
                  kernel_regularizer=l2(l2_reg),
                  name='ConvLSTM_2')(x)
    x = LayerNormalization(name='LayerNorm_2')(x)

    # Concatenate feature and mask along channels
    x_concat = Concatenate(axis=-1, name='Concat_CBAM_2')([x, mask_input])

    # Apply TimeDistributed CBAM
    x = TimeDistributed(StandardCBAM(name='CBAM_2'),
                        name='TimeDistributed_CBAM_2')(x_concat)

    # Third ConvLSTM2D Layer without return_sequences
    conv_lstm_output = ConvLSTM2D(filters=convlstm_3_filters,
                                  kernel_size=(3, 3),
                                  padding='same',
                                  return_sequences=False,
                                  kernel_initializer='glorot_normal',
                                  kernel_regularizer=l2(l2_reg),
                                  name='ConvLSTM_3')(x)
    x = LayerNormalization(name='LayerNorm_3')(conv_lstm_output)

    # Extract the last mask
    last_mask = Lambda(lambda t: t[:, -1, :, :, :], name='Extract_Last_Mask')(mask_input)

    # Concatenate feature and mask for CBAM_3
    x_concat = Concatenate(axis=-1, name='Concat_CBAM_3')([x, last_mask])

    # Apply CBAM_3 with mask, with return_attention=True
    cbam3_output = StandardCBAM(name='CBAM_3', return_attention=True)(x_concat)
    
    conv_lstm_output, spatial_attention_map = cbam3_output

    # ---------------------------
    # 4. Temporal Branch with Two LSTM Layers
    # ---------------------------
    
    # Reshape water_level_input from (batch, sequence_length, num_stations) to (batch * num_stations, sequence_length, 1)
    reshaped_water_level = Lambda(lambda x: tf.reshape(x, (-1, sequence_length, 1)), name='Reshape_Water_Level')(water_level_input)  # Shape: (batch * num_stations, sequence_length, 1)
    
    # Apply shared LSTM layers
    shared_lstm_layer_1 = LSTM(lstm_units_1, return_sequences=True, kernel_initializer='glorot_normal',
                                kernel_regularizer=l2(l2_reg), name='Shared_LSTM_1')(reshaped_water_level)  # Shape: (batch * num_stations, sequence_length, lstm_units_1)
    shared_lstm_layer_2 = LSTM(lstm_units_2, return_sequences=True, kernel_initializer='glorot_normal',
                                kernel_regularizer=l2(l2_reg), name='Shared_LSTM_2')(shared_lstm_layer_1)  # Shape: (batch * num_stations, sequence_length, lstm_units_2)
    
    # Apply CustomAttentionLayer
    attention_layer = CustomAttentionLayer(name='Temporal_Attention')
    attention_output, attention_weights = attention_layer(shared_lstm_layer_2)  # attention_output: (batch * num_stations, features), attention_weights: (batch * num_stations, sequence_length)
    
    # Reshape attention_output back to (batch, num_stations, features)
    attention_output = Lambda(lambda x: tf.reshape(x, (-1, num_stations, x.shape[-1])), name='Reshape_Attention_Output')(attention_output)  # Shape: (batch, num_stations, features)
    
    attention_outputs = attention_output  # Shape: (batch, num_stations, features)

    # ---------------------------
    # 5. Cluster-Based Application
    # ---------------------------

    # Instantiate the ClusterBasedApplication layer
    cluster_application = ClusterBasedApplication(
        num_stations=num_stations,
        height=X_train_shape[2],
        width=X_train_shape[3],
        name='Cluster_Based_Application'
    )

    # Apply ClusterBasedApplication
    combined_context = cluster_application([attention_outputs, cluster_masks_tensor])  # Shape: (batch, height, width, 1)

    # ---------------------------
    # 6. Modulate Spatial Features with Context
    # ---------------------------

    # Multiply ConvLSTM output with combined context: (batch_size, height, width, channels=conv_lstm_3_filters)
    modulated_output = Multiply(name='Modulate_Spatial_With_Context')([combined_context, conv_lstm_output])

    # ---------------------------
    # 7. Final Dense Layers for Prediction
    # ---------------------------

    # Flatten the modulated output
    z = Flatten(name='Flatten_Modulated_Output')(modulated_output)  # Shape: (batch_size, height * width * channels)

    # Dense layer 1
    z = Dense(dense_1_units, activation='relu',
              kernel_initializer='he_normal',
              kernel_regularizer=l2(l2_reg),
              name='Dense_1')(z)
    z = Dropout(dropout_rate, name='Dropout_1')(z)

    # # Dense layer 2
    # z = Dense(dense_2_units, activation='relu',
    #           kernel_initializer='glorot_normal',
    #           kernel_regularizer=l2(l2_reg),
    #           name='Dense_2')(z)
    # z = Dropout(dropout_rate, name='Dropout_2')(z)

    # Output Dense layer
    z = Dense(X_train_shape[2] * X_train_shape[3], activation='linear',
              kernel_initializer='he_normal',
              kernel_regularizer=l2(l2_reg),
              name='Dense_Output')(z)  # Shape: (batch_size, height * width)

    # Reshape to (batch_size, height, width)
    output = Reshape((X_train_shape[2], X_train_shape[3]), name='Reshape_Output')(z)  # Shape: (batch_size, height, width)

    # Cast the output to float32
    output = Lambda(lambda x: tf.cast(x, tf.float32), name='Cast_Output')(output)  # Shape: (batch_size, height, width)

    # ---------------------------
    # 8. Define and Compile the Model
    # ---------------------------

    # Define the model with multiple outputs
    model = Model(inputs=[spatial_input, mask_input, water_level_input],
                  outputs=output, name='Flood_Prediction_Model')

    # Compile the model with the masked MSE loss and additional metrics
    optimizer = Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer,
                  loss=masked_mse,
                  metrics=['mae', 'mse', TrueLoss()])

    print("Model built and compiled successfully with sampled hyperparameters.")

    return model

# ==========================================
# 7. Callbacks Definition
# ==========================================

class TrialCallback(Callback):
    """
    Custom callback to save training history and hyperparameters for each trial.
    """
    def __init__(self, trial, trial_number):
        super(TrialCallback, self).__init__()
        self.trial = trial
        self.trial_number = trial_number
        self.history = {}

    def on_train_begin(self, logs=None):
        self.history = {'epoch': [], 'loss': [], 'val_loss': [], 'mae': [], 'mse': [], 'TrueLoss': []}

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self.history['epoch'].append(epoch + 1)
        self.history['loss'].append(logs.get('loss'))
        self.history['val_loss'].append(logs.get('val_loss'))
        self.history['mae'].append(logs.get('mae'))
        self.history['mse'].append(logs.get('mse'))
        self.history['TrueLoss'].append(logs.get('val_TrueLoss'))

    def on_train_end(self, logs=None):
        # Save training history to CSV
        history_df = pd.DataFrame(self.history)
        history_csv_path = os.path.join(checkpoint_dir_BO, f'trial_{self.trial_number}_history.csv')
        history_df.to_csv(history_csv_path, index=False)
        print(f"Trial {self.trial_number}: Training history saved to {history_csv_path}")

        # Save hyperparameters and best val loss as PNG
        hyperparams = self.trial.params
        best_val_loss = min(self.history['val_loss']) if self.history['val_loss'] else None

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.axis('tight')
        ax.axis('off')
        table_data = [
            ['Hyperparameter', 'Value'],
            ['ConvLSTM_1 Filters', hyperparams.get('convlstm_1_filters')],
            ['ConvLSTM_2 Filters', hyperparams.get('convlstm_2_filters')],
            ['ConvLSTM_3 Filters', hyperparams.get('convlstm_3_filters')],
            ['LSTM Units 1', hyperparams.get('lstm_units_1')],
            ['LSTM Units 2', hyperparams.get('lstm_units_2')],
            ['Dense 1 Units', hyperparams.get('dense_1_units')],
            # ['Dense 2 Units', hyperparams.get('dense_2_units')],
            # ['L2 Regularization', hyperparams.get('l2_reg')],
            ['Learning Rate', hyperparams.get('learning_rate')],
            ['Dropout Rate', hyperparams.get('dropout_rate')],
            ['Best Val Loss', best_val_loss]
        ]
        table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
        table.scale(1, 2)
        plt.title(f'Trial {self.trial_number} Hyperparameters and Best Val Loss')
        png_path = os.path.join(checkpoint_dir_BO, f'trial_{self.trial_number}_hyperparams.png')
        plt.savefig(png_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Trial {self.trial_number}: Hyperparameters and best val loss saved to {png_path}")

# ==========================================
# 8. Bayesian Optimization with Optuna
# ==========================================

def objective(trial: Trial):
    """
    Objective function for Optuna to optimize.

    Args:
        trial (Trial): Optuna trial object.

    Returns:
        float: Best validation loss achieved by the model.
    """
    # Build the model with hyperparameters sampled by the trial
    model = build_model_with_cbam_weighted(
        trial=trial,
        X_train_shape=X_train_norm.shape,
        sequence_length=sequence_length,
        num_stations=num_stations,
        cluster_masks_tensor=tf.constant(cluster_masks, dtype=tf.float32)
    )

    # Define callbacks
    early_stopping_cb = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=2)
    lr_scheduler_cb = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=l2_reg,
        verbose=2
    )

    # Initialize trial number based on existing trials
    existing_trials = [f for f in os.listdir(checkpoint_dir_BO) if f.startswith('trial_') and f.endswith('_history.csv')]
    trial_number = len(existing_trials) + 1

    trial_cb = TrialCallback(trial=trial, trial_number=trial_number)

    # Fit the model
    history = model.fit(
        [X_train_norm, nan_masks, water_level_data_sequences],
        y_train_norm.squeeze(), 
        epochs=300,
        batch_size=2,
        validation_split=0.2,
        verbose=2,
        callbacks=[early_stopping_cb, lr_scheduler_cb, trial_cb]
    )

    # Get the best validation loss
    best_val_loss = min(history.history['val_loss']) if 'val_loss' in history.history else None

    # Free up memory
    del model
    gc.collect()
    tf.keras.backend.clear_session()

    return best_val_loss

def run_optimization():
    """
    Runs Bayesian Optimization using Optuna for hyperparameter tuning.
    """
    # Initialize Optuna study
    study_name = "Flood_Depth_Prediction_BO"
    storage_name = f"sqlite:///{os.path.join(checkpoint_dir_BO, 'study.db')}"
    sampler = TPESampler(seed=seed_value)
    try:
        study = optuna.load_study(study_name=study_name, storage=storage_name)
        print(f"Loaded existing study '{study_name}'.")
    except Exception as e:
        study = optuna.create_study(direction='minimize', sampler=sampler, study_name=study_name, storage=storage_name, load_if_exists=True)
        print(f"Created new study '{study_name}'.")

    # Optimize the objective function
    study.optimize(objective, n_trials=100, timeout=None)

    # Save the study results
    study_summary_path = os.path.join(checkpoint_dir_BO, 'study_summary.csv')
    study_df = study.trials_dataframe()
    study_df.to_csv(study_summary_path, index=False)
    print(f"Study summary saved to {study_summary_path}")

    # Plot optimization history
    try:
        fig1 = optuna.visualization.plot_optimization_history(study)
        fig1.write_image(os.path.join(checkpoint_dir_BO, 'optimization_history.png'))
        print(f"Optimization history plot saved to '{os.path.join(checkpoint_dir_BO, 'optimization_history.png')}'")
    except Exception as e:
        print(f"Error saving optimization history plot: {e}")

    # Plot parameter importances
    try:
        fig2 = optuna.visualization.plot_param_importances(study)
        fig2.write_image(os.path.join(checkpoint_dir_BO, 'param_importances.png'))
        print(f"Parameter importances plot saved to '{os.path.join(checkpoint_dir_BO, 'param_importances.png')}'")
    except Exception as e:
        print(f"Error saving parameter importances plot: {e}")

    # Print best trial
    best_trial = study.best_trial
    print("Best trial:")
    print(f"  Value (Best Val Loss): {best_trial.value}")
    print("  Hyperparameters:")
    for key, value in best_trial.params.items():
        print(f"    {key}: {value}")

    # Save best hyperparameters and val loss as PNG
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    ax3.axis('tight')
    ax3.axis('off')
    table_data = [
        ['Hyperparameter', 'Value'],
        ['ConvLSTM_1 Filters', best_trial.params.get('convlstm_1_filters')],
        ['ConvLSTM_2 Filters', best_trial.params.get('convlstm_2_filters')],
        ['ConvLSTM_3 Filters', best_trial.params.get('convlstm_3_filters')],
        ['LSTM Units 1', best_trial.params.get('lstm_units_1')],
        ['LSTM Units 2', best_trial.params.get('lstm_units_2')],
        ['Dense 1 Units', best_trial.params.get('dense_1_units')],
        # ['Dense 2 Units', best_trial.params.get('dense_2_units')],
        ['L2 Regularization', best_trial.params.get('l2_reg')],
        ['Learning Rate', best_trial.params.get('learning_rate')],
        ['Dropout Rate', best_trial.params.get('dropout_rate')],
        ['Best Val Loss', best_trial.value]
    ]
    table = ax3.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
    table.scale(1, 2)
    plt.title('Best Trial Hyperparameters and Val Loss')
    best_png_path = os.path.join(checkpoint_dir_BO, 'best_trial_hyperparams.png')
    plt.savefig(best_png_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Best trial hyperparameters and val loss saved to '{best_png_path}'")

# Run the optimization
run_optimization()

# ==========================================
# 9. Conclusion
# ==========================================

print("Bayesian Optimization completed successfully. All results are saved in the 'checkpoint_BO' folder.")