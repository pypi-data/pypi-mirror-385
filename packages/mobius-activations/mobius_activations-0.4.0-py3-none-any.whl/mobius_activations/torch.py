# mobius_activations/torch.py
import torch
import torch.nn as nn
from torch.optim import Optimizer

class MobiusActivation(nn.Module):
    """
    

    - 'projection' mode (default): A specialist 3D operator requiring an input of 3 channels.
    - 'grouped' mode: A powerful high-dimensional layer that applies the Möbius 
      transformation in parallel to groups of 3 channels.
    """
    def __init__(self, in_features=3, mode='projection', realities=None, learnable=False, axes=['x', 'y', 'z']):
        """
        Initializes the MobiusActivation layer.

        Args:
            in_features (int, optional): The number of input features. Required for 'grouped' mode.
                                         Defaults to 3.
            mode (str, optional): The operational mode: 'projection' or 'grouped'. 
                                  Defaults to 'projection'.
            realities (list, optional): A list of reality dictionaries for fixed mode.
            learnable (bool, optional): If True, the layer will learn its own parameters.
            axes (list, optional): A list of axes for learnable realities.
        """
        super().__init__()
        self.mode = mode
        self.in_features = in_features
        
        if self.mode == 'projection':
            if self.in_features != 3:
                raise ValueError("In 'projection' mode, in_features must be 3.")
            # In projection mode, we have one Möbius block.
            self.mobius_blocks = nn.ModuleList([
                self._create_mobius_block(realities, learnable, axes)
            ])
            
        elif self.mode == 'grouped':
            if self.in_features % 3 != 0:
                raise ValueError(f"In 'grouped' mode, in_features must be divisible by 3, but got {in_features}")
            self.num_groups = self.in_features // 3
            # In grouped mode, we create one block for each parallel group.
            self.mobius_blocks = nn.ModuleList(
                [self._create_mobius_block(realities, learnable, axes) for _ in range(self.num_groups)]
            )
        else:
            raise ValueError(f"Invalid mode '{self.mode}'. Choose 'projection' or 'grouped'.")

    def _create_mobius_block(self, realities, learnable, axes):
        # This is a helper to avoid code duplication. It returns a single
        # MobiusActivation 'core' with its own parameters.

        return _MobiusCore(realities=realities, learnable=learnable, axes=axes)

    def forward(self, x):
        if self.mode == 'projection':
            # Apply the single Möbius block to the 3D input
            return self.mobius_blocks[0](x)
            
        elif self.mode == 'grouped':
            # Split the input tensor into a list of (batch_size, 3) tensors
            x_chunks = torch.split(x, 3, dim=1)
            
            # Process each chunk with its corresponding Möbius block
            output_chunks = []
            for i in range(self.num_groups):
                transformed_chunk = self.mobius_blocks[i](x_chunks[i])
                output_chunks.append(transformed_chunk)
                
            # Concatenate the processed chunks back into a single tensor
            return torch.cat(output_chunks, dim=1)

# --- Internal Core Class ---

