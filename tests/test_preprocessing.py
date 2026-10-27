"""Tests for symptom preprocessing and NL extraction."""
import pytest
from src.preprocess_symptoms import extract_symptoms_from_text, clean_text

def test_extract_basic_symptoms():
    result = extract_symptoms_from_text("I have a headache and fever")
    assert "headache" in result["confirmed_symptoms"]
    assert "high_fever" in result["confirmed_symptoms"]

def test_extract_synonym_resolution():
    result = extract_symptoms_from_text("I feel shortness of breath and a sore throat")
    assert "breathlessness" in result["confirmed_symptoms"]
    assert "throat_irritation" in result["confirmed_symptoms"]

def test_negation_detection():
    result = extract_symptoms_from_text("I have a headache but no cough and not vomiting")
    assert "headache" in result["confirmed_symptoms"]
    assert "cough" in result["negated_symptoms"]
    assert "vomiting" in result["negated_symptoms"]
    assert "cough" not in result["confirmed_symptoms"]

def test_empty_input():
    result = extract_symptoms_from_text("")
    assert result["symptom_count"] == 0

def test_nonsense_input():
    result = extract_symptoms_from_text("hello world pizza basketball")
    assert result["symptom_count"] == 0

def test_clean_text_lowercases():
    assert clean_text("HEaDaCHe") == "headache"

def test_clean_text_strips_punctuation():
    cleaned = clean_text("chest-pain!! and (fever)")
    assert "chest pain" in cleaned
    assert "fever" in cleaned

def test_multiple_symptoms():
    result = extract_symptoms_from_text(
        "I have chills, high fever, sweating, nausea, muscle pain, and headache"
    )
    assert result["symptom_count"] >= 5

def test_case_insensitivity():
    r1 = extract_symptoms_from_text("I have HEADACHE")
    r2 = extract_symptoms_from_text("i have headache")
    assert r1["confirmed_symptoms"] == r2["confirmed_symptoms"]
