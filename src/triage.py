"""
MediGuide AI - Emergency Red-Flag Triage & Clinical Safety Protocol
Performs immediate heuristic screening for life-threatening symptoms before
any predictive modeling or medicine retrieval.
"""

import re
from typing import Dict, List, Any, Optional

# Verified Emergency Red-Flag Heuristics (CDC, AHA, WHO Triage Standards)
EMERGENCY_RED_FLAGS: List[Dict[str, Any]] = [
    {
        "category": "Suspected Acute Coronary Syndrome (Heart Attack)",
        "patterns": [
            r"\b(crushing chest pain|chest pain radiating|pain in left arm|chest pressure and sweating|chest tightness and jaw pain|heart attack)\b",
            r"\b(heavy chest|squeezing chest pain|radiating to (?:arm|jaw|neck|back))\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Your symptoms suggest potential acute coronary syndrome / heart attack. "
            "Call 911 (US) or 112 / 102 (India) immediately. Do NOT drive yourself to the hospital. "
            "Sit down, rest, and await paramedics."
        )
    },
    {
        "category": "Suspected Acute Stroke (FAST Protocol)",
        "patterns": [
            r"\b(facial drooping|face droop|slurred speech|slurring words|one side weakness|paralysis of arm|cannot lift arm|sudden numbness on one side)\b",
            r"\b(stroke signs|loss of speech|face numbness)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Potential stroke symptoms detected (FAST: Face, Arms, Speech, Time). "
            "Call 911 or 112 / 102 immediately. Time lost is brain lost. Seek emergency hospital care right away."
        )
    },
    {
        "category": "Severe Respiratory Distress / Anaphylaxis",
        "patterns": [
            r"\b(cannot breathe|unable to breathe|gasping for air|turning blue|blue lips|swelling of throat|swelling of tongue|choking feeling|anaphylaxis)\b",
            r"\b(severe wheezing and swelling|throat closing)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Severe respiratory distress or life-threatening allergic reaction (anaphylaxis). "
            "Use an epinephrine auto-injector (EpiPen) if prescribed and available. Call emergency services immediately."
        )
    },
    {
        "category": "Altered Consciousness / Coma / Seizures",
        "patterns": [
            r"\b(unconscious|passed out|unresponsive|blacked out completely|prolonged seizure|coma|severe confusion)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Loss of consciousness or severe neurological compromise. "
            "Ensure the person is lying safely on their side (recovery position) and call emergency services immediately."
        )
    },
    {
        "category": "Severe Hemorrhage / Massive Bleeding",
        "patterns": [
            r"\b(coughing up blood|vomiting blood|large amount of blood|uncontrolled bleeding|stabbing pain with bleeding)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Severe hemorrhage or gastrointestinal bleeding. "
            "Seek immediate emergency trauma / medical care."
        )
    },
    {
        "category": "Suspected Meningitis / Thunderclap Headache",
        "patterns": [
            r"\b(worst headache of my life|thunderclap headache|stiff neck and high fever and confusion)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Potential intracranial event or meningitis. "
            "Seek urgent emergency neurological evaluation immediately."
        )
    }
]

def screen_emergency_red_flags(user_text: str) -> Dict[str, Any]:
    """
    Screens natural language text for life-threatening emergency medical red flags.
    Returns detection status, matched category, and immediate emergency protocols.
    """
    clean_input = user_text.lower()
    
    for flag in EMERGENCY_RED_FLAGS:
        for pat in flag["patterns"]:
            if re.search(pat, clean_input):
                return {
                    "is_emergency": True,
                    "urgency_level": "CRITICAL_RED_FLAG",
                    "category": flag["category"],
                    "emergency_protocol": flag["emergency_guidance"],
                    "action_required": (
                        "Stop self-assessment. Dial 911 / 112 / 102 or proceed immediately to the nearest Emergency Department."
                    )
                }

    return {
        "is_emergency": False,
        "urgency_level": "NON_EMERGENCY_ROUTINE",
        "category": None,
        "emergency_protocol": None,
        "action_required": "Proceed with clinical condition estimation and symptom review."
    }

def generate_triage_questions(patient_profile: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Generates tailored clinical follow-up questions to clarify non-emergency cases.
    """
    if patient_profile is None:
        patient_profile = {}
        
    questions = []
    
    if not patient_profile.get("age_group"):
        questions.append("What is your approximate age group (e.g. child, adult, elderly)?")
        
    if not patient_profile.get("duration"):
        questions.append("How many days or hours have you experienced these symptoms?")
        
    if not patient_profile.get("severity"):
        questions.append("On a scale of 1 to 10, how severe is your discomfort?")
        
    if "is_pregnant" not in patient_profile:
        questions.append("Are you currently pregnant or breastfeeding (if applicable)?")
        
    if not patient_profile.get("known_allergies"):
        questions.append("Do you have any known medicine allergies (e.g., penicillin, sulfa, aspirin)?")
        
    return questions[:3]

if __name__ == "__main__":
    test_1 = "I feel a crushing chest pain radiating to my left arm with cold sweats!"
    res_1 = screen_emergency_red_flags(test_1)
    print("\n--- EMERGENCY TRIAGE TEST 1 ---")
    print(f"Input: {test_1}")
    print(f"Is Emergency: {res_1['is_emergency']}")
    print(f"Category: {res_1['category']}")
    print(f"Guidance: {res_1['emergency_protocol']}")
    
    test_2 = "I have a mild runny nose and sneezing since yesterday."
    res_2 = screen_emergency_red_flags(test_2)
    print("\n--- EMERGENCY TRIAGE TEST 2 ---")
    print(f"Input: {test_2}")
    print(f"Is Emergency: {res_2['is_emergency']}")
