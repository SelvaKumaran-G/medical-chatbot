"""
MediGuide AI — Symptom Prediction & Medicine Safety Chatbot
Advanced clinical AI application with ML-backed condition prediction, pathophysiological
symptom-match explanation, reference tablet suggestions, drug safety checks, and emergency triage.

⚠️ EDUCATIONAL RESEARCH PROTOTYPE — NOT a medical diagnosis or prescribing service.
"""

import streamlit as st
import json, os, time, base64

# ---------------------------------------------------------------------------
# Load background and doctor avatar assets
# ---------------------------------------------------------------------------
_bg_path = os.path.join(os.path.dirname(__file__), "assets", "medical_bg.jpg")
_avatar_path = os.path.join(os.path.dirname(__file__), "assets", "doctor_avatar.png")
_default_user_avatar_path = os.path.join(os.path.dirname(__file__), "assets", "user_avatar.png")

_bg_css = """
.stApp {
    background: #ffffff !important;
    color: #000000 !important;
}
"""

_doctor_avatar = _avatar_path if os.path.exists(_avatar_path) else "👨‍⚕️"
_avatar_b64 = ""
if os.path.exists(_avatar_path):
    try:
        with open(_avatar_path, "rb") as _f:
            _avatar_b64 = base64.b64encode(_f.read()).decode("utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dr. MediGuide AI — Medical Chatbot",
    page_icon="👨‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Lazy-load heavy modules only once
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_predictor():
    from src.predict_conditions import ConditionPredictor
    return ConditionPredictor()

@st.cache_resource(show_spinner=False)
def load_medicine_retriever():
    from src.medicine_retrieval import MedicineRetriever
    return MedicineRetriever()

@st.cache_resource(show_spinner=False)
def load_safety_checker():
    from src.medicine_safety import MedicineSafetyChecker
    return MedicineSafetyChecker()

# ---------------------------------------------------------------------------
# Custom CSS — Dynamic Medical Theme & Professional UI
# ---------------------------------------------------------------------------
st.markdown(f"<style>{_bg_css}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
/* ── Google Fonts: Inter & Outfit ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

/* ── Design Tokens — White & Blue Clinical Palette ── */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f0f7ff;
    --bg-card: #ffffff;
    --bg-card-hover: #f8fafc;
    --accent-primary: #2563eb;
    --accent-secondary: #0284c7;
    --accent-navy: #1e3a8a;
    --accent-light: #eff6ff;
    --accent-glow: rgba(37, 99, 235, 0.16);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --danger: #dc2626;
    --danger-bg: #fef2f2;
    --warning: #d97706;
    --warning-bg: #fffbeb;
    --success: #16a34a;
    --border: #dbeafe;
    --border-accent: #2563eb;
    --border-dark: #1e3a8a;
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}

/* ── Typography & Global resets ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #1e3a8a !important;
    letter-spacing: -0.02em;
}

p, span, label, div {
    color: inherit;
}

/* ── Sidebar Styling ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%) !important;
    border-right: 1.5px solid #dbeafe !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #1e3a8a !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stCaption {
    color: #475569 !important;
    font-size: 0.88rem;
}

/* ── Chat Messages ── */
.stChatMessage {
    background: #ffffff !important;
    border: 1.5px solid #dbeafe !important;
    border-radius: var(--radius-md) !important;
    padding: 1.2rem 1.4rem !important;
    margin-bottom: 0.85rem !important;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.05) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stChatMessage:hover {
    border-color: #2563eb !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.10) !important;
}
.stChatMessage img {
    border-radius: 50% !important;
    border: 2px solid #2563eb !important;
}

/* ── Chat Input ── */
.stChatInput > div {
    background: #ffffff !important;
    border: 2px solid #2563eb !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08) !important;
}
.stChatInput > div:focus-within {
    border-color: #1d4ed8 !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
}
.stChatInput textarea {
    color: #0f172a !important;
    font-size: 1rem !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #0369a1 100%) !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: #f0f7ff !important;
    border: 1px solid #dbeafe !important;
    border-radius: var(--radius-sm) !important;
    color: #1e3a8a !important;
    font-weight: 600 !important;
    padding: 0.65rem 1rem !important;
}
div[data-testid="stExpander"] details {
    background: #ffffff !important;
    border: 1.5px solid #dbeafe !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 0.75rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 2px solid #2563eb !important;
}
.stTabs [data-baseweb="tab"] {
    background: #ffffff !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    color: #475569 !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600;
    border: 1.5px solid #dbeafe !important;
    border-bottom: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1.5px solid #dbeafe !important;
    border-left: 4px solid #2563eb !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.2rem;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.05);
}
div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    font-weight: 800 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Hero Banner ── */
.doctor-hero-card {
    background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 60%, #eff6ff 100%);
    border: 2px solid #93c5fd;
    border-radius: var(--radius-lg);
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 30px rgba(37, 99, 235, 0.08);
}
.doctor-avatar-circle {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    border: 3px solid #2563eb;
    box-shadow: 0 0 20px rgba(37, 99, 235, 0.25);
    object-fit: cover;
    background: #eff6ff;
}
.status-badge-live {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1e40af;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.example-pill {
    background: #ffffff;
    border: 1.5px solid #bfdbfe;
    color: #1e40af;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.82rem;
    cursor: default;
    transition: all 0.2s;
    font-weight: 500;
}
.example-pill:hover {
    border-color: #2563eb;
    color: #ffffff;
    background: #2563eb;
}

/* ── Onboarding Welcome Screen ── */
.onboarding-container {
    max-width: 640px;
    margin: 2rem auto;
    padding: 2.5rem 2.8rem;
    background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 50%, #eff6ff 100%);
    border: 2px solid #93c5fd;
    border-radius: 24px;
    box-shadow: 0 12px 40px rgba(37, 99, 235, 0.10);
    text-align: center;
}
.onboarding-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid #2563eb;
    box-shadow: 0 0 30px rgba(37, 99, 235, 0.20);
    object-fit: cover;
    margin: 0 auto 1.2rem auto;
    display: block;
    background: #eff6ff;
}
.onboarding-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.8rem;
    font-weight: 800;
    color: #1e3a8a !important;
    margin: 0 0 0.4rem 0;
}
.onboarding-subtitle {
    color: #475569;
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

/* ── Sidebar User Profile Card ── */
.sidebar-profile-card {
    background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
    border: 2px solid #93c5fd;
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.08);
}
.sidebar-profile-avatar {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    border: 3px solid #2563eb;
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.18);
    object-fit: cover;
    margin: 0 auto 0.6rem auto;
    display: block;
    background: #eff6ff;
}
.sidebar-profile-name {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e3a8a;
    margin: 0 0 0.2rem 0;
}
.sidebar-profile-detail {
    font-size: 0.82rem;
    color: #475569;
    line-height: 1.4;
}

