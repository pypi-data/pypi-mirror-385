
# ==========================================
# Flood Depth Prediction Model with Attention
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

# ==========================================
# 1. Setup and Configuration
# ==========================================

# Set random seeds for reproducibility
seed_value = 3
np.random.seed(seed_value)
tf.random.set_seed(seed_value)

# Check if TensorFlow is using the GPU
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU memory growth enabled.")
    except RuntimeError as e:
        print(e)

# Enable mixed precision for faster computation
from tensorflow.keras.mixed_precision import set_global_policy
set_global_policy('float32')

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
        np.ndarray: Array of cluster masks with shape (num_clusters, height, width).
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

    return cluster_masks

def visualize_cluster_mapping(cluster_masks, cluster_indices, num_clusters):
    """
    Visualizes cluster masks and cluster indices for a single sample.

    Args:
        cluster_masks (np.ndarray): Array of cluster masks with shape (num_clusters, height, width).
        cluster_indices (np.ndarray): Array of cluster indices with shape (height, width).
        num_clusters (int): Number of clusters.
    """
    plt.figure(figsize=(12, 6))
    
    # Plot first 4 cluster masks
    for i in range(min(4, num_clusters)):  # Plot first 4 clusters for visibility
        plt.subplot(2, 2, i+1)
        plt.title(f'Cluster Mask {i+1}')
        plt.imshow(cluster_masks[i], cmap='gray')
        plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # Plot cluster indices
    plt.figure(figsize=(6, 6))
    plt.title('Cluster Indices')
    plt.imshow(cluster_indices, cmap='tab20')
    plt.colorbar()
    plt.axis('off')
    plt.savefig('cluster masks.png', dpi=300, bbox_inches='tight')
    plt.show()

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

