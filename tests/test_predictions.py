"""Tests for the ML prediction engine."""
import pytest
from src.predict_conditions import get_predictor

@pytest.fixture(scope="module")
def predictor():
    return get_predictor()

def test_model_loads(predictor):
    assert predictor.model is not None
    assert len(predictor.feature_names) > 50
    assert len(predictor.classes) > 10

def test_predict_known_symptoms(predictor):
    result = predictor.predict("I have high fever, chills, headache, nausea, and muscle pain")
    assert result["status"] == "SUCCESS"
    assert len(result["top_predictions"]) == 3

def test_predict_returns_probabilities(predictor):
    result = predictor.predict("cough, breathlessness, chest pain, high fever")
    for cand in result["top_predictions"]:
        assert 0.0 <= cand["calibrated_probability"] <= 1.0

def test_abstain_on_unknown_input(predictor):
    result = predictor.predict("I like playing soccer on weekends")
    assert result["status"] == "ABSTAIN_NO_SYMPTOMS"

def test_negated_symptoms_excluded(predictor):
    result = predictor.predict("I have headache but no fever and no cough")
    assert "high_fever" not in result["extracted_symptoms"]
    assert "cough" not in result["extracted_symptoms"]
    assert "headache" in result["extracted_symptoms"]

def test_insufficient_evidence_follow_up(predictor):
    result = predictor.predict("I have a headache")
    assert result["status"] == "SUCCESS"
    # Single symptom should trigger follow-up
    assert len(result.get("follow_up_questions", [])) > 0

def test_disclaimer_present(predictor):
    result = predictor.predict("fever and vomiting")
    assert "disclaimer" in result

def test_model_name_populated(predictor):
    result = predictor.predict("itching and skin rash")
    assert result["model_used"] is not None