/* ── Symptom Explanation Card ── */
.symptom-explain-card {
    background: #ffffff;
    border: 1.5px solid #dbeafe;
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin: 6px 0;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.symptom-explain-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08);
}
.symptom-explain-icon {
    font-size: 1.3rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.symptom-explain-content {
    flex: 1;
}
.symptom-explain-name {
    font-weight: 700;
    font-size: 0.92rem;
    color: #1e3a8a;
    margin-bottom: 2px;
}
.symptom-explain-desc {
    font-size: 0.82rem;
    color: #475569;
    line-height: 1.45;
    margin: 0;
}
.symptom-explain-match {
    font-size: 0.78rem;
    color: #0284c7;
    font-weight: 600;
    margin-top: 2px;
}

/* ── Predicted Conditions: 3 in 1 Horizontal Line, Vertical Square Shape ── */
.predictions-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 1rem 0 1.25rem 0;
    width: 100%;
}
@media (max-width: 860px) {
    .predictions-grid {
        grid-template-columns: 1fr;
    }
}
.prediction-square-card {
    background: #ffffff;
    border: 2px solid #3b82f6;
    border-radius: 14px;
    padding: 1.2rem 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: stretch;
    text-align: center;
    min-height: 250px;
    aspect-ratio: 1 / 1;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    box-sizing: border-box;
}
.prediction-square-card:hover {
    transform: translateY(-3px);
    border-color: #1d4ed8;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.15);
}
.pred-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    margin-bottom: 0.5rem;
}
.pred-rank-badge {
    background: #2563eb;
    color: #ffffff;
    font-size: 0.8rem;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 8px;
    font-family: 'Outfit', sans-serif;
}
.pred-confidence-tag {
    font-size: 0.82rem;
    font-weight: 700;
    color: #1d4ed8;
    background: #eff6ff;
    border: 1.5px solid #bfdbfe;
    padding: 3px 9px;
    border-radius: 12px;
}
.pred-card-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 0.4rem 0;
}
.pred-condition-title {
    margin: 0 0 0.35rem 0;
    font-size: 1.18rem;
    font-weight: 800;
    color: #1e3a8a !important;
    line-height: 1.3;
}
.pred-confidence-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
    margin-bottom: 6px;
}
.pred-bar-track {
    background: #dbeafe;
    border-radius: 6px;
    height: 8px;
    width: 100%;
    max-width: 170px;
    overflow: hidden;
    margin: 0 auto;
    border: 1px solid #bfdbfe;
}
.pred-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #2563eb, #0284c7);
    border-radius: 6px;
    transition: width 0.4s ease;
}
.pred-card-footer {
    width: 100%;
    margin-top: auto;
    padding-top: 0.6rem;
    border-top: 1px dashed #dbeafe;
}
.pred-features-label {
    color: #64748b;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}
.pred-features-list {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 4px;
}
.pred-feature-pill {
    display: inline-block;
    background: #f0f7ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 2px 7px;
    font-size: 0.75rem;
    color: #1e40af;
    font-weight: 600;
}

/* ── Symptom Match Explanation Section ── */
.symptom-match-card {
    background: #ffffff;
    border: 2px solid #3b82f6;
    border-radius: var(--radius-md);
    padding: 1.3rem 1.6rem;
    margin: 1rem 0;
    box-shadow: 0 4px 18px rgba(37, 99, 235, 0.06);
}
.symptom-match-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.8rem;
    flex-wrap: wrap;
    gap: 8px;
}
.match-score-badge {
    background: #dbeafe;
    border: 1.5px solid #2563eb;
    color: #1e40af;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 700;
}
.chip-pos {
    background: #eff6ff;
    border: 1.5px solid #3b82f6;
    color: #1d4ed8;
    padding: 3px 10px;
    border-radius: 14px;
    font-size: 0.82rem;
    display: inline-block;
    margin: 3px;
    font-weight: 600;
}
.chip-neg {
    background: #f8fafc;
    border: 1px dashed #94a3b8;
    color: #64748b;
    text-decoration: line-through;
    padding: 3px 10px;
    border-radius: 14px;
    font-size: 0.82rem;
    display: inline-block;
    margin: 3px;
}

