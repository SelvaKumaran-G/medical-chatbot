"""Tests for medicine retrieval and search."""
import pytest
from src.medicine_retrieval import get_medicine_retriever

@pytest.fixture(scope="module")
def retriever():
    return get_medicine_retriever()

def test_retriever_loads(retriever):
    assert len(retriever.medicines) > 0

def test_find_by_generic_name(retriever):
    med = retriever.get_by_name("Ibuprofen")
    assert med is not None
    assert "ibuprofen" in med["generic_name"].lower()

def test_find_by_brand_name(retriever):
    med = retriever.get_by_name("Tylenol")
    assert med is not None
    assert "acetaminophen" in med["generic_name"].lower() or "paracetamol" in med["generic_name"].lower()

def test_find_nonexistent_medicine(retriever):
    med = retriever.get_by_name("XyzNonexistentDrug12345")
    assert med is None

def test_search_by_condition(retriever):
    results = retriever.get_labeled_medicines_for_condition("Fever")
    assert len(results) > 0

def test_medicine_card_has_citation(retriever):
    med = retriever.get_by_name("Omeprazole")
    assert med is not None
    card = retriever.format_medicine_card(med)
    assert "source_citation" in card
    assert card["source_citation"]["url"]

def test_medicine_card_has_safety_disclaimer(retriever):
    med = retriever.get_by_name("Amoxicillin")
    assert med is not None
    card = retriever.format_medicine_card(med)
    assert "disclaimer" in card["safety_disclaimer"].lower() or "not" in card["safety_disclaimer"].lower()
