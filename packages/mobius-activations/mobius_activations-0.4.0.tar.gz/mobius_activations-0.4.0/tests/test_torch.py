# In tests/test_torch.py

import torch
import torch.nn as nn
import pytest

# Import your custom activation from the package
from mobius_activations.torch import MobiusActivation

# ==============================================================================
# 1. Unit Tests: Testing the layer in isolation
# ==============================================================================

def test_initialization_fixed_projection():
    """Tests that the layer initializes correctly in fixed projection mode."""
    realities = [{'axis': 'x', 'k': 1.0, 'w': 1.0}]
    # UPDATED: 'projection' mode is the default, but we'll be explicit.
    layer = MobiusActivation(realities=realities, mode='projection')
    assert layer.mode == 'projection'
    assert len(layer.mobius_blocks) == 1
    assert layer.mobius_blocks[0].fixed_realities is not None

def test_initialization_learnable_grouped():
    """Tests that the layer initializes correctly in learnable grouped mode."""
    # UPDATED: Test the 'grouped' mode with a valid number of features.
    layer = MobiusActivation(in_features=6, mode='grouped', learnable=True, axes=['x', 'z'])
    assert layer.mode == 'grouped'
    assert len(layer.mobius_blocks) == 2 # 6 features / 3 = 2 groups
    # UPDATED: Check the parameters inside the first internal block.
    assert layer.mobius_blocks[0].learnable
    assert len(layer.mobius_blocks[0].k_params) == 2
    assert len(layer.mobius_blocks[0].w_params) == 2

def test_initialization_errors():
    """Tests that the layer raises errors for invalid configurations."""
    # Should fail if learnable=False and no realities are provided
    with pytest.raises(ValueError):
        MobiusActivation(learnable=False)
    
    # Should fail if in grouped mode and in_features is not divisible by 3
    with pytest.raises(ValueError):
        MobiusActivation(in_features=5, mode='grouped')
        
    # Should fail in projection mode if in_features is not 3
    with pytest.raises(ValueError):
        MobiusActivation(in_features=4, mode='projection')

def test_shape_integrity_grouped():
    """Tests that the output shape is always the same as the input shape in grouped mode."""
    # UPDATED: Test with a high-dimensional input for grouped mode.
    layer = MobiusActivation(in_features=12, mode='grouped', learnable=True)
    # Input is (Batch Size, Features) -> (16, 12)
    input_tensor = torch.randn(16, 12)
    output_tensor = layer(input_tensor)
    assert input_tensor.shape == output_tensor.shape

# ==============================================================================
# 2. Integration Tests: Testing within a PyTorch model
# ==============================================================================

def test_pytorch_integration_and_gradients_grouped():
    """
    Tests if the grouped layer works in nn.Sequential and that gradients flow
    through both the model weights and the learnable reality parameters.
    """
    torch.manual_seed(42)

    model = nn.Sequential(
        nn.Linear(10, 6),
        # UPDATED: Use the final, most common configuration.
        MobiusActivation(in_features=6, mode='grouped', learnable=True, axes=['x', 'y']),
        nn.Linear(6, 1)
    )
    
    input_data = torch.randn(4, 10)
    target = torch.randn(4, 1)
    
    # UPDATED: Access the parameters from the internal blocks.
    mobius_layer = model[1]
    first_internal_block = mobius_layer.mobius_blocks[0]
    
    assert first_internal_block.k_params[0].requires_grad
    assert first_internal_block.w_params[0].requires_grad
    
    # Perform a backward pass
    output = model(input_data)
    loss = nn.MSELoss()(output, target)
    loss.backward()
    
    # Assert that gradients have been computed for all parameters
    assert model[0].weight.grad is not None
    assert first_internal_block.k_params[0].grad is not None
    assert first_internal_block.w_params[0].grad is not None
    assert model[2].weight.grad is not None
    print("\nIntegration Test Passed: Gradients flowed correctly.")

# ==============================================================================
# 3. Functional Tests: Formalizing our successful experiments
# ==============================================================================

def generate_spiral_data(n_points=200):
    """A smaller, faster version of the spiral generator for testing."""
    # (This function is perfect, no changes needed)
    torch.manual_seed(42); n=n_points//2; theta=torch.sqrt(torch.rand(n))*3*torch.pi
    r_a=2*theta+torch.pi; data_a=torch.stack([torch.cos(theta)*r_a,torch.sin(theta)*r_a],1)
    r_b=-2*theta-torch.pi; data_b=torch.stack([torch.cos(theta)*r_b,torch.sin(theta)*r_b],1)
    X=torch.cat([data_a,data_b],0); y=torch.cat([torch.zeros(n),torch.ones(n)],0).view(-1,1)
    return X,y

def test_functional_spiral_solver():
    """

    Tests if a model with the learnable activation can achieve high accuracy
    on the spiral problem. This codifies our experiment into a pass/fail test.
    """
    torch.manual_seed(42)
    X_train, y_train = generate_spiral_data()

    # UPDATED: Use the final architecture that is known to work.
    # We use 'projection' mode here because it's a simple 2D problem.
    model = nn.Sequential(
        nn.Linear(2, 3),
        nn.BatchNorm1d(3),
        MobiusActivation(mode='projection', learnable=True, axes=['x','y','z']),
        nn.Linear(3, 1)
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.BCEWithLogitsLoss()

    # Train for a fixed number of epochs
    for _ in range(500):
        optimizer.zero_grad()
        output = model(X_train)
        loss = loss_fn(output, y_train)
        loss.backward()
        optimizer.step()

    # Evaluate the final accuracy
    with torch.no_grad():
        preds = torch.sigmoid(model(X_train)) > 0.5
        accuracy = (preds.float() == y_train).float().mean()

    print(f"\nFunctional Spiral Test Final Accuracy: {accuracy.item():.4f}")
    # Assert that the accuracy is very high, proving the model learned
    assert accuracy > 0.95
