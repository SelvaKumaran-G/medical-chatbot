"""
MediGuide AI — Vercel Serverless Function & Clinical Engine Entrypoint
Handles clinical emergency triage, symptom NLP extraction, ML differential prediction,
verified medicine retrieval (FDA / CDSCO), and drug interaction safety checks.
Pure Python standard library implementation — zero heavy dependencies, ultra-fast cold start.
"""

import os
import sys
import json
import math
import re
import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional

# Ensure project directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ---------------------------------------------------------------------------
# Emergency Red-Flag Triage Protocols
# ---------------------------------------------------------------------------
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
            "CRITICAL MEDICAL EMERGENCY: Acute respiratory compromise or anaphylaxis detected. "
            "Seek emergency care / inject epinephrine auto-injector immediately if prescribed. Call 911 or 112."
        )
    },
    {
        "category": "Altered Mental Status / Prolonged Seizure",
        "patterns": [
            r"\b(unconscious|passed out|unresponsive|prolonged seizure|convulsing|coma|stupor)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Altered level of consciousness or status epilepticus. "
            "Call 911 or 112 immediately. Protect patient from injury, do not insert anything into mouth."
        )
    },
    {
        "category": "Active Massive Hemorrhage",
        "patterns": [
            r"\b(coughing up blood|vomiting blood|uncontrolled bleeding|gushing blood|spurting blood|black tarry stool)\b"
        ],
        "emergency_guidance": (
            "CRITICAL MEDICAL EMERGENCY: Active massive hemorrhage. "
            "Apply direct firm pressure with clean cloth and call 911 or 112 immediately."
        )
    }
]

def screen_emergency_red_flags_pure(user_text: str) -> Dict[str, Any]:
    text_lower = user_text.lower()
    for flag in EMERGENCY_RED_FLAGS:
        for pat in flag["patterns"]:
            if re.search(pat, text_lower, re.IGNORECASE):
                return {
                    "emergency_detected": True,
                    "is_emergency": True,
                    "category": flag["category"],
                    "guidance": flag["emergency_guidance"],
                    "matched_trigger": pat
                }
    return {
        "emergency_detected": False,
        "is_emergency": False,
        "category": None,
        "guidance": "No immediate life-threatening emergency red-flag triggers identified.",
        "matched_trigger": None
    }

try:
    from src.triage import screen_emergency_red_flags
except Exception:
    screen_emergency_red_flags = screen_emergency_red_flags_pure


# ---------------------------------------------------------------------------
# Data Resolution & Caching
# ---------------------------------------------------------------------------
_medicine_retriever = None
_safety_checker = None
_weights_cache = None
_vocab_cache = None
_meds_cache = None