class _MobiusCore(nn.Module):
    def __init__(self, realities, learnable, axes):
        super().__init__()
        self.learnable = learnable
        self._rotation_functions = {'x': self._rotate_x, 'y': self._rotate_y, 'z': self._rotate_z}

        if self.learnable:
            self.axes = axes
            num_realities = len(axes)
            self.k_params = nn.ParameterList([nn.Parameter(torch.rand(1)) for _ in range(num_realities)])
            self.w_params = nn.ParameterList([nn.Parameter(torch.ones(1)) for _ in range(num_realities)])
            self.fixed_realities = None
        else:
            if realities is None: raise ValueError("`realities` must be provided when learnable=False.")
            self.fixed_realities = realities
            self.k_params, self.w_params, self.axes = None, None, None
            
    
    def _rotate_z(self, z, k):
        mag = torch.linalg.norm(z, dim=1, keepdim=True) + 1e-8; theta = k * mag
        cos_t, sin_t = torch.cos(theta), torch.sin(theta)
        a = torch.zeros_like(z)
        a[:, 0] = z[:, 0] * cos_t.squeeze() - z[:, 1] * sin_t.squeeze()
        a[:, 1] = z[:, 0] * sin_t.squeeze() + z[:, 1] * cos_t.squeeze()
        a[:, 2] = z[:, 2]; return a
    def _rotate_y(self, z, k):
        mag = torch.linalg.norm(z, dim=1, keepdim=True) + 1e-8; theta = k * mag
        cos_t, sin_t = torch.cos(theta), torch.sin(theta)
        a = torch.zeros_like(z)
        a[:, 0] = z[:, 0] * cos_t.squeeze() + z[:, 2] * sin_t.squeeze()
        a[:, 1] = z[:, 1]
        a[:, 2] = -z[:, 0] * sin_t.squeeze() + z[:, 2] * cos_t.squeeze(); return a
    def _rotate_x(self, z, k):
        mag = torch.linalg.norm(z, dim=1, keepdim=True) + 1e-8; theta = k * mag
        cos_t, sin_t = torch.cos(theta), torch.sin(theta)
        a = torch.zeros_like(z)
        a[:, 0] = z[:, 0]
        a[:, 1] = z[:, 1] * cos_t.squeeze() - z[:, 2] * sin_t.squeeze()
        a[:, 2] = z[:, 1] * sin_t.squeeze() + z[:, 2] * cos_t.squeeze(); return a

    def forward(self, z):
        assert z.shape[1] == 3, f"Internal error: _MobiusCore expects 3 channels, but got {z.shape[1]}"
        
        if self.learnable:
            realities_to_use = [{'axis': axis, 'k': self.k_params[i], 'w': self.w_params[i]} for i, axis in enumerate(self.axes)]
        else:
            realities_to_use = self.fixed_realities

        total_activation = torch.zeros_like(z)
        for reality in realities_to_use:
            rotation_func = self._rotation_functions[reality['axis']]
            transformed_z = rotation_func(z, reality['k'])
            total_activation += reality['w'] * transformed_z
        return total_activation



class MobiusOptimizer(Optimizer):
    """
    MöbiusOptimizer: A  optimizer that uses an orbital component to navigate
    the loss landscape, inspired by the geometric principles of the Möbius strip.

    This optimizer is designed to better escape saddle points and find wider, more
    robust minima by exploring the space via a spiraling descent.
    """
    def __init__(self, params, lr=1e-3, twist_rate=0.1, beta1=0.9, eps=1e-8):
        if not 0.0 <= lr:
            raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= twist_rate:
            raise ValueError(f"Invalid twist rate: {twist_rate}")

        defaults = dict(lr=lr, twist_rate=twist_rate, beta1=beta1, eps=eps)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group['lr']
            twist_rate = group['twist_rate']
            beta1 = group['beta1']
            eps = group['eps']

            for p in group['params']:
                if p.grad is None:
                    continue
                
                grad = p.grad
                if grad.is_sparse:
                    raise RuntimeError('MöbiusOptimizer does not support sparse gradients.')

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    # Exponential moving average of gradient values (momentum)
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                exp_avg = state['exp_avg']
                state['step'] += 1

                # Update momentum (the "history" vector)
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)

                # --- Core Möbius Logic ---
                grad_flat = grad.flatten()
                exp_avg_flat = exp_avg.flatten()
                
                # Process in groups of 3
                num_elements = grad_flat.numel()
                num_groups = num_elements // 3
                
                orbital_step = torch.zeros_like(grad_flat)
                
                if num_groups > 0:
                    grad_groups = grad_flat[:num_groups * 3].view(-1, 3)
                    exp_avg_groups = exp_avg_flat[:num_groups * 3].view(-1, 3)
                    
                    # The "twist": cross product of gradient and history
                    cross_product = torch.linalg.cross(grad_groups, exp_avg_groups, dim=1)
                    orbital_step[:num_groups * 3] = cross_product.flatten()

                # The final update direction is a combination of descent and orbit
                update_direction = exp_avg + twist_rate * orbital_step.view_as(grad)
                
                p.add_(update_direction, alpha=-lr)
        return loss


