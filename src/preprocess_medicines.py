"""
MediGuide AI - Medicine Preprocessing and Indexing Module
Normalizes drug names, active ingredients, labeled indications, and builds
drug-drug interaction lookup indices.
"""

import os
import json
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")

def clean_drug_string(s: str) -> str:
    """Standardizes drug name for lookup."""
    return s.strip().lower()

def preprocess_medicine_database(raw_json_path: str = None) -> Dict[str, Any]:
    """
    Cleans raw medicine records and creates fast search indices:
    - Name-to-record index (both generic and brand names)
    - Ingredient index
    - Indication reverse index
    - Drug-drug interaction graph
    """
    if raw_json_path is None:
        raw_json_path = os.path.join(RAW_DATA_DIR, "raw_medicine_database.json")
        
    if not os.path.exists(raw_json_path):
        raise FileNotFoundError(f"Raw medicine database not found at {raw_json_path}")
        
    with open(raw_json_path, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)
        
    cleaned_records = []
    name_lookup_index: Dict[str, int] = {}
    indication_index: Dict[str, List[int]] = {}
    interaction_pairs: List[Dict[str, Any]] = []
    
    for idx, med in enumerate(records):
        generic_clean = med["generic_name"].strip()
        brand_clean = [b.strip() for b in med.get("brand_names", [])]
        ingredients_clean = [i.strip() for i in med.get("active_ingredients", [])]
        indications_clean = [ind.strip() for ind in med.get("labeled_indications", [])]
        
        cleaned_entry = {
            "id": idx + 1,
            "generic_name": generic_clean,
            "brand_names": brand_clean,
            "active_ingredients": ingredients_clean,
            "drug_class": med.get("drug_class", "Unspecified"),
            "labeled_indications": indications_clean,
            "contraindications": med.get("contraindications", []),
            "warnings_and_precautions": med.get("warnings_and_precautions", []),
            "common_side_effects": med.get("common_side_effects", []),
            "drug_interactions": med.get("drug_interactions", []),
            "allergy_risks": med.get("allergy_risks", []),
            "pregnancy_breastfeeding": med.get("pregnancy_breastfeeding", "Consult physician."),
            "jurisdiction": med.get("jurisdiction", "US FDA"),
            "source_org": med.get("source_org", "US FDA / DailyMed"),
            "source_url": med.get("source_url", "https://dailymed.nlm.nih.gov/dailymed/"),
            "label_revision_date": med.get("label_revision_date", "2025-01-01")
        }
        cleaned_records.append(cleaned_entry)
        
        # Build Name Indices
        name_lookup_index[clean_drug_string(generic_clean)] = idx
        # Also index simple base name without parentheses e.g. "Paracetamol"
        base_name = generic_clean.split("(")[0].strip()
        name_lookup_index[clean_drug_string(base_name)] = idx
        
        for b in brand_clean:
            name_lookup_index[clean_drug_string(b)] = idx
            
        for ing in ingredients_clean:
            name_lookup_index[clean_drug_string(ing)] = idx
            
        # Build Indication Reverse Index
        for ind in indications_clean:
            ind_key = clean_drug_string(ind)
            if ind_key not in indication_index:
                indication_index[ind_key] = []
            indication_index[ind_key].append(idx)
            
        # Build Pairwise Interactions
        for inter in med.get("drug_interactions", []):
            interaction_pairs.append({
                "drug_a": generic_clean,
                "drug_b": inter.get("interacting_drug"),
                "severity": inter.get("severity", "Moderate"),
                "clinical_effect": inter.get("effect", "")
            })
            
    # Save cleaned medicine records
    cleaned_out_path = os.path.join(PROCESSED_DATA_DIR, "medicines_cleaned.json")
    with open(cleaned_out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2)
    logger.info(f"Saved cleaned medicines to: {cleaned_out_path} ({len(cleaned_records)} records)")
    
    # Save Indices
    index_payload = {
        "name_to_index": name_lookup_index,
        "indication_index": indication_index,
        "interaction_pairs": interaction_pairs,
        "total_medicines": len(cleaned_records)
    }
    index_out_path = os.path.join(PROCESSED_DATA_DIR, "medicine_search_index.json")
    with open(index_out_path, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, indent=2)
    logger.info(f"Saved medicine search index to: {index_out_path}")
    
    return index_payload

if __name__ == "__main__":
    result = preprocess_medicine_database()
    print(f"Preprocessed {result['total_medicines']} medicines with {len(result['name_to_index'])} alias lookups.")
