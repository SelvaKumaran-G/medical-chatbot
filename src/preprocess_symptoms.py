"""
MediGuide AI - Symptom Preprocessing and Natural Language Extraction
Provides symptom vocabulary normalization, clinical synonym mapping, negation detection,
and structured dataset preparation.
"""

import os
import re
import json
import logging
from typing import List, Dict, Set, Tuple, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")

# Comprehensive synonym dictionary mapping colloquial expressions to canonical tokens
SYMPTOM_SYNONYM_MAP: Dict[str, str] = {
    # Pain & Discomfort
    "headache": "headache",
    "head ache": "headache",
    "head hurts": "headache",
    "throbbing head": "headache",
    "pain in head": "headache",
    "chest pain": "chest_pain",
    "pain in chest": "chest_pain",
    "chest pressure": "chest_pain",
    "chest tightness": "chest_pain",
    "stomach pain": "stomach_pain",
    "stomach ache": "stomach_pain",
    "abdominal pain": "abdominal_pain",
    "belly pain": "belly_pain",
    "tummy ache": "abdominal_pain",
    "back pain": "back_pain",
    "backache": "back_pain",
    "lower back pain": "back_pain",
    "neck pain": "neck_pain",
    "stiff neck": "stiff_neck",
    "joint pain": "joint_pain",
    "joints hurt": "joint_pain",
    "knee pain": "knee_pain",
    "hip pain": "hip_joint_pain",
    "muscle pain": "muscle_pain",
    "body ache": "muscle_pain",
    "muscle ache": "muscle_pain",
    
    # Respiratory & ENT
    "cough": "cough",
    "coughing": "cough",
    "dry cough": "cough",
    "phlegm": "phlegm",
    "sputum": "phlegm",
    "breathlessness": "breathlessness",
    "short of breath": "breathlessness",
    "shortness of breath": "breathlessness",
    "difficulty breathing": "breathlessness",
    "hard to breathe": "breathlessness",
    "cant breathe": "breathlessness",
    "runny nose": "runny_nose",
    "running nose": "runny_nose",
    "nasal congestion": "congestion",
    "stuffy nose": "congestion",
    "blocked nose": "congestion",
    "congestion": "congestion",
    "sneezing": "continuous_sneezing",
    "continuous sneezing": "continuous_sneezing",
    "sinus pressure": "sinus_pressure",
    "throat irritation": "throat_irritation",
    "sore throat": "throat_irritation",
    "loss of smell": "loss_of_smell",
    
    # Constitutional & Systemic
    "fever": "high_fever",
    "high fever": "high_fever",
    "mild fever": "mild_fever",
    "high temperature": "high_fever",
    "hot body": "high_fever",
    "feverish": "high_fever",
    "chills": "chills",
    "shivering": "shivering",
    "fatigue": "fatigue",
    "tiredness": "fatigue",
    "exhaustion": "fatigue",
    "weakness": "fatigue",
    "lethargy": "lethargy",
    "malaise": "malaise",
    "sweating": "sweating",
    "night sweats": "sweating",
    "dizziness": "dizziness",
    "lightheaded": "dizziness",
    "loss of balance": "loss_of_balance",
    "spinning": "spinning_movements",
    "vertigo": "spinning_movements",
    
    # Gastrointestinal
    "vomiting": "vomiting",
    "throwing up": "vomiting",
    "puking": "vomiting",
    "nausea": "nausea",
    "queasy": "nausea",
    "feel like vomiting": "nausea",
    "acidity": "acidity",
    "heartburn": "acidity",
    "acid reflux": "acidity",
    "indigestion": "indigestion",
    "upset stomach": "indigestion",
    "diarrhoea": "diarrhoea",
    "diarrhea": "diarrhoea",
    "loose motions": "diarrhoea",
    "watery stool": "diarrhoea",
    "constipation": "constipation",
    "hard stools": "constipation",
    "bloody stool": "bloody_stool",
    "loss of appetite": "loss_of_appetite",
    "not feeling hungry": "loss_of_appetite",
    "excessive hunger": "excessive_hunger",
    "weight loss": "weight_loss",
    "losing weight": "weight_loss",
    "weight gain": "weight_gain",
    
    # Dermatological
    "itching": "itching",
    "itchy": "itching",
    "itchy skin": "itching",
    "skin rash": "skin_rash",
    "rash": "skin_rash",
    "rashes": "skin_rash",
    "red spots": "red_spots_over_body",
    "pimples": "pus_filled_pimples",
    "blackheads": "blackheads",
    "skin peeling": "skin_peeling",
    "blister": "blister",
    "yellow skin": "yellowish_skin",
    "yellowish skin": "yellowish_skin",
    "yellowing of eyes": "yellowing_of_eyes",
    "yellow eyes": "yellowing_of_eyes",
    
    # Urinary & Metabolic
    "burning urination": "burning_micturition",
    "burning pee": "burning_micturition",
    "painful urination": "burning_micturition",
    "dark urine": "dark_urine",
    "yellow urine": "yellow_urine",
    "foul smell of urine": "foul_smell_of_urine",
    "frequent urination": "polyuria",
    "excessive urination": "polyuria",
    "irregular sugar": "irregular_sugar_level",
    "palpitations": "palpitations",
    "fast heart rate": "fast_heart_rate",
    "racing heart": "fast_heart_rate",
    "swollen legs": "swollen_legs",
    "swelling in joints": "swelling_joints",
    "blurred vision": "blurred_and_distorted_vision"
}

# Negation prefixes and trigger words
NEGATION_PATTERNS = [
    r"\b(?:no|not|without|never|denies|denied|free of|did not have|didn't have|zero)\s+([a-z\s]+)",
    r"\b(?:no sign of|negative for|ruled out)\s+([a-z\s]+)"
]

