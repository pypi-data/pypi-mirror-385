# Model Explain

---

[![Downloads](https://pepy.tech/badge/model-explain)](https://pepy.tech/project/model-explain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/model-explain.svg)](https://badge.fury.io/py/model-explain)

---

`model_explain` is a Python package for **interpreting** and **explaining** machine learning models. It provides a unified interface for popular explanation techniques, including **LIME**, **SHAP**, and **Grad-CAM** and supports a wide range of models and data types.

## Key Features

- **Unified API** for LIME and SHAP explanations
- **Model-agnostic**: works with any model supporting `predict` or `predict_proba`
- **Tabular, image, and text data** support
- **Visualizations** for both local and global explanations
- **Easy integration** with scikit-learn, XGBoost, LightGBM, and more
- **Feature importance** extraction and plotting
- **Interpretability for individual predictions** and datasets

## Installation

Install from PyPI:

```bash
pip install model-explain
```

Or, if you prefer to clone the repository and install manually:

```bash
git clone https://github.com/vaibhav-k/model_explain.git
cd model_explain
pip install .
```

## Quick Start

### Tabular Data Example (LIME)

```python
from model_explain.explainers.lime_explainer import lime_explainer

# model: trained scikit-learn model
# X_test: pandas DataFrame of test features

explanation = lime_explainer(model, X_test, instance_index=0)
explanation.show_in_notebook()
```

### Tabular Data Example (SHAP)

```python
import shap
from model_explain.explainers.shap_explainer import shap_explainer

# model: trained machine learning model
# X_test: pandas DataFrame of test features

shap_values = shap_explainer(model, X_test)
shap.summary_plot(shap_values, X_test)

```

### Image Data Example

```python
from model_explain.explainers.grad_cam import GradCAM
import matplotlib.pyplot as plt

# model: your trained CNN model (e.g., from torchvision)
# image: a preprocessed image tensor of shape [1, C, H, W]
# predicted_class: integer index of the predicted class

explainer = GradCAM(model, target_layer_name="layer4")  # specify the last conv layer
heatmap = explainer(image, target_idx=predicted_class)

plt.imshow(heatmap, cmap="jet", alpha=0.5)
plt.title("Grad-CAM Heatmap")
plt.axis("off")
plt.show()
```

## Supported Models

- Scikit-learn models
- XGBoost
- LightGBM
- PyTorch models
- Any model with `predict` or `predict_proba` methods

## Visualizations

- **SHAP summary plot**: global feature importance (use **plot_feature_importance** for custom bar plots)
- **LIME explanation plot**: local feature contributions (use **plot_feature_importance** for instance-level contributions)
- **Image region importance (Grad-CAM heatmap)**: highlights spatial regions in images that most influence the model's prediction

## Use Cases

- Debugging and validating ML models
- Regulatory compliance and transparency
- Feature selection and engineering
- Enhancing trust in AI systems
- Explaining model predictions to stakeholders

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on how to contribute.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
