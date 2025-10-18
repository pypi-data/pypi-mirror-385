# mobius_activations/visualize.py

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def visualize_neuron_state(mobius_activation, point, num_sphere_points=500):
    """
    Creates a comprehensive dashboard visualizing the state of a MobiusActivation neuron.

    It shows the global transformation, the conceptual state on the Möbius strip,
    and the local gradient effect at the specified input point.

    Args:
        mobius_activation: An instantiated MobiusActivation object.
        point (list or np.ndarray): A 3D point, e.g., [1.5, 1.0, 0.5].
        num_sphere_points (int): Number of points to sample for the global view.
    """
    # --- Framework Agnostic Setup ---
    framework = 'numpy'
    try:
        import torch
        if isinstance(mobius_activation, torch.nn.Module):
            framework = 'torch'
    except ImportError: pass

    try:
        import tensorflow as tf
        if isinstance(mobius_activation, tf.keras.layers.Layer):
            framework = 'tensorflow'
    except ImportError: pass
    
    # --- Data Preparation ---
    p_np = np.array(point, dtype=np.float32).reshape(1, 3)
    
    # --- Create the Figure ---
    fig = plt.figure(figsize=(24, 8))
    fig.suptitle(f"Möbius Neuron State at Input Point z = {np.round(p_np[0], 2)}", fontsize=16)

    # ===================================================================
    # Panel 1: Global Transformation (The Vortex)
    # ===================================================================
    ax1 = fig.add_subplot(1, 3, 1, projection='3d')
    
    # Generate sphere points
    golden_ratio = (1 + 5**0.5) / 2
    i = np.arange(0, num_sphere_points)
    theta_sphere = 2 * np.pi * i / golden_ratio
    phi = np.arccos(1 - 2 * (i + 0.5) / num_sphere_points)
    radius = np.linalg.norm(p_np) # Create a test sphere with the same radius as our point
    x_in = radius * np.sin(phi) * np.cos(theta_sphere)
    y_in = radius * np.sin(phi) * np.sin(theta_sphere)
    z_in = radius * np.cos(phi)
    sphere_points = np.vstack((x_in, y_in, z_in)).T
    
    # Pass sphere points and the single point through the activation
    if framework == 'torch':
        with torch.no_grad():
            sphere_torch = torch.from_numpy(sphere_points.astype(np.float32))
            p_torch = torch.from_numpy(p_np.astype(np.float32))
            transformed_sphere = mobius_activation(sphere_torch).numpy()
            p_prime_np = mobius_activation(p_torch).numpy()[0]
    elif framework == 'tensorflow':
        sphere_tf = tf.constant(sphere_points, dtype=tf.float32)
        p_tf = tf.constant(p_np, dtype=tf.float32)
        transformed_sphere = mobius_activation(sphere_tf).numpy()
        p_prime_np = mobius_activation(p_tf).numpy()[0]
    else: # Fallback for pure numpy if needed
        transformed_sphere = mobius_activation.forward(sphere_points)
        p_prime_np = mobius_activation.forward(p_np)[0]

    colors = sphere_points[:, 0]
    ax1.scatter(transformed_sphere[:, 0], transformed_sphere[:, 1], transformed_sphere[:, 2], c=colors, cmap='viridis', alpha=0.5, s=10)
    ax1.scatter(p_prime_np[0], p_prime_np[1], p_prime_np[2], color='red', s=100, label='Transformed Point F(z)')
    ax1.set_title('1. Global Transformation (Effect on Space)')
    ax1.legend()
    
    # ===================================================================
    # Panel 2: Conceptual State (The Möbius Strip Path)
    # ===================================================================
    ax2 = fig.add_subplot(1, 3, 2, projection='3d')
    
    # Parametrization of the Möbius strip
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(-1, 1, 20)
    u_grid, v_grid = np.meshgrid(u, v)
    X = (1 + 0.5 * v_grid * np.cos(u_grid / 2)) * np.cos(u_grid)
    Y = (1 + 0.5 * v_grid * np.cos(u_grid / 2)) * np.sin(u_grid)
    Z = 0.5 * v_grid * np.sin(u_grid / 2)
    ax2.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.6)
    
    # The key connection: magnitude ||z|| maps to the path along the strip.
    # We use the 'k' from the first reality as a proxy for the path scaling.


    # We access the internal block to get the parameters.
    # We will use the parameters from the FIRST block as a proxy for visualization.
    first_block = mobius_activation.mobius_blocks[0]
    
    # Check if the block is learnable to know where to get the 'k' value from.
    if hasattr(first_block, 'k_params') and first_block.k_params is not None:
        # Learnable Mode: get the detached tensor value
        k_proxy_tensor = first_block.k_params[0].detach()
        if 'torch' in str(type(k_proxy_tensor)): # Check if it's a torch tensor
             k_proxy = k_proxy_tensor.numpy()[0]
        else: # Assume tensorflow
             k_proxy = k_proxy_tensor.numpy()[0]
    else:
        # Fixed Mode: get the value from the dictionary
        k_proxy = first_block.fixed_realities[0]['k']
    
    mag = np.linalg.norm(p_np)
    u_point = (mag * k_proxy) % (2 * np.pi) # Wrap around the strip
    mag = np.linalg.norm(p_np)
    u_point = (mag * k_proxy) % (2 * np.pi) # Wrap around the strip
    
    # Calculate position of the point on the edge of the strip (v=1)
    xp = (1 + 0.5 * 1 * np.cos(u_point / 2)) * np.cos(u_point)
    yp = (1 + 0.5 * 1 * np.cos(u_point / 2)) * np.sin(u_point)
    zp = 0.5 * 1 * np.sin(u_point / 2)
    
    ax2.scatter(xp, yp, zp, color='red', s=150, label=f'Position on Path (||z||={mag:.2f})')
    ax2.set_title('2. Conceptual State (The "Why")')
    ax2.legend()
    
    # ===================================================================
    # Panel 3: Local Gradient Effect (The Jacobian)
    # ===================================================================
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    
    # Basis vectors
    i = np.array([[1.0, 0.0, 0.0]]); j = np.array([[0.0, 1.0, 0.0]]); k = np.array([[0.0, 0.0, 1.0]])
    p_i, p_j, p_k = p_np + i, p_np + j, p_np + k
    batch_input = np.vstack([p_np, p_i, p_j, p_k])
    
    # Pass through activation
    if framework == 'torch':
        with torch.no_grad():
            input_tensor = torch.from_numpy(batch_input.astype(np.float32))
            batch_output = mobius_activation(input_tensor).numpy()
    elif framework == 'tensorflow':
        batch_output = mobius_activation(tf.constant(batch_input, dtype=tf.float32)).numpy()
    else:
        batch_output = mobius_activation.forward(batch_input)
        
    p_prime, p_i_prime, p_j_prime, p_k_prime = batch_output
    i_prime, j_prime, k_prime = p_i_prime - p_prime, p_j_prime - p_prime, p_k_prime - p_prime
    
    # Plot original and transformed bases
    ax3.quiver(p_np[0,0], p_np[0,1], p_np[0,2], i[0,0], i[0,1], i[0,2], color='black', label='Original Basis')
    ax3.quiver(p_np[0,0], p_np[0,1], p_np[0,2], j[0,0], j[0,1], j[0,2], color='black')
    ax3.quiver(p_np[0,0], p_np[0,1], p_np[0,2], k[0,0], k[0,1], k[0,2], color='black')
    
    ax3.quiver(p_prime[0], p_prime[1], p_prime[2], i_prime[0], i_prime[1], i_prime[2], color='red', label='Transformed Basis')
    ax3.quiver(p_prime[0], p_prime[1], p_prime[2], j_prime[0], j_prime[1], j_prime[2], color='red')
    ax3.quiver(p_prime[0], p_prime[1], p_prime[2], k_prime[0], k_prime[1], k_prime[2], color='red')
    
    ax3.set_title('3. Local Gradient Effect (The "How")')
    ax3.legend()

    # --- Finalize and Show ---
    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        if ax != ax2: # Möbius plot has its own scale
            max_range = max(np.linalg.norm(p_np), np.linalg.norm(p_prime)) * 1.8
            ax.set_xlim([-max_range, max_range]); ax.set_ylim([-max_range, max_range]); ax.set_zlim([-max_range, max_range])

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()



