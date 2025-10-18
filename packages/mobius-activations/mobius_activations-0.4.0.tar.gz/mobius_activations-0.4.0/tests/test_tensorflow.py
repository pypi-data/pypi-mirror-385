#tests/test_tensorflow.py

import tensorflow as tf
from tensorflow.keras import layers, Sequential
import numpy as np
import pytest

# Import your custom activation from the package
from mobius_activations.tensorflow import MobiusActivation

# ==============================================================================
# 1. Unit Tests: Testing the layer in isolation
# ==============================================================================

class TensorFlowUnitTests(tf.test.TestCase):
    
    def test_initialization_fixed_projection(self):
        """Tests that the layer initializes correctly in fixed projection mode."""
        realities = [{'axis': 'x', 'k': 1.0, 'w': 1.0}]
        # UPDATED: Test with the final API
        layer = MobiusActivation(realities=realities, mode='projection')
        self.assertEqual(layer.mode, 'projection')
        self.assertEqual(layer.num_groups, 1)
        self.assertIsNotNone(layer.fixed_realities)

    def test_initialization_learnable_grouped(self):
        """Tests that the layer initializes correctly in learnable grouped mode."""
        # UPDATED: Test with grouped mode
        layer = MobiusActivation(in_features=9, mode='grouped', learnable=True, axes=['x', 'z'])
        self.assertEqual(layer.mode, 'grouped')
        self.assertEqual(layer.num_groups, 3)
        self.assertTrue(layer.learnable)
        self.assertEqual(len(layer.axes), 2)

    def test_initialization_errors(self):
        """Tests that the layer raises errors for invalid configurations."""
        with self.assertRaises(ValueError):
            MobiusActivation(learnable=False)
        with self.assertRaises(ValueError):
            MobiusActivation(in_features=7, mode='grouped')
        with self.assertRaises(ValueError):
            MobiusActivation(in_features=4, mode='projection')

    def test_shape_integrity_grouped(self):
        """Tests that the output shape is always the same as the input shape in grouped mode."""
        # UPDATED: Test with high-dimensional grouped mode
        layer = MobiusActivation(in_features=12, mode='grouped', learnable=True)
        input_tensor = tf.random.normal(shape=(16, 12))
        output_tensor = layer(input_tensor)
        self.assertShapeEqual(input_tensor.numpy(), output_tensor)

# ==============================================================================
# 2. Integration Tests: Testing within a Keras model
# ==============================================================================

class TensorFlowIntegrationTests(tf.test.TestCase):

    def test_keras_integration_and_gradients_grouped(self):
        """
        Tests if the grouped layer works in a Keras Sequential model and that gradients
        flow through all learnable parameters.
        """
        tf.random.set_seed(42)
        model = Sequential([
            layers.Dense(6, input_shape=(10,)),
            # UPDATED: Use the final, most common configuration
            MobiusActivation(in_features=6, mode='grouped', learnable=True, axes=['x', 'y']),
            layers.Dense(1)
        ])
        input_data = tf.random.normal(shape=(4, 10))
        target = tf.random.normal(shape=(4, 1))
        
        with tf.GradientTape() as tape:
            output = model(input_data)
            loss = tf.keras.losses.MeanSquaredError()(target, output)
        
        gradients = tape.gradient(loss, model.trainable_variables)
        
        # Assert that gradients have been computed for all parameters
        self.assertEqual(len(gradients), len(model.trainable_variables))
        for grad in gradients:
            self.assertIsNotNone(grad)
        
        # Get the MobiusActivation layer from the model
        mobius_layer = model.layers[1]
        
        # UPDATED: Get the internal blocks
        self.assertEqual(len(mobius_layer.mobius_blocks), 2) # 6 features = 2 groups
        
        # Check the parameters of the first internal block
        first_internal_block = mobius_layer.mobius_blocks[0]
        self.assertEqual(len(first_internal_block.trainable_variables), 4) # k_x, w_x, k_y, w_y
        
        param_names = [p.name for p in first_internal_block.trainable_variables]
        self.assertTrue(any('k_x' in name for name in param_names))
        self.assertTrue(any('w_y' in name for name in param_names))
        
        print("\nTF Integration Test Passed: Gradients flowed correctly.")
# ==============================================================================
# 3. Functional Tests: Formalizing our successful experiments
# ==============================================================================

def generate_spiral_data(n_points=200):
    """A smaller, faster version of the spiral generator for testing."""
    # (This function is perfect, no changes needed)
    np.random.seed(42); n=n_points//2; theta=np.sqrt(np.random.rand(n))*3*np.pi
    r_a=2*theta+np.pi; data_a=np.array([np.cos(theta)*r_a,np.sin(theta)*r_a]).T
    r_b=-2*theta-np.pi; data_b=np.array([np.cos(theta)*r_b,np.sin(theta)*r_b]).T
    X=np.vstack([data_a,data_b]); y=np.hstack([np.zeros(n),np.ones(n)]).reshape(-1,1)
    return tf.constant(X,dtype=tf.float32),tf.constant(y,dtype=tf.float32)

class TensorFlowFunctionalTests(tf.test.TestCase):

    def test_functional_spiral_solver(self):
        """
        Tests if a Keras model with the learnable activation can achieve high
        accuracy on the spiral problem.
        """
        tf.random.set_seed(42)
        X_train, y_train = generate_spiral_data()

        # UPDATED: Use the final architecture that is known to work
        model = Sequential([
            layers.Input(shape=(2,)),
            layers.Dense(3),
            layers.BatchNormalization(),
            MobiusActivation(mode='projection', learnable=True, axes=['x','y','z']),
            layers.Dense(1, activation='sigmoid')
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
                      loss='binary_crossentropy',
                      metrics=['accuracy'])

        # Train for a fixed number of epochs
        history = model.fit(X_train, y_train, epochs=500, verbose=0)

        # Evaluate the final accuracy
        loss, accuracy = model.evaluate(X_train, y_train, verbose=0)
        
        print(f"\nTF Functional Spiral Test Final Accuracy: {accuracy:.4f}")
        # Assert that the accuracy is very high, proving the model learned
        self.assertGreater(accuracy, 0.95)

# To run tests with pytest, it's helpful to have this at the end
if __name__ == '__main__':
    tf.test.main()
