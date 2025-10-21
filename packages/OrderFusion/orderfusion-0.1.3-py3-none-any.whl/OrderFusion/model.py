import os
import numpy as np
import random

import tensorflow as tf
from tensorflow.keras.layers import MultiHeadAttention, GlobalAveragePooling1D, Dense, Input, Add, Subtract, Lambda, Layer
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import LearningRateScheduler, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import custom_object_scope
from tensorflow.keras.saving import register_keras_serializable
#from keras.saving import register_keras_serializable

def set_random_seed(seed_value):

    # set random seed for reproducibility
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    np.random.seed(seed_value)
    random.seed(seed_value)
    tf.random.set_seed(seed_value)


def HierarchicalQuantileHeadQ50(shared_representation, quantiles):

    # Sort quantiles and find the index of the median
    sorted_quantiles = sorted(quantiles)
    median_index = sorted_quantiles.index(50)

    # Start with the median quantile
    output_median = Dense(1, name='q50_label')(shared_representation)
    outputs = {f'q50_label': output_median}
    
    # Process quantiles above the median
    prev_output = output_median
    for q in sorted_quantiles[median_index + 1:]:
        residual = Dense(1)(shared_representation)
        residual = Lambda(tf.nn.relu)(residual)
        output = Add(name=f'q{q:02}_label')([prev_output, residual])
        outputs[f'q{q:02}_label'] = output
        prev_output = output  

    # Process quantiles below the median in reverse order
    prev_output = output_median
    for q in reversed(sorted_quantiles[:median_index]):
        residual = Dense(1)(shared_representation)
        residual = Lambda(tf.nn.relu)(residual)
        output = Subtract(name=f'q{q:02}_label')([prev_output, residual])
        outputs[f'q{q:02}_label'] = output
        prev_output = output 
    
    return [outputs[f'q{q:02}_label'] for q in quantiles]


#from keras.saving import register_keras_serializable

@register_keras_serializable()
class TimeStepMask(Layer):
    def __init__(self, pad_value=10000.0, **kwargs):
        super().__init__(**kwargs)
        self.pad_value = pad_value

    def call(self, x):
        # x: (batch, T, F)
        mask = tf.reduce_any(tf.not_equal(x, self.pad_value), axis=-1, keepdims=True)
        return tf.cast(mask, tf.float32)  # (batch, T, 1)
    

@register_keras_serializable()
class TemporalDecayMask(Layer):
    def __init__(self, cutoff_len=1, **kwargs):
        """
        cutoff_len: int, controls the number of recent time steps to keep.
                     The mask keeps the last cutoff_len steps as 1, rest 0.
        """
        super().__init__(**kwargs)
        self.cutoff_len = cutoff_len

    def call(self, x):
        """
        x: Tensor of shape (B, T, F) — only shape[1] (T) is used
        returns: Binary mask of shape (B, T, 1)
        """
        B = tf.shape(x)[0]
        T = tf.shape(x)[1]

        # Number of timesteps to keep
        cutoff_len = tf.minimum(T, self.cutoff_len)

        # Construct [0, ..., 0, 1, ..., 1] where last `cutoff_len` entries are 1
        mask_tail = tf.ones([cutoff_len], dtype=tf.float32)
        mask_head = tf.zeros([T - cutoff_len], dtype=tf.float32)
        mask_1d = tf.concat([mask_head, mask_tail], axis=0)  # (T,)
        mask_3d = tf.reshape(mask_1d, [1, T, 1])              # (1, T, 1)

        # Broadcast across batch
        return tf.tile(mask_3d, [B, 1, 1])  # (B, T, 1)