def visualize_transformation_flow(
    activation_layer, 
    grid_range=3.0, 
    density=7, 
    num_steps=30,
    ax=None
):
    """
    Generates a 3D plot visualizing the transformation flow field.

    This function shows the path of a grid of points as they are transformed 
    by the provided MobiusActivation layer, illustrating the geometric warp.

    Args:
        activation_layer: The trained MobiusActivation layer to visualize.
        grid_range (float): The extent of the grid (from -range to +range).
        density (int): The number of points along each axis of the grid.
        num_steps (int): The number of interpolation steps for the flow trajectory.
        ax (matplotlib.axes.Axes): An existing 3D matplotlib axes object to plot on.
    """
    #print("Visualizing transformation flow...")

    # --- Step 1: Framework Detection and Parameter Extraction ---
    framework = None
    try:
        import torch
        from .torch import MobiusActivation as MobiusActivationTorch
        if isinstance(activation_layer, MobiusActivationTorch):
            framework = 'torch'
    except ImportError: pass
    
    try:
        import tensorflow as tf
        from .tensorflow import MobiusActivation as MobiusActivationTF
        if isinstance(activation_layer, MobiusActivationTF):
            framework = 'tensorflow'
    except ImportError: pass

    if framework is None:
        raise TypeError("Input must be an instance of a PyTorch or TensorFlow MobiusActivation layer.")

    # We will visualize the FIRST block of any given layer.
    first_block = activation_layer.mobius_blocks[0]
    
    # A robust check for learnability: Does the block have learnable params?
    if hasattr(first_block, 'k_params') and first_block.k_params is not None:
        # LEARNABLE MODE
        if framework == 'torch':
            final_k = [p.detach().numpy() for p in first_block.k_params]
            final_w = [p.detach().numpy() for p in first_block.w_params]
        elif framework == 'tensorflow':
            final_k = [p.numpy() for p in first_block.k_params]
            final_w = [p.numpy() for p in first_block.w_params]
        final_axes = first_block.axes
    else: 
        # FIXED MODE
        final_k = [np.array([r['k']]) for r in first_block.fixed_realities]
        final_w = [np.array([r['w']]) for r in first_block.fixed_realities]
        final_axes = [r['axis'] for r in first_block.fixed_realities]

    # --- Step 2: Define the Visualization Space ---
    x = np.linspace(-grid_range, grid_range, density)
    grid_x, grid_y, grid_z = np.meshgrid(x, x, x)
    initial_points = np.stack([grid_x.ravel(), grid_y.ravel(), grid_z.ravel()], axis=-1).astype(np.float32)

    # --- Step 3: Interpolate the Transformation ---
    flow_trajectories = []
    for alpha in np.linspace(0, 1, num_steps):
        interpolated_realities = []
        for i, axis in enumerate(final_axes):
            # Interpolate k from 0 (identity) to its final value.
            # Interpolate w from 1.0 (identity) to its final value.
            w_interpolated = 1.0 + (final_w[i].item() - 1.0) * alpha
            interpolated_realities.append({
                'axis': axis,
                'k': final_k[i].item() * alpha,
                'w': w_interpolated
            })
        
        # Use a temporary activation layer for the forward pass
        if framework == 'torch':
            temp_activation = MobiusActivationTorch(realities=interpolated_realities)
            with torch.no_grad():
                transformed_points = temp_activation(torch.from_numpy(initial_points)).numpy()
        elif framework == 'tensorflow':
            temp_activation = MobiusActivationTF(realities=interpolated_realities)
            transformed_points = temp_activation(tf.constant(initial_points)).numpy()
        
        flow_trajectories.append(transformed_points)

    flow_trajectories = np.stack(flow_trajectories, axis=1)

    # --- Step 4: Visualize the Flow Field ---
    if ax is None:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title("Flow Field of the Möbius Transformation", fontsize=16)
    
    for i in range(flow_trajectories.shape[0]):
        trajectory = flow_trajectories[i, :, :]
        color_val = (trajectory[0, 2] + grid_range) / (2 * grid_range) # Color by initial Z-height
        ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], color=plt.cm.viridis(color_val), alpha=0.6)

    final_positions = flow_trajectories[:, -1, :]
    ax.scatter(initial_points[:, 0], initial_points[:, 1], initial_points[:, 2], 
               color='blue', s=10, label='Start Positions', depthshade=True)
    ax.scatter(final_positions[:, 0], final_positions[:, 1], final_positions[:, 2], 
               color='red', s=15, label='End Positions', depthshade=True)

    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.legend()
    
    if 'fig' in locals():
        plt.show()


