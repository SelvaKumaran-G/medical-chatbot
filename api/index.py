"""
MediGuide AI — Vercel Serverless API & WSGI Entrypoint
Ultra-lightweight, zero-heavy-dependency REST API for clinical triage, symptom extraction,
ML condition prediction, verified medicine retrieval, and safety interaction screening.
"""

import os
import sys
import json
import math
import urllib.parse
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

    # Compute dot product
    x = [1 if f in active_symptoms else 0 for f in features]
    z = [
        sum(coef[c][j] * x[j] for j in range(len(features))) + intercept[c]
        for c in range(len(classes))
    ]

    # Softmax with numerical stability
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

    # 1. Emergency Heuristics Triage
    triage_result = screen_emergency_red_flags(text)

    # 2. Extract Symptoms
    extraction = extract_symptoms_from_text(text)
    confirmed = extraction.get("confirmed_symptoms", [])
    negated = extraction.get("negated_symptoms", [])

    # 3. Model Predictions
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

        # 4. Medicine Retrieval for Top Condition
        retriever = get_medicine_retriever()
        top_condition = predictions[0]["condition"] if predictions else ""
        ref_meds = retriever.get_labeled_medicines_for_condition(top_condition) if top_condition else []

        # 5. Patient Profile Safety Evaluation
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

def app(environ, start_response):
    """Standard WSGI entrypoint callable for Vercel, Gunicorn, and WSGI servers."""
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()

    cors_headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization"),
    ]

    # Preflight CORS
    if method == "OPTIONS":
        start_response("204 No Content", cors_headers)
        return [b""]

    # Parse query params
    query_string = environ.get("QUERY_STRING", "")
    query_params = urllib.parse.parse_qs(query_string)

    # Read POST body
    body = {}
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            if content_length > 0:
                body_bytes = environ["wsgi.input"].read(content_length)
                body = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            body = {}

    headers = [("Content-Type", "application/json")] + cors_headers

    try:
        if path.endswith("/api/predict") or path == "/api/predict":
            data = handle_predict_request(body)
            start_response("200 OK", headers)
            return [json.dumps(data).encode("utf-8")]

        elif path.endswith("/api/safety") or path == "/api/safety":
            data = handle_safety_check(body)
            start_response("200 OK", headers)
            return [json.dumps(data).encode("utf-8")]

        elif path.endswith("/api/medicines") or path == "/api/medicines":
            q = query_params.get("query", [""])[0]
            cond = query_params.get("condition", [""])[0]
            data = handle_medicines_search(q, cond)
            start_response("200 OK", headers)
            return [json.dumps(data).encode("utf-8")]

        elif path.endswith("/api/triage") or path == "/api/triage":
            text = body.get("text", query_params.get("text", [""])[0])
            data = screen_emergency_red_flags(text)
            start_response("200 OK", headers)
            return [json.dumps(data).encode("utf-8")]

        elif path.endswith("/api/symptoms") or path == "/api/symptoms":
            weights = get_model_weights()
            features = weights.get("feature_names", [])
            start_response("200 OK", headers)
            return [json.dumps({"symptoms": [f.replace("_", " ") for f in features]}).encode("utf-8")]

        elif path.endswith("/api/health") or path == "/api/health" or path in ("/", "/api"):
            data = {
                "name": "MediGuide AI Clinical API",
                "version": "1.0.0",
                "status": "healthy",
                "deployment": "Vercel Serverless / WSGI",
                "endpoints": [
                    "POST /api/predict",
                    "GET /api/medicines",
                    "POST /api/safety",
                    "POST /api/triage",
                    "GET /api/symptoms",
                    "GET /api/health"
                ]
            }
            start_response("200 OK", headers)
            return [json.dumps(data).encode("utf-8")]

        else:
            # 404
            start_response("404 Not Found", headers)
            return [json.dumps({"error": f"Endpoint not found: {path}"}).encode("utf-8")]

    except Exception as e:
        start_response("500 Internal Server Error", headers)
        return [json.dumps({"error": str(e)}).encode("utf-8")]

# Vercel entrypoint alias
handler = app
