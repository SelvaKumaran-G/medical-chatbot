"""
MediGuide AI - Data Quality Validation Module
Validates cleaned datasets, verifies absence of corrupted records,
checks class distribution balance, and generates structured data quality reports.
"""

import os
import json
import logging
import pandas as pd
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "data_quality")
os.makedirs(REPORTS_DIR, exist_ok=True)

def validate_processed_symptoms(csv_path: str = None) -> Dict[str, Any]:
    """Runs exhaustive data validation checks on the processed symptom dataset."""
    if csv_path is None:
        csv_path = os.path.join(PROCESSED_DATA_DIR, "symptoms_cleaned.csv")
        
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Processed symptom dataset not found at {csv_path}")
        
    df = pd.read_csv(csv_path)
    target_col = "prognosis"
    feature_cols = [c for c in df.columns if c != target_col]
    
    validation_status = "PASS"
    issues = []
    
    # 1. Missing value check
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    if total_nulls > 0:
        validation_status = "FAIL"
        issues.append(f"Found {total_nulls} null values across features.")
        
    # 2. Binary constraint check
    invalid_binary = 0
    for col in feature_cols:
        non_binary = df[~df[col].isin([0, 1])]
        if not non_binary.empty:
            invalid_binary += len(non_binary)
    if invalid_binary > 0:
        validation_status = "FAIL"
        issues.append(f"Found {invalid_binary} non-binary entries in symptom indicator matrix.")
        
    # 3. Degenerate zero-symptom row check
    row_sums = df[feature_cols].sum(axis=1)
    zero_symptom_rows = int((row_sums == 0).sum())
    if zero_symptom_rows > 0:
        validation_status = "WARN"
        issues.append(f"Found {zero_symptom_rows} cases with zero active symptoms.")
        
    # 4. Target class checks
    class_counts = df[target_col].value_counts().to_dict()
    num_classes = len(class_counts)
    min_count = min(class_counts.values())
    max_count = max(class_counts.values())
    imbalance_ratio = max_count / max(min_count, 1)
    
    if min_count < 10:
        validation_status = "WARN"
        issues.append(f"Rare class detected with fewer than 10 cases (min: {min_count}).")
        
    report = {
        "dataset_name": "Processed Disease Symptoms",
        "validation_status": validation_status,
        "total_cases": int(len(df)),
        "feature_count": len(feature_cols),
        "target_column": target_col,
        "num_classes": num_classes,
        "min_cases_per_class": int(min_count),
        "max_cases_per_class": int(max_count),
        "class_imbalance_ratio": round(imbalance_ratio, 3),
        "null_value_count": total_nulls,
        "zero_symptom_cases": zero_symptom_rows,
        "issues_detected": issues
    }
    return report

def validate_processed_medicines(json_path: str = None) -> Dict[str, Any]:
    """Validates completeness and integrity of the processed medicine knowledge base."""
    if json_path is None:
        json_path = os.path.join(PROCESSED_DATA_DIR, "medicines_cleaned.json")
        
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Processed medicine file not found at {json_path}")
        
    with open(json_path, "r", encoding="utf-8") as f:
        medicines = json.load(f)
        
    issues = []
    status = "PASS"
    
    for med in medicines:
        name = med.get("generic_name", "UNKNOWN")
        if not med.get("labeled_indications"):
            issues.append(f"Medicine '{name}' is missing labeled indications.")
        if not med.get("contraindications"):
            issues.append(f"Medicine '{name}' is missing contraindications.")
        if not med.get("warnings_and_precautions"):
            issues.append(f"Medicine '{name}' is missing warnings and precautions.")
        if not med.get("source_url"):
            issues.append(f"Medicine '{name}' is missing source URL citation.")
            
    if issues:
        status = "WARN" if len(issues) < 3 else "FAIL"
        
    report = {
        "dataset_name": "Processed Medicine Database",
        "validation_status": status,
        "total_records": len(medicines),
        "verified_with_citations": len([m for m in medicines if m.get("source_url")]),
        "total_issues": len(issues),
        "issues_detected": issues
    }
    return report

def generate_quality_report() -> Dict[str, Any]:
    """Generates and writes full data quality report in JSON and Markdown formats."""
    symptom_validation = validate_processed_symptoms()
    medicine_validation = validate_processed_medicines()
    
    full_report = {
        "overall_status": "PASS" if symptom_validation["validation_status"] == "PASS" and medicine_validation["validation_status"] == "PASS" else "REVIEW_NEEDED",
        "symptom_validation": symptom_validation,
        "medicine_validation": medicine_validation
    }
    
    # Save JSON report
    json_path = os.path.join(REPORTS_DIR, "data_quality_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
    logger.info(f"Saved data quality JSON report to: {json_path}")
    
    # Save Markdown report
    md_path = os.path.join(REPORTS_DIR, "data_quality_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# MediGuide AI - Data Quality & Integrity Report\n\n")
        f.write(f"**Overall Pipeline Status:** `{full_report['overall_status']}`\n\n")
        f.write("## 1. Symptom Dataset Validation\n\n")
        f.write(f"- **Status:** `{symptom_validation['validation_status']}`\n")
        f.write(f"- **Total Clinical Cases:** {symptom_validation['total_cases']}\n")
        f.write(f"- **Feature Dimension (Symptoms):** {symptom_validation['feature_count']}\n")
        f.write(f"- **Target Conditions:** {symptom_validation['num_classes']}\n")
        f.write(f"- **Class Imbalance Ratio:** {symptom_validation['class_imbalance_ratio']}\n")
        f.write(f"- **Null Values:** {symptom_validation['null_value_count']}\n\n")
        
        f.write("## 2. Medicine Knowledge Base Validation\n\n")
        f.write(f"- **Status:** `{medicine_validation['validation_status']}`\n")
        f.write(f"- **Total Cataloged Medicines:** {medicine_validation['total_records']}\n")
        f.write(f"- **Verified with Source Citations:** {medicine_validation['verified_with_citations']}\n")
        f.write(f"- **Issues Detected:** {medicine_validation['total_issues']}\n\n")
        
        f.write("## 3. Regulatory and Jurisdictional Notes\n\n")
        f.write("- Data reflects standardized educational and open FDA/CDSCO knowledge repositories.\n")
        f.write("- All predictions generated by downstream models are statistical correlations, not certified medical diagnoses.\n")
        
    logger.info(f"Saved data quality Markdown report to: {md_path}")
    return full_report

if __name__ == "__main__":
    generate_quality_report()
