# model_explain/utils/heatmap_overlay.py

"""
Utility for overlaying Grad-CAM heatmaps on input images for visualization.

This module provides a helper function to superimpose a class activation map (heatmap) over an original image using
OpenCV and NumPy.

Features:
- Supports adjustable transparency for the heatmap overlay.
- Utilizes OpenCV colormaps for better visualization.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-18
"""

import numpy as np
import cv2


def visualize_heatmap_on_image(
    image: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    colormap: int = cv2.COLORMAP_JET,
) -> np.ndarray:
    """
    Overlays a heatmap on the original image using OpenCV colormaps.

    Args:
        image (np.ndarray): Original image in HWC format.
            - Pixel values can be in [0, 1] (float32) or [0, 255] (uint8).
            - Must have 3 channels (RGB).
        heatmap (np.ndarray): Grad-CAM heatmap in HW format with values in [0, 1].
        alpha (float): Transparency of the heatmap overlay. Must be in [0, 1].
            - 0.0 means fully transparent heatmap.
            - 1.0 means fully opaque heatmap.
        colormap (int): OpenCV colormap constant (e.g., cv2.COLORMAP_JET).

    Returns:
        np.ndarray: The resulting image with heatmap overlay (HWC, dtype=uint8).
    """
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("Alpha must be between 0.0 and 1.0.")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Image must be HWC format with 3 channels (RGB).")

    if heatmap.ndim != 2:
        raise ValueError("Heatmap must be a 2D array.")

    # Normalize image if float
    if image.dtype != np.uint8:
        image = np.clip(image * 255, 0, 255).astype(np.uint8)

    # Normalize heatmap to [0, 255] and convert to uint8
    heatmap_norm = np.uint8(255 * np.clip(heatmap, 0, 1))

    # Resize heatmap to match input image size
    heatmap_resized = cv2.resize(heatmap_norm, (image.shape[1], image.shape[0]))

    # Apply colormap (e.g., JET)
    heatmap_color = cv2.applyColorMap(heatmap_resized, colormap)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)  # Convert BGR → RGB

    # Blend original image with heatmap
    overlay = cv2.addWeighted(image, 1 - alpha, heatmap_color, alpha, 0)

    return overlay