/* ── Reference Medicines Shelf (White & Blue Cards with Visuals) ── */
.meds-header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 1.3rem 0 0.85rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1.5px solid #dbeafe;
    flex-wrap: wrap;
    gap: 8px;
}
.meds-header-title {
    display: flex;
    align-items: center;
    gap: 8px;
}
.meds-header-title h3 {
    margin: 0 !important;
    font-size: 1.18rem !important;
    font-weight: 700 !important;
    color: #1e3a8a !important;
}
.meds-subtext {
    font-size: 0.84rem;
    color: #64748b;
    font-weight: 400;
}
.meds-header-action {
    font-size: 0.82rem;
    font-weight: 600;
    color: #0284c7;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    padding: 3px 10px;
    border-radius: 12px;
}
.tablets-shelf-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
    gap: 14px;
    margin-bottom: 1rem;
    width: 100%;
}
.tablet-shelf-card {
    background: #ffffff;
    border: 1.5px solid #dbeafe;
    border-radius: 14px;
    padding: 1.25rem 0.9rem 1rem 0.9rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    box-sizing: border-box;
}
.tablet-shelf-card:hover {
    transform: translateY(-3px);
    border-color: #3b82f6;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12);
}
.tablet-shelf-visual {
    width: 66px;
    height: 66px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.5rem;
}
.tablet-shelf-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
    line-height: 1.25;
}
.tablet-shelf-indication {
    font-size: 0.78rem;
    color: #64748b;
    line-height: 1.35;
    margin-bottom: 0.85rem;
    min-height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.tablet-details-dropdown {
    width: 100%;
    margin-top: auto;
}
.tablet-view-info-btn {
    display: block;
    width: 100%;
    background: #ffffff;
    border: 1.5px solid #2563eb;
    color: #2563eb;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s ease;
    list-style: none;
    box-sizing: border-box;
}
.tablet-view-info-btn::-webkit-details-marker {
    display: none;
}
.tablet-view-info-btn:hover {
    background: #eff6ff;
    border-color: #1d4ed8;
    color: #1d4ed8;
}
.tablet-info-popup {
    margin-top: 10px;
    padding: 10px 12px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    text-align: left;
    font-size: 0.8rem;
    color: #1e293b;
    line-height: 1.45;
}
.tablet-popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    flex-wrap: wrap;
    gap: 4px;
}
.tablet-popup-row {
    margin: 4px 0;
    color: #334155;
}
.tablet-popup-row strong {
    color: #0f172a;
}
.tablet-popup-caution {
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    padding: 5px 8px;
    margin-top: 6px;
    border-radius: 4px;
    color: #92400e;
    font-size: 0.76rem;
}
.badge-otc {
    background: #dcfce7;
    border: 1px solid #86efac;
    color: #166534;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 700;
}
.badge-rx {
    background: #ede9fe;
    border: 1px solid #c4b5fd;
    color: #5b21b6;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 700;
}

/* ── Emergency banner ── */
.emergency-banner {
    background: #fef2f2;
    border: 2px solid #dc2626;
    border-radius: var(--radius-md);
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(220, 38, 38, 0.15);
}

/* ── Safety warning ── */
.safety-warning {
    background: #f0f7ff;
    border: 2px solid #3b82f6;
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #1e40af;
    font-size: 0.88rem;
    font-weight: 500;
}

/* ── Citation box ── */
.source-citation {
    background: #f8fafc;
    border: 1.5px solid #dbeafe;
    border-radius: var(--radius-sm);
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0;
    font-size: 0.82rem;
    color: #334155;
}
.source-citation a {
    color: #2563eb !important;
    text-decoration: underline !important;
    font-weight: 600;
}