def _resolve_data_file(filename: str) -> Optional[str]:
    candidates = [
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join(BASE_DIR, "data", "processed", filename),
        os.path.join(BASE_DIR, "models", filename),
        os.path.join(BASE_DIR, "public", filename),
        os.path.join(BASE_DIR, filename),
        filename
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            return c
    return None

def get_model_weights() -> Dict[str, Any]:
    global _weights_cache
    if _weights_cache is None:
        target = _resolve_data_file("model_weights.json")
        if target:
            try:
                with open(target, "r", encoding="utf-8") as f:
                    _weights_cache = json.load(f)
            except Exception:
                _weights_cache = {}
        else:
            _weights_cache = {}
    return _weights_cache

def get_medicines_data() -> List[Dict[str, Any]]:
    global _meds_cache
    if _meds_cache is None:
        for name in ("medicines.json", "medicines_cleaned.json"):
            target = _resolve_data_file(name)
            if target:
                try:
                    with open(target, "r", encoding="utf-8") as f:
                        _meds_cache = json.load(f)
                        break
                except Exception:
                    pass
        if _meds_cache is None:
            _meds_cache = []
    return _meds_cache


# ---------------------------------------------------------------------------
# Symptom Extraction (NLP with Negation Detection)
# ---------------------------------------------------------------------------
try:
    from src.preprocess_symptoms import extract_symptoms_from_text, SYMPTOM_SYNONYM_MAP
except Exception:
    SYMPTOM_SYNONYM_MAP = {
        "headache": "headache", "fever": "high_fever", "high fever": "high_fever",
        "chills": "chills", "shivering": "shivering", "cough": "cough",
        "chest pain": "chest_pain", "stomach pain": "stomach_pain",
        "vomiting": "vomiting", "nausea": "nausea", "fatigue": "fatigue",
        "weakness": "fatigue", "joint pain": "joint_pain", "skin rash": "skin_rash",
        "rash": "skin_rash", "itching": "itching", "shortness of breath": "breathlessness",
        "breathlessness": "breathlessness", "diarrhoea": "diarrhoea", "diarrhea": "diarrhoea",
        "acidity": "acidity", "indigestion": "indigestion", "muscle ache": "muscle_pain",
        "muscle pain": "muscle_pain", "back pain": "back_pain", "yellowish skin": "yellowish_skin",
        "loss of appetite": "loss_of_appetite", "weight loss": "weight_loss", "sweating": "sweating",
        "dizziness": "dizziness", "lethargy": "lethargy", "throat irritation": "throat_irritation"
    }

    def extract_symptoms_from_text(user_text: str) -> Dict[str, Any]:
        text = user_text.lower()
        neg_patterns = [
            r"(?:no|not|without|never|denies|negative for)\s+([a-z\s_-]{3,30})",
            r"([a-z\s_-]{3,30})\s+(?:is absent|is gone|resolved)"
        ]
        negated = set()
        for np in neg_patterns:
            for match in re.finditer(np, text):
                matched_phrase = match.group(1).strip()
                for syn, canonical in SYMPTOM_SYNONYM_MAP.items():
                    if syn in matched_phrase:
                        negated.add(canonical)

        confirmed = set()
        for syn, canonical in SYMPTOM_SYNONYM_MAP.items():
            if re.search(r"\b" + re.escape(syn) + r"\b", text):
                if canonical not in negated:
                    confirmed.add(canonical)

        return {
            "raw_text": user_text,
            "confirmed_symptoms": sorted(list(confirmed)),
            "negated_symptoms": sorted(list(negated)),
            "symptom_count": len(confirmed)
        }


# ---------------------------------------------------------------------------
# Medicine Retriever & Safety Checker Singletons
# ---------------------------------------------------------------------------
class FallbackMedicineRetriever:
    def __init__(self):
        self.medicines = get_medicines_data()

    def search_medicines(self, query: str) -> List[Dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return self.medicines[:10]
        results = []
        for m in self.medicines:
            if q in m.get("generic_name", "").lower():
                results.append(m)
            elif any(q in b.lower() for b in m.get("brand_names", [])):
                results.append(m)
            elif any(q in ind.lower() for ind in m.get("labeled_indications", [])):
                results.append(m)
        return results

    def get_labeled_medicines_for_condition(self, condition: str) -> List[Dict[str, Any]]:
        cond_clean = condition.strip().lower()
        matching = []
        for m in self.medicines:
            for ind in m.get("labeled_indications", []):
                if cond_clean in ind.lower() or ind.lower() in cond_clean:
                    matching.append(m)
                    break
        return matching

class FallbackSafetyChecker:
    INTERACTION_RULES = [
        {"drugs": ["warfarin", "ibuprofen"], "severity": "Severe / Contraindicated",
         "description": "Marked synergism causing severe gastrointestinal hemorrhage and bleeding risk."},
        {"drugs": ["aspirin", "ibuprofen"], "severity": "Major / Caution",
         "description": "NSAID competition reduces aspirin cardioprotection and compounds ulcer perforation risk."},
        {"drugs": ["metformin", "contrast"], "severity": "High Risk / Caution",
         "description": "Precipitates acute renal compromise and fatal lactic acidosis."},
        {"drugs": ["lisinopril", "potassium"], "severity": "Moderate / Caution",
         "description": "Additive hyperkalemia risk requiring electrolyte monitoring."}
    ]

    def check_drug_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        d_lower = [d.strip().lower() for d in drugs]
        hits = []
        for rule in self.INTERACTION_RULES:
            r_drugs = rule["drugs"]
            if all(any(rd in user_d for user_d in d_lower) for rd in r_drugs):
                d1 = drugs[0] if len(drugs) > 0 else r_drugs[0]
                d2 = drugs[1] if len(drugs) > 1 else r_drugs[1]
                hits.append({
                    "drug_a": d1,
                    "drug_b": d2,
                    "drug_1": d1,
                    "drug_2": d2,
                    "severity": rule["severity"],
                    "clinical_effect": rule["description"],
                    "risk_description": rule["description"],
                    "recommendation": "Avoid concurrent use or consult a healthcare professional immediately."
                })
        return hits

    def evaluate_patient_profile(self, drug_name: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        alerts = []
        d_clean = drug_name.lower()
        allergies = [a.lower() for a in profile.get("known_allergies", [])]
        if "penicillin" in allergies and any(k in d_clean for k in ["amoxicillin", "ampicillin", "penicillin"]):
            alerts.append({"type": "ALLERGY_CONTRAINDICATION", "severity": "CONTRAINDICATED",
                           "message": "Patient has reported Penicillin allergy. Beta-lactam antibiotic is contraindicated."})
        if "nsaid" in allergies and any(k in d_clean for k in ["ibuprofen", "aspirin", "naproxen", "diclofenac"]):
            alerts.append({"type": "ALLERGY_CONTRAINDICATION", "severity": "CONTRAINDICATED",
                           "message": "Patient has reported NSAID allergy. Risk of bronchospasm or anaphylactoid response."})
        return {"drug": drug_name, "safety_alerts": alerts}

def get_medicine_retriever():
    global _medicine_retriever
    if _medicine_retriever is None:
        try:
            from src.medicine_retrieval import MedicineRetriever
            _medicine_retriever = MedicineRetriever()
        except Exception:
            _medicine_retriever = FallbackMedicineRetriever()
    return _medicine_retriever

def get_safety_checker():
    global _safety_checker
    if _safety_checker is None:
        try:
            from src.medicine_safety import MedicineSafetyChecker
            _safety_checker = MedicineSafetyChecker()
        except Exception:
            _safety_checker = FallbackSafetyChecker()
    return _safety_checker


# ---------------------------------------------------------------------------
# ML Differential Prediction Engine (Pure Python Logistic Regression)
# ---------------------------------------------------------------------------
def predict_conditions_pure(active_symptoms: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    wdata = get_model_weights()
    if not wdata or "classes" not in wdata:
        return []

    classes = wdata["classes"]
    features = wdata["feature_names"]
    coef = wdata["coef"]
    intercept = wdata["intercept"]

    x = [1 if f in active_symptoms else 0 for f in features]
    z = [
        sum(coef[c][j] * x[j] for j in range(len(features))) + intercept[c]
        for c in range(len(classes))
    ]

    max_z = max(z)
    exp_z = [math.exp(val - max_z) for val in z]
    total_exp = sum(exp_z)
    probs = [val / total_exp for val in exp_z]

    ranked = sorted(zip(classes, probs), key=lambda item: item[1], reverse=True)[:top_k]

    results = []
    for cond, p in ranked:
        c_idx = classes.index(cond)
        expl = []
        for s in active_symptoms:
            if s in features:
                f_idx = features.index(s)
                w = coef[c_idx][f_idx]
                expl.append({
                    "symptom": s.replace("_", " "),
                    "weight": round(w, 3),
                    "impact": "High positive contribution" if w > 1.0 else ("Moderate contribution" if w > 0 else "Neutral")
                })
        expl.sort(key=lambda item: item["weight"], reverse=True)
        results.append({
            "condition": cond,
            "probability": round(p, 4),
            "percentage": f"{round(p * 100, 1)}%",
            "feature_explanations": expl
        })
    return results


# ---------------------------------------------------------------------------
# Request Handlers
# ---------------------------------------------------------------------------
def handle_predict_request(body: Dict[str, Any]) -> Dict[str, Any]:
    text = body.get("text", "")
    profile = body.get("patient_profile", {})

    triage_result = screen_emergency_red_flags(text)
    extraction = extract_symptoms_from_text(text)
    confirmed = extraction.get("confirmed_symptoms", [])
    negated = extraction.get("negated_symptoms", [])

    if not confirmed:
        predictions = []
        status = "ABSTAIN_NO_SYMPTOMS"
        message = (
            "No recognized clinical symptoms were identified in your description. "
            "Please describe your symptoms clearly (e.g., 'fever, headache, chills, cough')."
        )
        follow_ups = [
            "Where specifically are you experiencing pain or discomfort?",
            "How long have you felt unwell, and do you have a fever or rash?"
        ]
        ref_meds = []
        safety_alerts = []
    else:
        predictions = predict_conditions_pure(confirmed, top_k=3)
        status = "PREDICTION_SUCCESS"
        message = "Symptom analysis and ML differential diagnosis complete."
        follow_ups = [
            "Have your symptoms worsened or stayed the same over the last 24-48 hours?",
            "Are you currently taking any prescription medications or over-the-counter supplements?"
        ]

        retriever = get_medicine_retriever()
        top_condition = predictions[0]["condition"] if predictions else ""
        ref_meds = retriever.get_labeled_medicines_for_condition(top_condition) if top_condition else []

        safety_checker = get_safety_checker()
        safety_alerts = []
        if profile and ref_meds:
            clean_profile = {
                "known_allergies": profile.get("allergies", profile.get("known_allergies", [])),
                "preexisting_conditions": profile.get("preexisting_conditions", profile.get("conditions", [])),
                "age": profile.get("age", 30),
                "age_range": profile.get("age_range", ""),
                "is_pregnant": profile.get("is_pregnant", False)
            }
            for m in ref_meds:
                g_name = m.get("generic_name", "")
                if g_name:
                    eval_res = safety_checker.evaluate_patient_profile(g_name, clean_profile)
                    safety_alerts.extend(eval_res.get("safety_alerts", []))

    return {
        "status": status,
        "message": message,
        "triage": triage_result,
        "extracted_symptoms": confirmed,
        "negated_symptoms": negated,
        "predictions": predictions,
        "reference_medicines": ref_meds[:4],
        "safety_alerts": safety_alerts,
        "follow_up_questions": follow_ups,
        "disclaimer": (
            "⚠️ EDUCATIONAL RESEARCH PROTOTYPE ONLY: This system provides statistical predictions "
            "and information retrieval for research purposes. It is NOT a clinical diagnosis, "
            "prescription, or medical advice. Always consult a qualified medical professional."
        )
    }

def handle_safety_check(body: Dict[str, Any]) -> Dict[str, Any]:
    drugs = body.get("drugs", [])
    allergies = body.get("allergies", [])
    conditions = body.get("conditions", [])

    checker = get_safety_checker()
    interactions = checker.check_drug_interactions(drugs)

    profile = {
        "known_allergies": allergies,
        "preexisting_conditions": conditions,
        "current_medications": drugs[1:] if len(drugs) > 1 else []
    }

    patient_evals = []
    for d in drugs:
        ev = checker.evaluate_patient_profile(d, profile)
        patient_evals.append({"drug": d, "evaluation": ev})

    return {
        "drug_interactions": interactions,
        "patient_evaluations": patient_evals,
        "checked_drugs": drugs
    }

def handle_medicines_search(query: str, condition: str = "") -> Dict[str, Any]:
    retriever = get_medicine_retriever()
    if condition:
        results = retriever.get_labeled_medicines_for_condition(condition)
    elif query:
        results = retriever.search_medicines(query)
    else:
        results = getattr(retriever, "medicines", [])[:12]
    return {"count": len(results), "medicines": results}


# ---------------------------------------------------------------------------
# Static File Helper
# ---------------------------------------------------------------------------
def _find_static_file(filepath: str) -> Optional[str]:
    candidates = [
        os.path.join(BASE_DIR, "public", filepath),
        os.path.join(BASE_DIR, filepath),
        os.path.join(os.path.dirname(__file__), "..", "public", filepath),
        os.path.join(os.path.dirname(__file__), "..", filepath),
        os.path.join(os.path.dirname(__file__), filepath),
        filepath
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            return c
    return None

def _get_content_type(filepath: str) -> str:
    if filepath.endswith(".html"): return "text/html; charset=utf-8"
    if filepath.endswith(".css"): return "text/css; charset=utf-8"
    if filepath.endswith(".js"): return "application/javascript; charset=utf-8"
    if filepath.endswith(".json"): return "application/json; charset=utf-8"
    if filepath.endswith(".png"): return "image/png"
    if filepath.endswith(".jpg") or filepath.endswith(".jpeg"): return "image/jpeg"
    if filepath.endswith(".svg"): return "image/svg+xml"
    if filepath.endswith(".ico"): return "image/x-icon"
    ctype, _ = mimetypes.guess_type(filepath)
    return ctype or "text/plain; charset=utf-8"


# ---------------------------------------------------------------------------
# Vercel BaseHTTPRequestHandler
# ---------------------------------------------------------------------------
class handler(BaseHTTPRequestHandler):
    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_file(self, rel_path: str):
        found = _find_static_file(rel_path)
        if found:
            with open(found, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", _get_content_type(rel_path))
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json_response(404, {"error": f"File not found: {rel_path}"})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = urllib.parse.parse_qs(parsed.query)

        try:
            if path in ("/api/health", "/api"):
                self._send_json_response(200, {
                    "name": "MediGuide AI Clinical API",
                    "status": "healthy",
                    "version": "1.0.0",
                    "endpoints": ["/api/predict", "/api/safety", "/api/medicines", "/api/symptoms", "/api/health"]
                })
            elif path == "/api/medicines":
                q = query.get("query", [""])[0]
                cond = query.get("condition", [""])[0]
                self._send_json_response(200, handle_medicines_search(q, cond))
            elif path == "/api/symptoms":
                weights = get_model_weights()
                features = weights.get("feature_names", [])
                self._send_json_response(200, {"symptoms": [f.replace("_", " ") for f in features]})
            # Static file fallbacks
            elif path in ("", "/", "/index.html"):
                self._send_file("index.html")
            elif path == "/style.css":
                self._send_file("style.css")
            elif path == "/app.js":
                self._send_file("app.js")
            elif path == "/model_weights.json":
                self._send_file("model_weights.json")
            elif path == "/medicines.json":
                self._send_file("medicines.json")
            elif path == "/symptom_vocabulary.json":
                self._send_file("symptom_vocabulary.json")
            elif path.startswith("/assets/"):
                self._send_file(parsed.path.lstrip("/"))
            else:
                self._send_json_response(404, {"error": f"Endpoint not found: {self.path}"})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        try:
            if path == "/api/predict":
                self._send_json_response(200, handle_predict_request(body))
            elif path == "/api/safety":
                self._send_json_response(200, handle_safety_check(body))
            elif path == "/api/triage":
                text = body.get("text", "")
                self._send_json_response(200, screen_emergency_red_flags(text))
            else:
                self._send_json_response(404, {"error": f"Endpoint not found: {self.path}"})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})


# ---------------------------------------------------------------------------
# WSGI Application Handler (Compatible with Vercel WSGI / Gunicorn / uWSGI)
# ---------------------------------------------------------------------------
def app(environ, start_response):
    raw_path = environ.get("PATH_INFO", "/")
    path = raw_path.rstrip("/")
    method = environ.get("REQUEST_METHOD", "GET").upper()

    cors_headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization")
    ]

    if method == "OPTIONS":
        start_response("204 No Content", cors_headers)
        return [b""]

    # Read body for POST
    content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
    body_bytes = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"
    try:
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception:
        body = {}

    query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))

    try:
        # 1. API Endpoints
        if path in ("/api/health", "/api"):
            resp = json.dumps({
                "name": "MediGuide AI Clinical API",
                "status": "healthy",
                "version": "1.0.0",
                "endpoints": ["/api/predict", "/api/safety", "/api/medicines", "/api/symptoms", "/api/health"]
            }).encode("utf-8")
            start_response("200 OK", cors_headers + [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp)))
            ])
            return [resp]

        elif path == "/api/predict" and method == "POST":
            resp = json.dumps(handle_predict_request(body)).encode("utf-8")
            start_response("200 OK", cors_headers + [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp)))
            ])
            return [resp]

        elif path == "/api/safety" and method == "POST":
            resp = json.dumps(handle_safety_check(body)).encode("utf-8")
            start_response("200 OK", cors_headers + [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp)))
            ])
            return [resp]

        elif path == "/api/triage" and method == "POST":
            text = body.get("text", "")
            resp = json.dumps(screen_emergency_red_flags(text)).encode("utf-8")
            start_response("200 OK", cors_headers + [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp)))
            ])
            return [resp]

        elif path == "/api/medicines":
            q = query.get("query", [""])[0]
            cond = query.get("condition", [""])[0]
            resp = json.dumps(handle_medicines_search(q, cond)).encode("utf-8")
            start_response("200 OK", cors_headers + [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp)))
            ])
            return [resp]

        elif path == "/api/symptoms":
            weights = get_model_weights()
            features = weights.get("feature_names", [])
            resp = json.dumps({"symptoms": [f.replace("_", " ") for f in features]}).encode("utf-8")
            start_response("200 OK", cors_headers + [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp)))
            ])
            return [resp]

        # 2. Static Web App Files
        file_to_serve = None
        if path in ("", "/", "/index.html"):
            file_to_serve = "index.html"
        elif path in ("/style.css", "/app.js", "/model_weights.json", "/medicines.json", "/symptom_vocabulary.json"):
            file_to_serve = path.lstrip("/")
        elif path.startswith("/assets/"):
            file_to_serve = raw_path.lstrip("/")

        if file_to_serve:
            found = _find_static_file(file_to_serve)
            if found:
                with open(found, "rb") as f:
                    content = f.read()
                start_response("200 OK", cors_headers + [
                    ("Content-Type", _get_content_type(file_to_serve)),
                    ("Content-Length", str(len(content)))
                ])
                return [content]

        # 3. 404 Not Found
        err = json.dumps({"error": f"Endpoint not found: {raw_path}"}).encode("utf-8")
        start_response("404 Not Found", cors_headers + [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(err)))
        ])
        return [err]

    except Exception as e:
        err = json.dumps({"error": str(e)}).encode("utf-8")
        start_response("500 Internal Server Error", cors_headers + [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(err)))
        ])
        return [err]
