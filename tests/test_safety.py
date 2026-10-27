"""Tests for emergency triage and drug interaction safety checks."""
import pytest
from src.triage import screen_emergency_red_flags, generate_triage_questions
from src.medicine_safety import get_safety_checker

# ── Emergency triage ──

def test_heart_attack_detection():
    result = screen_emergency_red_flags("I have a crushing chest pain radiating to my left arm")
    assert result["is_emergency"] is True
    assert "coronary" in result["category"].lower() or "heart" in result["category"].lower()

def test_stroke_detection():
    result = screen_emergency_red_flags("My face is drooping and I have slurred speech")
    assert result["is_emergency"] is True
    assert "stroke" in result["category"].lower()

def test_severe_breathing_detection():
    result = screen_emergency_red_flags("I cannot breathe and my lips are turning blue")
    assert result["is_emergency"] is True

def test_non_emergency_passes():
    result = screen_emergency_red_flags("I have a mild cough and runny nose since yesterday")
    assert result["is_emergency"] is False

def test_triage_followup_questions():
    qs = generate_triage_questions({})
    assert len(qs) > 0

# ── Drug interactions ──

@pytest.fixture(scope="module")
def checker():
    return get_safety_checker()

def test_warfarin_ibuprofen_interaction(checker):
    hits = checker.check_drug_interactions(["Warfarin", "Ibuprofen"])
    assert len(hits) > 0
    assert any(h["severity"] in ("Severe", "Major") for h in hits)

def test_no_interaction_for_unrelated_drugs(checker):
    hits = checker.check_drug_interactions(["Cetirizine", "Metformin"])
    assert len(hits) == 0

def test_penicillin_allergy_vs_amoxicillin(checker):
    alerts = checker.check_allergy_risks("Amoxicillin", ["Penicillin"])
    assert len(alerts) > 0
    assert any("contraindication" in a["severity"].lower() for a in alerts)

def test_no_allergy_conflict(checker):
    alerts = checker.check_allergy_risks("Omeprazole", ["Penicillin"])
    assert len(alerts) == 0

def test_patient_profile_evaluation(checker):
    profile = {
        "known_allergies": ["Penicillin"],
        "current_medications": ["Warfarin"],
        "is_pregnant": True
    }
    result = checker.evaluate_patient_profile("Amoxicillin", profile)
    assert result["total_alerts"] > 0