class AttentionVisualizationCallback(Callback):
    def __init__(self, main_model, validation_data, save_path='attention_maps'):
        super(AttentionVisualizationCallback, self).__init__()
        self.main_model = main_model
        self.validation_data = validation_data
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        # Access the CBAM_3 layer from the main model
        attention_layer = self.main_model.get_layer('CBAM_3')
        if attention_layer.return_attention:
            _, spatial_attention_map = attention_layer.output  # Unpack outputs
        else:
            raise ValueError("CBAM_3 layer does not return attention. Please set return_attention_in_cbam3=True when building the model.")
        
        # Create a model to output the spatial_attention_map
        self.spatial_attention_model = Model(
            inputs=self.main_model.input,
            outputs=spatial_attention_map
        )
    
    def on_epoch_end(self, epoch, logs=None):
        spatial_input, mask_input, water_level_input, y_true = self.validation_data
        
        try:
            attention = self.spatial_attention_model.predict([spatial_input, mask_input, water_level_input])
            
            # Process and plot the attention map
            if attention.ndim == 4:
                attention_map = attention[0, :, :, 0]
            else:
                raise ValueError(f"Unexpected attention map dimensions: {attention.shape}")
            
            # Plot the attention map
            plt.figure(figsize=(6, 6))
            plt.title(f'Spatial Attention Map - Epoch {epoch+1}')
            plt.imshow(attention_map, cmap='viridis')
            plt.colorbar()
            plt.axis('off')
            plt.savefig(os.path.join(self.save_path, f'attention_epoch_{epoch+1}.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        except Exception as e:
            print(f"Error in AttentionVisualizationCallback: {e}")

def build_visualization_model():
    # Rebuild the model architecture with return_attention_in_cbam3=True
    visualization_model = build_model_with_cbam_weighted(
        X_train_shape=X_train_norm.shape,
        sequence_length=sequence_length,
        num_stations=num_stations,
        cluster_masks_tensor=cluster_masks_tensor,
        return_attention_in_cbam3=True 
    )
    # Load the trained weights
    visualization_model.load_weights(os.path.join(checkpoint_dir, 'best_model.h5'))
    return visualization_model

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
                                  kernel_regularizer=l2(1e-6),
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

# Load cluster polygons
try:
    polygons_gdf = gpd.read_file(polygon_clusters_path)
    print("Loaded cluster polygons:")
    print(polygons_gdf.head())
except Exception as e:
    raise ValueError(f"Error loading shapefile: {e}")

# Load spatial input images
train_atm_pressure_images, train_atm_filenames, crs, transform = load_tiff_images(train_atm_pressure_dir)
train_wind_speed_images, train_wind_filenames, _, _ = load_tiff_images(train_wind_speed_dir)
train_precipitation_images, train_precip_filenames, _, _ = load_tiff_images(train_precipitation_dir)
train_river_discharge_images, train_river_discharge_filenames, _, _ = load_tiff_images(train_river_discharge_dir)

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

# Ensure 'checkpoints_cluster' directory exists
checkpoint_dir = 'checkpoints_cluster_35'
if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)

# Create cluster masks
cluster_masks = create_cluster_masks(
    polygon_shapefile=polygon_clusters_path,
    raster_shape=(train_atm_pressure_images.shape[1], train_atm_pressure_images.shape[2]),
    transform=transform
)

# Number of clusters
num_clusters = cluster_masks.shape[0]

# Convert cluster masks to tensor
cluster_masks_tensor = tf.constant(cluster_masks, dtype=tf.float32)  # Shape: (num_clusters, height, width)

np.save(os.path.join(checkpoint_dir, 'cluster_masks.npy'), cluster_masks)
print(f"Cluster masks saved to '{os.path.join(checkpoint_dir, 'cluster_masks.npy')}'")

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
np.save(os.path.join(checkpoint_dir, 'normalization_params.npy'), normalization_params)
print(f"Normalization parameters saved to '{checkpoint_dir}/normalization_params.npy'")

# Create sequences for water level data
water_level_data_sequences = []
for i in range(water_level_data_norm.shape[1] - sequence_length + 1):
    water_level_data_sequences.append(water_level_data_norm[:, i:i + sequence_length])
water_level_data_sequences = np.array(water_level_data_sequences)  # Shape: (num_sequences, num_stations, sequence_length)

# Transpose to match expected shape: (num_sequences, sequence_length, num_stations)
water_level_data_sequences = np.transpose(water_level_data_sequences, (0, 2, 1))  # Shape: (num_sequences, sequence_length, num_stations)

# Automatically infer the number of stations
num_stations = water_level_data_sequences.shape[-1]
print(f"Number of clusters: {num_clusters}")
print(f"Number of stations: {num_stations}")

# Ensure that the number of clusters matches the number of stations
assert num_clusters == num_stations, \
    f"Number of clusters ({num_clusters}) does not match number of stations ({num_stations}). Please ensure a one-to-one mapping."

# Verify the order alignment between clusters and stations
print("First 5 clusters and corresponding stations:")
for i in range(min(5, num_clusters)):
    cluster_name = polygons_gdf.iloc[i].name if 'name' in polygons_gdf.columns else f"Cluster_{i+1}"
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
# 6. Model Construction
# ==========================================

def build_model_with_cbam_weighted(X_train_shape, sequence_length, num_stations, cluster_masks_tensor, return_attention_in_cbam3=False):
    """
    Builds the flood depth prediction model with spatial and temporal branches, integrating CBAM and attention mechanisms.
    
    Args:
        X_train_shape (tuple): Shape of the normalized spatial input data.
        sequence_length (int): Length of the input sequences.
        num_stations (int): Number of water level stations.
        cluster_masks_tensor (tf.Tensor): Tensor of cluster masks.
        return_attention_in_cbam3 (bool): Whether to return attention from CBAM_3 layer.
    
    Returns:
        tensorflow.keras.Model: Compiled Keras model.
    """
    # ---------------------------
    # 1. Define Inputs
    # ---------------------------

    # Input for spatial data: (batch_size, sequence_length, height, width, channels)
    spatial_input = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], X_train_shape[4]), name='spatial_input')

    # Input for NaN masks: (batch_size, sequence_length, height, width, 1)
    mask_input = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], 1), name='mask_input')

    # Input for temporal water level data: (batch_size, sequence_length, num_stations)
    water_level_input = Input(shape=(sequence_length, num_stations), name='water_level_input')

    # ---------------------------
    # 2. Spatial Branch with CBAM
    # ---------------------------

    # First ConvLSTM2D Layer
    x = ConvLSTM2D(filters=64,
                  kernel_size=(3, 3),
                #   dilation_rate=(2, 2),
                  padding='same',
                  return_sequences=True,
                  kernel_initializer='glorot_normal',
                  kernel_regularizer=l2(1e-6),
                  name='ConvLSTM_1')(spatial_input)
    x = LayerNormalization(name='LayerNorm_1')(x)

    # Concatenate feature and mask along channels
    x_concat = Concatenate(axis=-1, name='Concat_CBAM_1')([x, mask_input])

    # Apply TimeDistributed CBAM
    x = TimeDistributed(StandardCBAM(name='CBAM_1'),
                        name='TimeDistributed_CBAM_1')(x_concat)

    # Second ConvLSTM2D Layer
    x = ConvLSTM2D(filters=48,
                  kernel_size=(3, 3),
                #   dilation_rate=(2, 2),
                  padding='same',
                  return_sequences=True,
                  kernel_initializer='glorot_normal',
                  kernel_regularizer=l2(1e-6),
                  name='ConvLSTM_2')(x)
    x = LayerNormalization(name='LayerNorm_2')(x)

    # Concatenate feature and mask along channels
    x_concat = Concatenate(axis=-1, name='Concat_CBAM_2')([x, mask_input])

    # Apply TimeDistributed CBAM
    x = TimeDistributed(StandardCBAM(name='CBAM_2'),
                        name='TimeDistributed_CBAM_2')(x_concat)

    # Third ConvLSTM2D Layer without return_sequences
    conv_lstm_output = ConvLSTM2D(filters=48,
                                  kernel_size=(3, 3),
                                  padding='same',
                                  return_sequences=False,
                                  kernel_initializer='glorot_normal',
                                  kernel_regularizer=l2(1e-6),
                                  name='ConvLSTM_3')(x)
    conv_lstm_output = LayerNormalization(name='LayerNorm_3')(conv_lstm_output)

    # Extract the last mask
    last_mask = Lambda(lambda t: t[:, -1, :, :, :], name='Extract_Last_Mask')(mask_input)

    # Concatenate feature and mask for CBAM_3
    conv_lstm_output_concat = Concatenate(axis=-1, name='Concat_CBAM_3')([conv_lstm_output, last_mask])

    # Apply CBAM_3 with mask, with return_attention controlled by parameter
    cbam3_output = StandardCBAM(name='CBAM_3', return_attention=return_attention_in_cbam3)(conv_lstm_output_concat)
    
    if return_attention_in_cbam3:
        conv_lstm_output, spatial_attention_map = cbam3_output
    else:
        conv_lstm_output = cbam3_output

    # ---------------------------
    # 3. Temporal Branch with Two LSTM Layers
    # ---------------------------
    
    # Reshape water_level_input from (batch, sequence_length, num_stations) to (batch * num_stations, sequence_length, 1)
    reshaped_water_level = Lambda(lambda x: tf.reshape(x, (-1, sequence_length, 1)), name='Reshape_Water_Level')(water_level_input)  # Shape: (batch * num_stations, sequence_length, 1)
    
    # Apply shared LSTM layers
    shared_lstm_layer_1 = LSTM(32, return_sequences=True, kernel_initializer='glorot_normal',
                                kernel_regularizer=l2(1e-6), name='Shared_LSTM_1')(reshaped_water_level)  # Shape: (batch * num_stations, sequence_length, 32)
    shared_lstm_layer_2 = LSTM(32, return_sequences=True, kernel_initializer='glorot_normal',
                                kernel_regularizer=l2(1e-6), name='Shared_LSTM_2')(shared_lstm_layer_1)  # Shape: (batch * num_stations, sequence_length, 32)
    
    # Apply CustomAttentionLayer
    attention_layer = CustomAttentionLayer(name='Temporal_Attention')
    attention_output, attention_weights = attention_layer(shared_lstm_layer_2)  # attention_output: (batch * num_stations, features), attention_weights: (batch * num_stations, sequence_length)
    
    # Reshape attention_output back to (batch, num_stations, features)
    attention_output = Lambda(lambda x: tf.reshape(x, (-1, num_stations, x.shape[-1])), name='Reshape_Attention_Output')(attention_output)  # Shape: (batch, num_stations, features)
    
    attention_outputs = attention_output  # Shape: (batch, num_stations, features)

    # ---------------------------
    # 4. Cluster-Based Application
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
    # 5. Modulate Spatial Features with Context
    # ---------------------------

    # Multiply ConvLSTM output with combined context: (batch_size, height, width, channels=64)
    modulated_output = Multiply(name='Modulate_Spatial_With_Context')([combined_context, conv_lstm_output])

    # ---------------------------
    # 6. Final Dense Layers for Prediction
    # ---------------------------

    # Flatten the modulated output
    z = Flatten(name='Flatten_Modulated_Output')(modulated_output)  # Shape: (batch_size, height * width * channels)

    # Dense layer 1
    z = Dense(32, activation='relu',
              kernel_initializer='he_normal',
              kernel_regularizer=l2(1e-6),
              name='Dense_1')(z)  # Shape: (batch_size, 64)
    z = Dropout(0.4022, name='Dropout_1')(z)

    # # Dense layer 2
    # z = Dense(32, activation='relu',
    #           kernel_initializer='glorot_normal',
    #           kernel_regularizer=l2(1e-6),
    #           name='Dense_2')(z)  # Shape: (batch_size, 32)
    # z = Dropout(0.3, name='Dropout_2')(z)

    # Output Dense layer
    z = Dense(X_train_shape[2] * X_train_shape[3], activation='linear',
              kernel_initializer='he_normal',
              kernel_regularizer=l2(1e-6),
              name='Dense_Output')(z)  # Shape: (batch_size, height * width)

    # Reshape to (batch_size, height, width)
    output = Reshape((X_train_shape[2], X_train_shape[3]), name='Reshape_Output')(z)  # Shape: (batch_size, height, width)

    # Cast the output to float32
    output = Lambda(lambda x: tf.cast(x, tf.float32), name='Cast_Output')(output)  # Shape: (batch_size, height, width)

    # ---------------------------
    # 7. Define and Compile the Model
    # ---------------------------

    # Define the model with multiple outputs
    model = Model(inputs=[spatial_input, mask_input, water_level_input],
                  outputs=output, name='Flood_Prediction_Model')

    # Compile the model with the weighted masked MSE loss and additional metrics
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0007455),
                  loss=masked_mse,
                  metrics=['mae', 'mse', TrueLoss()])

    print("Model built and compiled successfully.")

    return model