def visualize_optimizer_path(
    start_point=[-4, 3.5], 
    learning_rate=0.1, 
    twist_rate=0.15, 
    num_steps=50,
    ax=None
):
    """
    Generates a 2D plot visualizing the path of the MöbiusOptimizer against a
    standard SGD optimizer on a simple convex loss landscape.

    This function provides a clear, intuitive demonstration of the orbital
    descent unique to the MöbiusOptimizer.

    Args:
        start_point (list or np.ndarray): The starting [x, y] coordinates.
        learning_rate (float): The learning rate for both optimizers.
        twist_rate (float): The strength of the orbital component for the
                              MöbiusOptimizer. A value of 0.0 would make it
                              behave like SGD with momentum.
        num_steps (int): The number of optimization steps to simulate.
        ax (matplotlib.axes.Axes, optional): An existing axes object to plot on.
                                             If None, a new figure is created.
    """
    #print("Visualizing optimizer paths...")

    # --- Step 1: Define a simple loss landscape and its gradient ---
    def loss_function(x, y):
        return x**2 + y**2

    def gradient(x, y):
        return np.array([2 * x, 2 * y])

    # --- Step 2: Simulate the optimizers ---
    # Standard SGD Optimizer
    sgd_path = [np.array(start_point, dtype=float)]
    for _ in range(num_steps):
        grad = gradient(sgd_path[-1][0], sgd_path[-1][1])
        update = -learning_rate * grad
        sgd_path.append(sgd_path[-1] + update)
    sgd_path = np.array(sgd_path)

    # Möbius Optimizer
    mobius_path = [np.array(start_point, dtype=float)]
    for _ in range(num_steps):
        grad = gradient(mobius_path[-1][0], mobius_path[-1][1])
        # Descent component ("gravity")
        descent_step = -learning_rate * grad
        # Orbital component ("twist"), perpendicular to the gradient
        orbital_step = -twist_rate * np.array([-grad[1], grad[0]])
        # The final update is the sum of both forces
        mobius_path.append(mobius_path[-1] + descent_step + orbital_step)
    mobius_path = np.array(mobius_path)
    
    # --- Step 3: Visualize the results ---
    if ax is None:
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111)
        ax.set_title('Optimizer Paths on a Loss Landscape', fontsize=16)
    
    # Create the contour plot
    x_grid = np.linspace(-5, 5, 100)
    y_grid = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = loss_function(X, Y)
    ax.contourf(X, Y, Z, levels=20, cmap='viridis_r', alpha=0.7)

    # Plot the paths
    ax.plot(sgd_path[:, 0], sgd_path[:, 1], 'o-', color='cyan', label='Standard Optimizer (SGD)')
    ax.plot(mobius_path[:, 0], mobius_path[:, 1], 'o-', color='red', label='MöbiusOptimizer')

    # Plot the "Forces" at a few key steps for clarity
    for i in [1, 5, 15]:
        if i < len(mobius_path):
            pos = mobius_path[i]
            grad = gradient(pos[0], pos[1])
            descent_force = -learning_rate * grad
            orbital_force = -twist_rate * np.array([-grad[1], grad[0]])
            if i == 1: # Add labels only for the first set of arrows
                ax.quiver(pos[0], pos[1], descent_force[0], descent_force[1], color='lime', scale=1, label='Descent Force')
                ax.quiver(pos[0], pos[1], orbital_force[0], orbital_force[1], color='magenta', scale=1, label='Orbital Force (Twist)')
            else:
                ax.quiver(pos[0], pos[1], descent_force[0], descent_force[1], color='lime', scale=1)
                ax.quiver(pos[0], pos[1], orbital_force[0], orbital_force[1], color='magenta', scale=1)

    ax.set_xlabel('Weight 1'); ax.set_ylabel('Weight 2')
    ax.legend()
    ax.axis('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    if 'fig' in locals():
        plt.show()
