"""Tests for the Vercel serverless function entrypoint (api/index.py)."""
import json
import io
import pytest
import api.index as ai

def call_wsgi(path, method="GET", body_dict=None):
    status_code = None
    response_headers = []
    def start_response(status, headers):
        nonlocal status_code, response_headers
        status_code = status
        response_headers = headers

    body_bytes = b""
    if body_dict is not None:
        body_bytes = json.dumps(body_dict).encode("utf-8")

    environ = {
        "PATH_INFO": path,
        "REQUEST_METHOD": method,
        "CONTENT_LENGTH": str(len(body_bytes)),
        "wsgi.input": io.BytesIO(body_bytes),
        "QUERY_STRING": ""
    }
    response_iter = ai.app(environ, start_response)
    data = b"".join(response_iter)
    headers_dict = dict(response_headers)
    return status_code, headers_dict, data

def test_api_health():
    status, headers, body = call_wsgi("/api/health")
    assert status == "200 OK"
    assert "application/json" in headers.get("Content-Type", "")
    data = json.loads(body.decode("utf-8"))
    assert data["status"] == "healthy"
    assert "endpoints" in data

def test_api_predict_success():
    payload = {"text": "I have a high fever, severe headache, and chills"}
    status, headers, body = call_wsgi("/api/predict", method="POST", body_dict=payload)
    assert status == "200 OK"
    data = json.loads(body.decode("utf-8"))
    assert data["status"] == "PREDICTION_SUCCESS"
    assert len(data["predictions"]) > 0
    assert "chills" in data["extracted_symptoms"]

def test_api_predict_abstain_no_symptoms():
    payload = {"text": "Hello, good morning how are you"}
    status, headers, body = call_wsgi("/api/predict", method="POST", body_dict=payload)
    assert status == "200 OK"
    data = json.loads(body.decode("utf-8"))
    assert data["status"] == "ABSTAIN_NO_SYMPTOMS"
    assert len(data["predictions"]) == 0

def test_api_safety_interaction():
    payload = {"drugs": ["Warfarin", "Ibuprofen"], "allergies": ["penicillin"]}
    status, headers, body = call_wsgi("/api/safety", method="POST", body_dict=payload)
    assert status == "200 OK"
    data = json.loads(body.decode("utf-8"))
    assert len(data["drug_interactions"]) > 0

def test_api_triage_emergency():
    payload = {"text": "I have crushing chest pain radiating to my left arm and jaw"}
    status, headers, body = call_wsgi("/api/triage", method="POST", body_dict=payload)
    assert status == "200 OK"
    data = json.loads(body.decode("utf-8"))
    assert data["emergency_detected"] is True

def test_api_medicines_search():
    status, headers, body = call_wsgi("/api/medicines")
    assert status == "200 OK"
    data = json.loads(body.decode("utf-8"))
    assert "medicines" in data
    assert data["count"] > 0

def test_static_html_served():
    status, headers, body = call_wsgi("/")
    assert status == "200 OK"
    assert "text/html" in headers.get("Content-Type", "")
    assert b"MediGuide AI" in body

def test_static_css_served():
    status, headers, body = call_wsgi("/style.css")
    assert status == "200 OK"
    assert "text/css" in headers.get("Content-Type", "")

def test_static_js_served():
    status, headers, body = call_wsgi("/app.js")
    assert status == "200 OK"
    assert "application/javascript" in headers.get("Content-Type", "")

def test_cors_headers_present():
    status, headers, body = call_wsgi("/api/health")
    assert headers.get("Access-Control-Allow-Origin") == "*"
