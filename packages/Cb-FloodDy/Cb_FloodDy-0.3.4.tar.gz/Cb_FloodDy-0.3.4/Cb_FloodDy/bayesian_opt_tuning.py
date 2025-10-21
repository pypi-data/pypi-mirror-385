
# ==========================================
# Flood Depth Prediction Model with Attention
# ==========================================

# Import necessary libraries
import os
import re
import gc
import optuna
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
            outputs = attention_layer.output  # this is a list [features, spatial_attention]
            spatial_attention_map = outputs[1]
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
        # Detect whether we got multiple input SHAPES (e.g., [shapeA, shapeB]) or a single shape (tuple of dims)
        is_multi_input = (
            isinstance(input_shape, (list, tuple)) and
            len(input_shape) > 0 and
            # In the multi-input case, elements are themselves shapes (tuples/TensorShapes),
            # not scalar dims like None / int
            all(isinstance(s, (list, tuple, tf.TensorShape)) for s in input_shape)
        )

        if is_multi_input:
            # Sum channels across inputs; assume channel-last
            total_channels = 0
            for shp in input_shape:
                total_channels += int(shp[-1])
        else:
            # Single input shape like (None, H, W, C)
            total_channels = int(input_shape[-1])

        # Reserve the last channel as the mask
        self.feature_channels = total_channels - 1  # Last channel is mask

        # Channel Attention layers
        self.shared_dense_one = Dense(
            max(1, self.feature_channels // self.ratio),
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

        # Spatial Attention conv layer
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
        # Accept either a single concatenated tensor or a list/tuple of tensors
        if isinstance(inputs, (list, tuple)):
            inputs = tf.concat(inputs, axis=-1)
        
        # Split feature and mask channels
        feature = inputs[..., :self.feature_channels]
        mask = inputs[..., self.feature_channels:]  # Shape: (batch, height, width, 1)
        mask = tf.cast(mask, feature.dtype)

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
            return [refined_feature, spatial_attention]
        else:
            return refined_feature

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
# 6. Model Construction (parametrized)
# ==========================================

def build_model_with_cbam_weighted(
    X_train_shape,
    sequence_length,
    num_stations,
    cluster_masks_tensor,
    convlstm_filters=(16, 32, 48),
    lstm_units=(32, 48),
    dense_units=64,
    l2_reg=1e-6,
    dropout_rate=0.3,
    lr=5e-4,
    return_attention_in_cbam3=False
):
    spatial_input = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], X_train_shape[4]), name='spatial_input')
    mask_input    = Input(shape=(X_train_shape[1], X_train_shape[2], X_train_shape[3], 1), name='mask_input')
    water_level_input = Input(shape=(sequence_length, num_stations), name='water_level_input')

    x = ConvLSTM2D(filters=convlstm_filters[0], kernel_size=(3, 3), padding='same',
                   return_sequences=True, kernel_initializer='glorot_normal',
                   kernel_regularizer=l2(l2_reg), name='ConvLSTM_1')(spatial_input)
    x = LayerNormalization(name='LayerNorm_1')(x)

    x_concat = Concatenate(axis=-1, name='Concat_CBAM_1')([x, mask_input])
    x = TimeDistributed(StandardCBAM(name='CBAM_1'), name='TimeDistributed_CBAM_1')(x_concat)

    x = ConvLSTM2D(filters=convlstm_filters[1], kernel_size=(3, 3), padding='same',
                   return_sequences=True, kernel_initializer='glorot_normal',
                   kernel_regularizer=l2(l2_reg), name='ConvLSTM_2')(x)
    x = LayerNormalization(name='LayerNorm_2')(x)

    x_concat = Concatenate(axis=-1, name='Concat_CBAM_2')([x, mask_input])
    x = TimeDistributed(StandardCBAM(name='CBAM_2'), name='TimeDistributed_CBAM_2')(x_concat)

    conv_lstm_output = ConvLSTM2D(filters=convlstm_filters[2], kernel_size=(3, 3), padding='same',
                                  return_sequences=False, kernel_initializer='glorot_normal',
                                  kernel_regularizer=l2(l2_reg), name='ConvLSTM_3')(x)
    conv_lstm_output = LayerNormalization(name='LayerNorm_3')(conv_lstm_output)

    last_mask = Lambda(lambda t: t[:, -1, :, :, :], name='Extract_Last_Mask')(mask_input)
    conv_lstm_output_concat = Concatenate(axis=-1, name='Concat_CBAM_3')([conv_lstm_output, last_mask])

    cbam3_output = StandardCBAM(name='CBAM_3', return_attention=return_attention_in_cbam3)(conv_lstm_output_concat)
    if return_attention_in_cbam3:
        conv_lstm_output = cbam3_output[0]
        spatial_attention_map = cbam3_output[1]
    else:
        conv_lstm_output = cbam3_output

    reshaped_water_level = Lambda(lambda x: tf.reshape(x, (-1, sequence_length, 1)), name='Reshape_Water_Level')(water_level_input)
    shared_lstm_layer_1 = LSTM(lstm_units[0], return_sequences=True, kernel_initializer='glorot_normal',
                               kernel_regularizer=l2(l2_reg), name='Shared_LSTM_1')(reshaped_water_level)
    shared_lstm_layer_2 = LSTM(lstm_units[1], return_sequences=True, kernel_initializer='glorot_normal',
                               kernel_regularizer=l2(l2_reg), name='Shared_LSTM_2')(shared_lstm_layer_1)

    attention_layer = CustomAttentionLayer(name='Temporal_Attention')
    attention_output, attention_weights = attention_layer(shared_lstm_layer_2)
    attention_output = Lambda(lambda x: tf.reshape(x, (-1, num_stations, x.shape[-1])), name='Reshape_Attention_Output')(attention_output)

    cluster_application = ClusterBasedApplication(
        num_stations=num_stations,
        height=X_train_shape[2],
        width=X_train_shape[3],
        name='Cluster_Based_Application'
    )
    combined_context = cluster_application([attention_output, cluster_masks_tensor])

    modulated_output = Multiply(name='Modulate_Spatial_With_Context')([combined_context, conv_lstm_output])

    z = Flatten(name='Flatten_Modulated_Output')(modulated_output)
    z = Dense(dense_units, activation='relu', kernel_initializer='he_normal',
              kernel_regularizer=l2(l2_reg), name='Dense_1')(z)
    z = Dropout(dropout_rate, name='Dropout_1')(z)

    z = Dense(X_train_shape[2] * X_train_shape[3], activation='linear',
              kernel_initializer='he_normal', kernel_regularizer=l2(l2_reg),
              name='Dense_Output')(z)

    output = Reshape((X_train_shape[2], X_train_shape[3]), name='Reshape_Output')(z)
    output = Lambda(lambda x: tf.cast(x, tf.float32), name='Cast_Output')(output)

    model = Model(inputs=[spatial_input, mask_input, water_level_input], outputs=output, name='Flood_Prediction_Model')
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
                  loss=masked_mse,
                  metrics=['mae', 'mse', TrueLoss()])
    return model


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
                ckpt_dir = os.path.dirname(self.filepath)
                os.makedirs(ckpt_dir, exist_ok=True)
                with open(os.path.join(ckpt_dir, 'best_val_loss.txt'), 'w') as f:
                    f.write(str(self.best_val_loss))
        elif self.mode == 'max':
            if current_val_loss > self.best_val_loss:
                self.best_val_loss = current_val_loss
                self.best_epoch = epoch + 1
                self.model.save(self.filepath)
                print(f"\nEpoch {epoch + 1}: {self.monitor} improved to {self.best_val_loss:.6f}, saving model.")
                # Save the best validation loss
                ckpt_dir = os.path.dirname(self.filepath)
                os.makedirs(ckpt_dir, exist_ok=True)
                with open(os.path.join(ckpt_dir, 'best_val_loss.txt'), 'w') as f:
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
                ckpt_dir = os.path.dirname(self.filepath)
                os.makedirs(ckpt_dir, exist_ok=True)
                np.save(
                    os.path.join(ckpt_dir, 'best_temporal_attention_weights.npy'),
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

# ==========================================
# 8. Model Training
# ==========================================

def run_optimization(
    train_atm_pressure_dir,
    train_wind_speed_dir,
    train_precipitation_dir,
    train_water_depth_dir,
    train_river_discharge_dir,
    water_level_dir,
    polygon_clusters_path,
    sequence_length,
    n_trials,
    study_name,
    checkpoint_dir_BO,
    seed_value,
    convlstm_filters,
    lstm_units,
    dense_units,
    l2_reg_range,
    lr_range,
    dropout_range,
    es_monitor,
    early_stopping,
    es_restore_best,
    epochs,
    batch_size,
    val_split,
    dem_files,
    dem_timesteps,
    visualize=False   
):
    np.random.seed(seed_value)
    tf.random.set_seed(seed_value)

    # ---------- Load spatial & temporal data (reusing your helpers) ----------
    train_atm_pressure_images, _, crs, transform = load_tiff_images(train_atm_pressure_dir)
    train_wind_speed_images,  _, _, _ = load_tiff_images(train_wind_speed_dir)
    train_precipitation_images, _, _, _ = load_tiff_images(train_precipitation_dir)
    train_river_discharge_images, _, _, _ = load_tiff_images(train_river_discharge_dir)
    y_train, _, _, _ = load_tiff_images(train_water_depth_dir)

    # === Multi-DEM stack (inside run_optimization) ===
    def _build_multi_dem_stack(dem_files, dem_timesteps, total_timesteps, transform_ref=None):
        """
        Load each DEM tif in dem_files and tile it for the corresponding length in dem_timesteps.
        Validates that sum(dem_timesteps) == total_timesteps.
        Optionally checks shape compatibility using the first spatial raster.
        """
        if dem_files is None or dem_timesteps is None:
            raise ValueError("dem_files and dem_timesteps must be provided to run_optimization.")
    
        if len(dem_files) != len(dem_timesteps):
            raise ValueError(f"dem_files ({len(dem_files)}) and dem_timesteps ({len(dem_timesteps)}) must have same length.")
    
        if sum(dem_timesteps) != total_timesteps:
            raise AssertionError(
                f"sum(dem_timesteps)={sum(dem_timesteps)} must equal total timesteps={total_timesteps} "
                "(must match your atmospheric/wind/precip stacks)."
            )
    
        dem_tiles = []
        target_h = train_atm_pressure_images.shape[1]
        target_w = train_atm_pressure_images.shape[2]
    
        for dem_path, reps in zip(dem_files, dem_timesteps):
            with rasterio.open(dem_path) as src:
                dem = src.read(1)
                # sanity: same HxW
                if dem.shape != (target_h, target_w):
                    raise ValueError(
                        f"DEM shape {dem.shape} does not match raster shape {(target_h, target_w)}: {dem_path}"
                    )
            dem_tiles.append(np.tile(dem, (reps, 1, 1)))
    
        return np.concatenate(dem_tiles, axis=0)  # (T, H, W)
    
    # Build DEM stack aligned to time axis
    total_T = train_atm_pressure_images.shape[0]
    train_dem_images = _build_multi_dem_stack(
        dem_files=dem_files,
        dem_timesteps=dem_timesteps,
        total_timesteps=total_T
    )

    X_train = np.stack((
        train_atm_pressure_images,
        train_wind_speed_images,
        train_dem_images,
        train_precipitation_images,
        train_river_discharge_images
    ), axis=-1)

    # sequences
    X_train_sequences = np.array([X_train[i:i+sequence_length] for i in range(len(X_train)-sequence_length+1)])
    y_train_sequences = y_train[sequence_length-1:]
    y_train_sequences = y_train_sequences[:, np.newaxis, :, :]

    # normalize + mask
    X_train_norm_list, min_vals, max_vals, nan_masks_list = [], [], [], []
    for i in range(X_train_sequences.shape[-1]):
        norm_data, min_val, max_val, nan_mask = normalize_data_with_nan(X_train_sequences[..., i])
        X_train_norm_list.append(norm_data); min_vals.append(min_val); max_vals.append(max_val); nan_masks_list.append(nan_mask)
    X_train_norm = np.stack(X_train_norm_list, axis=-1)
    nan_masks_combined = np.any(np.stack(nan_masks_list, axis=-1), axis=-1).astype(float)
    nan_masks = np.expand_dims(1.0 - nan_masks_combined, axis=-1)

    y_train_norm, y_train_min, y_train_max, _ = normalize_data_with_nan(y_train_sequences)

    # clusters
    polygons_gdf = gpd.read_file(polygon_clusters_path)
    cluster_masks = create_cluster_masks(
        polygon_shapefile=polygon_clusters_path,
        raster_shape=(train_atm_pressure_images.shape[1], train_atm_pressure_images.shape[2]),
        transform=transform
    )
    num_clusters = cluster_masks.shape[0]
    cluster_masks_tensor = tf.constant(cluster_masks, dtype=tf.float32)
    
    # Save cluster masks once per run
    artifacts_dir = os.path.join(checkpoint_dir_BO, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    np.save(os.path.join(artifacts_dir, "cluster_masks.npy"), cluster_masks)
    print(f"Saved cluster masks to {os.path.join(artifacts_dir, 'cluster_masks.npy')}")

    # water level
    water_level_data, water_level_filenames = load_water_level_data(water_level_dir)
    wl_min, wl_max = np.min(water_level_data), np.max(water_level_data)
    water_level_data_norm = (water_level_data - wl_min) / (wl_max - wl_min)
    wl_seq = []
    for i in range(water_level_data_norm.shape[1] - sequence_length + 1):
        wl_seq.append(water_level_data_norm[:, i:i+sequence_length])
    wl_seq = np.transpose(np.array(wl_seq), (0, 2, 1))  # (num_sequences, sequence_length, num_stations)

    num_stations = wl_seq.shape[-1]
    assert num_clusters == num_stations, "Number of clusters must match number of stations."
    assert wl_seq.shape[0] == X_train_norm.shape[0], "Temporal and spatial sequences mismatch."

    # validation split
    N = X_train_norm.shape[0]
    val_n = int(val_split * N)
    X_val, M_val, WL_val, Y_val = X_train_norm[:val_n], nan_masks[:val_n], wl_seq[:val_n], y_train_norm[:val_n].squeeze()
    X_trn, M_trn, WL_trn, Y_trn = X_train_norm[val_n:], nan_masks[val_n:], wl_seq[val_n:], y_train_norm[val_n:].squeeze()

    os.makedirs(checkpoint_dir_BO, exist_ok=True)
    
    # Save normalization parameters once per run
    artifacts_dir = os.path.join(checkpoint_dir_BO, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    np.savez(
        os.path.join(artifacts_dir, "normalization_params.npz"),
        X_train_min_vals=np.array(min_vals, dtype=np.float32),
        X_train_max_vals=np.array(max_vals, dtype=np.float32),
        y_train_min=np.array(y_train_min, dtype=np.float32),
        y_train_max=np.array(y_train_max, dtype=np.float32),
        water_level_global_min=np.array(wl_min, dtype=np.float32),
        water_level_global_max=np.array(wl_max, dtype=np.float32)
    )
    print(f"Saved normalization params to {os.path.join(artifacts_dir, 'normalization_params.npz')}")

    # ---------- Optuna objective ----------
    def objective(trial: optuna.Trial):
        # sample hyperparams from provided grids/ranges
        f1 = trial.suggest_categorical("convlstm_f1", convlstm_filters)
        f2 = trial.suggest_categorical("convlstm_f2", convlstm_filters)
        f3 = trial.suggest_categorical("convlstm_f3", convlstm_filters)

        l1 = trial.suggest_categorical("lstm_u1", lstm_units)
        l2_ = trial.suggest_categorical("lstm_u2", lstm_units)

        d_units = trial.suggest_categorical("dense_units", dense_units)

        l2_reg = trial.suggest_float("l2_reg", l2_reg_range[0], l2_reg_range[1], log=True)
        lr     = trial.suggest_float("lr", lr_range[0], lr_range[1], log=True)
        drop   = trial.suggest_float("dropout", dropout_range[0], dropout_range[1])

        # per-trial checkpoint dir
        trial_ckpt_dir = os.path.join(checkpoint_dir_BO, f"trial_{trial.number:03d}")
        os.makedirs(trial_ckpt_dir, exist_ok=True)
        
        # --- pretty print trial banner and params, also save as CSV ---
        print("\n" + "="*80)
        print(f"Optuna Trial {trial.number + 1} / {n_trials}")
        params_print = {
            "convlstm_filters": (f1, f2, f3),
            "lstm_units": (l1, l2_),
            "dense_units": d_units,
            "l2_reg": l2_reg,
            "lr": lr,
            "dropout": drop,
        }
        try:
            param_df = pd.DataFrame.from_dict(params_print, orient="index", columns=["value"])
            print(param_df)
            param_df.to_csv(os.path.join(trial_ckpt_dir, "params_table.csv"))
        except Exception:
            # Fallback print if pandas table fails
            print("Params:", params_print)
        print("="*80 + "\n")

        model = build_model_with_cbam_weighted(
            X_train_shape=X_train_norm.shape,
            sequence_length=sequence_length,
            num_stations=num_stations,
            cluster_masks_tensor=cluster_masks_tensor,
            convlstm_filters=(f1, f2, f3),
            lstm_units=(l1, l2_),
            dense_units=d_units,
            l2_reg=l2_reg,
            dropout_rate=drop,
            lr=lr,
            return_attention_in_cbam3=True
        )

        # callbacks
        es_cb = EarlyStopping(monitor=es_monitor, patience=early_stopping,
                              restore_best_weights=es_restore_best, verbose=1)
        rlrop = ReduceLROnPlateau(monitor=es_monitor, factor=0.5, patience=max(1, early_stopping//2),
                                  min_lr=1e-6, verbose=1)

        custom_ckpt = CustomModelCheckpoint(
            filepath=os.path.join(trial_ckpt_dir, 'best_model.h5'),
            monitor=es_monitor,
            mode='min',
            save_best_only=True,
            best_val_loss=float('inf'),
            training_data=[X_val, M_val, WL_val],  # use val to extract attention
            batch_size=batch_size
        )

        hist = model.fit(
            [X_trn, M_trn, WL_trn],
            Y_trn,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=([X_val, M_val, WL_val], Y_val),
            verbose=2,
            callbacks=[es_cb, rlrop, custom_ckpt]
        )

        # record best metric
        best = np.min(hist.history[es_monitor])
        print(f"[Trial {trial.number}] Best {es_monitor}: {best:.6f}")

        # persist best_val_loss and hyperparams
        with open(os.path.join(trial_ckpt_dir, "best_val_loss.txt"), "w") as f:
            f.write(str(best))
        with open(os.path.join(trial_ckpt_dir, "hparams.txt"), "w") as f:
            f.write(str({
                "convlstm_filters": (f1, f2, f3),
                "lstm_units": (l1, l2_),
                "dense_units": d_units,
                "l2_reg": l2_reg,
                "lr": lr,
                "dropout": drop
            }))

        # -------- OPTIONAL VISUALIZATION FOR THIS TRIAL (best model) --------
        if visualize:
            viz_dir = os.path.join(trial_ckpt_dir, "viz")
            os.makedirs(viz_dir, exist_ok=True)

            # load best model saved by CustomModelCheckpoint
            best_model = tf.keras.models.load_model(
                os.path.join(trial_ckpt_dir, 'best_model.h5'),
                custom_objects={
                    'masked_mse': masked_mse,
                    'StandardCBAM': StandardCBAM,
                    'CustomAttentionLayer': CustomAttentionLayer,
                    'ClusterBasedApplication': ClusterBasedApplication,
                    'TrueLoss': TrueLoss
                }
            )

            # build attention extractor for CBAM_3 spatial attention
            attention_layer = best_model.get_layer('CBAM_3')
            spatial_attention_map = attention_layer.output[1]
            attention_model = Model(inputs=best_model.input, outputs=spatial_attention_map)

            # take first validation sample
            xs = X_val[:1]
            ms = M_val[:1]
            wls = WL_val[:1]
            y_true_sample = Y_val[:1]  # shape (1, H, W)

            # predict
            y_pred_sample = best_model.predict([xs, ms, wls], verbose=0)  # (1, H, W)
            attn_sample   = attention_model.predict([xs, ms, wls], verbose=0)  # (1, H, W, 1)

            y_true_2d = y_true_sample[0]
            y_pred_2d = y_pred_sample[0]
            attn_2d   = attn_sample[0, :, :, 0] * ms[0, -1, :, :, 0]  # mask valid cells

            # compute common color scale for depth maps
            vmin = float(min(np.min(y_true_2d), np.min(y_pred_2d)))
            vmax = float(max(np.max(y_true_2d), np.max(y_pred_2d)))

            # save prediction vs ground truth
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            plt.title('Actual Flood Depth (val[0])')
            plt.imshow(y_true_2d, cmap='viridis', vmin=vmin, vmax=vmax)
            plt.colorbar(); plt.axis('off')
            plt.subplot(1, 2, 2)
            plt.title('Predicted Flood Depth (val[0])')
            plt.imshow(y_pred_2d, cmap='viridis', vmin=vmin, vmax=vmax)
            plt.colorbar(); plt.axis('off')
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'pred_vs_actual_val0.png'), dpi=300, bbox_inches='tight')
            plt.close()

            # save spatial attention map
            plt.figure(figsize=(6, 6))
            plt.title('Spatial Attention Map (val[0])')
            plt.imshow(attn_2d, cmap='viridis')
            plt.colorbar(); plt.axis('off')
            plt.savefig(os.path.join(viz_dir, 'spatial_attention_val0.png'), dpi=300, bbox_inches='tight')
            plt.close()

        return float(best)

    study = optuna.create_study(direction="minimize", study_name=study_name)
    study.optimize(objective, n_trials=n_trials)
    
    # ---- create & save study summary table ----
    try:
        rows = []
        for t in study.trials:
            row = {"trial": t.number, "value": t.value, "state": t.state.name}
            row.update(t.params)
            rows.append(row)
        summary_df = pd.DataFrame(rows)
        summary_path_csv = os.path.join(checkpoint_dir_BO, "study_summary.csv")
        summary_df.to_csv(summary_path_csv, index=False)
        print("\nStudy summary saved to:", summary_path_csv)
        if len(summary_df) > 0 and "value" in summary_df.columns:
            print("\nTop 5 trials by objective:")
            print(summary_df.sort_values("value", ascending=True).head(5))
    except Exception as e:
        print("Could not write study summary table:", e)

    # summary dictionary
    return {
        "best_trial": study.best_trial.number,
        "best_value": study.best_value,
        "best_params": study.best_trial.params,
        "checkpoint_dir_BO": checkpoint_dir_BO
    }