/* ── Educational disclaimer footer ── */
.disclaimer-box {
    background: #f8fafc;
    border: 1.5px dashed #93c5fd;
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem;
    color: #475569;
    font-size: 0.82rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_profile_photo_b64" not in st.session_state:
    st.session_state.user_profile_photo_b64 = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "patient_profile" not in st.session_state:
    st.session_state.patient_profile = {
        "age": 32,
        "age_range": "Young Adult (18 - 35 yrs)",
        "biological_sex": "Unspecified",
        "is_pregnant": False,
        "preexisting_conditions": [],
        "other_health_issues": "",
        "known_allergies": [],
        "current_medications": []
    }

# ---------------------------------------------------------------------------
# Helper: build user avatar for chat
# ---------------------------------------------------------------------------
def _get_user_chat_avatar():
    """Returns user profile photo path or emoji for chat avatar."""
    if st.session_state.user_profile_photo_b64:
        # Save temp file for Streamlit's avatar usage
        _temp_avatar_path = os.path.join(os.path.dirname(__file__), "assets", "user_profile_upload.png")
        if not os.path.exists(_temp_avatar_path):
            try:
                with open(_temp_avatar_path, "wb") as f:
                    f.write(base64.b64decode(st.session_state.user_profile_photo_b64))
            except Exception:
                return "🧑‍💼"
        return _temp_avatar_path
    return "🧑‍💼"

# ===========================================================================
# 🎬 ONBOARDING WELCOME SCREEN — Ask Name + Optional Profile
# ===========================================================================
if not st.session_state.onboarded:
    # Show the onboarding welcome screen
    avatar_onboard_tag = f'<img src="data:image/png;base64,{_avatar_b64}" class="onboarding-avatar" alt="Dr. MediGuide AI" />' if _avatar_b64 else '<div style="font-size:5rem;text-align:center;margin-bottom:1rem;">👨‍⚕️</div>'

    st.markdown(f"""
    <div class="onboarding-container">
        {avatar_onboard_tag}
        <div class="onboarding-title">Welcome to Dr. MediGuide AI</div>
        <p class="onboarding-subtitle">
            Your personal AI Medical Assistant is ready to help.<br>
            Let's get to know you first so I can provide personalized health insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Name input (required)
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("#### 👤 Tell us about yourself")
        onboard_name = st.text_input(
            "Your Name *",
            placeholder="e.g. Rahul, Priya, Alex…",
            key="onboard_name_input"
        )

        st.markdown("#### 📷 Profile Photo *(optional)*")
        st.caption("Upload a photo to personalize your chat experience")
        onboard_photo = st.file_uploader(
            "Upload Profile Picture",
            type=["png", "jpg", "jpeg", "webp"],
            key="onboard_photo_upload",
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("#### 🩺 Quick Health Profile *(optional — you can update later in sidebar)*")

        onboard_age_range = st.selectbox("Age Range", [
            "Infant / Child (0 - 12 yrs)",
            "Adolescent (13 - 17 yrs)",
            "Young Adult (18 - 35 yrs)",
            "Adult (36 - 64 yrs)",
            "Senior / Geriatric (65+ yrs)"
        ], index=2, key="onboard_age_range")

        onboard_sex = st.selectbox("Biological Sex", ["Unspecified", "Female", "Male"], index=0, key="onboard_sex")

        onboard_conditions = st.multiselect("Any Pre-existing Conditions?", [
            "Type 2 Diabetes",
            "Hypertension (High Blood Pressure)",
            "Chronic Kidney Disease (CKD)",
            "Liver Cirrhosis / Hepatic Disease",
            "Bronchial Asthma / COPD",
            "Peptic Ulcer Disease / Acid Reflux (GERD)",
            "Coronary Artery Disease (CAD) / Heart Disease",
            "Thyroid Disorder",
            "None / Generally Healthy"
        ], key="onboard_conditions")

        st.markdown("")
        if st.button("🚀 Start Consultation", use_container_width=True, type="primary"):
            if not onboard_name.strip():
                st.error("Please enter your name to continue.")
            else:
                st.session_state.user_name = onboard_name.strip()
                st.session_state.onboarded = True

                # Save profile photo if uploaded
                if onboard_photo is not None:
                    photo_bytes = onboard_photo.read()
                    st.session_state.user_profile_photo_b64 = base64.b64encode(photo_bytes).decode("utf-8")
                    # Save to disk for avatar usage
                    _upload_path = os.path.join(os.path.dirname(__file__), "assets", "user_profile_upload.png")
                    try:
                        with open(_upload_path, "wb") as f:
                            f.write(photo_bytes)
                    except Exception:
                        pass

                # Save optional profile data
                # Determine default age from range
                _range_age_map = {
                    "Infant / Child (0 - 12 yrs)": 6,
                    "Adolescent (13 - 17 yrs)": 15,
                    "Young Adult (18 - 35 yrs)": 28,
                    "Adult (36 - 64 yrs)": 45,
                    "Senior / Geriatric (65+ yrs)": 70
                }
                st.session_state.patient_profile.update({
                    "age": _range_age_map.get(onboard_age_range, 28),
                    "age_range": onboard_age_range,
                    "biological_sex": onboard_sex,
                    "preexisting_conditions": onboard_conditions,
                })

                st.rerun()

    # Stop here — don't show the chat yet
    st.stop()

# ===========================================================================
# 🏥 MAIN APPLICATION — User is onboarded
# ===========================================================================

# ---------------------------------------------------------------------------
# Sidebar — User Profile Card + Patient Clinical Profile
# ---------------------------------------------------------------------------
with st.sidebar:
    # ── User Profile Card at top of sidebar ──
    user_name = st.session_state.user_name
    prof = st.session_state.patient_profile

    if st.session_state.user_profile_photo_b64:
        sidebar_avatar_html = f'<img src="data:image/png;base64,{st.session_state.user_profile_photo_b64}" class="sidebar-profile-avatar" alt="{user_name}" />'
    else:
        _initial = user_name[0].upper() if user_name else "U"
        sidebar_avatar_html = f'<div style="width:72px;height:72px;border-radius:50%;border:3px solid #2563eb;background:linear-gradient(135deg,#2563eb,#0284c7);display:flex;align-items:center;justify-content:center;margin:0 auto 0.6rem auto;font-size:2rem;color:#ffffff;">{_initial}</div>'

    profile_details_parts = []
    if prof.get("age_range"):
        profile_details_parts.append(f"📅 {prof['age_range']}")
    if prof.get("biological_sex") and prof["biological_sex"] != "Unspecified":
        profile_details_parts.append(f"⚧ {prof['biological_sex']}")
    pre_conditions = [c for c in prof.get("preexisting_conditions", []) if "None" not in c]
    if pre_conditions:
        profile_details_parts.append(f"🩺 {', '.join(pre_conditions[:2])}")

    profile_detail_html = "<br>".join(profile_details_parts) if profile_details_parts else "No health details added yet"

    st.markdown(f"""
    <div class="sidebar-profile-card">
        {sidebar_avatar_html}
        <div class="sidebar-profile-name">👋 {user_name}</div>
        <div class="sidebar-profile-detail">{profile_detail_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👤 Patient Clinical Profile")
    st.caption("Update your profile to tailor diagnostic analysis, chronic disease precautions, and tablet safety.")

    # Age Range Form & Specific Age Slider
    age_brackets = [
        "Infant / Child (0 - 12 yrs)",
        "Adolescent (13 - 17 yrs)",
        "Young Adult (18 - 35 yrs)",
        "Adult (36 - 64 yrs)",
        "Senior / Geriatric (65+ yrs)"
    ]
    saved_range = st.session_state.patient_profile.get("age_range", "Young Adult (18 - 35 yrs)")
    default_range_idx = age_brackets.index(saved_range) if saved_range in age_brackets else 2
    p_age_range = st.selectbox("Age Range / Bracket", age_brackets, index=default_range_idx)

    # Dynamic limits for slider based on bracket
    if "0 - 12" in p_age_range:
        min_a, max_a, def_a = 0, 12, 6
    elif "13 - 17" in p_age_range:
        min_a, max_a, def_a = 13, 17, 15
    elif "18 - 35" in p_age_range:
        min_a, max_a, def_a = 18, 35, 28
    elif "36 - 64" in p_age_range:
        min_a, max_a, def_a = 36, 64, 45
    else:
        min_a, max_a, def_a = 65, 100, 70

    current_saved_age = st.session_state.patient_profile.get("age", def_a)
    slider_val = min(max(current_saved_age, min_a), max_a)
    p_age = st.slider("Specific Age (Years)", min_value=min_a, max_value=max_a, value=slider_val)

    # Pre-existing Chronic Diseases & Issues
    st.markdown("#### 🩺 Existing Medical Issues")
    chronic_options = [
        "Type 2 Diabetes",
        "Hypertension (High Blood Pressure)",
        "Chronic Kidney Disease (CKD)",
        "Liver Cirrhosis / Hepatic Disease",
        "Bronchial Asthma / COPD",
        "Peptic Ulcer Disease / Acid Reflux (GERD)",
        "Coronary Artery Disease (CAD) / Heart Disease",
        "Stroke History",
        "Thyroid Disorder",
        "None / Generally Healthy"
    ]
    saved_dis = st.session_state.patient_profile.get("preexisting_conditions", [])
    p_diseases = st.multiselect(
        "Pre-existing Diseases & Health Issues",
        chronic_options,
        default=[d for d in saved_dis if d in chronic_options]
    )

    p_other_issues = st.text_input(
        "Other Symptoms / Health Notes",
        value=st.session_state.patient_profile.get("other_health_issues", ""),
        placeholder="e.g. chronic acidity, heavy smoker, migraine"
    )

    p_sex = st.selectbox("Biological Sex", ["Unspecified", "Female", "Male"],
                         index=["Unspecified", "Female", "Male"].index(st.session_state.patient_profile.get("biological_sex", "Unspecified")))
    p_preg = False
    if p_sex == "Female":
        p_preg = st.checkbox("Pregnant or Breastfeeding?", value=st.session_state.patient_profile.get("is_pregnant", False))

    common_allergies = ["Penicillin", "Amoxicillin", "Aspirin / NSAIDs", "Sulfa drugs", "Macrolides", "Latex"]
    p_allergies = st.multiselect("Known Drug Allergies", common_allergies, default=st.session_state.patient_profile.get("known_allergies", []))

    common_meds = ["Warfarin", "Aspirin", "Metformin", "Omeprazole", "Atorvastatin", "Lisinopril", "Alcohol (regular)", "Lithium"]
    p_meds = st.multiselect("Current Medications", common_meds, default=st.session_state.patient_profile.get("current_medications", []))

    st.session_state.patient_profile = {
        "age": p_age,
        "age_range": p_age_range,
        "preexisting_conditions": p_diseases,
        "other_health_issues": p_other_issues,
        "biological_sex": p_sex,
        "is_pregnant": p_preg,
        "known_allergies": p_allergies,
        "current_medications": p_meds
    }

    st.markdown("---")
    st.markdown("### 🔍 Medicine Lookup")
    med_query = st.text_input("Search brand/generic/ingredient", placeholder="e.g. Dolo 650, Tylenol, Brufen")
    if med_query:
        retriever = load_medicine_retriever()
        results = retriever.search_medicines(med_query)
        if results:
            for m in results[:2]:
                with st.expander(f"💊 {m['generic_name']}", expanded=True):
                    st.write(f"**Brands:** {', '.join(m['brand_names'])}")
                    st.write(f"**Class:** {m['drug_class']}")
                    st.write(f"**Indications:** {', '.join(m['labeled_indications'][:4])}")
                    st.write(f"**Side Effects:** {', '.join(m.get('common_side_effects', [])[:3])}")
        else:
            st.info("No matching medicine in local curated database.")

    st.markdown("---")
    st.markdown("### ⚠️ Drug Interaction Checker")
    check_drugs = st.multiselect("Select 2+ drugs to test pairwise safety",
                                 ["Warfarin", "Ibuprofen", "Aspirin", "Paracetamol", "Amoxicillin", "Omeprazole", "Metformin", "Atorvastatin"],
                                 default=["Warfarin", "Ibuprofen"])
    if len(check_drugs) >= 2:
        safety_checker = load_safety_checker()
        report = safety_checker.check_polypharmacy_interactions(check_drugs)
        if report["interactions_found"]:
            for inter in report["interactions_found"]:
                effect_msg = inter.get("clinical_effect") or inter.get("effect") or "Potential adverse drug interaction."
                st.error(f"🚨 **{inter['drug_a']} + {inter['drug_b']}** ({inter.get('severity', 'Caution')})\n\n{effect_msg}")
        else:
            st.success("✅ No documented severe interactions found between selected drugs in database.")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="disclaimer-box">
        <strong>⚕️ Clinical Notice</strong><br>
        MediGuide AI is an <strong>educational research prototype</strong>. It does not provide definitive medical diagnoses or prescribe medications.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main Chat Area — Header with 3D Doctor Avatar
# ---------------------------------------------------------------------------
avatar_img_tag = f'<img src="data:image/png;base64,{_avatar_b64}" class="doctor-avatar-circle" alt="Dr. MediGuide AI" />' if _avatar_b64 else '<div style="font-size:3.5rem;">👨‍⚕️</div>'

user_name = st.session_state.user_name
greeting_name = user_name if user_name else "there"

st.markdown(f"""
<div class="doctor-hero-card">
    <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;">
        {avatar_img_tag}
        <div style="flex:1;min-width:260px;">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.25rem;">
                <h1 style="margin:0;font-size:2rem;color:#000000;">Dr. MediGuide AI</h1>
                <span class="status-badge-live">● CLINICAL ASSISTANT ACTIVE</span>
            </div>
            <p style="margin:0 0 0.5rem 0;color:#52525b;font-size:0.98rem;line-height:1.5;">
                Hello <strong>{greeting_name}</strong>! 👋 I am your AI Medical Assistant. Describe your symptoms naturally or ask about medicines.
                I will analyze hallmark markers, predict possible conditions, explain the underlying symptom correlation, and recommend standard reference tablets with strict safety checks — all personalized to your health profile.
            </p>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.6rem;">
                <span class="example-pill">💡 "High fever with chills, shivering, and headache"</span>
                <span class="example-pill">💡 "Severe stomach burning after meals"</span>
                <span class="example-pill">💡 "Continuous sneezing, watery eyes, and runny nose"</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Four-column metrics row
col1, col2, col3, col4 = st.columns(4)
try:
    meta_path = os.path.join("models", "model_metadata.json")
    with open(meta_path) as f:
        meta = json.load(f)
    col1.metric("Model Accuracy", f"{meta.get('held_out_accuracy',0)*100:.1f}%")
    col2.metric("Macro F1", f"{meta.get('held_out_macro_f1',0)*100:.1f}%")
    col3.metric("Top-3 Accuracy", f"{meta.get('held_out_top_3_accuracy',0)*100:.1f}%")
    col4.metric("Conditions Covered", meta.get("num_classes", 41))
except Exception:
    col1.metric("Model", "Loaded ✓")
    col2.metric("Conditions", "41")
    col3.metric("Medicines", "10+")
    col4.metric("Safety Rules", "30+")

st.markdown("")

# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------
user_chat_avatar = _get_user_chat_avatar()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=user_chat_avatar if msg["role"] == "user" else _doctor_avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Chat input handler
# ---------------------------------------------------------------------------
if user_input := st.chat_input(f"Hi {greeting_name}! Describe your symptoms or ask about a tablet…"):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=user_chat_avatar):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant", avatar=_doctor_avatar):
        with st.spinner(f"Dr. MediGuide is analyzing {greeting_name}'s symptoms and clinical guidelines…"):
            response_parts = []
            prof = st.session_state.get("patient_profile", {})

            # Build personalized profile summary for response text
            _profile_summary_parts = []
            if prof.get("age"):
                _profile_summary_parts.append(f"Age {prof['age']} ({prof.get('age_range', '')})")
            if prof.get("biological_sex") and prof["biological_sex"] != "Unspecified":
                _profile_summary_parts.append(prof["biological_sex"])
            _pre_conds = [c for c in prof.get("preexisting_conditions", []) if "None" not in c]
            if _pre_conds:
                _profile_summary_parts.append(f"with {', '.join(_pre_conds[:2])}")
            if prof.get("known_allergies"):
                _profile_summary_parts.append(f"allergic to {', '.join(prof['known_allergies'][:2])}")
            _profile_text = " · ".join(_profile_summary_parts) if _profile_summary_parts else ""

            # ── Step 1: Emergency triage ──
            from src.triage import screen_emergency_red_flags, generate_triage_questions
            triage = screen_emergency_red_flags(user_input)

            if triage["is_emergency"]:
                emergency_html = f"""
<div class="emergency-banner">
    <h3 style="color:#ef4444;margin:0 0 0.5rem 0;">🚨 {triage['category']}</h3>
    <p style="color:#991b1b;margin:0 0 0.5rem 0;font-size:0.95rem;"><strong>{greeting_name}</strong>, {triage['emergency_protocol']}</p>
    <p style="color:#ef4444;font-weight:700;margin:0;">
        {triage['action_required']}
    </p>
</div>
"""
                st.markdown(emergency_html, unsafe_allow_html=True)
                response_parts.append(emergency_html)
            else:
                # ── Step 2: Predict conditions ──
                predictor = load_predictor()
                result = predictor.predict(user_input, top_k=3)

                if result["status"] == "ABSTAIN_NO_SYMPTOMS":
                    abstain_html = f"""
<div class="safety-warning">
    <strong>🤔 Hi {greeting_name}, {result['message']}</strong>
</div>
"""
                    st.markdown(abstain_html, unsafe_allow_html=True)
                    if result.get("follow_up_questions"):
                        st.markdown("**Follow-up questions:**")
                        for q in result["follow_up_questions"]:
                            st.markdown(f"- {q}")
                    response_parts.append(abstain_html)
                else:
                    syms = result["extracted_symptoms"]
                    neg_syms = result["negated_symptoms"]

                    # ── Personalized greeting in response ──
                    greeting_html = f"""
<div style="margin-bottom:1rem;padding:0.8rem 1.2rem;background:linear-gradient(135deg,#eff6ff,#ffffff);border:1.5px solid #93c5fd;border-radius:12px;">
    <p style="margin:0;color:#1e3a8a;font-size:0.95rem;line-height:1.6;">
        <strong>👋 {greeting_name}</strong>, thank you for describing your symptoms. Based on your health profile
        ({_profile_text if _profile_text else 'general assessment'}), here is my detailed clinical analysis:
    </p>
</div>
"""
                    st.markdown(greeting_html, unsafe_allow_html=True)
                    response_parts.append(greeting_html)

                    # ── Detected Symptoms with per-symptom explanations ──
                    from src.medical_sources import get_condition_info, explain_symptom_match, get_symptom_2line_definition
                    st.markdown("### 🔬 Detected Symptoms — Explained")

                    symptom_cards_html = ""
                    for s in syms:
                        sym_def = get_symptom_2line_definition(s)
                        symptom_cards_html += f"""
<div class="symptom-explain-card">
    <div class="symptom-explain-icon">✅</div>
    <div class="symptom-explain-content">
        <div class="symptom-explain-name">{sym_def['name']}</div>
        <p class="symptom-explain-desc">{sym_def['line1_definition']}</p>
        <div class="symptom-explain-match">🎯 {sym_def['line2_match']}</div>
    </div>
</div>
"""
                    # Show negated symptoms
                    for s in neg_syms:
                        sym_def = get_symptom_2line_definition(s)
                        symptom_cards_html += f"""
<div class="symptom-explain-card" style="border-left-color:#94a3b8;opacity:0.7;">
    <div class="symptom-explain-icon">❌</div>
    <div class="symptom-explain-content">
        <div class="symptom-explain-name" style="text-decoration:line-through;color:#64748b;">{sym_def['name']}</div>
        <p class="symptom-explain-desc" style="color:#94a3b8;">{sym_def['line1_definition']} <em>(Ruled out by you)</em></p>
    </div>
</div>
"""
                    st.markdown(symptom_cards_html, unsafe_allow_html=True)
                    response_parts.append(symptom_cards_html)

                    # ── Step 3: Top predictions with explanations (3 in 1 horizontal line, square cards) ──
                    st.markdown(f"### 🩺 Predicted Conditions for {greeting_name}")
                    cards_html_list = []
                    for cand in result["top_predictions"]:
                        bar_pct = min(cand["calibrated_probability"] * 100, 100)
                        contrib_items = "".join(
                            f"<span class='pred-feature-pill'>{e['symptom']}</span>"
                            for e in cand["contributing_symptoms"][:4]
                        )
                        cards_html_list.append(f"""
<div class="prediction-square-card">
    <div class="pred-card-top">
        <span class="pred-rank-badge">#{cand['rank']}</span>
        <span class="pred-confidence-tag">{cand['confidence_percentage']}</span>
    </div>
    <div class="pred-card-body">
        <h4 class="pred-condition-title">{cand['condition']}</h4>
        <div class="pred-confidence-label">Match Probability</div>
        <div class="pred-bar-track">
            <div class="pred-bar-fill" style="width:{bar_pct}%;"></div>
        </div>
    </div>
    <div class="pred-card-footer">
        <div class="pred-features-label">Key Contributing Symptoms</div>
        <div class="pred-features-list">
            {contrib_items if contrib_items else '<span style="color:#71717a;font-size:0.75rem;">None identified</span>'}
        </div>
    </div>
</div>
""")
                    grid_html = f"""
<div class="predictions-grid">
    {''.join(cards_html_list)}
</div>
"""
                    st.markdown(grid_html, unsafe_allow_html=True)
                    response_parts.append(grid_html)

                    # ── Step 4: Comprehensive Symptom-to-Disease Match Explanation ──
                    top_cond = result["top_predictions"][0]["condition"] if result["top_predictions"] else None

                    if top_cond:
                        match_info = explain_symptom_match(top_cond, syms, neg_syms)
                        info = get_condition_info(top_cond)

                        match_chips = "".join([f'<span class="chip-pos">🎯 {s}</span>' for s in match_info['matched_symptoms']])

                        explanation_html = f"""
<div class="symptom-match-card">
    <div class="symptom-match-header">
        <h4 style="margin:0;color:#000000;display:flex;align-items:center;gap:8px;">
            🧠 {greeting_name}, Why Your Symptoms Match {top_cond}
        </h4>
        <span class="match-score-badge">★ {match_info['match_percentage']}% Hallmark Match</span>
    </div>
    <div style="margin-bottom:0.75rem;">
        <span style="color:#52525b;font-size:0.85rem;"><strong>Hallmark Signs Correlated:</strong></span>
        <div style="margin-top:3px;">{match_chips}</div>
    </div>
    <p style="color:#09090b;font-size:0.92rem;line-height:1.6;margin:0 0 0.6rem 0;">
        <strong>Clinical Rationale:</strong> {match_info['clinical_rationale']}
    </p>
    <p style="color:#52525b;font-size:0.88rem;line-height:1.5;margin:0 0 0.5rem 0;">
        <strong>Pathophysiological Mechanism:</strong> {match_info['pathophysiological_mechanism']}
    </p>
    <p style="color:#71717a;font-size:0.84rem;margin:0;">
        <strong>Differential Assessment:</strong> {match_info['differential_ruleout']}
    </p>
</div>
"""
                        st.markdown(explanation_html, unsafe_allow_html=True)
                        response_parts.append(explanation_html)

                        # ── Step 4b: Personalized Profile & Pre-existing Condition Analysis ──
                        checker = load_safety_checker()
                        profile_impact = checker.evaluate_disease_profile_impact(top_cond, prof)

                        if profile_impact.get("has_profile_risks"):
                            vuln_items = "".join([f"<li style='margin-bottom:5px;'>{v}</li>" for v in profile_impact["vulnerabilities"]])
                            advice_items = "".join([f"<li style='margin-bottom:5px;'>{a}</li>" for a in profile_impact["tailored_advice"]])
                            pre_tags = "".join([f"<span class='chip-pos' style='background:#f4f4f5;border-color:#000000;color:#000000;'>🩺 {d}</span>" for d in prof.get("preexisting_conditions", []) if "None" not in d])
                            
                            profile_html = f"""
<div class="symptom-match-card" style="border:2px solid #000000;background:#ffffff;">
    <div class="symptom-match-header">
        <h4 style="margin:0;color:#000000;display:flex;align-items:center;gap:8px;">
            👤 Personalized Analysis for {greeting_name}
        </h4>
        <span style="background:#000000;border:1px solid #000000;color:#ffffff;padding:3px 10px;border-radius:14px;font-size:0.78rem;font-weight:700;">
            Age: {prof.get('age', 32)} yrs ({prof.get('age_range', 'Adult')}) · {prof.get('biological_sex', '')}
        </span>
    </div>
    <div style="margin-bottom:0.6rem;">{pre_tags}</div>
    <div style="color:#09090b;font-size:0.9rem;line-height:1.5;margin-bottom:0.6rem;">
        <strong style="color:#000000;">⚠️ {greeting_name}, Clinical Vulnerabilities with {top_cond}:</strong>
        <ul style="margin:4px 0 8px 18px;padding:0;color:#18181b;">{vuln_items}</ul>
    </div>
    <div style="color:#09090b;font-size:0.9rem;line-height:1.5;">
        <strong style="color:#000000;">🛡️ Customized Care Directives for {greeting_name}:</strong>
        <ul style="margin:4px 0 0 18px;padding:0;color:#18181b;">{advice_items}</ul>
    </div>
</div>
"""
                            st.markdown(profile_html, unsafe_allow_html=True)
                            response_parts.append(profile_html)

                        # ── Step 5: Suggested Tablets & Medicines ──
                        ref_tablets = info.get("reference_tablets", [])
                        if ref_tablets:
                            st.markdown(f"### 💊 Recommended Reference Tablets for {greeting_name}")
                            # Personalized safety caption
                            _allergy_note = f" | ⚠️ Known Allergies: {', '.join(prof.get('known_allergies', []))}" if prof.get("known_allergies") else ""
                            _meds_note = f" | 💊 Current Meds: {', '.join(prof.get('current_medications', []))}" if prof.get("current_medications") else ""
                            st.caption(f"⚕️ Standard clinical reference medications — safety-checked against your profile ({_profile_text}){_allergy_note}{_meds_note}")

                            tablets_html_list = []
                            for tab in ref_tablets:
                                badge_class = "badge-otc" if "otc" in tab.get("prescription_status", "").lower() else "badge-rx"

                                # Comprehensive profile safety check (Allergies + Pre-existing Diseases + Age + Current Meds)
                                safety_alert_html = ""
                                eval_result = checker.evaluate_patient_profile(tab["name"], prof)
                                if eval_result.get("safety_alerts"):
                                    for al in eval_result["safety_alerts"]:
                                        is_contra = "contraindicated" in al.get("severity", "").lower()
                                        col = "#dc2626" if is_contra else "#d97706"
                                        bg_col = "#fef2f2" if is_contra else "#fffbeb"
                                        category_label = al.get("category", "Safety Alert")
                                        safety_alert_html += f"""
<div style="background:{bg_col};border:1.5px solid {col};border-radius:6px;padding:6px 10px;margin-top:6px;font-size:0.83rem;color:{col};font-weight:600;">
    ⚠️ [{category_label} for {greeting_name}]: {al.get('clinical_warning','')}
</div>
"""
                                else:
                                    safety_alert_html = f"""
<div style="background:#f4f4f5;border:1.5px solid #000000;border-radius:6px;padding:5px 10px;margin-top:6px;font-size:0.8rem;color:#000000;font-weight:600;">
    ✅ Compatible with {greeting_name}'s reported health profile and age bracket.
</div>
"""

                                tab_html = f"""
<div class="tablet-card">
    <div class="tablet-header">
        <div class="tablet-name">💊 {tab['name']}</div>
        <span class="{badge_class}">{tab.get('prescription_status','Reference')}</span>
    </div>
    <div class="tablet-row"><strong>Purpose / Indication:</strong> {tab.get('indication','')}</div>
    <div class="tablet-row"><strong>Dosage Form:</strong> {tab.get('dosage_form','Tablet')} &nbsp;|&nbsp; <strong>Class:</strong> {tab.get('category','')}</div>
    <div class="tablet-row"><strong>Clinical Usage Guidance:</strong> {tab.get('clinical_guidance','')}</div>
    <div class="tablet-caution"><strong>⚠️ Precaution:</strong> {tab.get('precautions','')}</div>
    {safety_alert_html}
</div>
"""
                                st.markdown(tab_html, unsafe_allow_html=True)
                                tablets_html_list.append(tab_html)

                            response_parts.append("\n".join(tablets_html_list))

                        # ── Step 6: Verified Medical Knowledge & Citations ──
                        with st.expander(f"📖 Official Medical Information & Evidence — {top_cond}", expanded=False):
                            st.markdown(f"**Clinical Overview:** {info['overview']}")
                            st.markdown(f"**Recommended Clinical Steps:** {info['recommended_next_steps']}")
                            if info.get("urgent_warnings"):
                                st.markdown(f"""
<div class="safety-warning">⚠️ <strong>Urgent Warning:</strong> {info['urgent_warnings']}</div>
""", unsafe_allow_html=True)
                            st.markdown("**📚 Official Health Authority Citations:**")
                            for cite in info.get("citations", []):
                                st.markdown(f"""
<div class="source-citation">
    🏛️ <strong>{cite['source']}</strong><br>
    🔗 <a href="{cite['url']}" target="_blank" style="color:#000000;text-decoration:underline;">{cite['url']}</a>
</div>
""", unsafe_allow_html=True)

                    # ── Step 7: Clinical Follow-up Inquiries ──
                    fups = result.get("follow_up_questions", [])
                    profile_qs = generate_triage_questions(st.session_state.get("patient_profile", {}))
                    all_qs = list(dict.fromkeys(fups + profile_qs))
                    if all_qs:
                        st.markdown(f"### 🗣️ Follow-up Questions for {greeting_name}")
                        for q in all_qs[:3]:
                            st.markdown(f"- {q}")

                    # ── Step 8: Strict Clinical Disclaimer ──
                    disclaimer_html = f"""
<div class="disclaimer-box" style="margin-top:1.2rem;">
    ⚕️ <strong>Clinical Disclaimer for {greeting_name}:</strong> {result.get('disclaimer',
    'MediGuide AI is an educational research prototype. These predictions and tablet recommendations are for informational analysis only. Always consult a licensed physician or pharmacist for clinical diagnosis and prescriptions.')}
</div>
"""
                    st.markdown(disclaimer_html, unsafe_allow_html=True)
                    response_parts.append(disclaimer_html)

            # Save assistant message in chat history
            full_response = "\n".join(response_parts) if response_parts else f"Hi {greeting_name}, please describe your symptoms."
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# ---------------------------------------------------------------------------
# Bottom tabs — About · Methodology · Safety Protocols
# ---------------------------------------------------------------------------
st.markdown("---")
tab_about, tab_method, tab_safety = st.tabs(["ℹ️ About MediGuide", "🔬 AI Architecture", "🛡️ Clinical Safety Protocols"])

with tab_about:
    st.markdown("""
    ### About Dr. MediGuide AI
    MediGuide AI is a research-oriented symptom prediction and medicine safety intelligence platform combining:
    - **Machine Learning Benchmark:** Trained across 4,920 cases, 131 clinical symptom features, and 41 disease classes.
    - **Regulatory Pharmacovigilance:** Drug interaction matrix and indications benchmarked against US FDA DailyMed and CDSCO India.
    - **Emergency Red-Flag Screening:** Continuous triage based on CDC, AHA, and WHO emergency algorithms.
    """)

with tab_method:
    st.markdown("""
    ### Machine Learning Architecture
    - **Champion Model:** Calibrated Multinomial Logistic Regression & Random Forest ensemble with Platt scaling.
    - **NLP Extraction:** Lemmatized n-gram matching with 120+ medical symptom synonym dictionaries and negation resolution.
    - **Top-3 Diagnostic Candidates:** Outputs probability-ranked candidate conditions with feature contribution attribution.
    """)

with tab_safety:
    st.markdown("""
    ### Medical Safety Protocols
    - **Zero Autonomous Prescriptions:** All tablet references are provided strictly as educational standard-of-care references.
    - **Active Allergy Screening:** Real-time cross-reactivity checking (e.g., Penicillin allergy vs. Beta-lactams).
    - **Emergency Prioritisation:** Chest pain, stroke, or anaphylaxis trigger immediate 911 / 112 guidance ahead of all ML predictions.
    """)