# Build the model for training
model = build_model_with_cbam_weighted(
    X_train_shape=X_train_norm.shape,
    sequence_length=sequence_length,
    num_stations=num_stations,
    cluster_masks_tensor=cluster_masks_tensor,
    return_attention_in_cbam3=True  # Enable attention return
)

# Display the updated model summary
model.summary()

# ==========================================
# 7. Callbacks Definition
# ==========================================

class CustomModelCheckpoint(Callback):
    def __init__(self, filepath, monitor='val_loss', mode='min', save_best_only=True,
                 best_val_loss=float('inf'), training_data=None, batch_size=2):
        super(CustomModelCheckpoint, self).__init__()
        self.filepath = filepath
        self.monitor = monitor
        self.mode = mode
        self.save_best_only = save_best_only
        self.best_val_loss = best_val_loss
        self.best_epoch = None
        self.training_data = training_data
        self.batch_size = batch_size

    def on_epoch_end(self, epoch, logs=None):
        current_val_loss = logs.get(self.monitor)
        if current_val_loss is None:
            print(f"Monitor '{self.monitor}' not found. Skipping checkpoint.")
            return

        if self.mode == 'min':
            if current_val_loss < self.best_val_loss:
                self.best_val_loss = current_val_loss
                self.best_epoch = epoch + 1
                self.model.save(self.filepath)
                print(f"\nEpoch {epoch + 1}: {self.monitor} improved to {self.best_val_loss:.6f}, saving model.")
                # Save the best validation loss
                with open(os.path.join(checkpoint_dir, 'best_val_loss.txt'), 'w') as f:
                    f.write(str(self.best_val_loss))
        elif self.mode == 'max':
            if current_val_loss > self.best_val_loss:
                self.best_val_loss = current_val_loss
                self.best_epoch = epoch + 1
                self.model.save(self.filepath)
                print(f"\nEpoch {epoch + 1}: {self.monitor} improved to {self.best_val_loss:.6f}, saving model.")
                # Save the best validation loss
                with open(os.path.join(checkpoint_dir, 'best_val_loss.txt'), 'w') as f:
                    f.write(str(self.best_val_loss))

    def on_train_end(self, logs=None):
        if self.best_epoch is not None:
            print(f'\nTraining ended. Best model found at epoch {self.best_epoch}, saving attention vectors.')

            try:
                # Prepare the data
                X_train_tensor = self.training_data[0]
                nan_masks_tensor = self.training_data[1]
                water_level_sequences_tensor = self.training_data[2]

                # Reload the best model
                best_model = tf.keras.models.load_model(
                    self.filepath,
                    custom_objects={
                        'masked_mse': masked_mse,
                        'StandardCBAM': StandardCBAM,
                        'CustomAttentionLayer': CustomAttentionLayer,
                        'ClusterBasedApplication': ClusterBasedApplication,  # Include this line
                        'TrueLoss': TrueLoss
                    }
                )

                # Access the Temporal_Attention layer
                attention_layer = best_model.get_layer('Temporal_Attention')
                # The outputs of the attention layer are [summed_output, attention_weights]
                attention_weights_output = attention_layer.output[1]
                
                # Create a model to extract temporal attention weights
                temporal_attention_model = Model(
                    inputs=best_model.inputs,
                    outputs=attention_weights_output
                )
                
                # Predict temporal attention weights
                temporal_attention_weights = temporal_attention_model.predict(
                    [X_train_tensor, nan_masks_tensor, water_level_sequences_tensor],
                    batch_size=self.batch_size
                )
                
                # Determine the number of sequences and stations
                num_sequences = water_level_sequences_tensor.shape[0]
                num_stations = water_level_sequences_tensor.shape[2]
                sequence_length = water_level_sequences_tensor.shape[1]

                # Reshape attention_weights from (num_sequences * num_stations, sequence_length) to (num_sequences, num_stations, sequence_length)
                temporal_attention_weights = temporal_attention_weights.reshape((num_sequences, num_stations, sequence_length))

                # Save reshaped attention weights
                np.save(
                    os.path.join(checkpoint_dir, 'best_temporal_attention_weights.npy'),
                    temporal_attention_weights
                )
                print("Attention weights saved successfully with shape:", temporal_attention_weights.shape)

            except Exception as e:
                print(f"Error saving attention vectors: {e}")

