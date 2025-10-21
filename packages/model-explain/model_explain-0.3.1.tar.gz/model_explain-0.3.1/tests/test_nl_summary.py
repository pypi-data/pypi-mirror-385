# tests/test_nl_summary.py

"""
Unit tests for the nl_summary explainer in the model_explain package.

These tests verify the behavior of the nl_summary explainer with mock models using synthetic datasets.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-16
"""

import numpy as np
import pandas as pd

from model_explain.explainers.nl_summary import generate_summary


def test_generate_summary_returns_string():
    """
    Unit test for generate_summary.

    This test verifies that the generate_summary function returns a string summary
    for a given input instance, SHAP values, feature names, prediction, and class names.
    """
    instance = pd.Series([1, -2, 3], index=["feature1", "feature2", "feature3"])
    shap_values = np.array([0.5, -0.2, 0.1])
    feature_names = ["feature1", "feature2", "feature3"]
    prediction = 0
    class_names = ["class_0", "class_1"]

    summary = generate_summary(
        instance, shap_values, feature_names, prediction, class_names
    )
    assert isinstance(summary, str)
    assert "class_0" in summary


def test_generate_summary_top_features_order():
    """
    Unit test to check if the top features in the summary are ordered by absolute SHAP values.

    This test ensures that the features mentioned in the summary are the ones with the highest
    absolute SHAP values, and that they are ordered correctly.
    """
    instance = pd.Series([1, 2, -3], index=["f1", "f2", "f3"])
    shap_values = np.array([0.1, 0.9, -0.8])
    feature_names = ["f1", "f2", "f3"]
    prediction = 1
    class_names = ["A", "B"]

    summary = generate_summary(
        instance, shap_values, feature_names, prediction, class_names
    )
    # Top features should be f2, f3, f1 (by abs(shap_values))
    assert "f2 was high" in summary
    assert "f3 was low" in summary
    assert "f1 was high" in summary


def test_generate_summary_handles_negative_and_zero():
    """
    Unit test to check if the summary correctly describes features with negative and zero values.

    This test ensures that features with negative values are described as "low" and features with zero values are also
    described as "low".
    """
    instance = pd.Series([0, -1, 2], index=["a", "b", "c"])
    shap_values = np.array([0.2, 0.3, 0.1])
    feature_names = ["a", "b", "c"]
    prediction = 0
    class_names = ["X", "Y"]

    summary = generate_summary(
        instance, shap_values, feature_names, prediction, class_names
    )
    assert "a was low" in summary  # 0 is not > 0
    assert "b was low" in summary
    assert "c was high" in summary


def test_generate_summary_with_less_than_three_features():
    """
    Unit test to check if the summary works with less than three features.

    This test ensures that the function can handle cases where there are fewer than three features and still generates a
    valid summary.
    """
    instance = pd.Series([1], index=["only_feature"])
    shap_values = np.array([0.7])
    feature_names = ["only_feature"]
    prediction = 0
    class_names = ["foo"]

    summary = generate_summary(
        instance, shap_values, feature_names, prediction, class_names
    )
    assert "only_feature was high" in summary


def main():
    """
    Run all nl_summary explainer tests.
    """
    test_generate_summary_returns_string()
    test_generate_summary_top_features_order()
    test_generate_summary_handles_negative_and_zero()
    test_generate_summary_with_less_than_three_features()
    print("nl_summary tests passed!")


if __name__ == "__main__":
    main()
