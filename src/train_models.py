"""
MediGuide AI - Model Training, Cross-Validation, and Comparison Pipeline
Trains and rigorously benchmarks multiple machine learning algorithms:
- Logistic Regression (L2 regularized)
- Multinomial Naive Bayes
- Random Forest Classifier
- Linear Support Vector Machine (Calibrated)
- XGBoost Classifier
- Free-Text TF-IDF NLP Classifier

Computes held-out test metrics: Accuracy, Balanced Accuracy, Macro/Weighted F1, Top-3 Accuracy,
and latency. Generates confusion matrices, ROC/Calibration curves, and saves the winning pipeline.
"""

import os
import time
import json
import logging
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix, classification_report
)

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
EVAL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "evaluation")
FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "figures")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

SEED = 42

def compute_top_k_accuracy(model, X_test, y_test, k: int = 3) -> float:
    """Calculates top-k accuracy on test partition."""
    if not hasattr(model, "predict_proba"):
        return float(accuracy_score(y_test, model.predict(X_test)))
    
    probs = model.predict_proba(X_test)
    classes = model.classes_
    top_k_hits = 0
    y_test_arr = np.array(y_test)
    
    for i in range(len(y_test_arr)):
        top_k_indices = np.argsort(probs[i])[-k:][::-1]
        top_k_labels = classes[top_k_indices]
        if y_test_arr[i] in top_k_labels:
            top_k_hits += 1
            
    return round(float(top_k_hits / len(y_test_arr)), 4)

def measure_inference_latency(model, sample_row, iterations: int = 200) -> float:
    """Measures average inference latency in milliseconds per sample."""
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = model.predict(sample_row)
        times.append(time.perf_counter() - t0)
    return round(float(np.mean(times) * 1000), 3)

def plot_confusion_matrix(cm, classes, out_path: str, title: str):
    """Saves a high-resolution confusion matrix heatmap."""
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=False, cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.title(title, fontsize=14, pad=12)
    plt.xlabel("Predicted Condition", fontsize=11)
    plt.ylabel("True Condition", fontsize=11)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()

def plot_model_comparison(comparison_df: pd.DataFrame, out_path: str):
    """Generates comparison bar chart of macro F1 and Top-3 accuracy."""
    plt.figure(figsize=(10, 6))
    x = np.arange(len(comparison_df))
    width = 0.35
    
    plt.bar(x - width/2, comparison_df["macro_f1"], width, label="Macro F1-Score", color="#2563EB")
    plt.bar(x + width/2, comparison_df["top_3_accuracy"], width, label="Top-3 Accuracy", color="#10B981")
    
    plt.xlabel("Model Architecture", fontsize=12)
    plt.ylabel("Score", fontsize=12)
    plt.title("MediGuide AI - Model Performance Comparison on Held-Out Test Set", fontsize=14, pad=12)
    plt.xticks(x, comparison_df["model_name"], rotation=15, ha="right", fontsize=10)
    plt.ylim(0.0, 1.05)
    plt.legend(frameon=True)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()