class LossHistoryCallback(Callback):
    """
    Callback to print loss and validation loss at the end of each epoch.
    """
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        loss = logs.get('loss')
        val_loss = logs.get('val_loss')
        print(f"Epoch {epoch + 1}: Loss = {loss:.6f}, Validation Loss = {val_loss:.6f}")

loss_history_callback = LossHistoryCallback()

# Instantiate callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1)
lr_scheduler = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=1e-6,
    verbose=1
)

custom_checkpoint = CustomModelCheckpoint(
    filepath=os.path.join(checkpoint_dir, 'best_model.h5'),
    monitor='val_loss',
    mode='min',
    save_best_only=True,
    best_val_loss=float('inf'),
    training_data=[X_train_norm, nan_masks, water_level_data_sequences],
    batch_size=2
)

# Prepare validation data (e.g., first 10 samples)
val_spatial = X_train_norm[:10]
val_mask = nan_masks[:10]
val_water_level = water_level_data_sequences[:10]
val_y_true = y_train_norm[:10]

# Instantiate the attention visualizer with a reference to the main model
attention_visualizer = AttentionVisualizationCallback(
    main_model=model,
    validation_data=(val_spatial, val_mask, val_water_level, val_y_true),
    save_path='attention_maps'
)

# ==========================================
# 8. Model Training
# ==========================================

