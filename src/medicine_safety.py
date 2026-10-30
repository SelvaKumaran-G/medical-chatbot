"""
MediGuide AI - Medicine Safety and Drug Interaction Engine
Evaluates pairwise drug-drug interactions, checks patient medicine allergies,
screens pre-existing chronic conditions/diseases, age-range vulnerabilities,
and generates clinical safety alerts for vulnerable patient groups.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
MEDICINES_PATH = os.path.join(PROCESSED_DATA_DIR, "medicines_cleaned.json")

# Verified Allergy Class Cross-Reactivity Mapping
ALLERGY_CROSS_REACTIVITY: Dict[str, Dict[str, Any]] = {
    "penicillin": {
        "flagged_keywords": ["amoxicillin", "ampicillin", "penicillin", "piperacillin", "augmentin"],
        "risk_description": "Severe hypersensitivity / anaphylaxis risk due to shared beta-lactam core."
    },
    "nsaid": {
        "flagged_keywords": ["ibuprofen", "aspirin", "naproxen", "diclofenac", "advil", "motrin", "brufen"],
        "risk_description": "Aspirin/NSAID hypersensitivity: risk of bronchospasm, urticaria, or anaphylactoid reaction."
    },
    "sulfa": {
        "flagged_keywords": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine"],
        "risk_description": "Sulfonamide antimicrobial allergy cross-reactivity."
    },
    "acetaminophen": {
        "flagged_keywords": ["paracetamol", "acetaminophen", "tylenol", "calpol", "dolo"],
        "risk_description": "Rare paracetamol hypersensitivity or acute cutaneous reaction risk."
    }
}

# Preexisting Diseases / Conditions vs Drug Contraindications & Warnings
PREEXISTING_DISEASE_RULES: Dict[str, List[Dict[str, Any]]] = {
    "kidney": [
        {
            "drug_keywords": ["ibuprofen", "aspirin", "naproxen", "diclofenac", "advil", "motrin", "brufen"],
            "severity": "CONTRAINDICATED",
            "warning": "NSAIDs inhibit renal prostaglandins, precipitating acute kidney injury (AKI) and worsening renal clearance."
        },
        {
            "drug_keywords": ["metformin", "glycomet", "glucophage"],
            "severity": "HIGH RISK / CAUTION",
            "warning": "Risk of life-threatening lactic acidosis in impaired renal function (eGFR < 30 mL/min). Requires eGFR monitoring."
        },
        {
            "drug_keywords": ["amoxicillin", "augmentin"],
            "severity": "CAUTION",
            "warning": "Excreted primarily through kidneys; clinical dose reduction required based on creatinine clearance."
        }
    ],
    "liver": [
        {
            "drug_keywords": ["paracetamol", "acetaminophen", "tylenol", "calpol", "dolo", "crocin"],
            "severity": "HIGH RISK / CAUTION",
            "warning": "Compromised hepatic glutathione reserves heighten acute liver injury risk. Strictly cap at max 2,000 mg/day or avoid in severe cirrhosis."
        },
        {
            "drug_keywords": ["atorvastatin", "lipitor", "statin"],
            "severity": "CONTRAINDICATED",
            "warning": "Contraindicated in active liver disease with unexplained persistent transaminase elevations."
        }
    ],
    "asthma": [
        {
            "drug_keywords": ["ibuprofen", "aspirin", "naproxen", "diclofenac", "advil", "motrin", "brufen"],
            "severity": "HIGH RISK / CONTRAINDICATED",
            "warning": "Risk of Aspirin-Exacerbated Respiratory Disease (AERD) precipitating severe, life-threatening bronchospasm in asthmatic patients."
        },
        {
            "drug_keywords": ["propranolol", "atenolol", "beta blocker"],
            "severity": "CONTRAINDICATED",
            "warning": "Non-cardioselective beta-blockers antagonize beta-2 receptors, causing severe refractory bronchoconstriction."
        }
    ],
    "ulcer": [
        {
            "drug_keywords": ["ibuprofen", "aspirin", "naproxen", "diclofenac", "advil", "motrin", "brufen"],
            "severity": "SEVERE CONTRAINDICATION",
            "warning": "Inhibits COX-1 protective gastric prostaglandins, causing recurrent ulceration, perforation, and catastrophic GI bleeding."
        }
    ],
    "hypertension": [
        {
            "drug_keywords": ["ibuprofen", "aspirin", "naproxen", "diclofenac", "advil", "motrin", "brufen"],
            "severity": "MODERATE CAUTION",
            "warning": "Causes sodium retention, blunts efficacy of ACE inhibitors and diuretics, and elevates mean arterial blood pressure."
        }
    ],
    "heart": [
        {
            "drug_keywords": ["ibuprofen", "advil", "motrin", "brufen"],
            "severity": "HIGH RISK / CONTRAINDICATED",
            "warning": "FDA Black Box Warning: Elevated risk of cardiovascular thrombotic events, myocardial infarction, and fluid retention in heart disease."
        }
    ],
    "diabetes": [
        {
            "drug_keywords": ["pseudoephedrine", "decongestant", "steroid"],
            "severity": "CAUTION",
            "warning": "May induce acute hyperglycemia and destabilize tight glycemic control."
        }
    ]
}

# Age-Specific Safety Rules
AGE_SAFETY_RULES: Dict[str, List[Dict[str, Any]]] = {
    "pediatric": [
        {
            "drug_keywords": ["aspirin"],
            "severity": "STRICT CONTRAINDICATION",
            "warning": "Strictly contraindicated in children/adolescents with viral symptoms due to fatal Reye's Syndrome risk."
        },
        {
            "drug_keywords": ["ibuprofen", "paracetamol", "amoxicillin"],
            "severity": "PEDIATRIC DOSING REQUIRED",
            "warning": "Adult tablets must NOT be given to children. Use weight-based pediatric liquid/drops under pediatrician prescription."
        }
    ],
    "geriatric": [
        {
            "drug_keywords": ["cetirizine", "antihistamine", "sedative"],
            "severity": "CAUTION (Beers Criteria)",
            "warning": "Anticholinergic burden in seniors: somnolence, increased fall risk, confusion, and urinary retention."
        },
        {
            "drug_keywords": ["ibuprofen", "nsaid"],
            "severity": "HIGH RISK IN ELDERLY",
            "warning": "Markedly elevated vulnerability to acute peptic ulcer hemorrhage and acute renal decline in individuals aged 65+."
        }
    ]
}

class MedicineSafetyChecker:
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
            
        self.med_by_name = {}
        for m in self.medicines:
            self.med_by_name[m["generic_name"].lower()] = m
            base = m["generic_name"].split("(")[0].strip().lower()
            self.med_by_name[base] = m
            for b in m.get("brand_names", []):
                self.med_by_name[b.lower()] = m

    def check_drug_interactions(self, drug_list: List[str]) -> List[Dict[str, Any]]:
        """
        Evaluates all pairs in a list of medications for documented drug-drug interactions.
        Returns detailed severity ratings and clinical mechanism explanations.
        """
        interactions_found = []
        clean_drugs = [d.strip().lower() for d in drug_list if d.strip()]
        
        for i in range(len(clean_drugs)):
            for j in range(i + 1, len(clean_drugs)):
                drug1 = clean_drugs[i]
                drug2 = clean_drugs[j]
                
                med1 = self.med_by_name.get(drug1)
                med2 = self.med_by_name.get(drug2)
                
                matched = False
                if med1:
                    for inter in med1.get("drug_interactions", []):
                        target = inter.get("interacting_drug", "").lower()
                        if target in drug2 or drug2 in target or (med2 and target in med2["generic_name"].lower()):
                            interactions_found.append({
                                "drug_a": med1["generic_name"],
                                "drug_b": drug2.title(),
                                "severity": inter.get("severity", "Moderate"),
                                "clinical_effect": inter.get("effect", "Potential interaction."),
                                "recommendation": "Avoid concurrent use or consult a prescribing doctor immediately.",
                                "source_org": med1.get("source_org", "US FDA / DailyMed"),
                                "source_url": med1.get("source_url", "")
                            })
                            matched = True
                            break
                            
                if not matched and med2:
                    for inter in med2.get("drug_interactions", []):
                        target = inter.get("interacting_drug", "").lower()
                        if target in drug1 or drug1 in target or (med1 and target in med1["generic_name"].lower()):
                            interactions_found.append({
                                "drug_a": med2["generic_name"],
                                "drug_b": drug1.title(),
                                "severity": inter.get("severity", "Moderate"),
                                "clinical_effect": inter.get("effect", "Potential interaction."),
                                "recommendation": "Avoid concurrent use or consult a prescribing doctor immediately.",
                                "source_org": med2.get("source_org", "US FDA / DailyMed"),
                                "source_url": med2.get("source_url", "")
                            })
                            break

        return interactions_found

    def check_polypharmacy_interactions(self, drug_list: List[str]) -> Dict[str, Any]:
        """
        Evaluates multi-drug interactions across a patient's polypharmacy regimen.
        Returns a structured dictionary report of interactions found.
        """
        hits = self.check_drug_interactions(drug_list)
        return {
            "drugs_evaluated": drug_list,
            "interactions_found": hits,
            "total_interactions": len(hits)
        }

    def check_allergy_risks(self, candidate_medication: str, patient_allergies: List[str]) -> List[Dict[str, Any]]:
        """
        Checks whether a candidate medicine triggers known patient allergies.
        """
        allergy_alerts = []
        med_lower = candidate_medication.strip().lower()
        
        for allergy in patient_allergies:
            a_clean = allergy.strip().lower()
            
            # Check direct name match
            if a_clean in med_lower or med_lower in a_clean:
                allergy_alerts.append({
                    "allergy_reported": allergy,
                    "conflicting_medicine": candidate_medication,
                    "severity": "CONTRAINDICATED / HIGH RISK",
                    "clinical_warning": f"Direct match with reported patient allergy to '{allergy}'."
                })
                continue
                
            # Check cross-reactive classes
            for class_key, class_info in ALLERGY_CROSS_REACTIVITY.items():
                if class_key in a_clean or any(k in a_clean for k in class_info["flagged_keywords"]):
                    if any(k in med_lower for k in class_info["flagged_keywords"]):
                        allergy_alerts.append({
                            "allergy_reported": allergy,
                            "conflicting_medicine": candidate_medication,
                            "severity": "SEVERE CONTRAINDICATION",
                            "clinical_warning": class_info["risk_description"]
                        })
                        break

        return allergy_alerts

    def evaluate_patient_profile(self, candidate_medication: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive clinical evaluation of medicine safety against patient context:
        - Age bracket / range
        - Pre-existing chronic diseases / health issues
        - Allergies
        - Pregnancy & breastfeeding
        - Current medications
        """
        med_rec = self.med_by_name.get(candidate_medication.strip().lower())
        med_lower = candidate_medication.strip().lower()
        alerts = []
        
        # 1. Check Allergies
        allergies = profile.get("known_allergies", [])
        if allergies:
            allergy_hits = self.check_allergy_risks(candidate_medication, allergies)
            alerts.extend(allergy_hits)
            
        # 2. Check Pre-existing Diseases / Health Issues
        diseases = profile.get("preexisting_conditions", [])
        for dis in diseases:
            dis_lower = dis.lower()
            for rule_key, rule_items in PREEXISTING_DISEASE_RULES.items():
                if rule_key in dis_lower:
                    for rule in rule_items:
                        if any(kw in med_lower for kw in rule["drug_keywords"]):
                            alerts.append({
                                "category": f"Preexisting Disease: {dis}",
                                "severity": rule["severity"],
                                "conflicting_medicine": candidate_medication,
                                "clinical_warning": rule["warning"]
                            })

        # 3. Check Age Range / Bracket
        age_bracket = profile.get("age_range", "").lower()
        age_num = profile.get("age", 30)
        is_pediatric = "child" in age_bracket or "infant" in age_bracket or "toddler" in age_bracket or age_num < 13
        is_geriatric = "senior" in age_bracket or "elderly" in age_bracket or "geriatric" in age_bracket or age_num >= 65

        if is_pediatric:
            for rule in AGE_SAFETY_RULES["pediatric"]:
                if any(kw in med_lower for kw in rule["drug_keywords"]):
                    alerts.append({
                        "category": "Age Safety (Pediatric)",
                        "severity": rule["severity"],
                        "conflicting_medicine": candidate_medication,
                        "clinical_warning": rule["warning"]
                    })
        elif is_geriatric:
            for rule in AGE_SAFETY_RULES["geriatric"]:
                if any(kw in med_lower for kw in rule["drug_keywords"]):
                    alerts.append({
                        "category": "Age Safety (Geriatric 65+)",
                        "severity": rule["severity"],
                        "conflicting_medicine": candidate_medication,
                        "clinical_warning": rule["warning"]
                    })

        # 4. Check Pregnancy / Breastfeeding
        is_pregnant = profile.get("is_pregnant", False)
        if is_pregnant and med_rec:
            preg_warn = med_rec.get("pregnancy_breastfeeding", "")
            if "avoid" in preg_warn.lower() or "contraindicated" in preg_warn.lower() or "category c" in preg_warn.lower():
                alerts.append({
                    "category": "Pregnancy Safety Warning",
                    "severity": "HIGH RISK / CAUTION",
                    "conflicting_medicine": candidate_medication,
                    "clinical_warning": f"Pregnancy Precaution: {preg_warn}"
                })
                
        # 5. Check Current Medication Interactions
        current_meds = profile.get("current_medications", [])
        if current_meds:
            inter_hits = self.check_drug_interactions([candidate_medication] + current_meds)
            for hit in inter_hits:
                alerts.append({
                    "category": "Drug Interaction",
                    "severity": hit["severity"],
                    "conflicting_medicine": f"{hit['drug_a']} + {hit['drug_b']}",
                    "clinical_warning": hit["clinical_effect"],
                    "recommendation": hit["recommendation"]
                })

        overall_status = "SAFE_NO_KNOWN_CONFLICTS"
        if any("contraindicated" in a.get("severity", "").lower() for a in alerts):
            overall_status = "CONTRAINDICATED"
        elif alerts:
            overall_status = "CAUTION_ALERTS_PRESENT"

        return {
            "medicine_evaluated": candidate_medication,
            "overall_safety_status": overall_status,
            "safety_alerts": alerts,
            "total_alerts": len(alerts)
        }

    def evaluate_disease_profile_impact(self, predicted_condition: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes how the patient's existing chronic diseases, health issues, and age bracket
        impact the vulnerability, clinical course, and precautions for the predicted condition.
        """
        cond_lower = predicted_condition.lower()
        diseases = profile.get("preexisting_conditions", [])
        age_range = profile.get("age_range", "Adult (18-64 yrs)")
        age_num = profile.get("age", 30)

        vulnerabilities = []
        tailored_advice = []

        # Age impacts
        if "child" in age_range.lower() or "infant" in age_range.lower() or age_num < 13:
            vulnerabilities.append("Pediatric physiology: Children have higher fluid turnover and rapid dehydration risk with fever/vomiting.")
            tailored_advice.append("Maintain rigorous hydration with oral electrolytes. Never administer adult tablets or Aspirin. Seek pediatric consultation promptly.")
        elif "senior" in age_range.lower() or "elderly" in age_range.lower() or age_num >= 65:
            vulnerabilities.append("Geriatric vulnerability: Seniors have lower cardiovascular reserve, blunted febrile responses, and heightened fall/dehydration risks.")
            tailored_advice.append("Closely monitor hydration, blood pressure, and mental alertness. Avoid sudden posture changes.")

        # Chronic condition impacts
        for d in diseases:
            d_low = d.lower()
            if "diabetes" in d_low:
                vulnerabilities.append(f"Pre-existing {d}: Acute infection triggers stress hormones (cortisol, epinephrine) causing sharp glycemic spikes or severe hypoglycemia.")
                tailored_advice.append("Increase blood glucose monitoring frequency (every 4-6 hours) and watch for ketones or extreme thirst.")
            elif "hypertension" in d_low or "heart" in d_low:
                vulnerabilities.append(f"Pre-existing {d}: Systemic infection and fever increase cardiac workload, heart rate, and metabolic oxygen demand.")
                tailored_advice.append("Monitor blood pressure regularly. Avoid OTC decongestants and NSAIDs which aggravate hypertension.")
            elif "kidney" in d_low or "renal" in d_low:
                vulnerabilities.append(f"Pre-existing {d}: Decreased renal filtration impairs excretion of medications and metabolites.")
                tailored_advice.append("Strictly avoid all NSAID pain relievers (Ibuprofen/Naproxen). Maintain adequate fluid intake under nephrology guidance.")
            elif "asthma" in d_low or "copd" in d_low:
                vulnerabilities.append(f"Pre-existing {d}: Viral or bacterial infections frequently trigger reactive airway bronchospasm.")
                tailored_advice.append("Keep short-acting beta-agonist rescue inhaler (Salbutamol) immediately accessible. Track peak flow readings.")
            elif "liver" in d_low or "hepatic" in d_low:
                vulnerabilities.append(f"Pre-existing {d}: Impaired hepatic drug metabolism raises risk of drug-induced hepatotoxicity.")
                tailored_advice.append("Keep Paracetamol below 2,000 mg/24h or use alternative fever reduction methods under physician care.")
            elif "ulcer" in d_low or "gerd" in d_low:
                vulnerabilities.append(f"Pre-existing {d}: Gastrointestinal mucosa is sensitized to acid erosions and bleeding.")
                tailored_advice.append("Do not consume NSAIDs or aspirin. Take prescribed acid-suppression therapy (Omeprazole) as directed.")

        return {
            "has_profile_risks": len(vulnerabilities) > 0,
            "vulnerabilities": vulnerabilities,
            "tailored_advice": tailored_advice,
            "age_range": age_range,
            "preexisting_conditions": diseases
        }

_SAFETY_CHECKER_INSTANCE = None

def get_safety_checker() -> MedicineSafetyChecker:
    """Returns singleton instance of MedicineSafetyChecker."""
    global _SAFETY_CHECKER_INSTANCE
    if _SAFETY_CHECKER_INSTANCE is None:
        _SAFETY_CHECKER_INSTANCE = MedicineSafetyChecker()
    return _SAFETY_CHECKER_INSTANCE
