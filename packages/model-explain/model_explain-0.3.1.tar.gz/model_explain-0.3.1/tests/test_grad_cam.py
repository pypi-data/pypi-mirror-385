# tests/test_grad_cam.py

"""
Unit tests for the Grad-CAM explainer in the model_explain package.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-18
"""

import numpy as np
import pytest
import torch
import torch.nn as nn

from model_explain.explainers.grad_cam import GradCAM


class DummyCNN(nn.Module):
    """
    A simple CNN for testing GradCAM functionality.
    """

    def __init__(self):
        """
        Initialize the DummyCNN with one convolutional layer, ReLU, pooling, and a fully connected layer.

        :attributes:
            conv1 (nn.Conv2d): Convolutional layer.
            relu (nn.ReLU): ReLU activation function.
            pool (nn.AdaptiveAvgPool2d): Adaptive average pooling layer.
            fc (nn.Linear): Fully connected layer.
        """
        super().__init__()
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(8, 2)
        self.activations = None  # initialize activations attribute

    def forward(self, x):
        x = self.conv1(x)  # target layer
        x = self.relu(x)
        self.activations = x  # save for shape checking
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


@pytest.fixture
def dummy_model():
    """Fixture to create and return a dummy CNN model."""
    return DummyCNN()


@pytest.fixture
def dummy_input():
    """Fixture to create and return a dummy input tensor."""
    # Batch size 1, 3 channels, 32x32 image
    return torch.randn(1, 3, 32, 32, requires_grad=True)


def test_grad_cam_output_shape(dummy_model, dummy_input):
    """
    Test that the Grad-CAM output is a 2D numpy array matching input spatial dimensions.

    :param dummy_model: A dummy CNN model.
    :type dummy_model: nn.Module
    :param dummy_input: A dummy input tensor.
    :type dummy_input: torch.Tensor
    """
    grad_cam = GradCAM(dummy_model, target_layer_name="conv1")
    heatmap = grad_cam(dummy_input, target_idx=1)
    assert isinstance(heatmap, np.ndarray)
    assert heatmap.shape == (32, 32), "Heatmap must match input spatial dimensions."


def test_grad_cam_output_range(dummy_model, dummy_input):
    """
    Test that the Grad-CAM output values are in [0, 1].

    :param dummy_model: A dummy CNN model.
    :type dummy_model: nn.Module
    :param dummy_input: A dummy input tensor.
    :type dummy_input: torch.Tensor
    """
    grad_cam = GradCAM(dummy_model, target_layer_name="conv1")
    heatmap = grad_cam(dummy_input, target_idx=1)
    assert heatmap.min() >= 0.0, "Heatmap values must be >= 0"
    assert heatmap.max() <= 1.0, "Heatmap values must be <= 1"


def test_invalid_layer_name(dummy_model):
    """
    Ensure an invalid layer name raises a clear error.

    :param dummy_model: A dummy CNN model.
    :type dummy_model: nn.Module
    """
    with pytest.raises(ValueError, match="Layer 'invalid' not found"):
        GradCAM(dummy_model, target_layer_name="invalid")


def test_grad_cam_target_class_0(dummy_model, dummy_input):
    """
    Check that Grad-CAM works for target class 0.

    :param dummy_model: A dummy CNN model.
    :type dummy_model: nn.Module
    :param dummy_input: A dummy input tensor.
    :type dummy_input: torch.Tensor
    """
    grad_cam = GradCAM(dummy_model, target_layer_name="conv1")
    heatmap = grad_cam(dummy_input, target_idx=0)
    assert heatmap.shape == (32, 32)
    assert np.isfinite(heatmap).all(), "Heatmap must not contain NaNs or Infs"


def test_grad_cam_without_training(dummy_model, dummy_input):
    """
    Grad-CAM should still work even if the model is untrained.

    :param dummy_model: A dummy CNN model.
    :type dummy_model: nn.Module
    :param dummy_input: A dummy input tensor.
    :type dummy_input: torch.Tensor
    """
    grad_cam = GradCAM(dummy_model, target_layer_name="conv1")
    heatmap = grad_cam(dummy_input, target_idx=1)
    assert heatmap is not None
    assert heatmap.shape == (32, 32)


def test_model_output_tuple_support():
    """
    Test Grad-CAM on a model that returns a tuple (e.g., (logits, aux)).
    """

    class TupleModel(DummyCNN):
        def forward(self, x):
            logits = super().forward(x)
            return logits, torch.tensor([1.0])  # fake auxiliary output

    model = TupleModel()
    input_tensor = torch.randn(1, 3, 32, 32)
    grad_cam = GradCAM(model, target_layer_name="conv1")
    heatmap = grad_cam(input_tensor, target_idx=1)
    assert isinstance(heatmap, np.ndarray)


def main():
    """
    Run all Grad-CAM tests.
    """
    test_grad_cam_output_shape(dummy_model(), dummy_input())
    test_grad_cam_output_range(dummy_model(), dummy_input())
    test_invalid_layer_name(dummy_model())
    test_grad_cam_target_class_0(dummy_model(), dummy_input())
    test_grad_cam_without_training(dummy_model(), dummy_input())
    test_model_output_tuple_support()
    print("All Grad-CAM tests passed!")


if __name__ == "__main__":
    main()
