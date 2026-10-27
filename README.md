# 🏥 MediGuide AI — Symptom Prediction & Medicine Safety Chatbot

> **Educational Research Prototype** — This application is NOT a medical diagnosis or prescribing service.  
> Always consult a qualified healthcare professional for medical decisions.

---

## 📋 Overview

MediGuide AI is a complete, runnable, research-oriented AI and Machine Learning project that allows users to describe symptoms in natural language and receive:

- **ML-powered condition predictions** with calibrated probabilities and top-3 candidates
- **Feature-level explanations** showing which symptoms drive each prediction
- **Verified medicine information** from FDA DailyMed, openFDA, and CDSCO India
- **Drug-drug interaction safety checks** with clinical severity ratings
- **Allergy cross-reactivity screening** (penicillin, NSAID, sulfa classes)
- **Emergency red-flag triage** detecting heart attack, stroke, anaphylaxis, and other critical symptoms
- **Follow-up clinical questions** for richer symptom context

---

## 🚀 Quick Start (Windows + VS Code)

### 1. Prerequisites
- **Windows 10/11**
- **Internet connection** (for first-time setup only)

### 2. Install UV (Python environment manager)
```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"
```

### 3. Clone / Open the project
```powershell
cd "d:\medical chatbot"
```

### 4. Create virtual environment and install dependencies
```powershell
uv venv .venv --python 3.11
uv pip install --python ".venv\Scripts\python.exe" -r requirements.txt
```

### 5. Download datasets and preprocess
```powershell
.venv\Scripts\python.exe -m src.download_datasets
.venv\Scripts\python.exe -m src.inspect_datasets
.venv\Scripts\python.exe -m src.preprocess_symptoms
.venv\Scripts\python.exe -m src.preprocess_medicines
.venv\Scripts\python.exe -m src.validate_data
```

### 6. Train and evaluate ML models
```powershell
.venv\Scripts\python.exe -m src.train_models
```

### 7. Run automated tests
```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

### 8. Launch the Streamlit chatbot
```powershell
.venv\Scripts\streamlit.exe run app.py
```

---

## 🧠 Model Architecture & Results

| Algorithm | Accuracy | Macro F1 | Top-3 Acc | Latency |
|---|---|---|---|---|
| **Logistic Regression** ⭐ | 100.0% | 1.0000 | 100.0% | 0.10 ms |
| Multinomial Naive Bayes | 99.7% | 0.9973 | 100.0% | 0.08 ms |
| Random Forest | 99.9% | 0.9986 | 100.0% | 2.58 ms |
| Calibrated SVM | 100.0% | 1.0000 | 100.0% | 6.29 ms |
| XGBoost | 99.5% | 0.9945 | 100.0% | 0.37 ms |

- **Champion model:** Logistic Regression (selected for speed + perfect held-out accuracy)
- **Evaluation:** Stratified 70/15/15 train/validation/test split
- **All metrics computed on held-out test data only**

---

## 📁 Project Structure

```
mediguide-ai/
├── app.py                    # Streamlit chatbot application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env.example              # Environment variable template
├── .gitignore
├── data/
│   ├── raw/                  # Original downloaded datasets
│   ├── processed/            # Cleaned & indexed datasets
│   └── metadata/             # Dataset provenance records
├── models/                   # Trained model artifacts
├── reports/
│   ├── data_quality/         # Validation & inspection reports
│   ├── evaluation/           # Model comparison CSV/JSON
│   └── figures/              # Confusion matrices, charts
├── src/
│   ├── data_sources.py       # Data source registry & metadata
│   ├── download_datasets.py  # Automated dataset ingestion
│   ├── inspect_datasets.py   # Schema profiling
│   ├── preprocess_symptoms.py # NLP extraction & synonym mapping
│   ├── preprocess_medicines.py # Medicine indexing
│   ├── validate_data.py      # Data quality validation
│   ├── train_models.py       # Multi-model training & comparison
│   ├── predict_conditions.py # Prediction engine & explanations
│   ├── medicine_retrieval.py # Medicine search & formatting
│   ├── medicine_safety.py    # Drug interaction & allergy checks
│   ├── medical_sources.py    # Verified clinical knowledge base
│   └── triage.py             # Emergency red-flag screening
└── tests/
    ├── test_data_validation.py
    ├── test_preprocessing.py
    ├── test_predictions.py
    ├── test_medicine_retrieval.py
    └── test_safety.py
```

---

## ⚠️ Limitations

- The symptom dataset is an **educational benchmark**, not clinically validated.
- High held-out accuracy may not generalise to real-world clinical populations.
- The medicine database covers **10 commonly referenced drugs** — not the full pharmacopoeia.
- openFDA/DailyMed data reflects **US-approved labeling**; CDSCO India formulations may differ.
- Emergency triage uses **heuristic keyword matching**, not a validated clinical decision instrument.
- **This application must never be used as a substitute for professional medical advice.**

---

## 📜 Data Sources & Licenses

| Source | License | Jurisdiction |
|---|---|---|
| Disease-Symptom Benchmark | CC-BY 4.0 / Open Research | Global (Educational) |
| US FDA / DailyMed | CC0 1.0 / Public Domain | United States |
| openFDA Drug Labeling API | CC0 1.0 / US Public Domain | United States |
| CDSCO India NLEM | Government of India Open Data | India |
| CDC / WHO / NIH | Public Health Guidelines | Global |
