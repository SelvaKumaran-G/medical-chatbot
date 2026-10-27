"""Tests for data validation pipeline."""
import pytest
import os
import pandas as pd

def test_processed_symptom_file_exists():
    path = os.path.join("data", "processed", "symptoms_cleaned.csv")
    assert os.path.exists(path), "Processed symptom CSV must exist after preprocessing."

def test_symptom_dataset_has_no_nulls():
    df = pd.read_csv(os.path.join("data", "processed", "symptoms_cleaned.csv"))
    assert df.isnull().sum().sum() == 0, "Processed dataset must have zero null values."

def test_symptom_dataset_binary_features():
    df = pd.read_csv(os.path.join("data", "processed", "symptoms_cleaned.csv"))
    feature_cols = [c for c in df.columns if c != "prognosis"]
    for col in feature_cols:
        assert set(df[col].unique()).issubset({0, 1}), f"Column {col} has non-binary values."

def test_symptom_dataset_has_target_column():
    df = pd.read_csv(os.path.join("data", "processed", "symptoms_cleaned.csv"))
    assert "prognosis" in df.columns

def test_symptom_dataset_class_count():
    df = pd.read_csv(os.path.join("data", "processed", "symptoms_cleaned.csv"))
    assert df["prognosis"].nunique() >= 10, "Must have at least 10 conditions."

def test_no_zero_symptom_rows():
    df = pd.read_csv(os.path.join("data", "processed", "symptoms_cleaned.csv"))
    feature_cols = [c for c in df.columns if c != "prognosis"]
    zero_rows = (df[feature_cols].sum(axis=1) == 0).sum()
    assert zero_rows == 0, f"Found {zero_rows} rows with zero active symptoms."

def test_duplicate_rows_are_acceptable():
    """Duplicates may exist due to symptom overlap — just ensure dataset loads."""
    df = pd.read_csv(os.path.join("data", "processed", "symptoms_cleaned.csv"))
    assert len(df) > 100

def test_medicine_database_exists():
    path = os.path.join("data", "processed", "medicines_cleaned.json")
    assert os.path.exists(path)

def test_medicine_database_not_empty():
    import json
    with open(os.path.join("data", "processed", "medicines_cleaned.json")) as f:
        meds = json.load(f)
    assert len(meds) > 0
