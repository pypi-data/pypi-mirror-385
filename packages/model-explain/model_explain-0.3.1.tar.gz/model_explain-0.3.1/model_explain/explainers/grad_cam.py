# model_explain/explainers/grad_cam.py

"""
Grad-CAM implementation for convolutional neural networks in PyTorch.

This module provides the GradCAM class, which enables generation of class-specific heatmaps indicating the spatial
importance of image regions contributing to a model's prediction.

Features:
- Supports any PyTorch convolutional neural network model.
- Computes gradients and activations from a specified convolutional layer.

Reference:
Selvaraju et al., Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization
(https://arxiv.org/abs/1610.02391)

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-18
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2


def _get_target_layer(model, layer_name):
    """Helper function to retrieve the target layer by name."""
    for name, module in model.named_modules():
        if name == layer_name:
            return module
    raise ValueError(
        f"Layer '{layer_name}' not found in model. "
        f"Available layers: {[name for name, _ in model.named_modules()]}"
    )


class GradCAM:
    """
    GradCAM generates class activation maps (CAMs) for convolutional neural networks.

    This class supports PyTorch models and computes heatmaps that highlight
    regions in the input image that were important for a specific class prediction.

    Attributes:
        model (torch.nn.Module): The neural network model.
        target_layer (torch.nn.Module): The layer to compute gradients from.
        activations (torch.Tensor): Forward activations of the target layer.
        gradients (torch.Tensor): Gradients of the output w.r.t. the target layer.
    """

    def __init__(self, model, target_layer_name):
        """
        Initializes the GradCAM object and registers hooks on the target layer.

        :param model: The neural network model.
        :type model: torch.nn.Module
        :param target_layer_name: Name of the convolutional layer to target for Grad-CAM.
        :type target_layer_name: str
        """
        self.model = model
        self.target_layer = _get_target_layer(model, target_layer_name)
        self.activations = None
        self.gradients = None

        # Register hooks to capture activations and gradients
        self.target_layer.register_forward_hook(self._forward_hook)
        self.target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, input, output):
        self.activations = output.detach()

    def _backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def _save_activation(self, output):
        """
        Hook to save forward activations from the target layer.

        :param output: The forward activation of the target layer.
        :type output: torch.Tensor
        """
        self.activations = output.detach()

    def _save_gradient(self, grad_output):
        """
        Hook to save gradients w.r.t. the output of the target layer.

        :param grad_output: The gradient of the loss w.r.t. the target layer's output.
        :type grad_output: torch.Tensor
        """
        self.gradients = grad_output[0].detach()

    def __call__(self, input_tensor, target_idx):
        """
        Generates the Grad-CAM heatmap for the specified target class index.

        :param input_tensor: Input image tensor of shape (1, C, H, W).
        :type input_tensor: torch.Tensor
        :param target_idx: Index of the target class to compute Grad-CAM for.
        :type target_idx: int
        :return: Heatmap of shape (H, W) normalized to [0, 1].
        :rtype: np.ndarray
        """
        self.model.eval()

        # Forward pass
        output = self.model(input_tensor)
        if isinstance(output, tuple):  # Handle models that return (logits, ...)
            output = output[0]

        # Create one-hot output vector for target class
        one_hot = torch.zeros_like(output)
        one_hot[0, target_idx] = 1

        # Backward pass
        self.model.zero_grad()
        output.backward(gradient=one_hot, retain_graph=True)

        # Global average pooling of gradients
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])  # shape: (C,)

        # Weight the activations by the pooled gradients
        weighted_activations = self.activations * pooled_gradients.view(1, -1, 1, 1)

        # Compute the heatmap
        heatmap = torch.mean(weighted_activations, dim=1).squeeze()
        heatmap = F.relu(heatmap)
        heatmap = heatmap / torch.max(heatmap + 1e-8)  # Normalize to [0, 1]

        # Resize to input size
        heatmap_np = heatmap.cpu().numpy()
        height, width = input_tensor.shape[2], input_tensor.shape[3]
        heatmap_resized = cv2.resize(heatmap_np, (width, height))

        return heatmap_resized
