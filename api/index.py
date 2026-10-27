"""
MediGuide AI — Vercel Serverless Function Entrypoint
Official BaseHTTPRequestHandler implementation for Vercel Python Runtime.
Handles clinical triage, symptom entity extraction, ML differential prediction,
medicine retrieval, and drug-drug interaction safety checks.
"""

import os
import sys
import json
import math
import urllib.parse
from http.server import BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.triage import screen_emergency_red_flags
from src.preprocess_symptoms import extract_symptoms_from_text
from src.medicine_retrieval import MedicineRetriever
from src.medicine_safety import MedicineSafetyChecker

# Cache singletons
_medicine_retriever = None
_safety_checker = None
_weights_cache = None

def get_medicine_retriever():
    global _medicine_retriever
    if _medicine_retriever is None:
        _medicine_retriever = MedicineRetriever()
    return _medicine_retriever

def get_safety_checker():
    global _safety_checker
    if _safety_checker is None:
        _safety_checker = MedicineSafetyChecker()
    return _safety_checker

def get_model_weights():
    global _weights_cache
    if _weights_cache is None:
        weights_path = os.path.join(BASE_DIR, "models", "model_weights.json")
        if os.path.exists(weights_path):
            with open(weights_path, "r", encoding="utf-8") as f:
                _weights_cache = json.load(f)
        else:
            _weights_cache = {}
    return _weights_cache

def predict_conditions_pure(active_symptoms: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """Evaluates Logistic Regression using exported weights without requiring scikit-learn."""
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
        results = retriever.medicines[:10]
    return {"count": len(results), "medicines": results}


# =============================================================================
# Vercel Serverless HTTP Handler Class
# =============================================================================
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
            if path in ("/api/health", "/api") or path == "":
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


# WSGI application callable fallback for WSGI runners
def app(environ, start_response):
    path = environ.get("PATH_INFO", "/").rstrip("/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization")
    ]

    if method == "OPTIONS":
        start_response("204 No Content", headers)
        return [b""]

    content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
    body_bytes = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"
    try:
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception:
        body = {}

    query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))

    try:
        if path in ("/api/health", "/api") or path == "":
            start_response("200 OK", headers)
            return [json.dumps({"name": "MediGuide AI", "status": "healthy"}).encode("utf-8")]
        elif path == "/api/predict":
            start_response("200 OK", headers)
            return [json.dumps(handle_predict_request(body)).encode("utf-8")]
        elif path == "/api/safety":
            start_response("200 OK", headers)
            return [json.dumps(handle_safety_check(body)).encode("utf-8")]
        elif path == "/api/medicines":
            q = query.get("query", [""])[0]
            cond = query.get("condition", [""])[0]
            start_response("200 OK", headers)
            return [json.dumps(handle_medicines_search(q, cond)).encode("utf-8")]
        else:
            start_response("404 Not Found", headers)
            return [json.dumps({"error": "Not found"}).encode("utf-8")]
    except Exception as e:
        start_response("500 Internal Server Error", headers)
        return [json.dumps({"error": str(e)}).encode("utf-8")]