# Train the model
history = model.fit(
    [X_train_norm, nan_masks, water_level_data_sequences],
    y_train_norm.squeeze(), 
    epochs=300,
    batch_size=2,
    validation_split=0.2,
    verbose=2,
    callbacks=[early_stopping, lr_scheduler, loss_history_callback, custom_checkpoint, attention_visualizer]
)

# ==========================================
# 9. Save Training History
# ==========================================

# Convert history to DataFrame
history_df = pd.DataFrame(history.history)

# Save history to CSV
history_csv_file = os.path.join(checkpoint_dir, 'training_history.csv')
history_df.to_csv(history_csv_file, index=False)
print(f"Training history saved to '{history_csv_file}'")

# ==========================================
# 10. Sample Forward Pass for Verification
# ==========================================

# Select a small sample
sample_spatial = X_train_norm[:1]
sample_mask = nan_masks[:1]
sample_water_level = water_level_data_sequences[:1]

# Build the visualization model
visualization_model = build_visualization_model()

# Perform a forward pass
prediction_outputs = visualization_model.predict([sample_spatial, sample_mask, sample_water_level])

# If your model outputs multiple outputs, unpack them
if isinstance(prediction_outputs, list):
    prediction_output = prediction_outputs[0]
else:
    prediction_output = prediction_outputs

