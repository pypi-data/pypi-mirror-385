"""
Keras layers and blocks for Cb_FloodDy (CBAM + simple temporal attention)
"""
from __future__ import annotations
from typing import Optional
import tensorflow as tf
from tensorflow.keras.layers import (
    Layer, Dense, GlobalAveragePooling2D, GlobalMaxPooling2D, Conv2D, Multiply, Add, Activation,
    GlobalAveragePooling1D, GlobalMaxPooling1D, Conv1D, Softmax
)

__all__ = ["cbam_block2d", "cbam_block1d", "TemporalAttention1D"]

def cbam_block2d(x, reduction: int = 8, spatial_kernel: int = 7, name: Optional[str] = None):
    ch = x.shape[-1]
    avg_pool = GlobalAveragePooling2D(name=None if not name else name + "_gap")(x)
    max_pool = GlobalMaxPooling2D(name=None if not name else name + "_gmp")(x)
    shared_mlp = tf.keras.Sequential([
        Dense(ch // reduction, activation="relu"),
        Dense(ch, activation="sigmoid")
    ])
    ca = Add()([shared_mlp(avg_pool), shared_mlp(max_pool)])
    ca = Activation("sigmoid", name=None if not name else name + "_channel_sig")(ca)
    ca = tf.reshape(ca, (-1, 1, 1, ch))
    x = Multiply(name=None if not name else name + "_channel_mul")([x, ca])
    avg_pool = tf.reduce_mean(x, axis=-1, keepdims=True)
    max_pool = tf.reduce_max(x, axis=-1, keepdims=True)
    concat = tf.concat([avg_pool, max_pool], axis=-1)
    sa = Conv2D(filters=1, kernel_size=spatial_kernel, padding="same", activation="sigmoid",
                name=None if not name else name + "_spatial_conv")(concat)
    x = Multiply(name=None if not name else name + "_spatial_mul")([x, sa])
    return x

def cbam_block1d(x, reduction: int = 8, spatial_kernel: int = 7, name: Optional[str] = None):
    ch = x.shape[-1]
    avg_pool = GlobalAveragePooling1D(name=None if not name else name + "_gap")(x)
    max_pool = GlobalMaxPooling1D(name=None if not name else name + "_gmp")(x)
    shared_mlp = tf.keras.Sequential([
        Dense(ch // reduction, activation="relu"),
        Dense(ch, activation="sigmoid")
    ])
    ca = Add()([shared_mlp(avg_pool), shared_mlp(max_pool)])
    ca = Activation("sigmoid", name=None if not name else name + "_channel_sig")(ca)
    ca = tf.reshape(ca, (-1, 1, ch))
    x = Multiply(name=None if not name else name + "_channel_mul")([x, ca])
    avg_pool = tf.reduce_mean(x, axis=-1, keepdims=True)
    max_pool = tf.reduce_max(x, axis=-1, keepdims=True)
    concat = tf.concat([avg_pool, max_pool], axis=-1)
    sa = Conv1D(filters=1, kernel_size=spatial_kernel, padding="same", activation="sigmoid",
                name=None if not name else name + "_spatial_conv")(concat)
    x = Multiply(name=None if not name else name + "_spatial_mul")([x, sa])
    return x

class TemporalAttention1D(Layer):
    """Applies a learnable attention over the time axis for (batch, timesteps, features)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dense = Dense(1)
        self.softmax = Softmax(axis=1)

    def call(self, inputs):
        scores = self.dense(inputs)           # (B, T, 1)
        weights = self.softmax(scores)        # (B, T, 1)
        context = tf.reduce_sum(inputs * weights, axis=1)  # (B, F)
        return context

    def get_config(self):
        base = super().get_config()
        return base
