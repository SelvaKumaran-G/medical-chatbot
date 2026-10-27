"""
MediGuide AI - Medical & Symptom Data Sources Registry
Contains documented metadata, schemas, terms of use, licenses, and jurisdictional caveats.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class DataSourceMetadata:
    name: str
    category: str  # 'symptom_prediction', 'medicine_information', 'clinical_guidelines'
    source_url: str
    license_type: str
    version: str
    jurisdiction: str
    terms_summary: str
    limitations: str
    retrieval_date: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))

DATA_SOURCES_REGISTRY: Dict[str, DataSourceMetadata] = {
    "disease_symptom_benchmark": DataSourceMetadata(
        name="Disease-Symptom Multivariable Benchmark Dataset",
        category="symptom_prediction",
        source_url="https://huggingface.co/datasets/disease-symptoms-benchmark",
        license_type="CC-BY 4.0 / Open Data",
        version="2.1.0",
        jurisdiction="Global (Research / Educational)",
        terms_summary="Freely available for educational and non-commercial research under CC-BY 4.0.",
        limitations=(
            "Educational and research prototype dataset. Synthesized from standardized medical symptom matrices. "
            "It must NOT be treated as a clinically validated diagnostic tool or used as a substitute for professional "
            "laboratory pathology or doctor diagnosis."
        )
    ),
    "openfda_drug_labeling": DataSourceMetadata(
        name="openFDA Drug Product Labeling API",
        category="medicine_information",
        source_url="https://open.fda.gov/apis/drug/label/",
        license_type="CC0 1.0 Universal / US Public Domain",
        version="v2 (Live API)",
        jurisdiction="United States (US FDA)",
        terms_summary="Public domain data provided by the US Food and Drug Administration.",
        limitations=(
            "openFDA data reflects US-approved drug product labels. Adverse-event reports do not demonstrate "
            "causality. Drug approvals and formulations in other jurisdictions (such as India under CDSCO) may differ."
        )
    ),
    "dailymed_nlm": DataSourceMetadata(
        name="DailyMed National Library of Medicine",
        category="medicine_information",
        source_url="https://dailymed.nlm.nih.gov/dailymed/",
        license_type="NLM Terms of Service / Public Domain",
        version="2026 Monthly Release",
        jurisdiction="United States",
        terms_summary="Official provider of FDA label information (package inserts).",
        limitations="Package inserts may not reflect off-label or regional practice variations."
    ),
    "rxnorm_nlm": DataSourceMetadata(
        name="RxNorm Standardized Nomenclature for Clinical Drugs",
        category="medicine_information",
        source_url="https://www.nlm.nih.gov/research/umls/rxnorm/index.html",
        license_type="UMLS Metathesaurus License",
        version="2026.04",
        jurisdiction="United States / International standard",
        terms_summary="Normalized names and unique identifiers for medicines and clinical ingredients.",
        limitations="Semantic mappings should be validated against current regional pharmacopeias."
    ),
    "cdsco_india": DataSourceMetadata(
        name="Central Drugs Standard Control Organisation (CDSCO) India",
        category="medicine_information",
        source_url="https://cdscoonline.gov.in/CDSCO/",
        license_type="Government of India Open Data",
        version="National List of Essential Medicines (NLEM)",
        jurisdiction="India",
        terms_summary="Statutory authority for regulatory approval and pharmaceutical control in India.",
        limitations=(
            "US FDA labels cannot be presumed active or identical in India without independent CDSCO Schedule H/H1 "
            "verification."
        )
    ),
    "emergency_clinical_triage": DataSourceMetadata(
        name="Emergency Medical Triage Red-Flag Protocols",
        category="clinical_guidelines",
        source_url="https://www.cdc.gov/triage / https://www.who.int/emergencies",
        license_type="Public Health Guidelines",
        version="2026 Edition",
        jurisdiction="Global",
        terms_summary="Verified red-flag indicators for life-threatening conditions requiring emergency medical service.",
        limitations="Emergency triage rules are safety heuristics and do not constitute an exhaustive emergency assessment."
    )
}

def get_source_metadata(source_key: str) -> Optional[DataSourceMetadata]:
    """Retrieve metadata for a specified data source."""
    return DATA_SOURCES_REGISTRY.get(source_key)

def list_all_sources() -> List[DataSourceMetadata]:
    """List all registered data sources."""
    return list(DATA_SOURCES_REGISTRY.values())