# Extract the spatial attention map
# Define a model to extract spatial_attention_map
attention_layer = visualization_model.get_layer('CBAM_3')
_, spatial_attention_map = attention_layer.output  # Unpack outputs

# Create a model to output the spatial_attention_map
attention_model = Model(
    inputs=visualization_model.input,
    outputs=spatial_attention_map
)

# Predict spatial attention map
spatial_attention_map_output = attention_model.predict([sample_spatial, sample_mask, sample_water_level])

# Visualize prediction
# First, define actual and predicted flood depths
actual_flood_depth = y_train_norm[0, 0, :, :]
predicted_flood_depth = prediction_output[0, :, :]

# Compute the global minimum and maximum values across both actual and predicted flood depths
global_min = min(actual_flood_depth.min(), predicted_flood_depth.min())
global_max = max(actual_flood_depth.max(), predicted_flood_depth.max())

plt.figure(figsize=(12, 6))

# Actual Flood Depth
plt.subplot(1, 2, 1)
plt.title('Actual Flood Depth')
plt.imshow(actual_flood_depth, cmap='viridis', vmin=global_min, vmax=global_max)
plt.colorbar()
plt.axis('off')

# Predicted Flood Depth
plt.subplot(1, 2, 2)
plt.title('Predicted Flood Depth')
plt.imshow(predicted_flood_depth, cmap='viridis', vmin=global_min, vmax=global_max)
plt.colorbar()
plt.axis('off')
plt.tight_layout()
plt.savefig('Predictedsample.png', dpi=300, bbox_inches='tight')
plt.show()

# Visualize Spatial Attention Map
attention_map = spatial_attention_map_output[0, :, :, 0]

# Use sample_mask instead of mask_input
masked_attention_map = attention_map * sample_mask[0, -1, :, :, 0]

plt.figure(figsize=(6, 6))
plt.title('Spatial Attention Map (Valid Cells Only)')
plt.imshow(masked_attention_map, cmap='viridis')
plt.colorbar()
plt.axis('off')
plt.savefig('spatial_attention_map.png', dpi=300, bbox_inches='tight')
plt.show()

# Print shapes for verification
print('Predicted Flood Depth Shape:', predicted_flood_depth.shape)
print('Actual Flood Depth Shape:', actual_flood_depth.shape)
print('Spatial Attention Map Shape:', attention_map.shape)

# ==========================================
# 11. Conclusion
# ==========================================

print("Model training and evaluation completed successfully.")








