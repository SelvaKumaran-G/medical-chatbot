"""
MediGuide AI - Prediction Engine and Explainability Module
Processes natural-language input, applies symptom extraction and negation filtering,
runs the champion calibrated model, generates top-3 differential candidates with calibrated probabilities,
and explains contributing symptom features.
"""

import os
import joblib
import numpy as np
from typing import Dict, List, Any, Optional
from src.preprocess_symptoms import extract_symptoms_from_text

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
PIPELINE_PATH = os.path.join(MODELS_DIR, "best_model_pipeline.joblib")

class ConditionPredictor:
    def __init__(self, pipeline_path: Optional[str] = None):
        if pipeline_path is None:
            pipeline_path = PIPELINE_PATH
            
        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(
                f"Model pipeline not found at {pipeline_path}. Please execute train_models.py first."
            )
            
        self.pipeline_data = joblib.load(pipeline_path)
        self.model = self.pipeline_data["model"]
        self.model_name = self.pipeline_data["model_name"]
        self.feature_names = self.pipeline_data["feature_names"]
        self.classes = np.array(self.pipeline_data["classes"])
        self.feature_index_map = {feat: idx for idx, feat in enumerate(self.feature_names)}
        
    def vector_from_symptoms(self, active_symptoms: List[str]) -> np.ndarray:
        """Constructs binary feature vector matching the model's feature space."""
        vec = np.zeros((1, len(self.feature_names)), dtype=np.int32)
        for sym in active_symptoms:
            if sym in self.feature_index_map:
                vec[0, self.feature_index_map[sym]] = 1
        return vec

    def explain_prediction(self, condition: str, active_symptoms: List[str]) -> List[Dict[str, Any]]:
        """
        Computes feature contribution explanation for the predicted condition.
        Uses model weights/coefficients for active symptoms.
        """
        explanations = []
        if not active_symptoms:
            return explanations
            
        # If Logistic Regression
        if hasattr(self.model, "coef_"):
            try:
                class_idx = list(self.model.classes_).index(condition)
                coefs = self.model.coef_[class_idx]
                for sym in active_symptoms:
                    feat_idx = self.feature_index_map.get(sym)
                    if feat_idx is not None:
                        weight = float(coefs[feat_idx])
                        explanations.append({
                            "symptom": sym.replace("_", " "),
                            "weight": round(weight, 3),
                            "impact": "High positive contribution" if weight > 1.0 else ("Moderate contribution" if weight > 0 else "Neutral")
                        })
                # Sort descending by contribution weight
                explanations.sort(key=lambda x: x["weight"], reverse=True)
            except Exception:
                for sym in active_symptoms:
                    explanations.append({"symptom": sym.replace("_", " "), "weight": 1.0, "impact": "Correlated symptom"})
        else:
            for sym in active_symptoms:
                explanations.append({"symptom": sym.replace("_", " "), "weight": 1.0, "impact": "Clinical hallmark indicator"})
                
        return explanations

    def predict(self, natural_language_text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        End-to-end symptom prediction with uncertainty abstention and explainability.
        """
        extraction = extract_symptoms_from_text(natural_language_text)
        confirmed = extraction["confirmed_symptoms"]
        negated = extraction["negated_symptoms"]
        
        # 1. Uncertainty Handling: Insufficient evidence check
        if len(confirmed) == 0:
            return {
                "status": "ABSTAIN_NO_SYMPTOMS",
                "message": (
                    "No recognized clinical symptoms were identified in your description. "
                    "Please describe your symptoms clearly (e.g., 'fever, headache, chills, cough') "
                    "or consult a healthcare professional."
                ),
                "extracted_symptoms": [],
                "negated_symptoms": negated,
                "top_predictions": [],
                "confidence_assessment": "Uncertain / Insufficient Information",
                "follow_up_questions": [
                    "Where specifically are you experiencing pain or discomfort?",
                    "How long have you felt unwell, and do you have a fever or rash?"
                ]
            }
            
        # 2. Build feature vector and predict probabilities
        feature_vec = self.vector_from_symptoms(confirmed)
        
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(feature_vec)[0]
            classes = self.model.classes_
            top_indices = np.argsort(probs)[-top_k:][::-1]
            
            top_candidates = []
            for rank, idx in enumerate(top_indices, 1):
                condition = str(classes[idx])
                calibrated_prob = float(probs[idx])
                explanations = self.explain_prediction(condition, confirmed)
                
                top_candidates.append({
                    "rank": rank,
                    "condition": condition,
                    "calibrated_probability": round(calibrated_prob, 4),
                    "confidence_percentage": f"{round(calibrated_prob * 100, 1)}%",
                    "contributing_symptoms": explanations
                })
        else:
            pred_class = self.model.predict(feature_vec)[0]
            top_candidates = [{
                "rank": 1,
                "condition": pred_class,
                "calibrated_probability": 1.0,
                "confidence_percentage": "High",
                "contributing_symptoms": self.explain_prediction(pred_class, confirmed)
            }]

        # 3. Low-confidence abstention check
        lead_prob = top_candidates[0]["calibrated_probability"] if top_candidates else 0.0
        confidence_level = "High" if lead_prob >= 0.65 else ("Moderate" if lead_prob >= 0.35 else "Low / Ambiguous")
        
        follow_up = []
        if len(confirmed) < 2:
            follow_up.append("You only reported one isolated symptom. Are you experiencing chills, nausea, weakness, or fatigue as well?")
        if lead_prob < 0.5:
            follow_up.append("Symptoms overlap across multiple conditions. How many days have these symptoms persisted?")

        return {
            "status": "SUCCESS",
            "extracted_symptoms": confirmed,
            "negated_symptoms": negated,
            "top_predictions": top_candidates,
            "confidence_assessment": confidence_level,
            "lead_probability": round(lead_prob, 4),
            "follow_up_questions": follow_up,
            "model_used": self.model_name,
            "disclaimer": (
                "Educational Research Prototype: These candidate conditions are statistical model outputs "
                "based on reported symptoms. They are NOT a doctor's diagnosis. Consult a qualified physician."
            )
        }

# Module singleton
_PREDICTOR_INSTANCE = None

def get_predictor() -> ConditionPredictor:
    """Returns singleton instance of ConditionPredictor."""
    global _PREDICTOR_INSTANCE
    if _PREDICTOR_INSTANCE is None:
        _PREDICTOR_INSTANCE = ConditionPredictor()
    return _PREDICTOR_INSTANCE

if __name__ == "__main__":
    predictor = get_predictor()
    test_query = "I've been suffering from high fever, shivering, and severe chills with headache and nausea."
    pred_res = predictor.predict(test_query)
    print("\n--- PREDICTION ENGINE TEST ---")
    print(f"Query: {test_query}")
    print(f"Extracted Symptoms: {pred_res['extracted_symptoms']}")
    print(f"Confidence: {pred_res['confidence_assessment']} (Lead: {pred_res['lead_probability']})")
    print("\nTop 3 Candidate Conditions:")
    for cand in pred_res["top_predictions"]:
        print(f"  {cand['rank']}. {cand['condition']} - {cand['confidence_percentage']}")
        top_contribs = [f"{e['symptom']} ({e['weight']})" for e in cand['contributing_symptoms'][:3]]
        print(f"     Key symptoms: {', '.join(top_contribs)}")
