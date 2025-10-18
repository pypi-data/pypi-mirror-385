# mobius_activations/tensorflow.py
import tensorflow as tf
from tensorflow.keras import layers

class MobiusActivation(layers.Layer):
    """

    - 'projection' mode (default): A specialist 3D operator requiring an input of 3 channels.
    - 'grouped' mode: A powerful high-dimensional layer that applies the Möbius 
      transformation in parallel to groups of 3 channels.
    """

    def __init__(self, in_features=3, mode='projection', realities=None, learnable=False, axes=['x', 'y', 'z'], **kwargs):
        super().__init__(**kwargs)

        self.in_features = in_features
        self.mode = mode
        self.learnable = learnable
        self.axes = axes
        self.fixed_realities = realities

        # Perform validation on the instance attributes.
        if self.learnable:
            if not self.axes:
                raise ValueError("The 'axes' argument must be provided in learnable mode.")
        else:
            if self.fixed_realities is None:
                raise ValueError("The 'realities' argument must be provided when learnable=False.")


        if self.mode == 'projection':
            if self.in_features != 3:
                raise ValueError("In 'projection' mode, in_features must be 3.")
            self.num_groups = 1
        elif self.mode == 'grouped':
            if self.in_features % 3 != 0:
                raise ValueError(f"In 'grouped' mode, in_features must be divisible by 3, but got {in_features}")
            self.num_groups = self.in_features // 3
        else:
            raise ValueError(f"Invalid mode '{self.mode}'. Choose 'projection' or 'grouped'.")
    
    def build(self, input_shape):
        # Create the internal Möbius blocks
        self.mobius_blocks = [
            _MobiusCore(
                realities=self.fixed_realities, 
                learnable=self.learnable, 
                axes=self.axes,
                name=f'mobius_core_{i}'
            ) for i in range(self.num_groups)
        ]
        super().build(input_shape)

    def call(self, x):
        if self.mode == 'projection':
            return self.mobius_blocks[0](x)
            
        elif self.mode == 'grouped':
            x_chunks = tf.split(x, num_or_size_splits=self.num_groups, axis=1)
            output_chunks = []
            for i in range(self.num_groups):
                transformed_chunk = self.mobius_blocks[i](x_chunks[i])
                output_chunks.append(transformed_chunk)
            return tf.concat(output_chunks, axis=1)

# --- Internal Core Class for TensorFlow ---
class _MobiusCore(layers.Layer):
    def __init__(self, realities, learnable, axes, **kwargs):
        super().__init__(**kwargs)
        self.learnable = learnable
        self.axes_config = axes
        self.fixed_realities = realities
        self._rotation_functions = {'x': self._rotate_x, 'y': self._rotate_y, 'z': self._rotate_z}
        
        if not self.learnable and self.fixed_realities is None:
            raise ValueError("`realities` must be provided when learnable=False.")

    def build(self, input_shape):
        if self.learnable:
            self.k_params = []
            self.w_params = []
            for axis in self.axes_config:
                self.k_params.append(self.add_weight(name=f'k_{axis}', shape=(1,), initializer='random_uniform', trainable=True))
                self.w_params.append(self.add_weight(name=f'w_{axis}', shape=(1,), initializer='ones', trainable=True))
        super().build(input_shape)

    def _rotate_z(self, z, k):
        mag=tf.linalg.norm(z,axis=1,keepdims=True)+1e-8;theta=k*mag;cos_t,sin_t=tf.cos(theta),tf.sin(theta)
        return tf.concat([z[:,0:1]*cos_t-z[:,1:2]*sin_t,z[:,0:1]*sin_t+z[:,1:2]*cos_t,z[:,2:3]],axis=1)
    def _rotate_y(self, z, k):
        mag=tf.linalg.norm(z,axis=1,keepdims=True)+1e-8;theta=k*mag;cos_t,sin_t=tf.cos(theta),tf.sin(theta)
        return tf.concat([z[:,0:1]*cos_t+z[:,2:3]*sin_t,z[:,1:2],-z[:,0:1]*sin_t+z[:,2:3]*cos_t],axis=1)
    def _rotate_x(self, z, k):
        mag=tf.linalg.norm(z,axis=1,keepdims=True)+1e-8;theta=k*mag;cos_t,sin_t=tf.cos(theta),tf.sin(theta)
        return tf.concat([z[:,0:1],z[:,1:2]*cos_t-z[:,2:3]*sin_t,z[:,1:2]*sin_t+z[:,2:3]*cos_t],axis=1)

    def call(self, z):
        tf.Assert(tf.equal(tf.shape(z)[1], 3), [f"Internal error: _MobiusCore expects 3 channels, but got {tf.shape(z)[1]}"])
        
        if self.learnable:
            realities_to_use = [{'axis': axis, 'k': self.k_params[i], 'w': self.w_params[i]} for i, axis in enumerate(self.axes_config)]
        else:
            realities_to_use = self.fixed_realities
            
        total_activation = tf.zeros_like(z)
        for reality in realities_to_use:
            rotation_func = self._rotation_functions[reality['axis']]
            transformed_z = rotation_func(z, reality['k'])
            total_activation += reality['w'] * transformed_z
        return total_activation