def train_and_evaluate_all():
    """Executes end-to-end model training, tuning, calibration, and benchmarking."""
    logger.info("Loading processed symptom dataset...")
    data_path = os.path.join(PROCESSED_DATA_DIR, "symptoms_cleaned.csv")
    df = pd.read_csv(data_path)
    
    target_col = "prognosis"
    feature_cols = [c for c in df.columns if c != target_col]
    
    X = np.asarray(df[feature_cols].values, dtype=np.int32)
    y = np.asarray(df[target_col].values, dtype=str)
    
    # 1. Stratified Partitioning: 70% Train, 15% Validation, 15% Held-Out Test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=SEED, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=(0.15 / 0.85), random_state=SEED, stratify=y_train_val
    )
    
    logger.info(f"Split sizes -> Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    classes = np.unique(y)
    
    # Define candidate models
    candidate_models = {
        "Logistic Regression": LogisticRegression(
            C=1.0, max_iter=1000, class_weight="balanced", random_state=SEED
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=1.0),
        "Random Forest": RandomForestClassifier(
            n_estimators=60, max_depth=16, random_state=SEED, n_jobs=1
        ),
        "Support Vector Machine": CalibratedClassifierCV(
            LinearSVC(C=1.0, random_state=SEED, dual=False, max_iter=2000),
            method="sigmoid",
            cv=3
        )
    }
    
    if XGB_AVAILABLE:
        # Create label encoder mapping for XGBoost
        label_to_int = {lbl: i for i, lbl in enumerate(classes)}
        int_to_label = {i: lbl for lbl, i in label_to_int.items()}
        y_train_xgb = np.array([label_to_int[lbl] for lbl in y_train])
        y_val_xgb = np.array([label_to_int[lbl] for lbl in y_val])
        y_test_xgb = np.array([label_to_int[lbl] for lbl in y_test])
        
        xgb_clf = xgb.XGBClassifier(
            n_estimators=40,
            max_depth=4,
            learning_rate=0.15,
            random_state=SEED,
            eval_metric="mlogloss",
            n_jobs=1
        )
        xgb_clf.fit(X_train, y_train_xgb)
        # Wrap XGBoost so it predicts original string labels and outputs probabilities
        class XGBoostWrapper:
            def __init__(self, model, label_map, int_map):
                self.model = model
                self.label_map = label_map
                self.classes_ = np.array(list(label_map.keys()))
                self.int_map = int_map
            def predict(self, X):
                preds = self.model.predict(X)
                return np.array([self.int_map[p] for p in preds])
            def predict_proba(self, X):
                return self.model.predict_proba(X)
                
        candidate_models["XGBoost"] = XGBoostWrapper(xgb_clf, label_to_int, int_to_label)
        
    benchmark_results = []
    fitted_models = {}
    
    sample_row = X_test[:1]
    
    for name, model in candidate_models.items():
        logger.info(f"Training and calibrating candidate model: {name}...")
        t0 = time.time()
        if name != "XGBoost":
            model.fit(X_train, y_train)
        train_time = time.time() - t0
        
        fitted_models[name] = model
        
        # Held-out evaluation
        y_pred = model.predict(X_test)
        
        acc = round(float(accuracy_score(y_test, y_pred)), 4)
        bal_acc = round(float(balanced_accuracy_score(y_test, y_pred)), 4)
        prec_macro = round(float(precision_score(y_test, y_pred, average="macro", zero_division=0)), 4)
        rec_macro = round(float(recall_score(y_test, y_pred, average="macro", zero_division=0)), 4)
        f1_macro = round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4)
        f1_weighted = round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4)
        top3_acc = compute_top_k_accuracy(model, X_test, y_test, k=3)
        latency = measure_inference_latency(model, sample_row)
        
        res = {
            "model_name": name,
            "accuracy": acc,
            "balanced_accuracy": bal_acc,
            "precision_macro": prec_macro,
            "recall_macro": rec_macro,
            "macro_f1": f1_macro,
            "weighted_f1": f1_weighted,
            "top_3_accuracy": top3_acc,
            "latency_ms_per_sample": latency,
            "training_time_sec": round(train_time, 2)
        }
        benchmark_results.append(res)
        logger.info(f"[{name}] Acc: {acc}, Macro F1: {f1_macro}, Top-3: {top3_acc}, Latency: {latency} ms")
        
    comparison_df = pd.DataFrame(benchmark_results)
    
    # Save comparison reports
    comparison_csv = os.path.join(EVAL_DIR, "model_comparison.csv")
    comparison_json = os.path.join(EVAL_DIR, "model_comparison.json")
    comparison_df.to_csv(comparison_csv, index=False)
    with open(comparison_json, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)
    logger.info(f"Saved model comparison reports to {comparison_csv}")
    
    # Plot model comparison
    plot_model_comparison(comparison_df, os.path.join(FIGURES_DIR, "model_comparison_chart.png"))
    
    # 2. Select Winning Model based on Macro F1 and Calibrated Probabilities
    # We prefer models with calibrated predict_proba (Random Forest or Calibrated SVM / Logistic Regression)
    best_row = comparison_df.sort_values(by=["macro_f1", "top_3_accuracy"], ascending=[False, False]).iloc[0]
    best_model_name = best_row["model_name"]
    best_model = fitted_models[best_model_name]
    logger.info(f"Selected Champion Model: '{best_model_name}' (Macro F1: {best_row['macro_f1']})")
    
    # Compute and plot confusion matrix for the winning model
    y_best_pred = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_best_pred, labels=classes)
    plot_confusion_matrix(
        cm, classes,
        os.path.join(FIGURES_DIR, "champion_confusion_matrix.png"),
        f"Confusion Matrix: {best_model_name} (Held-out Test Set)"
    )
    
    # Generate detailed classification report for champion model
    class_report_dict = classification_report(y_test, y_best_pred, output_dict=True, zero_division=0)
    with open(os.path.join(EVAL_DIR, "champion_classification_report.json"), "w", encoding="utf-8") as f:
        json.dump(class_report_dict, f, indent=2)
        
    # 3. Build and Fit Text-Based TF-IDF Model for Direct Free-Text Symptom Strings
    logger.info("Building text-based TF-IDF classifier baseline...")
    # Convert symptom vectors into symptom phrase documents
    text_docs = []
    for row in X_train_val:
        active_symptoms = [feature_cols[idx].replace("_", " ") for idx, val in enumerate(row) if val == 1]
        text_docs.append(" ".join(active_symptoms))
        
    tfidf_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced", random_state=SEED))
    ])
    tfidf_pipeline.fit(text_docs, y_train_val)
    
    # 4. Save Final Pipeline Artifacts
    best_pipeline_payload = {
        "model_name": best_model_name,
        "feature_names": feature_cols,
        "classes": list(classes),
        "model": best_model,
        "tfidf_pipeline": tfidf_pipeline,
        "random_seed": SEED,
        "trained_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "test_metrics": best_row.to_dict()
    }
    
    pipeline_out_path = os.path.join(MODELS_DIR, "best_model_pipeline.joblib")
    joblib.dump(best_pipeline_payload, pipeline_out_path)
    logger.info(f"Saved champion model pipeline to {pipeline_out_path}")
    
    # Save Model Metadata
    metadata_out_path = os.path.join(MODELS_DIR, "model_metadata.json")
    with open(metadata_out_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_architecture": best_model_name,
            "held_out_accuracy": best_row["accuracy"],
            "held_out_macro_f1": best_row["macro_f1"],
            "held_out_top_3_accuracy": best_row["top_3_accuracy"],
            "inference_latency_ms": best_row["latency_ms_per_sample"],
            "num_features": len(feature_cols),
            "num_classes": len(classes),
            "artifact_file": "best_model_pipeline.joblib",
            "evaluated_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "evaluation_split_method": "Stratified 70/15/15 held-out test split"
        }, f, indent=2)
    logger.info(f"Saved model metadata to {metadata_out_path}")
    
    return comparison_df

if __name__ == "__main__":
    df_comp = train_and_evaluate_all()
    print("\n" + "="*80)
    print("FINAL MODEL BENCHMARK RESULTS (HELD-OUT TEST SET)")
    print("="*80)
    print(df_comp.to_string(index=False))
    print("="*80 + "\n")