def Iterative_Fusion(input_buy, input_sell, hidden_dim, order, num_heads, mask_buy, mask_sell):

    masked_cross_attn_b = input_buy
    masked_cross_attn_s = input_sell

    for _ in range(order):

        # cross-attention + mask
        cross_attn_b = MultiHeadAttention(num_heads=num_heads, key_dim=hidden_dim // num_heads)(query=masked_cross_attn_b,  key=masked_cross_attn_s, value=masked_cross_attn_s)
        cross_attn_s = MultiHeadAttention(num_heads=num_heads, key_dim=hidden_dim // num_heads)(query=masked_cross_attn_s, key=masked_cross_attn_b, value=masked_cross_attn_b)

        masked_cross_attn_b = cross_attn_b * mask_buy
        masked_cross_attn_s = cross_attn_s * mask_sell
        
    return masked_cross_attn_b, masked_cross_attn_s

    
def OrderFusion(hidden_dim, max_degree, num_heads, input_shape, quantiles, cutoff_len, pad_value=10000.0):
    model_input = Input(shape=input_shape, name='input')
    raw_buy  = model_input[..., 0]  # (B, T, F)
    raw_sell = model_input[..., 1]

    decay_mask = TemporalDecayMask(cutoff_len)(raw_buy)  # or raw_sell, just to get the shape (B, T, 1)

    binary_mask_buy  = TimeStepMask(pad_value)(raw_buy)      # shape (B, T, 1)
    binary_mask_sell = TimeStepMask(pad_value)(raw_sell)     # shape (B, T, 1)

    # element-wise mask multiplication
    mask_buy  = binary_mask_buy  * decay_mask                # shape (B, T, 1)
    mask_sell = binary_mask_sell * decay_mask                # shape (B, T, 1)

    # broadcasted elementwise multiplication
    out_buy  = raw_buy  * mask_buy
    out_sell = raw_sell * mask_sell

    # Collect base + residuals in a list
    buy_orders  = []
    sell_orders = []

    for order in range(1, max_degree + 1):
        out_buy_k, out_sell_k = Iterative_Fusion(out_buy, out_sell, hidden_dim, order, num_heads, mask_buy, mask_sell)
        buy_orders.append(out_buy_k)
        sell_orders.append(out_sell_k)

    # Residual addition for all orders
    if buy_orders:
        out_buy  = Add(name=f"buy_residual_sum_order") (buy_orders)

    if sell_orders:
        out_sell = Add(name=f"sell_residual_sum_order")(sell_orders)

    # Compute weighted average representation
    out_buy = GlobalAveragePooling1D()(out_buy)
    out_sell = GlobalAveragePooling1D()(out_sell)

    rep = Add()([out_buy, out_sell])
    outputs = HierarchicalQuantileHeadQ50(rep, quantiles)

    return Model(inputs=model_input, outputs=outputs)


def quantile_loss(q, name):
    def loss(y_true, y_pred):
        e = y_true - y_pred
        return tf.reduce_mean(tf.maximum(q * e, (q - 1) * e))
    loss.__name__ = f'{name}_label'
    return loss


def lr_schedule(epoch):

    # decay learning rate every 10 epochs
    initial_lr = 4e-3
    decay_factor = 0.95
    decay_interval = 10
    
    num_decays = epoch // decay_interval
    return initial_lr * (decay_factor ** num_decays)


def select_model(target_model, hidden_dim, max_degree, num_heads, input_shape, quantiles, cutoff_len):

    if target_model == 'OrderFusion':
            model = OrderFusion(hidden_dim, max_degree, num_heads, input_shape, quantiles, cutoff_len)

    else:
        raise ValueError(f"Unknown target_model: {target_model}")

    return model


def optimize_model(X_train, y_train, X_val, y_val, exp_setup):

    country, resolution, indice, hidden_dim, max_degree, num_heads, epoch, batch_size, save_path, target_model, quantiles, cutoff_len, show_progress_bar = exp_setup
    input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3])
    model = select_model(target_model, hidden_dim, max_degree, num_heads, input_shape, quantiles, cutoff_len)
    
    # Generate y_train_dict and y_val_dict
    y_train_dict = {f'q{q:02}_label': y_train for q in quantiles}
    y_val_dict = {f'q{q:02}_label': y_val for q in quantiles}
    quantiles_dict = {f'q{q:02}': q / 100 for q in quantiles}

    # Define quantile loss
    quantile_losses = {}
    for name, q in quantiles_dict.items():
        loss_name = f'{name}_label'
        quantile_losses[loss_name] = quantile_loss(q, name)

    model.compile(optimizer=Adam(learning_rate=1e-3), loss=quantile_losses)
    lr_scheduler = LearningRateScheduler(lr_schedule)

    # Count model params
    model_paras_count = model.count_params()
    print(f"paras: {model_paras_count}")

    # Validate model
    checkpoint_path = os.path.join(f"{save_path}Model", f"{target_model}_{country}_{resolution}_{indice}.keras")
    checkpoint_callback = ModelCheckpoint(checkpoint_path,
                                          monitor='val_loss',
                                          save_freq="epoch",
                                          save_best_only=True,
                                          mode='min',
                                          verbose=show_progress_bar)
    
    history = model.fit(X_train, y_train_dict, 
                        epochs=epoch, verbose=0,
                        validation_data=(X_val, y_val_dict),
                        callbacks=[checkpoint_callback, lr_scheduler],
                        batch_size=batch_size)

    # Load the best model with lowest val loss
    custom_objects = {f'{name}_label': quantile_loss(q, name) for name, q in quantiles_dict.items()}
    with custom_object_scope(custom_objects):
        best_model = load_model(checkpoint_path, custom_objects=custom_objects)

    return best_model, history.history, model_paras_count

