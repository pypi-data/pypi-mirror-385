"""
Setup script for the model_explain package.

Author:
    Vaibhav Kulshrestha

Date:
    2025-10-20
"""

# Import necessary modules
from setuptools import setup, find_packages

setup(
    name="model_explain",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        "torch",
        "plotly",
        "fairlearn",
        "dice-ml",
        "numpy",
        "pandas",
        "scikit-learn",
        "shap",
        "lime",
        "streamlit",
        "xgboost",
        "joblib",
        "matplotlib",
        "seaborn",
    ],
    entry_points={"console_scripts": ["explain-cli=model_explain.cli:main"]},
    author="Vaibhav Kulshrestha",
    author_email="vaibhav1kulshrestha@gmail.com",
    description="A package for interpreting and explaining machine learning models. It provides a unified interface for popular explanation techniques, including LIME, SHAP, and Grad-CAM and supports a wide range of models and data types.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    url="https://github.com/vaibhav-k/model_explain",  # GitHub repository
    project_urls={
        "Source": "https://github.com/vaibhav-k/model_explain",
        "Tracker": "https://github.com/vaibhav-k/model_explain/issues",
    },
)
