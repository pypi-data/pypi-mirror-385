# tests/test_summary.py

"""
Unit tests for the summary explainer in the model_explain package.

These tests verify the behavior of the summary explainer with mock models using synthetic datasets.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-16
"""

from unittest.mock import patch

import numpy as np
import pandas as pd

from model_explain.explainers.summary import batch_generate_summaries


def test_batch_generate_summaries_returns_list_of_strings():
    """
    Unit test for batch_generate_summaries.

    This test verifies that the batch_generate_summaries function returns a list of strings,
    with each string corresponding to a summary for an input instance. It uses mock data and
    patches the generate_summary function to return predefined summaries.

    Steps:
        1. Create a small DataFrame and mock SHAP values, predictions, and class labels.
        2. Patch generate_summary to return two specific summary strings.
        3. Call batch_generate_summaries with the test data.
        4. Assert that the result is a list of strings, matches the input length, and contains
           the expected summaries.

    Expected behavior:
        - The output is a list of strings.
        - The list length matches the number of input instances.
        - The summaries match the mocked return values.
    """
    # Create mock data
    data = pd.DataFrame({
        "feature1": [1, 2],
        "feature2": [3, 4]
    })
    # Synthetic SHAP values, predictions, and class labels
    shap_values = np.array([[0.1, -0.2], [0.3, 0.4]])
    predictions = np.array([0, 1])
    classes = ["class_0", "class_1"]

    # Patch generate_summary to return predefined summaries
    with patch("model_explain.explainers.summary.generate_summary", side_effect=[
        "Summary for instance 1",
        "Summary for instance 2"
    ]):
        summaries = batch_generate_summaries(data, shap_values, predictions, classes)

        assert isinstance(summaries, list)
        assert all(isinstance(summary, str) for summary in summaries)
        assert len(summaries) == len(data)
        assert summaries[0] == "Summary for instance 1"
        assert summaries[1] == "Summary for instance 2"


def main():
    """
    Run all summary explainer tests.
    """
    test_batch_generate_summaries_returns_list_of_strings()
    print("Summary tests passed!")


if __name__ == "__main__":
    main()