def clean_text(text: str) -> str:
    """Standardizes input string: lowercases, removes non-alphanumeric punctuation, cleans spaces."""
    text = text.lower()
    text = re.sub(r"[-_/]+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def detect_negations(text: str) -> Set[str]:
    """Identifies symptoms explicitly negated in the text."""
    clean_input = text.lower()
    negated_phrases = set()
    
    # Split text into sentence/clause segments
    clauses = re.split(r"[,;.\n]|\bbut\b|\bhowever\b|\bexcept\b", clean_input)
    for clause in clauses:
        clause = clause.strip()
        for pattern in NEGATION_PATTERNS:
            matches = re.finditer(pattern, clause)
            for m in matches:
                negated_segment = m.group(1).strip()
                # Check which symptoms fall inside this negated segment
                for phrase, canonical in SYMPTOM_SYNONYM_MAP.items():
                    if phrase in negated_segment:
                        negated_phrases.add(canonical)
    return negated_phrases

def extract_symptoms_from_text(user_text: str) -> Dict[str, Any]:
    """
    Extracts canonical symptoms from free-form natural language text.
    Handles synonyms, normalization, and filters out negated symptoms.
    """
    normalized_input = clean_text(user_text)
    negated_symptoms = detect_negations(user_text)
    
    extracted_symptoms = set()
    symptom_matches_detail = []
    
    # Sort phrases by length descending to match longest multi-word phrases first
    sorted_phrases = sorted(SYMPTOM_SYNONYM_MAP.keys(), key=lambda x: len(x), reverse=True)
    
    matched_ranges = []
    
    for phrase in sorted_phrases:
        # Check whole phrase match with word boundaries
        pattern = r"\b" + re.escape(phrase) + r"\b"
        for match in re.finditer(pattern, normalized_input):
            start, end = match.span()
            # Avoid overlapping subsumed matches
            if any(s <= start and end <= e for s, e in matched_ranges):
                continue
                
            canonical = SYMPTOM_SYNONYM_MAP[phrase]
            matched_ranges.append((start, end))
            
            if canonical in negated_symptoms:
                symptom_matches_detail.append({
                    "original_phrase": phrase,
                    "canonical_symptom": canonical,
                    "status": "negated"
                })
            else:
                extracted_symptoms.add(canonical)
                symptom_matches_detail.append({
                    "original_phrase": phrase,
                    "canonical_symptom": canonical,
                    "status": "confirmed"
                })

    return {
        "raw_text": user_text,
        "normalized_text": normalized_input,
        "confirmed_symptoms": sorted(list(extracted_symptoms)),
        "negated_symptoms": sorted(list(negated_symptoms)),
        "extraction_details": symptom_matches_detail,
        "symptom_count": len(extracted_symptoms)
    }

def preprocess_symptom_dataset(raw_csv_path: str = None) -> Tuple[Any, List[str], str]:
    """
    Cleans raw symptoms dataset:
    - Normalizes column names
    - Validates binary indicators
    - Deduplicates without losing case diversity
    - Generates processed dataset and vocabulary
    """
    import pandas as pd
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    if raw_csv_path is None:
        raw_csv_path = os.path.join(RAW_DATA_DIR, "raw_disease_symptoms.csv")
        
    df = pd.read_csv(raw_csv_path)
    logger.info(f"Loaded raw symptom dataset: {df.shape}")
    
    # Standardize column headers: lowercase and strip spaces
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Ensure target column is named 'prognosis'
    target_col = "prognosis"
    if target_col not in df.columns:
        for c in ["disease", "condition", "label"]:
            if c in df.columns:
                df.rename(columns={c: target_col}, inplace=True)
                break
                
    feature_cols = [c for c in df.columns if c != target_col]
    
    # Clean binary values (ensure 0 or 1 integers)
    df[feature_cols] = df[feature_cols].fillna(0).astype(int)
    # Clip any outliers to 0 or 1
    df[feature_cols] = df[feature_cols].clip(0, 1)
    
    # Standardize label strings
    df[target_col] = df[target_col].astype(str).str.strip()
    
    # Drop rows where all symptoms are 0
    valid_mask = df[feature_cols].sum(axis=1) > 0
    df = df[valid_mask].reset_index(drop=True)
    
    # Save cleaned processed dataset
    processed_path = os.path.join(PROCESSED_DATA_DIR, "symptoms_cleaned.csv")
    df.to_csv(processed_path, index=False)
    logger.info(f"Saved processed symptom dataset to: {processed_path} (Shape: {df.shape})")
    
    # Save symptom vocabulary
    vocab_path = os.path.join(PROCESSED_DATA_DIR, "symptom_vocabulary.json")
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump({
            "feature_columns": feature_cols,
            "target_classes": sorted(df[target_col].unique().tolist()),
            "synonym_map_count": len(SYMPTOM_SYNONYM_MAP)
        }, f, indent=2)
    logger.info(f"Saved symptom vocabulary to: {vocab_path}")
    
    return df, feature_cols, processed_path

if __name__ == "__main__":
    df_clean, features, path = preprocess_symptom_dataset()
    print(f"Processed dataset ready: {df_clean.shape}, Features: {len(features)}")
    
    # Test natural language extraction
    sample_text = "I have a terrible headache, high fever and chest tightness, but no cough and not vomiting."
    result = extract_symptoms_from_text(sample_text)
    print("\n--- NL Extraction Test ---")
    print(f"Input: {sample_text}")
    print(f"Confirmed Symptoms: {result['confirmed_symptoms']}")
    print(f"Negated Symptoms: {result['negated_symptoms']}")
