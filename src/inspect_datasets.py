"""
MediGuide AI - Dataset Inspection and Schema Profiler
Inspects raw dataset schemas, column types, null values, label balances, and data distributions.
"""

import os
import json
import logging
import pandas as pd
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "data_quality")
os.makedirs(REPORTS_DIR, exist_ok=True)

def inspect_symptom_dataset(csv_path: str = None) -> Dict[str, Any]:
    """Inspects the schema and distribution of the symptom-disease dataset."""
    if csv_path is None:
        csv_path = os.path.join(RAW_DATA_DIR, "raw_disease_symptoms.csv")
        
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Symptom dataset not found at: {csv_path}")
        
    df = pd.read_csv(csv_path)
    
    # 1. Basic Dimensions
    total_rows, total_cols = df.shape
    
    # 2. Target Column Identification
    target_col = None
    for cand in ["prognosis", "disease", "label", "condition"]:
        if cand in df.columns:
            target_col = cand
            break
    if not target_col:
        target_col = df.columns[-1]
        
    feature_cols = [c for c in df.columns if c != target_col]
    
    # 3. Missing Value Analysis
    missing_by_col = df.isnull().sum()
    total_missing = int(missing_by_col.sum())
    
    # 4. Data Types
    dtype_counts = df.dtypes.astype(str).value_counts().to_dict()
    
    # 5. Duplicate Rows Analysis
    num_exact_duplicates = int(df.duplicated().sum())
    
    # 6. Class Balance Analysis
    class_counts = df[target_col].value_counts().to_dict()
    num_classes = len(class_counts)
    min_class_count = min(class_counts.values()) if class_counts else 0
    max_class_count = max(class_counts.values()) if class_counts else 0
    imbalance_ratio = round(max_class_count / max(min_class_count, 1), 3)
    
    # 7. Feature Sparsity
    feature_sums = df[feature_cols].sum()
    min_feature_occurrence = int(feature_sums.min())
    max_feature_occurrence = int(feature_sums.max())
    mean_feature_occurrence = round(float(feature_sums.mean()), 2)
    
    report = {
        "dataset_path": csv_path,
        "row_count": total_rows,
        "column_count": total_cols,
        "feature_count": len(feature_cols),
        "target_column": target_col,
        "num_classes": num_classes,
        "class_imbalance_ratio": imbalance_ratio,
        "total_missing_values": total_missing,
        "num_exact_duplicates": num_exact_duplicates,
        "data_types": dtype_counts,
        "feature_occurrence_summary": {
            "min_cases_with_symptom": min_feature_occurrence,
            "max_cases_with_symptom": max_feature_occurrence,
            "mean_cases_with_symptom": mean_feature_occurrence
        },
        "sample_features": feature_cols[:10],
        "classes": list(class_counts.keys())
    }
    
    return report

def inspect_medicine_dataset(json_path: str = None) -> Dict[str, Any]:
    """Inspects the schema and completeness of the verified medicine dataset."""
    if json_path is None:
        json_path = os.path.join(RAW_DATA_DIR, "raw_medicine_database.json")
        
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Medicine database not found at: {json_path}")
        
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    num_records = len(records)
    required_fields = [
        "generic_name", "brand_names", "active_ingredients", "labeled_indications",
        "contraindications", "warnings_and_precautions", "common_side_effects",
        "drug_interactions", "source_url"
    ]
    
    field_completeness = {field: 0 for field in required_fields}
    total_interactions = 0
    
    for r in records:
        for field in required_fields:
            if field in r and r[field]:
                field_completeness[field] += 1
        total_interactions += len(r.get("drug_interactions", []))
        
    report = {
        "dataset_path": json_path,
        "record_count": num_records,
        "required_field_completeness": {
            k: f"{v}/{num_records} ({round(v/max(num_records, 1)*100, 1)}%)"
            for k, v in field_completeness.items()
        },
        "total_documented_interactions": total_interactions,
        "medicines_cataloged": [r.get("generic_name") for r in records]
    }
    
    return report

def run_inspection():
    """Executes full inspection and prints formatted findings."""
    logger.info("Running dataset schema inspection...")
    symptom_report = inspect_symptom_dataset()
    med_report = inspect_medicine_dataset()
    
    combined_report = {
        "symptom_dataset_inspection": symptom_report,
        "medicine_dataset_inspection": med_report
    }
    
    out_file = os.path.join(REPORTS_DIR, "schema_inspection_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(combined_report, f, indent=2)
        
    logger.info(f"Inspection complete. Saved to: {out_file}")
    print("\n" + "="*60)
    print("SYMPTOM DATASET INSPECTION")
    print("="*60)
    print(f"Total Cases: {symptom_report['row_count']}")
    print(f"Total Features (Symptoms): {symptom_report['feature_count']}")
    print(f"Target Column: {symptom_report['target_column']}")
    print(f"Number of Disease Classes: {symptom_report['num_classes']}")
    print(f"Missing Values: {symptom_report['total_missing_values']}")
    print(f"Exact Duplicates: {symptom_report['num_exact_duplicates']}")
    print(f"Class Imbalance Ratio: {symptom_report['class_imbalance_ratio']}")
    
    print("\n" + "="*60)
    print("MEDICINE DATASET INSPECTION")
    print("="*60)
    print(f"Total Medicines Cataloged: {med_report['record_count']}")
    print(f"Total Documented Drug Interactions: {med_report['total_documented_interactions']}")
    print("Completeness:")
    for field, val in med_report['required_field_completeness'].items():
        print(f"  - {field}: {val}")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_inspection()