class MobiusOptimizer(tf.keras.optimizers.Optimizer):

    """
    MöbiusOptimizer:  optimizer that uses an orbital component to navigate
    the loss landscape, inspired by the geometric principles of the Möbius strip.

    This optimizer is designed to better escape saddle points and find wider, more
    robust minima by exploring the space via a spiraling descent.
    """
    def __init__(self, learning_rate=1e-3, twist_rate=0.1, beta_1=0.9, epsilon=1e-8, name="MobiusOptimizer", **kwargs):
        super().__init__(name, **kwargs)
        self._set_hyper('learning_rate', learning_rate)
        self._set_hyper('twist_rate', twist_rate)
        self._set_hyper('beta_1', beta_1)
        self._set_hyper('epsilon', epsilon)

    def _create_slots(self, var_list):
        # Create a slot for the first moment (momentum)
        for var in var_list:
            self.add_slot(var, 'm')

    def _resource_apply_dense(self, grad, var):
        var_dtype = var.dtype.base_dtype
        lr = self._get_hyper('learning_rate', var_dtype)
        twist_rate = self._get_hyper('twist_rate', var_dtype)
        beta_1 = self._get_hyper('beta_1', var_dtype)
        epsilon = self._get_hyper('epsilon', var_dtype)
        
        # Get the momentum slot
        m = self.get_slot(var, 'm')
        
        # Update momentum
        m_new = m * beta_1 + grad * (1 - beta_1)

        # --- Core Möbius Logic ---
        grad_flat = tf.reshape(grad, [-1])
        m_new_flat = tf.reshape(m_new, [-1])
        
        num_elements = tf.shape(grad_flat)[0]
        num_groups = num_elements // 3
        
        orbital_step = tf.zeros_like(grad_flat)
        
        if num_groups > 0:
            grad_groups = tf.reshape(grad_flat[:num_groups * 3], [-1, 3])
            m_new_groups = tf.reshape(m_new_flat[:num_groups * 3], [-1, 3])
            
            # The "twist"
            cross_product = tf.linalg.cross(grad_groups, m_new_groups)
            orbital_update_part = tf.reshape(cross_product, [-1])
            # Pad with zeros for the remainder part
            orbital_step = tf.concat([orbital_update_part, tf.zeros(num_elements - num_groups * 3, dtype=var_dtype)], axis=0)
        
        # Final update direction
        update_direction = m_new + twist_rate * tf.reshape(orbital_step, tf.shape(grad))
        
        # Apply update to the variable
        var_update = var.assign_sub(lr * update_direction, use_locking=self._use_locking)
        
        # Update the momentum state
        m_update = m.assign(m_new, use_locking=self._use_locking)

        return tf.group(*[var_update, m_update])

    def get_config(self):
        config = super().get_config()
        config.update({
            'learning_rate': self._serialize_hyperparameter('learning_rate'),
            'twist_rate': self._serialize_hyperparameter('twist_rate'),
            'beta_1': self._serialize_hyperparameter('beta_1'),
            'epsilon': self._serialize_hyperparameter('epsilon'),
        })
        return config


