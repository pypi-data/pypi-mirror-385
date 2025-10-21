# tests/test_surrogate_explainer.py

"""
Unit tests for the surrogate explainer in the model_explain package.

These tests verify the behavior of the surrogate explainer with mock models using synthetic datasets.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-16
"""

from unittest.mock import MagicMock

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from model_explain.explainers.surrogate import train_surrogate


def test_train_surrogate_returns_decision_tree():
    """
    Test that train_surrogate returns a DecisionTreeClassifier with correct depth.
    """
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([0, 1, 0])

    mock_model = MagicMock()
    mock_model.predict.return_value = y

    surrogate = train_surrogate(mock_model, X)

    assert isinstance(surrogate, DecisionTreeClassifier)
    assert surrogate.get_depth() <= 3
    assert surrogate.n_features_in_ == X.shape[1]


def main():
    """
    Run all surrogate explainer tests.
    """
    test_train_surrogate_returns_decision_tree()
    print("Surrogate tests passed!")


if __name__ == "__main__":
    main()
