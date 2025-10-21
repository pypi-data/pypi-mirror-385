# tests/test_model_comparison.py

"""
Unit tests for the model comparison explainer in the model_explain package.

These tests verify the behavior of the model comparison explainer with mock models using synthetic datasets.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-16
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from model_explain.explainers.model_comparison import compare_models


@pytest.fixture
def sample_data():
    """
    Fixture to provide sample models and test data.
    """
    # Create a simple DataFrame with 4 features and 3 samples
    X_test = pd.DataFrame(
        {"f1": [1, 2, 3], "f2": [4, 5, 6], "f3": [7, 8, 9], "f4": [10, 11, 12]}
    )
    # Create mock models
    models = {"model_a": MagicMock(), "model_b": MagicMock()}
    return models, X_test


@patch("model_explain.explainers.model_comparison.shap.Explainer")
def test_compare_models_returns_dict_of_top_features(mock_explainer, sample_data):
    """
    Unit test for compare_models.

    This test verifies that the compare_models function returns a dictionary with model names
    as keys and lists of the top 3 feature names as values. It uses mock models and patches the
    SHAP Explainer to return predefined SHAP values.
    """
    models, X_test = sample_data

    # Mock SHAP values
    mock_shap_vals = MagicMock()
    # Simulate .abs.mean(0).argsort() for 4 features
    mock_shap_vals.abs.mean.return_value.argsort.return_value = np.array([0, 1, 2, 3])
    mock_explainer.return_value = lambda x: mock_shap_vals

    result = compare_models(models, X_test)
    assert isinstance(result, dict)
    assert set(result.keys()) == set(models.keys())
    for features in result.values():
        assert isinstance(features, list)
        assert len(features) == 3
        for f in features:
            assert f in X_test.columns


@patch("model_explain.explainers.model_comparison.shap.Explainer")
def test_compare_models_handles_empty_models(sample_data):
    """
    Test that compare_models handles empty models dictionary gracefully.

    This test ensures that when an empty dictionary of models is provided, the function
    returns an empty dictionary without errors.
    """
    _, X_test = sample_data
    # Call compare_models with empty models
    result = compare_models({}, X_test)
    # assert that the result is an empty dictionary
    assert result == {}


@patch("model_explain.explainers.model_comparison.shap.Explainer")
def test_compare_models_handles_less_than_three_features(mock_explainer):
    """
    Test that compare_models handles cases with less than three features.

    This test ensures that when the input data has fewer than three features, the function
    still returns the available features without errors.
    """
    # Create test data with only 2 features and a single model
    X_test = pd.DataFrame({"f1": [1, 2], "f2": [3, 4]})
    models = {"model_a": MagicMock()}
    # Mock SHAP values
    mock_shap_vals = MagicMock()
    mock_shap_vals.abs.mean.return_value.argsort.return_value = np.array([0, 1])
    mock_explainer.return_value = lambda x: mock_shap_vals

    # Assert that compare_models returns the available features
    result = compare_models(models, X_test)
    assert isinstance(result, dict)
    assert len(result["model_a"]) == 2


def main():
    """
    Run all model comparison tests.
    """
    test_compare_models_returns_dict_of_top_features()
    test_compare_models_handles_empty_models()
    test_compare_models_handles_less_than_three_features()
    print("Model comparison tests passed!")


if __name__ == "__main__":
    pytest.main([__file__])
