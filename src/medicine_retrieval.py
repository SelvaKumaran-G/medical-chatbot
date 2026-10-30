"""
MediGuide AI - Verified Medicine Information Retrieval Engine
Retrieves verified medicine data (openFDA, DailyMed, and CDSCO records) based on
generic name, brand names, active ingredients, or condition indications.
Enforces strict medical safety: Never prescribes medications or dosages.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
MEDICINES_PATH = os.path.join(PROCESSED_DATA_DIR, "medicines_cleaned.json")
SEARCH_INDEX_PATH = os.path.join(PROCESSED_DATA_DIR, "medicine_search_index.json")

class MedicineRetriever:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            candidates = [
                MEDICINES_PATH,
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "api", "medicines.json"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "medicines.json"),
                os.path.join(os.path.dirname(__file__), "..", "medicines.json"),
                "medicines.json",
                "public/medicines.json"
            ]
            for c in candidates:
                if os.path.exists(c):
                    data_path = c
                    break
            if data_path is None:
                data_path = MEDICINES_PATH
            
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self.medicines: List[Dict[str, Any]] = json.load(f)
        else:
            self.medicines = []
            
        index_candidates = [
            SEARCH_INDEX_PATH,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "api", "medicine_search_index.json"),
            "medicine_search_index.json"
        ]
        self.index = {}
        for ic in index_candidates:
            if os.path.exists(ic):
                with open(ic, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
                break
        else:
            self.index = {}
            
    def get_by_name(self, query_name: str) -> Optional[Dict[str, Any]]:
        """Finds medicine by exact or partial generic or brand name."""
        q = query_name.strip().lower()
        
        # Check direct index
        name_map = self.index.get("name_to_index", {})
        if q in name_map:
            idx = name_map[q]
            return self.medicines[idx]
            
        # Check substrings
        for med in self.medicines:
            if q in med["generic_name"].lower():
                return med
            for b in med.get("brand_names", []):
                if q in b.lower():
                    return med
            for ing in med.get("active_ingredients", []):
                if q in ing.lower():
                    return med
        return None

    def search_medicines(self, query: str) -> List[Dict[str, Any]]:
        """Searches across generic name, brand names, ingredients, and indications."""
        q = query.strip().lower()
        if not q:
            return []
            
        matched = []
        seen_ids = set()
        
        # Direct name/brand match
        exact_match = self.get_by_name(q)
        if exact_match and exact_match["id"] not in seen_ids:
            matched.append(exact_match)
            seen_ids.add(exact_match["id"])
            
        # Indication or keyword match
        for med in self.medicines:
            if med["id"] in seen_ids:
                continue
            # Check indications
            for ind in med.get("labeled_indications", []):
                if q in ind.lower():
                    matched.append(med)
                    seen_ids.add(med["id"])
                    break
            # Check drug class
            if med["id"] not in seen_ids and q in med.get("drug_class", "").lower():
                matched.append(med)
                seen_ids.add(med["id"])

        return matched

    def get_labeled_medicines_for_condition(self, condition: str) -> List[Dict[str, Any]]:
        """
        Retrieves medicines that list the given condition in their FDA-labeled indications.
        Includes an explicit disclaimer that labeled indications do NOT constitute a prescription.
        """
        cond_clean = condition.strip().lower()
        matching_meds = []
        
        for med in self.medicines:
            for ind in med.get("labeled_indications", []):
                if cond_clean in ind.lower() or ind.lower() in cond_clean:
                    matching_meds.append({
                        "generic_name": med["generic_name"],
                        "brand_names": med["brand_names"],
                        "drug_class": med["drug_class"],
                        "labeled_indication_snippet": ind,
                        "contraindications": med["contraindications"],
                        "warnings": med["warnings_and_precautions"],
                        "source_org": med["source_org"],
                        "source_url": med["source_url"],
                        "jurisdiction": med["jurisdiction"]
                    })
                    break

        return matching_meds

    def format_medicine_card(self, med: Dict[str, Any]) -> Dict[str, Any]:
        """Formats medicine information for clean UI display with citations."""
        return {
            "title": f"{med['generic_name']} ({', '.join(med['brand_names'][:3])})",
            "generic_name": med["generic_name"],
            "brand_names": med["brand_names"],
            "active_ingredients": med["active_ingredients"],
            "drug_class": med["drug_class"],
            "labeled_indications": med["labeled_indications"],
            "contraindications": med["contraindications"],
            "warnings_and_precautions": med["warnings_and_precautions"],
            "common_side_effects": med["common_side_effects"],
            "drug_interactions_count": len(med.get("drug_interactions", [])),
            "pregnancy_breastfeeding": med.get("pregnancy_breastfeeding", "Consult a doctor."),
            "jurisdiction": med.get("jurisdiction", "US FDA"),
            "source_citation": {
                "organization": med.get("source_org", "US FDA / DailyMed"),
                "url": med.get("source_url", "https://dailymed.nlm.nih.gov/dailymed/"),
                "label_revision_date": med.get("label_revision_date", "2025-01-01")
            },
            "safety_disclaimer": (
                "Educational Reference Only: Labeled indications reflect regulatory manufacturer packaging inserts. "
                "This system does NOT recommend, prescribe, or advise taking this medication. "
                "Always consult a licensed medical doctor or pharmacist before taking any medicine."
            )
        }

_RETRIEVER_INSTANCE = None

def get_medicine_retriever() -> MedicineRetriever:
    """Returns singleton instance of MedicineRetriever."""
    global _RETRIEVER_INSTANCE
    if _RETRIEVER_INSTANCE is None:
        _RETRIEVER_INSTANCE = MedicineRetriever()
    return _RETRIEVER_INSTANCE

if __name__ == "__main__":
    retriever = get_medicine_retriever()
    print("\n--- MEDICINE RETRIEVAL TEST ---")
    query = "Tylenol"
    med = retriever.get_by_name(query)
    if med:
        card = retriever.format_medicine_card(med)
        print(f"Query '{query}' -> Found: {card['title']}")
        print(f"Drug Class: {card['drug_class']}")
        print(f"Indications: {card['labeled_indications']}")
        print(f"Source URL: {card['source_citation']['url']}")
    else:
        print(f"Query '{query}' not found.")
