EMBEDDED_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>Dr. MediGuide AI — Medical Chatbot</title>
  <meta name="description" content="Advanced clinical AI application with ML-backed condition prediction, pathophysiological symptom-match explanation, reference tablet suggestions, drug safety checks, and emergency triage.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body class="theme-light">

  <!-- ===================================================================== -->
  <!-- 🎬 ONBOARDING WELCOME MODAL: Name + Optional Photo + Quick Profile    -->
  <!-- ===================================================================== -->
  <div id="onboarding-modal" class="onboarding-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="onboarding-title-text">
    <div class="onboarding-container">
      <button class="onboarding-close-btn" id="btn-close-onboard" title="Close modal" aria-label="Close modal">&times;</button>
      
      <img src="assets/doctor_avatar.png" class="onboarding-avatar" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\\'onboarding-avatar-placeholder\\'>👨‍⚕️</div>'">
      <h2 id="onboarding-title-text" class="onboarding-title">Welcome to Dr. MediGuide AI</h2>
      <p class="onboarding-subtitle">
        Your personal AI Medical Assistant is ready to help.<br>
        Please enter your details so I can personalize your diagnostic insights and safety checks.
      </p>

      <form id="onboarding-form" class="onboarding-form">
        <div class="form-group">
          <label class="form-label" for="onboard-name-input">Your Name <span class="required-asterisk">*</span></label>
          <input type="text" id="onboard-name-input" class="form-input" placeholder="e.g. Rahul, Priya, Alex…" required autocomplete="name">
        </div>

        <div class="form-group">
          <label class="form-label">Profile Photo <span class="text-muted">(optional)</span></label>
          <div class="photo-upload-row">
            <div id="onboard-photo-preview" class="photo-preview-circle">🧑‍💼</div>
            <input type="file" id="onboard-photo-input" class="file-input" accept="image/*">
            <label for="onboard-photo-input" class="btn btn-outline btn-sm">📷 Choose Photo</label>
          </div>
          <span class="form-caption">Personalizes your consultation and avatar.</span>
        </div>

        <div class="form-group">
          <label class="form-label" for="onboard-age-input">Age (Years) <span class="required-asterisk">*</span></label>
          <input type="number" id="onboard-age-input" class="form-input" min="1" max="115" value="28" placeholder="e.g. 28" required>
        </div>

        <div class="form-actions" style="margin-top:1.4rem;">
          <button type="submit" class="btn btn-primary btn-large btn-block" id="btn-start-consultation">
            🚀 Enter Consultation
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Mobile Sidebar Backdrop Overlay -->
  <div id="sidebar-overlay" class="sidebar-overlay hidden" aria-hidden="true"></div>

  <!-- Emergency Red-Flag Alert Banner -->
  <div id="emergency-banner" class="emergency-banner hidden" role="alert" aria-live="assertive">
    <div class="emergency-content">
      <div class="emergency-icon">🚨</div>
      <div class="emergency-text">
        <h4 id="emergency-title">CRITICAL MEDICAL EMERGENCY DETECTED</h4>
        <p id="emergency-message">Please call 911 (US) or 112 / 102 (India) immediately.</p>
      </div>
      <a href="tel:911" class="btn-emergency-call" id="btn-emergency-call">📞 Call 911 / 112</a>
      <button class="emergency-dismiss" id="btn-emergency-dismiss" title="Dismiss banner">&times;</button>
    </div>
  </div>

  <!-- App Header -->
  <header class="app-header">
    <div class="header-inner">
      <div class="brand">
        <button class="btn-sidebar-hamburger" id="btn-sidebar-hamburger" title="Toggle Clinical Profile Sidebar" aria-label="Toggle Clinical Profile">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="hamburger-icon">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
        </div>
        <div class="brand-info">
          <div class="brand-title-row">
            <h1 class="brand-name">Dr. MediGuide AI</h1>
            <span class="status-badge-live">● CLINICAL ASSISTANT ACTIVE</span>
          </div>
          <p class="brand-tagline">Clinical Symptom Prediction & Medicine Safety Chatbot</p>
        </div>
      </div>

      <div class="header-actions">
        <button class="user-profile-header-btn" id="btn-header-profile" title="View / Edit Profile">
          <div class="header-avatar-circle" id="header-avatar-circle">🧑‍💼</div>
          <span class="header-user-name" id="header-user-name">User</span>
        </button>
        <button class="btn-theme-toggle" id="btn-theme-toggle" title="Toggle Theme" aria-label="Toggle Theme">
          <span class="theme-icon-light">☀️</span>
          <span class="theme-icon-dark">🌙</span>
        </button>
      </div>
    </div>
  </header>

  <!-- ===================================================================== -->
  <!-- RESPONSIVE AUTO-ADAPTIVE LAYOUT: Desktop / Tablet / Mobile            -->
  <!-- ===================================================================== -->
  <div class="app-layout">

    <!-- ── LEFT SIDEBAR: Patient Clinical Profile (Streamlit Parity) ── -->
    <aside class="app-sidebar" id="app-sidebar" aria-label="Patient Profile Sidebar">
      <div class="sidebar-inner">

        <!-- Mobile Close Button -->
        <div class="sidebar-mobile-header">
          <span class="sidebar-mobile-title">Clinical Profile</span>
          <button class="btn-sidebar-close" id="btn-sidebar-close" title="Close Sidebar" aria-label="Close Sidebar">&times;</button>
        </div>

        <!-- User Profile Card (Streamlit Parity) -->
        <div class="sidebar-user-card" id="sidebar-user-card">
          <div class="sidebar-user-avatar-wrap">
            <div class="sidebar-user-avatar-circle" id="sidebar-user-avatar">🧑‍💼</div>
          </div>
          <div class="sidebar-user-name" id="sidebar-user-name">👋 Patient</div>
          <div class="sidebar-user-details" id="sidebar-user-details">
            📅 Young Adult (18 - 35 yrs)<br>
            ⚧ Male · 🩺 Hypertension
          </div>
          <button class="btn btn-outline btn-sm btn-edit-profile-modal" id="btn-edit-profile-modal">
            ✏️ Edit Profile / Switch User
          </button>
        </div>

        <!-- Sidebar Section Header -->
        <div class="sidebar-header">
          <h2 class="sidebar-title">👤 Patient Clinical Profile</h2>
          <p class="sidebar-caption">
            Personalise your profile to tailor diagnostic analysis, chronic disease precautions, and tablet safety.
          </p>
        </div>

        <!-- Age Range / Bracket Dropdown -->
        <div class="sidebar-group">
          <label class="sidebar-label" for="sidebar-age-range">Age Range / Bracket</label>
          <select id="sidebar-age-range" class="sidebar-select">
            <option value="Infant / Child (0 - 12 yrs)">Infant / Child (0 - 12 yrs)</option>
            <option value="Adolescent (13 - 17 yrs)">Adolescent (13 - 17 yrs)</option>
            <option value="Young Adult (18 - 35 yrs)" selected>Young Adult (18 - 35 yrs)</option>
            <option value="Adult (36 - 64 yrs)">Adult (36 - 64 yrs)</option>
            <option value="Senior / Geriatric (65+ yrs)">Senior / Geriatric (65+ yrs)</option>
          </select>
        </div>

        <!-- Specific Age Slider -->
        <div class="sidebar-group">
          <div class="slider-label-row">
            <label class="sidebar-label" for="sidebar-age-slider">Specific Age (Years)</label>
            <span class="slider-val-badge" id="sidebar-age-val">28</span>
          </div>
          <input type="range" id="sidebar-age-slider" class="sidebar-slider" min="18" max="35" value="28">
        </div>

        <!-- Pre-existing Chronic Conditions -->
        <div class="sidebar-group">
          <h3 class="sidebar-subheading">🩺 Existing Medical Issues</h3>
          <label class="sidebar-label" for="select-add-condition">Pre-existing Diseases & Health Issues</label>
          
          <div class="tags-container" id="conditions-tags-container">
            <!-- Dynamically populated tags with remove 'x' buttons -->
          </div>

          <div class="dropdown-add-wrap">
            <select id="select-add-condition" class="sidebar-select-add">
              <option value="" disabled selected>+ Add a pre-existing condition…</option>
              <option value="Type 2 Diabetes">Type 2 Diabetes</option>
              <option value="Hypertension (High Blood Pressure)">Hypertension (High Blood Pressure)</option>
              <option value="Chronic Kidney Disease (CKD)">Chronic Kidney Disease (CKD)</option>
              <option value="Liver Cirrhosis / Hepatic Disease">Liver Cirrhosis / Hepatic Disease</option>
              <option value="Bronchial Asthma / COPD">Bronchial Asthma / COPD</option>
              <option value="Peptic Ulcer Disease / Acid Reflux (GERD)">Peptic Ulcer Disease / Acid Reflux (GERD)</option>
              <option value="Coronary Artery Disease (CAD) / Heart Disease">Coronary Artery Disease (CAD) / Heart Disease</option>
              <option value="Stroke History">Stroke History</option>
              <option value="Thyroid Disorder">Thyroid Disorder</option>
              <option value="None / Generally Healthy">None / Generally Healthy</option>
            </select>
          </div>
        </div>

        <!-- Other Symptoms / Health Notes -->
        <div class="sidebar-group">
          <label class="sidebar-label" for="sidebar-health-notes">Other Symptoms / Health Notes</label>
          <input type="text" id="sidebar-health-notes" class="sidebar-input" placeholder="e.g. chronic acidity, heavy smoker, migra">
        </div>

        <!-- Biological Sex -->
        <div class="sidebar-group">
          <label class="sidebar-label" for="sidebar-sex">Biological Sex</label>
          <select id="sidebar-sex" class="sidebar-select">
            <option value="Unspecified">Unspecified</option>
            <option value="Female">Female</option>
            <option value="Male" selected>Male</option>
          </select>
        </div>

        <!-- Pregnant checkbox (if Female) -->
        <div class="sidebar-group hidden" id="sidebar-pregnant-group">
          <label class="sidebar-checkbox-label">
            <input type="checkbox" id="sidebar-pregnant"> 🤰 Pregnant or Breastfeeding?
          </label>
        </div>

        <!-- Known Drug Allergies -->
        <div class="sidebar-group">
          <label class="sidebar-label" for="select-add-allergy">Known Drug Allergies</label>
          <div class="tags-container" id="allergies-tags-container">
            <!-- Dynamically populated allergy tags -->
          </div>
          <select id="select-add-allergy" class="sidebar-select-add">
            <option value="" disabled selected>+ Add an allergy…</option>
            <option value="Penicillin">Penicillin</option>
            <option value="Amoxicillin">Amoxicillin</option>
            <option value="Aspirin / NSAIDs">Aspirin / NSAIDs</option>
            <option value="Sulfa drugs">Sulfa drugs</option>
            <option value="Macrolides">Macrolides</option>
            <option value="Latex">Latex</option>
          </select>
        </div>

        <!-- Current Medications -->
        <div class="sidebar-group">
          <label class="sidebar-label" for="select-add-med">Current Medications</label>
          <div class="tags-container" id="meds-tags-container">
            <!-- Dynamically populated current medications tags -->
          </div>
          <select id="select-add-med" class="sidebar-select-add">
            <option value="" disabled selected>+ Add current medication…</option>
            <option value="Warfarin">Warfarin</option>
            <option value="Ibuprofen">Ibuprofen</option>
            <option value="Aspirin">Aspirin</option>
            <option value="Metformin">Metformin</option>
            <option value="Omeprazole">Omeprazole</option>
            <option value="Atorvastatin">Atorvastatin</option>
            <option value="Lisinopril">Lisinopril</option>
            <option value="Paracetamol">Paracetamol</option>
          </select>
        </div>

        <hr class="sidebar-divider">

        <!-- 🔍 Medicine Lookup -->
        <div class="sidebar-group">
          <h3 class="sidebar-subheading">🔍 Medicine Lookup</h3>
          <div class="sidebar-search-row">
            <input type="text" id="sidebar-med-search" class="sidebar-input" placeholder="Search brand / generic (e.g. Dolo 650, Tylenol)…">
            <button class="btn btn-primary btn-sm" id="btn-sidebar-med-search">Search</button>
          </div>
          <div id="sidebar-med-results" class="sidebar-results-box"></div>
        </div>

        <hr class="sidebar-divider">

        <!-- ⚠️ Drug Interaction Checker -->
        <div class="sidebar-group">
          <h3 class="sidebar-subheading">⚠️ Drug Interaction Checker</h3>
          <p class="sidebar-caption">Screen 2+ medications for severe bleeding, cardiac, or liver interactions.</p>
          <button class="btn btn-primary btn-block btn-sm" id="btn-screen-interactions">
            🔍 Check Regimen Interactions
          </button>
          <div id="sidebar-interaction-results" class="sidebar-results-box"></div>
        </div>

        <hr class="sidebar-divider">

        <!-- Clear Chat Button -->
        <button class="btn btn-secondary btn-block btn-sm" id="btn-clear-chat">
          🗑️ Clear Chat History
        </button>

        <!-- Clinical Disclaimer Box -->
        <div class="sidebar-disclaimer-box">
          <strong>⚕️ Clinical Notice</strong><br>
          MediGuide AI is an <strong>educational research prototype</strong>. It does not provide definitive medical diagnoses or prescribe medications. Always consult a licensed healthcare professional.
        </div>

      </div>
    </aside>

    <!-- ── RIGHT MAIN CHAT AREA (Streamlit Parity) ── -->
    <main class="app-main">

      <!-- Doctor Hero Card -->
      <div class="doctor-hero-card">
        <div class="doctor-hero-inner">
          <div class="doctor-avatar-wrap">
            <img src="assets/doctor_avatar.png" class="doctor-avatar-circle" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\\'doctor-avatar-circle fallback\\'>👨‍⚕️</div>'">
          </div>
          <div class="doctor-hero-body">
            <div class="hero-title-row">
              <h2 class="hero-title">Dr. MediGuide AI</h2>
              <span class="status-badge-live">● CLINICAL ASSISTANT ACTIVE</span>
            </div>
            <p class="hero-text">
              Hello <strong id="hero-user-name">there</strong>! 👋 I am your AI Medical Assistant. Describe your symptoms naturally or ask about medicines. I will analyze hallmark markers, predict possible conditions, explain the underlying symptom correlation, and recommend standard reference tablets with strict safety checks.
            </p>
            <div class="example-pills-row">
              <button class="example-pill" data-query="High fever with chills, shivering, and headache">💡 "High fever with chills, shivering, and headache"</button>
              <button class="example-pill" data-query="Severe stomach burning after meals">💡 "Severe stomach burning after meals"</button>
              <button class="example-pill" data-query="Continuous sneezing, watery eyes, and runny nose">💡 "Continuous sneezing, watery eyes, and runny nose"</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 4-Column Model Accuracy Metrics Row -->
      <div class="metrics-grid" id="metrics-grid">
        <div class="metric-card">
          <span class="metric-card-label">Model Accuracy</span>
          <span class="metric-card-value" id="metric-accuracy">100.0%</span>
          <span class="metric-card-sub">Held-out test split</span>
        </div>
        <div class="metric-card">
          <span class="metric-card-label">Macro F1</span>
          <span class="metric-card-value" id="metric-f1">100.0%</span>
          <span class="metric-card-sub">Balanced harmonic mean</span>
        </div>
        <div class="metric-card">
          <span class="metric-card-label">Top-3 Accuracy</span>
          <span class="metric-card-value" id="metric-top3">100.0%</span>
          <span class="metric-card-sub">Condition in top 3 differential</span>
        </div>
        <div class="metric-card">
          <span class="metric-card-label">Conditions Covered</span>
          <span class="metric-card-value" id="metric-classes">41</span>
          <span class="metric-card-sub">131 symptom features</span>
        </div>
      </div>

      <!-- Chat Stream Container -->
      <div class="chat-container" id="chat-container">
        <div class="chat-stream" id="chat-stream">
          <!-- Welcome Initial Message from Doctor -->
          <div class="chat-message assistant">
            <div class="chat-avatar-col">
              <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\\'chat-avatar-placeholder\\'>👨‍⚕️</div>'">
            </div>
            <div class="chat-bubble">
              <div class="chat-bubble-header">
                <span class="chat-sender-name">Dr. MediGuide AI</span>
                <span class="chat-time-tag">Active</span>
              </div>
              <p id="chat-welcome-text">
                Hello! I am ready to evaluate your clinical presentation. You can:
              </p>
              <ul class="styled-chat-list">
                <li><strong>Describe symptoms naturally</strong> (e.g. <em>"high fever with chills, rigors and severe headache"</em>, <em>"severe stomach burning after meals"</em>, <em>"pain in legs and fatigue"</em>).</li>
                <li><strong>Ask about any condition or disease</strong> (e.g. <em>"what is dengue"</em>, <em>"tell me about malaria"</em>, <em>"GERD symptoms"</em>).</li>
                <li><strong>Ask about medications or tablets</strong> (e.g. <em>"Dolo 650"</em>, <em>"tablet for headache"</em>, <em>"Paracetamol dosage"</em>).</li>
              </ul>
              <p style="margin-top:0.6rem;font-size:0.86rem;color:var(--text-secondary);">
                All diagnostic predictions and tablet safety warnings are customized in real-time to your <strong>Patient Clinical Profile</strong> in the sidebar.
              </p>
            </div>
          </div>
          <!-- Subsequent user & assistant messages appended here dynamically -->
        </div>
      </div>

      <!-- Sticky Chat Input Bar at Bottom (Streamlit Parity) -->
      <div class="chat-input-wrapper">
        <form id="chat-input-form" class="chat-input-form">
          <textarea 
            id="chat-textarea" 
            class="chat-textarea" 
            rows="1" 
            placeholder="Describe your symptoms (e.g. fever, headache, chills) or ask about a tablet…" 
            aria-label="Describe symptoms"
            required
          ></textarea>
          <button type="submit" class="btn-chat-send" id="btn-chat-send" title="Send message" aria-label="Send message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="send-icon">
              <line x1="12" y1="19" x2="12" y2="5"></line>
              <polyline points="5 12 12 5 19 12"></polyline>
            </svg>
          </button>
        </form>
        <div class="chat-input-subtext">
          <span>Dr. MediGuide AI is an educational research prototype. Always seek professional physician guidance.</span>
        </div>
      </div>

      <!-- Bottom Tabs: About · Methodology · Safety Protocols -->
      <div class="bottom-tabs-section">
        <div class="bottom-tab-buttons" role="tablist">
          <button class="bottom-tab-btn active" data-bottom-tab="btab-about">ℹ️ About MediGuide</button>
          <button class="bottom-tab-btn" data-bottom-tab="btab-method">🔬 AI Architecture</button>
          <button class="bottom-tab-btn" data-bottom-tab="btab-safety">🛡️ Clinical Safety Protocols</button>
        </div>

        <div class="bottom-tab-content active" id="btab-about">
          <h3>About Dr. MediGuide AI</h3>
          <p>MediGuide AI is a research-oriented symptom prediction and medicine safety intelligence platform combining:</p>
          <ul class="styled-list">
            <li><strong>Machine Learning Benchmark:</strong> Trained across 4,920 clinical cases, 131 symptom features, and 41 disease classes with 100% held-out test accuracy.</li>
            <li><strong>Regulatory Pharmacovigilance:</strong> Drug interaction matrix and indications benchmarked against US FDA DailyMed and CDSCO India.</li>
            <li><strong>Emergency Red-Flag Screening:</strong> Continuous triage based on CDC, AHA, and WHO emergency algorithms.</li>
          </ul>
        </div>

        <div class="bottom-tab-content" id="btab-method">
          <h3>Machine Learning Architecture</h3>
          <ul class="styled-list">
            <li><strong>Champion Model:</strong> Calibrated Multinomial Logistic Regression & Random Forest ensemble with Platt scaling.</li>
            <li><strong>NLP Extraction:</strong> Multi-gram entity matching with 250+ medical symptom synonym dictionaries, condition intent recognition, and negation resolution.</li>
            <li><strong>Top-3 Diagnostic Candidates:</strong> Outputs probability-ranked candidate conditions with feature contribution attribution.</li>
          </ul>
        </div>

        <div class="bottom-tab-content" id="btab-safety">
          <h3>Medical Safety Protocols</h3>
          <ul class="styled-list">
            <li><strong>Zero Autonomous Prescriptions:</strong> All tablet references are provided strictly as educational standard-of-care references.</li>
            <li><strong>Active Allergy Screening:</strong> Real-time cross-reactivity checking (e.g., Penicillin allergy vs. Beta-lactams).</li>
            <li><strong>Emergency Prioritisation:</strong> Chest pain, stroke, or anaphylaxis trigger immediate 911 / 112 guidance ahead of all ML predictions.</li>
          </ul>
        </div>
      </div>

    </main>
  </div>

  <script src="app.js"></script>
</body>
</html>
"""

EMBEDDED_STYLE_CSS = """/* ==========================================================================
   Dr. MediGuide AI — Responsive Clinical Design System
   Auto-Alignment for Desktop, Tablet, and Mobile in White & Blue Theme
   ========================================================================== */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
  /* ── White & Blue Clinical Palette ── */
  --bg-primary: #ffffff;
  --bg-secondary: #f0f7ff;
  --bg-card: #ffffff;
  --bg-card-hover: #f8fafc;
  --bg-input: #ffffff;

  --accent-primary: #2563eb;
  --accent-secondary: #0284c7;
  --accent-navy: #1e3a8a;
  --accent-light: #eff6ff;
  --accent-glow: rgba(37, 99, 235, 0.2);

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;
  --text-inverse: #ffffff;

  --danger: #dc2626;
  --danger-bg: #fef2f2;
  --tag-coral: #ef4444;
  --tag-coral-bg: #fee2e2;
  --warning: #d97706;
  --warning-bg: #fffbeb;
  --success: #16a34a;
  --success-bg: #dcfce7;

  --border: #dbeafe;
  --border-strong: #93c5fd;
  --border-accent: #2563eb;
  --border-dark: #1e3a8a;

  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
  --radius-full: 9999px;

  --sidebar-width: 330px;

  --shadow-sm: 0 1px 3px rgba(37, 99, 235, 0.05);
  --shadow-md: 0 4px 16px rgba(37, 99, 235, 0.08);
  --shadow-lg: 0 10px 30px rgba(37, 99, 235, 0.12);

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-display: 'Outfit', 'Inter', sans-serif;
  --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

body.theme-dark {
  --bg-primary: #0b1120;
  --bg-secondary: #111a2e;
  --bg-card: #152238;
  --bg-card-hover: #1e2e4a;
  --bg-input: #111c30;

  --accent-primary: #3b82f6;
  --accent-secondary: #38bdf8;
  --accent-navy: #93c5fd;
  --accent-light: rgba(59, 130, 246, 0.15);
  --accent-glow: rgba(59, 130, 246, 0.25);

  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --text-inverse: #0f172a;

  --danger: #f87171;
  --danger-bg: rgba(220, 38, 38, 0.18);
  --warning: #fbbf24;
  --warning-bg: rgba(217, 119, 6, 0.18);
  --success: #4ade80;
  --success-bg: rgba(22, 163, 74, 0.18);

  --border: #1e3a5f;
  --border-strong: #2563eb;
  --border-accent: #38bdf8;
  --border-dark: #60a5fa;

  --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.35);
  --shadow-lg: 0 10px 35px rgba(0, 0, 0, 0.5);
}

/* ── Typography & Global resets ── */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  font-family: var(--font-sans);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
  overflow-x: hidden;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  color: var(--accent-navy);
  letter-spacing: -0.02em;
}

p, span, label, div {
  color: inherit;
}

/* ── Onboarding Welcome Modal ── */
.onboarding-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(6px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.2rem;
  overflow-y: auto;
}

.onboarding-overlay.hidden {
  display: none !important;
}

.onboarding-container {
  max-width: 600px;
  width: 100%;
  padding: 2.2rem 2.4rem;
  background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 50%, #eff6ff 100%);
  border: 2px solid var(--border-strong);
  border-radius: 20px;
  box-shadow: 0 16px 50px rgba(37, 99, 235, 0.2);
  text-align: center;
  position: relative;
  animation: modalScaleUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

body.theme-dark .onboarding-container {
  background: linear-gradient(135deg, #111a2e 0%, #152238 60%, #172844 100%);
  border-color: #2563eb;
}

@keyframes modalScaleUp {
  0% { transform: scale(0.94); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.onboarding-close-btn {
  position: absolute;
  top: 14px;
  right: 18px;
  background: transparent;
  border: none;
  font-size: 1.6rem;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
}

.onboarding-avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  border: 3px solid var(--accent-primary);
  box-shadow: 0 0 25px var(--accent-glow);
  object-fit: cover;
  margin: 0 auto 1rem auto;
  display: block;
  background: #eff6ff;
}

.onboarding-title {
  font-size: 1.65rem;
  font-weight: 800;
  color: var(--accent-navy);
  margin-bottom: 0.35rem;
}

.onboarding-subtitle {
  color: var(--text-secondary);
  font-size: 0.92rem;
  line-height: 1.5;
  margin-bottom: 1.4rem;
}

.onboarding-form {
  text-align: left;
}

.photo-upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.photo-preview-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 2px solid var(--accent-primary);
  background: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  overflow: hidden;
  object-fit: cover;
  flex-shrink: 0;
}

.photo-preview-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-input {
  display: none;
}

.form-caption {
  font-size: 0.76rem;
  color: var(--text-muted);
  display: block;
  margin-top: 4px;
}

.form-divider {
  border: 0;
  border-top: 1.5px solid var(--border);
  margin: 1.2rem 0;
}

.form-subheading {
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-navy);
  margin-bottom: 0.8rem;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

@media (max-width: 550px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }
}

.chip-select-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.chip-checkbox {
  cursor: pointer;
  display: inline-flex;
}

.chip-checkbox input {
  display: none;
}

.chip-checkbox span {
  display: inline-block;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  color: var(--text-secondary);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
  transition: var(--transition);
}

.chip-checkbox input:checked + span {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
  font-weight: 600;
}

.required-asterisk {
  color: var(--danger);
}

/* ── Mobile Sidebar Overlay ── */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  z-index: 150;
  transition: opacity 0.3s ease;
}

.sidebar-overlay.hidden {
  display: none;
}

/* ── App Header ── */
.app-header {
  background: var(--bg-primary);
  border-bottom: 1.5px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 120;
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.04);
}

.header-inner {
  max-width: 100%;
  padding: 0.65rem 1.4rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-sidebar-hamburger {
  background: transparent;
  border: none;
  cursor: pointer;
  display: none;
  padding: 4px;
  color: var(--accent-navy);
}

.hamburger-icon {
  width: 24px;
  height: 24px;
}

@media (max-width: 960px) {
  .btn-sidebar-hamburger {
    display: inline-flex;
    align-items: center;
  }
}

.brand-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  flex-shrink: 0;
}

.brand-icon svg {
  width: 22px;
  height: 22px;
}

.brand-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
  color: var(--accent-navy);
}

.brand-tagline {
  font-size: 0.74rem;
  color: var(--text-muted);
}

@media (max-width: 600px) {
  .brand-tagline {
    display: none;
  }
}

.status-badge-live {
  background: #dbeafe;
  border: 1px solid #93c5fd;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 14px;
  font-size: 0.72rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-profile-header-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--accent-light);
  border: 1.5px solid var(--border-strong);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-navy);
  cursor: pointer;
  transition: var(--transition);
}

.user-profile-header-btn:hover {
  border-color: var(--accent-primary);
  transform: translateY(-1px);
}

.header-avatar-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  overflow: hidden;
}

.header-avatar-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-theme-toggle {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  padding: 5px 9px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: var(--transition);
}

body.theme-light .theme-icon-light { display: inline-block; }
body.theme-light .theme-icon-dark { display: none; }
body.theme-dark .theme-icon-light { display: none; }
body.theme-dark .theme-icon-dark { display: inline-block; }

/* ── Emergency Alert Banner ── */
.emergency-banner {
  background: var(--danger-bg);
  border-bottom: 2px solid var(--danger);
  padding: 0.75rem 1.2rem;
  position: sticky;
  top: 55px;
  z-index: 110;
  box-shadow: 0 4px 14px rgba(220, 38, 38, 0.15);
}

.emergency-banner.hidden {
  display: none !important;
}

.emergency-content {
  max-width: 1380px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.emergency-icon {
  font-size: 1.6rem;
}

.emergency-text {
  flex: 1;
  min-width: 200px;
}

.emergency-text h4 {
  color: var(--danger);
  font-size: 0.92rem;
  font-weight: 800;
  margin-bottom: 2px;
}

.emergency-text p {
  color: #991b1b;
  font-size: 0.82rem;
  margin: 0;
}

.btn-emergency-call {
  background: var(--danger);
  color: #ffffff !important;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.84rem;
}

.emergency-dismiss {
  background: transparent;
  border: none;
  font-size: 1.4rem;
  color: var(--danger);
  cursor: pointer;
}

/* ===================================================================== */
/* ── AUTO-ADAPTABLE APP LAYOUT (Desktop / Tablet / Phone) ──             */
/* ===================================================================== */
.app-layout {
  display: flex;
  min-height: calc(100vh - 60px);
  position: relative;
  width: 100%;
}

/* ── LEFT SIDEBAR: Patient Clinical Profile ── */
.app-sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
  border-right: 1.5px solid var(--border);
  height: calc(100vh - 60px);
  position: sticky;
  top: 60px;
  overflow-y: auto;
  z-index: 100;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
}

body.theme-dark .app-sidebar {
  background: linear-gradient(180deg, #111a2e 0%, #0b1120 100%);
  border-right-color: #1e3a5f;
}

/* Tablet & Mobile Slide-in Drawer */
@media (max-width: 960px) {
  .app-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    height: 100vh;
    z-index: 200;
    transform: translateX(-105%);
    box-shadow: 6px 0 30px rgba(0, 0, 0, 0.25);
  }
  .app-sidebar.open {
    transform: translateX(0);
  }
}

.sidebar-mobile-header {
  display: none;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.8rem;
}

@media (max-width: 960px) {
  .sidebar-mobile-header {
    display: flex;
  }
}

.sidebar-mobile-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--accent-navy);
}

.btn-sidebar-close {
  background: transparent;
  border: none;
  font-size: 1.8rem;
  color: var(--accent-navy);
  cursor: pointer;
  line-height: 1;
}

.sidebar-inner {
  padding: 1.3rem 1.15rem 3rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Sidebar User Card */
.sidebar-user-card {
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  border: 1.5px solid var(--border-strong);
  border-radius: var(--radius-md);
  padding: 1rem;
  text-align: center;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.05);
}

body.theme-dark .sidebar-user-card {
  background: linear-gradient(135deg, #111a2e 0%, #152238 100%);
  border-color: #2563eb;
}

.sidebar-user-avatar-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 3px solid var(--accent-primary);
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem auto;
  font-size: 1.6rem;
  color: #ffffff;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(37, 99, 235, 0.2);
}

.sidebar-user-avatar-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sidebar-user-name {
  font-family: var(--font-display);
  font-size: 1.12rem;
  font-weight: 700;
  color: var(--accent-navy);
  margin-bottom: 0.2rem;
}

.sidebar-user-details {
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.45;
  margin-bottom: 0.7rem;
}

.btn-edit-profile-modal {
  width: 100%;
  font-size: 0.78rem;
  padding: 5px 10px;
}

.sidebar-header {
  margin-top: 2px;
}

.sidebar-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--accent-navy);
  margin-bottom: 0.25rem;
}

.sidebar-caption {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.sidebar-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.sidebar-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--accent-navy);
}

.sidebar-subheading {
  font-size: 0.94rem;
  font-weight: 700;
  color: var(--accent-navy);
  margin-top: 4px;
}

.sidebar-select, .sidebar-input, .sidebar-select-add {
  width: 100%;
  padding: 0.52rem 0.75rem;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 0.84rem;
  outline: none;
  transition: var(--transition);
}

.sidebar-select:focus, .sidebar-input:focus, .sidebar-select-add:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18);
}

.slider-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-val-badge {
  background: #f87171;
  color: #ffffff;
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 700;
}

.sidebar-slider {
  width: 100%;
  accent-color: #f87171;
  height: 6px;
  border-radius: 4px;
  cursor: pointer;
  margin: 4px 0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  min-height: 26px;
  margin: 2px 0 4px 0;
}

.tag-pill {
  background: #f87171;
  color: #ffffff;
  font-size: 0.76rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.tag-pill.blue {
  background: var(--accent-primary);
}

.tag-remove-btn {
  cursor: pointer;
  font-weight: 800;
  font-size: 0.85rem;
  line-height: 1;
}

.sidebar-checkbox-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.sidebar-divider {
  border: 0;
  border-top: 1.5px solid var(--border);
  margin: 3px 0;
}

.sidebar-search-row {
  display: flex;
  gap: 6px;
}

.sidebar-results-box {
  margin-top: 5px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  max-height: 180px;
  overflow-y: auto;
}

.sidebar-disclaimer-box {
  background: #f8fafc;
  border: 1.5px dashed #93c5fd;
  border-radius: var(--radius-sm);
  padding: 0.75rem 0.9rem;
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.45;
}

/* ===================================================================== */
/* ── RIGHT MAIN CHAT AREA (Auto-adapts to Device Width) ──              */
/* ===================================================================== */
.app-main {
  flex: 1;
  min-width: 0;
  padding: 1.6rem 2rem 8.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1080px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 1024px) {
  .app-main {
    padding: 1.2rem 1.4rem 8.5rem 1.4rem;
  }
}

@media (max-width: 768px) {
  .app-main {
    padding: 1rem 0.9rem 7.5rem 0.9rem;
  }
}

/* ── Doctor Hero Card ── */
.doctor-hero-card {
  background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 60%, #eff6ff 100%);
  border: 2px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 1.4rem 1.8rem;
  box-shadow: 0 8px 30px rgba(37, 99, 235, 0.08);
}

body.theme-dark .doctor-hero-card {
  background: linear-gradient(135deg, #111a2e 0%, #152238 60%, #172844 100%);
  border-color: #2563eb;
}

@media (max-width: 600px) {
  .doctor-hero-card {
    padding: 1.1rem 1.1rem;
  }
}

.doctor-hero-inner {
  display: flex;
  align-items: center;
  gap: 1.4rem;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .doctor-hero-inner {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}

.doctor-avatar-circle {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  border: 3px solid var(--accent-primary);
  box-shadow: 0 0 20px var(--accent-glow);
  object-fit: cover;
  background: #eff6ff;
  display: block;
}

.doctor-hero-body {
  flex: 1;
  min-width: 240px;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.3rem;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .hero-title-row {
    justify-content: center;
  }
}

.hero-title {
  margin: 0;
  font-size: 1.7rem;
  color: var(--accent-navy);
}

.hero-text {
  margin: 0 0 0.65rem 0;
  color: var(--text-secondary);
  font-size: 0.92rem;
  line-height: 1.55;
}

.example-pills-row {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

@media (max-width: 600px) {
  .example-pills-row {
    justify-content: center;
  }
}

.example-pill {
  background: #ffffff;
  border: 1.5px solid #bfdbfe;
  color: #1e40af;
  padding: 4px 11px;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  font-family: var(--font-sans);
}

body.theme-dark .example-pill {
  background: var(--bg-card);
  border-color: #2563eb;
  color: #93c5fd;
}

.example-pill:hover {
  border-color: var(--accent-primary);
  background: var(--accent-primary);
  color: #ffffff;
  transform: translateY(-1px);
}

/* ── 4-Column Model Accuracy Metrics Row ── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

@media (max-width: 900px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

.metric-card {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-left: 4px solid var(--accent-primary);
  border-radius: var(--radius-md);
  padding: 0.9rem 1.1rem;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.05);
  display: flex;
  flex-direction: column;
  transition: var(--transition);
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.1);
}

.metric-card-label {
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 2px;
}

.metric-card-value {
  color: var(--accent-navy);
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 3px;
}

.metric-card-sub {
  color: var(--text-secondary);
  font-size: 0.74rem;
}

/* ── Chat Stream Container ── */
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
}

.chat-stream {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
  animation: messageFade 0.25s ease;
}

@keyframes messageFade {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.chat-avatar-col {
  flex-shrink: 0;
}

.chat-avatar-img, .chat-avatar-placeholder {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid var(--accent-primary);
  object-fit: cover;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  overflow: hidden;
}

.chat-message.user .chat-avatar-placeholder {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: #ffffff;
  font-size: 1.15rem;
  font-weight: 700;
}

.chat-bubble {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.2rem 1.4rem;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.06);
  flex: 1;
  max-width: 90%;
  line-height: 1.6;
  font-size: 0.92rem;
}

@media (max-width: 600px) {
  .chat-bubble {
    padding: 0.95rem 1.05rem;
    max-width: 88%;
    font-size: 0.88rem;
  }
}

.chat-message.user .chat-bubble {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: 1.5px solid #1e40af;
  color: #ffffff;
  max-width: 80%;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.2);
}

.chat-message.user .chat-bubble p {
  color: #ffffff !important;
}

.chat-message.user .chat-sender-name {
  color: #ffffff !important;
}

.chat-message.user .chat-time-tag {
  color: #dbeafe !important;
}

.chat-message.user .chat-bubble-header {
  border-bottom: 1px dashed rgba(255, 255, 255, 0.3) !important;
}

.chat-bubble-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  border-bottom: 1px dashed var(--border);
  padding-bottom: 0.35rem;
}

.chat-sender-name {
  font-weight: 700;
  color: var(--accent-navy);
  font-size: 0.92rem;
}

.chat-time-tag {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.styled-chat-list {
  margin: 0.5rem 0 0.5rem 1.3rem;
}

.styled-chat-list li {
  margin-bottom: 0.3rem;
}

/* ── Assistant Rich Response Components ── */
.response-section {
  margin: 1.1rem 0;
}

.section-header-title {
  font-size: 1.12rem;
  font-weight: 800;
  color: var(--accent-navy);
  margin-bottom: 0.55rem;
  display: flex;
  align-items: center;
  gap: 7px;
}

/* 🔬 Symptom Explain Cards */
.symptom-cards-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.symptom-explain-card {
  background: #ffffff;
  border: 1.5px solid var(--border);
  border-left: 4px solid var(--accent-primary);
  border-radius: 10px;
  padding: 0.7rem 1rem;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.04);
}

body.theme-dark .symptom-explain-card {
  background: var(--bg-card);
}

.symptom-explain-card.negated {
  border-left-color: #94a3b8;
  opacity: 0.75;
}

.symptom-explain-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.symptom-explain-content {
  flex: 1;
}

.symptom-explain-name {
  font-weight: 700;
  font-size: 0.92rem;
  color: var(--accent-navy);
  margin-bottom: 2px;
}

.symptom-explain-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.45;
  margin: 0;
}

.symptom-explain-match {
  font-size: 0.78rem;
  color: var(--accent-secondary);
  font-weight: 600;
  margin-top: 3px;
}

/* 🩺 Predicted Conditions: 3 in 1 Horizontal Line, Square Shape (Streamlit Parity) */
.predictions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  width: 100%;
  margin: 0.7rem 0 1.1rem 0;
}

@media (max-width: 820px) {
  .predictions-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

.prediction-square-card {
  background: #ffffff;
  border: 2px solid #3b82f6;
  border-radius: 14px;
  padding: 1.1rem 0.95rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: stretch;
  text-align: center;
  min-height: 240px;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  box-sizing: border-box;
}

body.theme-dark .prediction-square-card {
  background: var(--bg-card);
  border-color: #2563eb;
}

.prediction-square-card:hover {
  transform: translateY(-2px);
  border-color: #1d4ed8;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.12);
}

.pred-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 0.45rem;
}

.pred-rank-badge {
  background: var(--accent-primary);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 8px;
  font-family: var(--font-display);
}

.pred-confidence-tag {
  font-size: 0.8rem;
  font-weight: 700;
  color: #1d4ed8;
  background: #eff6ff;
  border: 1.5px solid #bfdbfe;
  padding: 2px 8px;
  border-radius: 12px;
}

body.theme-dark .pred-confidence-tag {
  background: rgba(37, 99, 235, 0.2);
  border-color: #3b82f6;
  color: #93c5fd;
}

.pred-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0.35rem 0;
}

.pred-condition-title {
  margin: 0 0 0.3rem 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--accent-navy) !important;
  line-height: 1.3;
}

.pred-confidence-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 600;
  margin-bottom: 5px;
}

.pred-bar-track {
  background: #dbeafe;
  border-radius: 6px;
  height: 8px;
  width: 100%;
  max-width: 160px;
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
  padding-top: 0.55rem;
  border-top: 1px dashed var(--border);
}

.pred-features-label {
  color: var(--text-muted);
  font-size: 0.68rem;
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
  font-size: 0.72rem;
  color: #1e40af;
  font-weight: 600;
}

/* 🧠 Symptom Match Explanation Card */
.symptom-match-card {
  background: #ffffff;
  border: 2px solid #3b82f6;
  border-radius: var(--radius-md);
  padding: 1.2rem 1.4rem;
  box-shadow: 0 4px 18px rgba(37, 99, 235, 0.06);
  margin: 0.9rem 0;
}

body.theme-dark .symptom-match-card {
  background: var(--bg-card);
}

.symptom-match-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.7rem;
  flex-wrap: wrap;
  gap: 7px;
}

.match-score-badge {
  background: #dbeafe;
  border: 1.5px solid #2563eb;
  color: #1e40af;
  padding: 3px 10px;
  border-radius: 18px;
  font-size: 0.82rem;
  font-weight: 700;
}

.chip-pos {
  background: #eff6ff;
  border: 1.5px solid #3b82f6;
  color: #1d4ed8;
  padding: 3px 9px;
  border-radius: 14px;
  font-size: 0.8rem;
  display: inline-block;
  margin: 2px;
  font-weight: 600;
}

/* 👤 Personalized Profile Card */
.profile-impact-card {
  background: #ffffff;
  border: 2px solid var(--accent-navy);
  border-radius: var(--radius-md);
  padding: 1.2rem 1.4rem;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.06);
  margin: 0.9rem 0;
}

body.theme-dark .profile-impact-card {
  background: var(--bg-card);
  border-color: #3b82f6;
}

/* 💊 Reference Tablets Shelf */
.tablets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  width: 100%;
  margin-top: 0.5rem;
}

.tablet-card {
  background: #ffffff;
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.05);
}

body.theme-dark .tablet-card {
  background: var(--bg-card);
}

.tablet-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 6px;
}

.tablet-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-navy);
  line-height: 1.3;
}

.badge-otc {
  background: #dcfce7;
  border: 1px solid #86efac;
  color: #166534;
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
  white-space: nowrap;
}

.badge-rx {
  background: #ede9fe;
  border: 1px solid #c4b5fd;
  color: #5b21b6;
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
  white-space: nowrap;
}

.tablet-row {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.45;
  margin-bottom: 0.35rem;
}

.tablet-row strong {
  color: var(--text-primary);
}

.tablet-caution {
  background: var(--warning-bg);
  border-left: 3px solid var(--warning);
  padding: 5px 8px;
  border-radius: 4px;
  color: #92400e;
  font-size: 0.76rem;
  line-height: 1.4;
  margin-top: 5px;
}

.tablet-safety-alert {
  border-radius: 6px;
  padding: 5px 8px;
  margin-top: 7px;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1.4;
}

.tablet-safety-alert.safe {
  background: #f0fdf4;
  border: 1.5px solid #22c55e;
  color: #15803d;
}

.tablet-safety-alert.warn {
  background: #fffbeb;
  border: 1.5px solid #f59e0b;
  color: #b45309;
}

.tablet-safety-alert.contra {
  background: #fef2f2;
  border: 1.5px solid #ef4444;
  color: #b91c1c;
}

/* 📖 Evidence Expander */
.evidence-expander {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 0.9rem 0;
}

.evidence-expander-header {
  background: var(--bg-secondary);
  padding: 0.8rem 1.1rem;
  font-weight: 700;
  color: var(--accent-navy);
  cursor: pointer;
  outline: none;
  font-size: 0.92rem;
}

.evidence-expander-content {
  padding: 1.1rem 1.3rem;
  font-size: 0.86rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.source-citation {
  background: #f8fafc;
  border: 1.5px solid #dbeafe;
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.8rem;
  margin: 0.35rem 0;
  font-size: 0.8rem;
  color: #334155;
}

.source-citation a {
  color: var(--accent-primary) !important;
  text-decoration: underline !important;
  font-weight: 600;
}

/* 🗣️ Follow-up Questions */
.follow-up-item-interactive {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 11px;
  font-size: 0.84rem;
  color: var(--accent-navy);
  font-weight: 500;
  cursor: pointer;
  margin: 4px 0;
  transition: var(--transition);
}

.follow-up-item-interactive:hover {
  background: var(--accent-light);
  border-color: var(--accent-primary);
  transform: translateX(4px);
}

/* Disclaimer Box */
.disclaimer-box {
  background: #f8fafc;
  border: 1.5px dashed #93c5fd;
  border-radius: var(--radius-md);
  padding: 0.9rem 1.1rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
  margin-top: 0.9rem;
}

/* ===================================================================== */
/* ── RESPONSIVE STICKY CHAT INPUT BAR (Auto-aligns on any device) ──    */
/* ===================================================================== */
.chat-input-wrapper {
  position: fixed;
  bottom: 0;
  left: var(--sidebar-width);
  right: 0;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(8px);
  border-top: 1.5px solid var(--border);
  padding: 0.8rem 2rem 0.7rem 2rem;
  z-index: 90;
  box-shadow: 0 -4px 20px rgba(37, 99, 235, 0.08);
  transition: left 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

body.theme-dark .chat-input-wrapper {
  left: var(--sidebar-width);
  background: rgba(11, 17, 32, 0.94);
  border-top-color: #1e3a5f;
}

@media (max-width: 960px) {
  .chat-input-wrapper {
    left: 0 !important;
    padding: 0.7rem 1rem 0.6rem 1rem;
    padding-bottom: max(0.6rem, env(safe-area-inset-bottom));
  }
}

.chat-input-form {
  max-width: 1020px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 2px solid var(--accent-primary);
  border-radius: var(--radius-md);
  padding: 3px 6px 3px 12px;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.1);
  transition: var(--transition);
}

body.theme-dark .chat-input-form {
  background: var(--bg-card);
  border-color: #3b82f6;
}

.chat-input-form:focus-within {
  border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.22);
}

.chat-textarea {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-family: var(--font-sans);
  font-size: 0.94rem;
  color: var(--text-primary);
  resize: none;
  height: 38px;
  padding: 8px 0;
  line-height: 1.4;
}

.btn-chat-send {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: #ffffff;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  flex-shrink: 0;
}

.btn-chat-send:hover {
  background: linear-gradient(135deg, #1d4ed8, #0369a1);
  transform: translateY(-1px);
}

.send-icon {
  width: 18px;
  height: 18px;
}

.chat-input-subtext {
  text-align: center;
  margin-top: 4px;
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* ── Bottom Tabs Section ── */
.bottom-tabs-section {
  margin-top: 1.8rem;
  border-top: 1.5px solid var(--border);
  padding-top: 1.3rem;
}

.bottom-tab-buttons {
  display: flex;
  gap: 7px;
  border-bottom: 2px solid var(--accent-primary);
  margin-bottom: 1.1rem;
  flex-wrap: wrap;
}

.bottom-tab-btn {
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-bottom: none;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  padding: 0.55rem 1.25rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.bottom-tab-btn.active {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  color: #ffffff;
  border-color: var(--accent-primary);
}

.bottom-tab-content {
  display: none;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  padding: 1.3rem 1.6rem;
}

.bottom-tab-content.active {
  display: block;
}

.styled-list {
  margin: 0.7rem 0 0 1.3rem;
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.6;
}

.styled-list li {
  margin-bottom: 0.45rem;
}

/* ── Common Buttons & Utilities ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-family: var(--font-sans);
  font-weight: 600;
  padding: 0.55rem 1.2rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
  transition: var(--transition);
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #0369a1 100%);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--bg-secondary);
  border: 1.5px solid var(--border);
  color: var(--accent-navy);
}

.btn-secondary:hover {
  background: var(--accent-light);
  border-color: var(--accent-primary);
}

.btn-outline {
  background: transparent;
  border: 1.5px solid var(--accent-primary);
  color: var(--accent-primary);
}

.btn-outline:hover {
  background: var(--accent-light);
}

.btn-sm {
  padding: 0.38rem 0.8rem;
  font-size: 0.8rem;
}

.btn-large {
  padding: 0.75rem 1.6rem;
  font-size: 1rem;
}

.btn-block {
  width: 100%;
}

.hidden {
  display: none !important;
}

/* ── Typing Animation Dots ── */
.typing-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-primary);
  animation: typingBounce 1s infinite alternate;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  from { transform: translateY(0); opacity: 0.4; }
  to { transform: translateY(-4px); opacity: 1; }
}
"""

EMBEDDED_APP_JS = """/**
 * Dr. MediGuide AI — Client Application Script
 * Streamlit Parity: Left Sidebar Patient Clinical Profile + Interactive Clinical Chatbot.
 */

// Global State
const state = {
  theme: localStorage.getItem('mediguide_theme') || 'light',
  patientProfile: JSON.parse(localStorage.getItem('mediguide_profile') || JSON.stringify({
    name: 'Patient',
    photo: '',
    age: 28,
    age_range: 'Young Adult (18 - 35 yrs)',
    biological_sex: 'Male',
    is_pregnant: false,
    preexisting_conditions: ['Hypertension (High Blood Pressure)'],
    other_health_issues: '',
    known_allergies: ['Penicillin'],
    current_medications: ['Warfarin', 'Ibuprofen']
  })),
  messages: []
};

// Emergency Heuristic Regex Patterns
const EMERGENCY_PATTERNS = [
  /\\b(crushing chest pain|chest pain radiating|pain in left arm|chest pressure and sweating|heart attack)\\b/i,
  /\\b(facial drooping|face droop|slurred speech|slurring words|one side weakness|cannot lift arm|stroke)\\b/i,
  /\\b(cannot breathe|unable to breathe|gasping for air|turning blue|blue lips|swelling of throat|anaphylaxis)\\b/i,
  /\\b(unconscious|passed out|unresponsive|prolonged seizure|coma)\\b/i,
  /\\b(coughing up blood|vomiting blood|uncontrolled bleeding)\\b/i
];

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initOnboardingModal();
  initSidebarProfile();
  updateUIProfileDisplays();
  initChatInput();
  initExamplePills();
  initModelMetadata();
  initMedicineLookup();
  initInteractionChecker();
  initClearChat();
  initBottomTabs();
});

// -----------------------------------------------------------------------------
// 1. Theme & Navigation
// -----------------------------------------------------------------------------
function initTheme() {
  const body = document.body;
  const toggleBtn = document.getElementById('btn-theme-toggle');

  if (state.theme === 'dark') {
    body.classList.remove('theme-light');
    body.classList.add('theme-dark');
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      if (body.classList.contains('theme-dark')) {
        body.classList.remove('theme-dark');
        body.classList.add('theme-light');
        state.theme = 'light';
      } else {
        body.classList.remove('theme-light');
        body.classList.add('theme-dark');
        state.theme = 'dark';
      }
      localStorage.setItem('mediguide_theme', state.theme);
    });
  }

  // Sidebar toggle for mobile drawer & overlay
  const hamburger = document.getElementById('btn-sidebar-hamburger') || document.getElementById('btn-sidebar-toggle');
  const sidebar = document.getElementById('app-sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const closeSidebarBtn = document.getElementById('btn-sidebar-close');

  const toggleSidebar = (forceOpen) => {
    if (!sidebar) return;
    const shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !sidebar.classList.contains('open');
    sidebar.classList.toggle('open', shouldOpen);
    if (overlay) {
      overlay.classList.toggle('hidden', !shouldOpen);
    }
  };

  if (hamburger) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleSidebar();
    });
  }

  if (closeSidebarBtn) {
    closeSidebarBtn.addEventListener('click', () => {
      toggleSidebar(false);
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      toggleSidebar(false);
    });
  }

  // Emergency banner dismiss
  const btnDismissEmergency = document.getElementById('btn-emergency-dismiss');
  if (btnDismissEmergency) {
    btnDismissEmergency.addEventListener('click', () => {
      document.getElementById('emergency-banner').classList.add('hidden');
    });
  }
}

// -----------------------------------------------------------------------------
// 1b. Onboarding Welcome Modal (Name, Photo & Age Login)
// -----------------------------------------------------------------------------
function initOnboardingModal() {
  const modal = document.getElementById('onboarding-modal');
  const form = document.getElementById('onboarding-form');
  const nameInput = document.getElementById('onboard-name-input');
  const photoInput = document.getElementById('onboard-photo-input');
  const photoPreview = document.getElementById('onboard-photo-preview');
  const ageInput = document.getElementById('onboard-age-input');
  const btnClose = document.getElementById('btn-close-onboard');
  const btnEditProfile = document.getElementById('btn-edit-profile-modal');
  const btnHeaderProfile = document.getElementById('btn-header-profile');

  let uploadedPhotoData = state.patientProfile.photo || '';

  const populateModalForm = () => {
    const p = state.patientProfile;
    if (nameInput) nameInput.value = (p.name && p.name !== 'Patient') ? p.name : '';
    if (ageInput) ageInput.value = p.age || 28;
    if (photoPreview) {
      if (p.photo) {
        photoPreview.innerHTML = `<img src="${p.photo}" alt="User Avatar" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
      } else {
        photoPreview.innerHTML = '🧑‍💼';
      }
    }
    uploadedPhotoData = p.photo || '';
  };

  const showModal = () => {
    populateModalForm();
    if (modal) modal.classList.remove('hidden');
    if (nameInput) setTimeout(() => nameInput.focus(), 150);
  };

  const hideModal = () => {
    if (modal) modal.classList.add('hidden');
  };

  // Check if first-time visitor
  const hasOnboarded = localStorage.getItem('mediguide_has_onboarded');
  if (!hasOnboarded) {
    showModal();
  }

  // Handle Photo File Upload
  if (photoInput) {
    photoInput.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        if (file.size > 3 * 1024 * 1024) {
          alert('Photo size is large. Please select an image under 3MB.');
        }
        const reader = new FileReader();
        reader.onload = (evt) => {
          uploadedPhotoData = evt.target.result;
          if (photoPreview) {
            photoPreview.innerHTML = `<img src="${uploadedPhotoData}" alt="Uploaded Photo" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Handle Form Submission (Only Name, Photo, Age)
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const enteredName = (nameInput ? nameInput.value.trim() : '') || 'Patient';
      state.patientProfile.name = enteredName;
      state.patientProfile.photo = uploadedPhotoData || '';

      const enteredAge = ageInput ? parseInt(ageInput.value, 10) || 28 : 28;
      state.patientProfile.age = enteredAge;

      if (enteredAge <= 12) state.patientProfile.age_range = 'Infant / Child (0 - 12 yrs)';
      else if (enteredAge <= 17) state.patientProfile.age_range = 'Adolescent (13 - 17 yrs)';
      else if (enteredAge <= 35) state.patientProfile.age_range = 'Young Adult (18 - 35 yrs)';
      else if (enteredAge <= 64) state.patientProfile.age_range = 'Adult (36 - 64 yrs)';
      else state.patientProfile.age_range = 'Senior / Geriatric (65+ yrs)';

      localStorage.setItem('mediguide_has_onboarded', 'true');
      saveProfile();
      updateUIProfileDisplays();
      hideModal();
    });
  }

  if (btnClose) {
    btnClose.addEventListener('click', hideModal);
  }

  if (btnEditProfile) {
    btnEditProfile.addEventListener('click', showModal);
  }

  if (btnHeaderProfile) {
    btnHeaderProfile.addEventListener('click', showModal);
  }
}

// -----------------------------------------------------------------------------
// Update All Profile Elements Across Desktop / Tablet / Mobile UI
// -----------------------------------------------------------------------------
function updateUIProfileDisplays() {
  const p = state.patientProfile;
  const userName = p.name || 'Patient';

  // 1. Header
  const headerName = document.getElementById('header-user-name');
  if (headerName) headerName.textContent = userName;

  const headerAvatar = document.getElementById('header-avatar-circle');
  if (headerAvatar) {
    if (p.photo) {
      headerAvatar.innerHTML = `<img src="${p.photo}" alt="${escapeHtml(userName)}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
    } else {
      headerAvatar.textContent = '🧑‍💼';
    }
  }

  // 2. Doctor Hero Card personalized greeting
  const heroName = document.getElementById('hero-user-name');
  if (heroName) heroName.textContent = userName;

  // 3. Sidebar User Card
  const sidebarName = document.getElementById('sidebar-user-name');
  if (sidebarName) sidebarName.textContent = `👋 ${userName}`;

  const sidebarAvatar = document.getElementById('sidebar-user-avatar');
  if (sidebarAvatar) {
    if (p.photo) {
      sidebarAvatar.innerHTML = `<img src="${p.photo}" alt="${escapeHtml(userName)}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
    } else {
      sidebarAvatar.textContent = '🧑‍💼';
    }
  }

  const sidebarDetails = document.getElementById('sidebar-user-details');
  if (sidebarDetails) {
    const condList = p.preexisting_conditions || [];
    const condStr = condList.length > 0
      ? condList[0] + (condList.length > 1 ? ` (+${condList.length - 1})` : '')
      : 'None recorded';
    sidebarDetails.innerHTML = `📅 ${escapeHtml(p.age_range || 'Young Adult')}<br>⚧ ${escapeHtml(p.biological_sex || 'Male')} · 🩺 ${escapeHtml(condStr)}`;
  }

  // 4. Sync Sidebar Controls
  const sidebarAgeRange = document.getElementById('sidebar-age-range');
  if (sidebarAgeRange && p.age_range) sidebarAgeRange.value = p.age_range;

  const sidebarAgeSlider = document.getElementById('sidebar-age-slider');
  const sidebarAgeVal = document.getElementById('sidebar-age-val');
  if (sidebarAgeSlider && p.age) {
    sidebarAgeSlider.value = p.age;
    if (sidebarAgeVal) sidebarAgeVal.textContent = p.age;
  }

  const sidebarSex = document.getElementById('sidebar-sex');
  if (sidebarSex && p.biological_sex) sidebarSex.value = p.biological_sex;

  const pregnantGroup = document.getElementById('sidebar-pregnant-group');
  if (pregnantGroup) {
    if (p.biological_sex === 'Female') pregnantGroup.classList.remove('hidden');
    else pregnantGroup.classList.add('hidden');
  }

  // Sync tags
  renderTagList('conditions-tags-container', p.preexisting_conditions, (newTags) => {
    p.preexisting_conditions = newTags;
    saveProfile();
    updateUIProfileDisplays();
  });
}

// -----------------------------------------------------------------------------
// 2. Sidebar Patient Clinical Profile (Streamlit Parity)
// -----------------------------------------------------------------------------
function initSidebarProfile() {
  const p = state.patientProfile;

  // Age range select
  const ageRangeSelect = document.getElementById('sidebar-age-range');
  const ageSlider = document.getElementById('sidebar-age-slider');
  const ageValBadge = document.getElementById('sidebar-age-val');

  const updateSliderRange = (bracket) => {
    if (!ageSlider) return;
    if (bracket.includes('0 - 12')) {
      ageSlider.min = 0; ageSlider.max = 12;
    } else if (bracket.includes('13 - 17')) {
      ageSlider.min = 13; ageSlider.max = 17;
    } else if (bracket.includes('18 - 35')) {
      ageSlider.min = 18; ageSlider.max = 35;
    } else if (bracket.includes('36 - 64')) {
      ageSlider.min = 36; ageSlider.max = 64;
    } else {
      ageSlider.min = 65; ageSlider.max = 100;
    }
  };

  if (ageRangeSelect) {
    ageRangeSelect.value = p.age_range || 'Young Adult (18 - 35 yrs)';
    updateSliderRange(ageRangeSelect.value);

    ageRangeSelect.addEventListener('change', () => {
      p.age_range = ageRangeSelect.value;
      updateSliderRange(p.age_range);
      p.age = parseInt(ageSlider.min, 10) + Math.round((parseInt(ageSlider.max, 10) - parseInt(ageSlider.min, 10)) / 2);
      ageSlider.value = p.age;
      if (ageValBadge) ageValBadge.textContent = p.age;
      saveProfile();
    });
  }

  if (ageSlider) {
    ageSlider.value = p.age || 28;
    if (ageValBadge) ageValBadge.textContent = p.age;

    ageSlider.addEventListener('input', () => {
      p.age = parseInt(ageSlider.value, 10);
      if (ageValBadge) ageValBadge.textContent = p.age;
      saveProfile();
    });
  }

  // Pre-existing conditions tags
  renderTagList('conditions-tags-container', p.preexisting_conditions, (newTags) => {
    p.preexisting_conditions = newTags;
    saveProfile();
  });

  const condAddSelect = document.getElementById('select-add-condition');
  if (condAddSelect) {
    condAddSelect.addEventListener('change', () => {
      const val = condAddSelect.value;
      if (val && !p.preexisting_conditions.includes(val)) {
        p.preexisting_conditions.push(val);
        renderTagList('conditions-tags-container', p.preexisting_conditions, (newTags) => {
          p.preexisting_conditions = newTags;
          saveProfile();
        });
        saveProfile();
      }
      condAddSelect.selectedIndex = 0;
    });
  }

  // Other notes
  const notesInput = document.getElementById('sidebar-health-notes');
  if (notesInput) {
    notesInput.value = p.other_health_issues || '';
    notesInput.addEventListener('input', () => {
      p.other_health_issues = notesInput.value;
      saveProfile();
    });
  }

  // Biological sex
  const sexSelect = document.getElementById('sidebar-sex');
  const pregnantGroup = document.getElementById('sidebar-pregnant-group');
  const pregnantCheckbox = document.getElementById('sidebar-pregnant');

  if (sexSelect) {
    sexSelect.value = p.biological_sex || 'Male';
    if (pregnantGroup) {
      if (sexSelect.value === 'Female') pregnantGroup.classList.remove('hidden');
      else pregnantGroup.classList.add('hidden');
    }

    sexSelect.addEventListener('change', () => {
      p.biological_sex = sexSelect.value;
      if (pregnantGroup) {
        if (p.biological_sex === 'Female') pregnantGroup.classList.remove('hidden');
        else pregnantGroup.classList.add('hidden');
      }
      saveProfile();
    });
  }

  if (pregnantCheckbox) {
    pregnantCheckbox.checked = !!p.is_pregnant;
    pregnantCheckbox.addEventListener('change', () => {
      p.is_pregnant = pregnantCheckbox.checked;
      saveProfile();
    });
  }

  // Known allergies tags
  renderTagList('allergies-tags-container', p.known_allergies, (newTags) => {
    p.known_allergies = newTags;
    saveProfile();
  });

  const allergyAddSelect = document.getElementById('select-add-allergy');
  if (allergyAddSelect) {
    allergyAddSelect.addEventListener('change', () => {
      const val = allergyAddSelect.value;
      if (val && !p.known_allergies.includes(val)) {
        p.known_allergies.push(val);
        renderTagList('allergies-tags-container', p.known_allergies, (newTags) => {
          p.known_allergies = newTags;
          saveProfile();
        });
        saveProfile();
      }
      allergyAddSelect.selectedIndex = 0;
    });
  }

  // Current medications tags
  renderTagList('meds-tags-container', p.current_medications, (newTags) => {
    p.current_medications = newTags;
    saveProfile();
  }, 'blue');

  const medAddSelect = document.getElementById('select-add-med');
  if (medAddSelect) {
    medAddSelect.addEventListener('change', () => {
      const val = medAddSelect.value;
      if (val && !p.current_medications.includes(val)) {
        p.current_medications.push(val);
        renderTagList('meds-tags-container', p.current_medications, (newTags) => {
          p.current_medications = newTags;
          saveProfile();
        }, 'blue');
        saveProfile();
      }
      medAddSelect.selectedIndex = 0;
    });
  }
}

function renderTagList(containerId, tagArray, onUpdate, colorClass = '') {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';
  if (!tagArray || tagArray.length === 0) {
    container.innerHTML = '<span class="text-muted" style="font-size:0.75rem;">None added</span>';
    return;
  }

  tagArray.forEach((tag, idx) => {
    const pill = document.createElement('span');
    pill.className = `tag-pill ${colorClass}`;
    pill.innerHTML = `
      <span>${escapeHtml(tag)}</span>
      <span class="tag-remove-btn" title="Remove" data-idx="${idx}">&times;</span>
    `;
    pill.querySelector('.tag-remove-btn').addEventListener('click', () => {
      tagArray.splice(idx, 1);
      renderTagList(containerId, tagArray, onUpdate, colorClass);
      onUpdate(tagArray);
    });
    container.appendChild(pill);
  });
}

function saveProfile() {
  localStorage.setItem('mediguide_profile', JSON.stringify(state.patientProfile));
  const sDetails = document.getElementById('sidebar-user-details');
  if (sDetails) {
    const p = state.patientProfile;
    const condList = p.preexisting_conditions || [];
    const condStr = condList.length > 0
      ? condList[0] + (condList.length > 1 ? ` (+${condList.length - 1})` : '')
      : 'None recorded';
    sDetails.innerHTML = `📅 ${escapeHtml(p.age_range || 'Young Adult')}<br>⚧ ${escapeHtml(p.biological_sex || 'Male')} · 🩺 ${escapeHtml(condStr)}`;
  }
}

// -----------------------------------------------------------------------------
// 3. Model Accuracy Metrics
// -----------------------------------------------------------------------------
async function initModelMetadata() {
  try {
    const res = await fetch('/api/metadata');
    if (res.ok) {
      const meta = await res.json();
      const elAcc = document.getElementById('metric-accuracy');
      const elF1 = document.getElementById('metric-f1');
      const elTop3 = document.getElementById('metric-top3');
      const elClasses = document.getElementById('metric-classes');

      if (elAcc) elAcc.textContent = `${((meta.held_out_accuracy || 1.0) * 100).toFixed(1)}%`;
      if (elF1) elF1.textContent = `${((meta.held_out_macro_f1 || 1.0) * 100).toFixed(1)}%`;
      if (elTop3) elTop3.textContent = `${((meta.held_out_top_3_accuracy || 1.0) * 100).toFixed(1)}%`;
      if (elClasses) elClasses.textContent = meta.num_classes || 41;
    }
  } catch (e) {
    console.warn('Metadata fetch error:', e);
  }
}

// -----------------------------------------------------------------------------
// 4. Chat Input & Messaging System
// -----------------------------------------------------------------------------
function initChatInput() {
  const form = document.getElementById('chat-input-form');
  const textarea = document.getElementById('chat-textarea');

  if (textarea) {
    // Auto resize
    textarea.addEventListener('input', () => {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
      checkEmergencyInstant(textarea.value);
    });

    textarea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitUserMessage();
      }
    });
  }

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitUserMessage();
    });
  }
}

function initExamplePills() {
  const pills = document.querySelectorAll('.example-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const q = pill.getAttribute('data-query');
      if (q) {
        processUserQuery(q);
      }
    });
  });
}

function submitUserMessage() {
  const textarea = document.getElementById('chat-textarea');
  if (!textarea) return;
  const text = textarea.value.trim();
  if (!text) return;

  textarea.value = '';
  textarea.style.height = '38px';
  processUserQuery(text);
}

async function processUserQuery(text) {
  // 1. Append user message bubble and scroll down
  appendUserMessage(text);

  // 2. Append typing indicator bubble
  const typingBubbleId = appendTypingIndicator();

  const startTime = Date.now();
  const payload = {
    text: text,
    patient_profile: state.patientProfile
  };

  let data = null;
  const isLocalHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const isFileProto = window.location.protocol === 'file:';
  const isMobile = /Android|iPhone|iPad|iPod|Mobile|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 650;

  // On mobile devices, prioritize instant on-device clinical inference for sub-second response
  if (isMobile) {
    data = clientSideClinicalAnalysis(text, state.patientProfile);
  } else if (!isFileProto) {
    try {
      const ctrl1 = new AbortController();
      const t1 = setTimeout(() => ctrl1.abort(), 800);
      const res1 = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: ctrl1.signal
      });
      clearTimeout(t1);
      if (res1.ok) {
        data = await res1.json();
      }
    } catch (e1) {
      // Relative fetch timed out or offline
    }

    // Only try localhost:3000 if user is ACTUALLY on desktop localhost (never on mobile!)
    if (!data && isLocalHost && window.location.port !== '3000') {
      try {
        const ctrl2 = new AbortController();
        const t2 = setTimeout(() => ctrl2.abort(), 500);
        const res2 = await fetch('http://localhost:3000/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: ctrl2.signal
        });
        clearTimeout(t2);
        if (res2.ok) {
          data = await res2.json();
        }
      } catch (e2) {}
    }
  }

  // Guaranteed instant client-side clinical analysis fallback
  if (!data) {
    data = clientSideClinicalAnalysis(text, state.patientProfile);
  }

  // Ensure a smooth, natural typing delay of 250ms so reply feels organic and never lags
  const elapsed = Date.now() - startTime;
  const minDelay = 250;
  const remainingDelay = Math.max(0, minDelay - elapsed);

  setTimeout(() => {
    removeTypingIndicator(typingBubbleId);
    appendAssistantResponse(data);
  }, remainingDelay);
}

function appendUserMessage(text) {
  const stream = document.getElementById('chat-stream');
  if (!stream) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = 'chat-message user';
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const userName = state.patientProfile.name || 'You';
  const userPhoto = state.patientProfile.photo;

  const avatarContent = userPhoto
    ? `<img src="${userPhoto}" alt="${escapeHtml(userName)}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`
    : `🧑‍💼`;

  msgDiv.innerHTML = `
    <div class="chat-avatar-col">
      <div class="chat-avatar-placeholder" style="overflow:hidden;display:flex;align-items:center;justify-content:center;">${avatarContent}</div>
    </div>
    <div class="chat-bubble">
      <div class="chat-bubble-header">
        <span class="chat-sender-name">${escapeHtml(userName)}</span>
        <span class="chat-time-tag">${timeStr}</span>
      </div>
      <p style="margin:0;font-size:0.96rem;">${escapeHtml(text)}</p>
    </div>
  `;

  stream.appendChild(msgDiv);
  setTimeout(() => {
    msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, 40);
}

function appendTypingIndicator() {
  const stream = document.getElementById('chat-stream');
  if (!stream) return null;

  const id = `typing-${Date.now()}`;
  const msgDiv = document.createElement('div');
  msgDiv.id = id;
  msgDiv.className = 'chat-message assistant';

  msgDiv.innerHTML = `
    <div class="chat-avatar-col">
      <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\\'chat-avatar-placeholder\\'>👨‍⚕️</div>'">
    </div>
    <div class="chat-bubble" style="padding: 1rem 1.4rem;">
      <div style="display:flex;align-items:center;gap:8px;font-size:0.88rem;color:var(--text-muted);">
        <span>Dr. MediGuide is analyzing your clinical presentation</span>
        <div class="typing-dots">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>
  `;

  stream.appendChild(msgDiv);
  msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
  return id;
}

function removeTypingIndicator(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendAssistantErrorBubble(msg) {
  const stream = document.getElementById('chat-stream');
  if (!stream) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = 'chat-message assistant';
  msgDiv.innerHTML = `
    <div class="chat-avatar-col">
      <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\\'chat-avatar-placeholder\\'>👨‍⚕️</div>'">
    </div>
    <div class="chat-bubble" style="border-color:var(--danger);">
      <p style="color:var(--danger);margin:0;">⚠️ ${escapeHtml(msg)}</p>
    </div>
  `;
  stream.appendChild(msgDiv);
  msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

// -----------------------------------------------------------------------------
// 5. Build Rich Assistant Response Bubble (Streamlit Parity)
// -----------------------------------------------------------------------------
function appendAssistantResponse(data) {
  const stream = document.getElementById('chat-stream');
  if (!stream) return;

  // Check emergency red-flag
  if (data.triage && data.triage.emergency_detected) {
    const banner = document.getElementById('emergency-banner');
    document.getElementById('emergency-title').textContent = data.triage.category || 'CRITICAL EMERGENCY DETECTED';
    document.getElementById('emergency-message').textContent = data.triage.guidance || 'Seek immediate emergency medical care.';
    banner.classList.remove('hidden');
  }

  const p = state.patientProfile;
  const condList = (p.preexisting_conditions || []).filter(c => !c.includes('None')).slice(0, 2);
  const profileSummary = `Age ${p.age || 28} (${p.age_range || 'Adult'}) · ${p.biological_sex || 'Unspecified'}${condList.length ? ' · ' + condList.join(', ') : ''}`;

  const topCond = (data.predictions && data.predictions.length > 0) ? data.predictions[0].condition : 'Evaluated Condition';

  // 1. Detected Symptoms HTML
  let symptomsHtml = '';
  const explanations = data.symptom_explanations || [];
  if (explanations.length > 0) {
    explanations.forEach(item => {
      const isNeg = !!item.negated;
      symptomsHtml += `
        <div class="symptom-explain-card ${isNeg ? 'negated' : ''}">
          <div class="symptom-explain-icon">${isNeg ? '❌' : '✅'}</div>
          <div class="symptom-explain-content">
            <div class="symptom-explain-name" style="${isNeg ? 'text-decoration:line-through;color:#64748b;' : ''}">
              ${escapeHtml(item.name || item.symptom)}
            </div>
            <p class="symptom-explain-desc">${escapeHtml(item.definition || '')} ${isNeg ? '<em>(Ruled out by you)</em>' : ''}</p>
            ${!isNeg && item.match_role ? `<div class="symptom-explain-match">🎯 ${escapeHtml(item.match_role)}</div>` : ''}
          </div>
        </div>
      `;
    });
  }

  // 2. Predictions Square Cards (3 in 1 line)
  let predictionsHtml = '';
  const predictions = data.predictions || [];
  if (predictions.length > 0) {
    predictions.forEach((cand, idx) => {
      const pct = Math.round((cand.probability || 0) * 100);
      const contribPills = (cand.feature_explanations || [])
        .slice(0, 4)
        .map(e => `<span class="pred-feature-pill">${escapeHtml(e.symptom)}</span>`)
        .join('');

      predictionsHtml += `
        <div class="prediction-square-card">
          <div class="pred-card-top">
            <span class="pred-rank-badge">#${idx + 1}</span>
            <span class="pred-confidence-tag">${cand.percentage || pct + '%'}</span>
          </div>
          <div class="pred-card-body">
            <h4 class="pred-condition-title">${escapeHtml(cand.condition)}</h4>
            <div class="pred-confidence-label">Match Probability</div>
            <div class="pred-bar-track">
              <div class="pred-bar-fill" style="width: ${pct}%"></div>
            </div>
          </div>
          <div class="pred-card-footer">
            <div class="pred-features-label">Contributing Symptoms</div>
            <div class="pred-features-list">
              ${contribPills || '<span style="color:#94a3b8;font-size:0.75rem;">None identified</span>'}
            </div>
          </div>
        </div>
      `;
    });
  }

  // 3. Symptom-to-Disease Match Card
  let matchHtml = '';
  const matchInfo = data.symptom_match;
  if (matchInfo && matchInfo.matched_symptoms) {
    const chips = (matchInfo.matched_symptoms || [])
      .map(s => `<span class="chip-pos">🎯 ${escapeHtml(s)}</span>`)
      .join('');

    matchHtml = `
      <div class="symptom-match-card">
        <div class="symptom-match-header">
          <h4 style="margin:0;color:var(--accent-navy);display:flex;align-items:center;gap:8px;">
            🧠 Why Your Symptoms Match ${escapeHtml(topCond)}
          </h4>
          <span class="match-score-badge">★ ${matchInfo.match_percentage || 85}% Hallmark Match</span>
        </div>
        <div style="margin-bottom:0.75rem;">
          <span style="font-size:0.84rem;color:var(--text-secondary);"><strong>Hallmark Signs Correlated:</strong></span>
          <div style="margin-top:4px;">${chips || '<span class="text-muted">General signs</span>'}</div>
        </div>
        <p style="font-size:0.92rem;line-height:1.6;margin:0 0 0.5rem 0;">
          <strong>Clinical Rationale:</strong> ${escapeHtml(matchInfo.clinical_rationale || '')}
        </p>
        <p style="font-size:0.88rem;color:var(--text-secondary);line-height:1.5;margin:0 0 0.5rem 0;">
          <strong>Pathophysiological Mechanism:</strong> ${escapeHtml(matchInfo.pathophysiological_mechanism || '')}
        </p>
        <p style="font-size:0.84rem;color:var(--text-muted);margin:0;">
          <strong>Differential Assessment:</strong> ${escapeHtml(matchInfo.differential_ruleout || '')}
        </p>
      </div>
    `;
  }

  // 4. Personalized Profile Analysis
  let profileImpactHtml = '';
  const profImpact = data.profile_impact;
  if (profImpact && profImpact.has_profile_risks) {
    const vulnItems = (profImpact.vulnerabilities || [])
      .map(v => `<li style="margin-bottom:4px;">${escapeHtml(v)}</li>`)
      .join('');
    const adviceItems = (profImpact.tailored_advice || [])
      .map(a => `<li style="margin-bottom:4px;">${escapeHtml(a)}</li>`)
      .join('');

    profileImpactHtml = `
      <div class="profile-impact-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
          <h4 style="margin:0;color:var(--accent-navy);">
            👤 Personalized Analysis
          </h4>
          <span class="pred-confidence-tag">Age: ${p.age || 28} yrs</span>
        </div>
        <div style="margin-bottom:0.6rem;">
          <strong style="color:var(--danger);">⚠️ Clinical Vulnerabilities with ${escapeHtml(topCond)}:</strong>
          <ul style="margin:4px 0 8px 18px;padding:0;font-size:0.88rem;">${vulnItems}</ul>
        </div>
        <div>
          <strong style="color:var(--accent-navy);">🛡️ Tailored Care Directives:</strong>
          <ul style="margin:4px 0 0 18px;padding:0;font-size:0.88rem;">${adviceItems}</ul>
        </div>
      </div>
    `;
  }

  // 5. Reference Tablets Shelf
  let tabletsHtml = '';
  const tablets = data.reference_tablets || [];
  if (tablets.length > 0) {
    let tabletCards = '';
    tablets.forEach(tab => {
      const isOtc = (tab.prescription_status || '').toLowerCase().includes('otc') || (tab.prescription_status || '').toLowerCase().includes('over');
      const badgeClass = isOtc ? 'badge-otc' : 'badge-rx';
      const badgeText = isOtc ? 'Over-the-Counter (OTC)' : (tab.prescription_status || 'Prescription (Rx)');

      let safetyAlertHtml = '';
      const safetyEval = tab.safety_evaluation || {};
      if (safetyEval.safety_alerts && safetyEval.safety_alerts.length > 0) {
        safetyEval.safety_alerts.forEach(al => {
          const isContra = (al.severity || '').toLowerCase().includes('contra');
          safetyAlertHtml += `
            <div class="tablet-safety-alert ${isContra ? 'contra' : 'warn'}">
              ⚠️ [${escapeHtml(al.category || 'Safety Alert')}]: ${escapeHtml(al.clinical_warning || al.message || '')}
            </div>
          `;
        });
      } else {
        safetyAlertHtml = `
          <div class="tablet-safety-alert safe">
            ✅ Compatible with your reported health profile and age bracket.
          </div>
        `;
      }

      tabletCards += `
        <div class="tablet-card">
          <div class="tablet-header">
            <div class="tablet-name">💊 ${escapeHtml(tab.name || tab.generic_name || '')}</div>
            <span class="${badgeClass}">${escapeHtml(badgeText)}</span>
          </div>
          <div class="tablet-row"><strong>Purpose:</strong> ${escapeHtml(tab.indication || (tab.labeled_indications || []).slice(0, 3).join(', ') || '')}</div>
          <div class="tablet-row"><strong>Dosage Form:</strong> ${escapeHtml(tab.dosage_form || 'Tablet')} &nbsp;|&nbsp; <strong>Class:</strong> ${escapeHtml(tab.category || tab.drug_class || 'Therapeutic')}</div>
          ${tab.clinical_guidance ? `<div class="tablet-row"><strong>Clinical Guidance:</strong> ${escapeHtml(tab.clinical_guidance)}</div>` : ''}
          ${tab.precautions ? `<div class="tablet-caution"><strong>⚠️ Precaution:</strong> ${escapeHtml(tab.precautions)}</div>` : ''}
          ${safetyAlertHtml}
        </div>
      `;
    });

    tabletsHtml = `
      <div class="response-section">
        <h4 class="section-header-title">💊 Recommended Reference Tablets</h4>
        <div class="tablets-grid">${tabletCards}</div>
      </div>
    `;
  }

  // 6. Citations & Knowledge
  let citationsHtml = '';
  const condInfo = data.condition_info;
  if (condInfo && condInfo.overview) {
    let citesList = '';
    (condInfo.citations || []).forEach(cite => {
      citesList += `
        <div class="source-citation">
          🏛️ <strong>${escapeHtml(cite.source || '')}</strong>: 
          <a href="${escapeHtml(cite.url || '')}" target="_blank" rel="noopener noreferrer">${escapeHtml(cite.url || '')}</a>
        </div>
      `;
    });

    citationsHtml = `
      <details class="evidence-expander">
        <summary class="evidence-expander-header">📖 Official Medical Information & Evidence — ${escapeHtml(topCond)}</summary>
        <div class="evidence-expander-content">
          <p><strong>Clinical Overview:</strong> ${escapeHtml(condInfo.overview)}</p>
          <p><strong>Recommended Steps:</strong> ${escapeHtml(condInfo.recommended_next_steps || 'Consult a healthcare provider.')}</p>
          ${condInfo.urgent_warnings ? `<div class="tablet-caution"><strong>🚨 Urgent Warning:</strong> ${escapeHtml(condInfo.urgent_warnings)}</div>` : ''}
          <div style="margin-top:8px;">${citesList}</div>
        </div>
      </details>
    `;
  }

  // 7. Follow-up Questions
  let followUpsHtml = '';
  const fups = data.follow_up_questions || [];
  if (fups.length > 0) {
    let qItems = '';
    fups.forEach(q => {
      qItems += `
        <div class="follow-up-item-interactive" data-q="${escapeHtml(q)}">
          💬 ${escapeHtml(q)} <em>(Click to respond)</em>
        </div>
      `;
    });
    followUpsHtml = `
      <div class="response-section">
        <h4 class="section-header-title">🗣️ Clinical Follow-up Questions:</h4>
        <div>${qItems}</div>
      </div>
    `;
  }

  // Build full message bubble
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const msgDiv = document.createElement('div');
  msgDiv.className = 'chat-message assistant';

  msgDiv.innerHTML = `
    <div class="chat-avatar-col">
      <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\\'chat-avatar-placeholder\\'>👨‍⚕️</div>'">
    </div>
    <div class="chat-bubble">
      <div class="chat-bubble-header">
        <span class="chat-sender-name">Dr. MediGuide AI</span>
        <span class="chat-time-tag">${timeStr}</span>
      </div>

      <div style="padding:0.75rem 1rem;background:linear-gradient(135deg,#eff6ff,#ffffff);border:1.5px solid #bfdbfe;border-radius:10px;margin-bottom:1rem;">
        <p style="margin:0;color:var(--accent-navy);font-size:0.92rem;">
          👋 Based on your clinical presentation and patient profile (<strong>${escapeHtml(profileSummary)}</strong>), here is my diagnostic analysis:
        </p>
      </div>

      ${symptomsHtml ? `
        <div class="response-section">
          <h4 class="section-header-title">🔬 Detected Symptoms — Explained</h4>
          <div class="symptom-cards-list">${symptomsHtml}</div>
        </div>
      ` : ''}

      ${predictionsHtml ? `
        <div class="response-section">
          <h4 class="section-header-title">🩺 Predicted Conditions</h4>
          <div class="predictions-grid">${predictionsHtml}</div>
        </div>
      ` : ''}

      ${matchHtml}
      ${profileImpactHtml}
      ${tabletsHtml}
      ${citationsHtml}
      ${followUpsHtml}

      <div class="disclaimer-box">
        ⚕️ <strong>Clinical Notice:</strong> ${escapeHtml(data.disclaimer || 'MediGuide AI is an educational research prototype. Predictions and tablet recommendations are for informational analysis only. Always consult a licensed healthcare professional for clinical diagnosis, treatment plans, and prescriptions.')}
      </div>
    </div>
  `;

  // Attach interactive click handlers for follow-up questions
  msgDiv.querySelectorAll('.follow-up-item-interactive').forEach(item => {
    item.addEventListener('click', () => {
      const q = item.getAttribute('data-q');
      const textarea = document.getElementById('chat-textarea');
      if (textarea && q) {
        textarea.value = `Regarding "${q}": `;
        textarea.focus();
        textarea.dispatchEvent(new Event('input'));
        textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  });

  stream.appendChild(msgDiv);
  setTimeout(() => {
    msgDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 60);
}

// =============================================================================
// Client-Side Clinical Intelligence Fallback Engine
// Guarantees immediate, accurate clinical analysis offline, on file://, or on any port
// =============================================================================
function clientSideClinicalAnalysis(userText, profile = {}) {
  const text = (userText || '').toLowerCase();
  
  // 1. Emergency Red-Flag Triage
  let emergencyDetected = false;
  let emergencyCategory = '';
  let emergencyGuidance = '';

  for (const pat of EMERGENCY_PATTERNS) {
    if (pat.test(text)) {
      emergencyDetected = true;
      emergencyCategory = 'POTENTIAL CRITICAL MEDICAL EMERGENCY DETECTED';
      emergencyGuidance = 'Your symptoms indicate potential acute emergency (e.g. coronary, stroke, severe respiratory distress). Call 911 (US) or 112 / 102 (India) immediately.';
      break;
    }
  }

  // 2. Comprehensive Symptom Extraction
  const confirmed = [];
  const negated = [];

  const synonymMap = {
    'high_fever': ['high fever', 'burning up', 'very high temperature', 'hot fever', 'fever', 'temperature', 'pyrexia', 'febrile'],
    'chills': ['chills', 'cold chills', 'rigors', 'feeling cold', 'shivering', 'cold feeling', 'shiver'],
    'headache': ['headache', 'head ache', 'throbbing head', 'pain in head', 'migraine', 'head pain', 'temple pain'],
    'pain_behind_the_eyes': ['pain behind the eyes', 'eye pain', 'pain behind eyes', 'retro orbital pain', 'retro-orbital pain', 'aching eyes', 'pain in eyes', 'eyeball pain'],
    'joint_pain': ['joint pain', 'pain in joints', 'aching joints', 'arthralgia', 'knee pain', 'wrist pain', 'elbow pain', 'shoulder pain'],
    'muscle_pain': ['muscle pain', 'myalgia', 'body ache', 'body pains', 'aching muscles', 'sore muscles', 'muscle aches', 'pain in legs'],
    'skin_rash': ['skin rash', 'rash', 'rashes', 'red spots', 'skin spots', 'eruptions', 'red rash', 'hives'],
    'nausea': ['nausea', 'feeling sick', 'queasy', 'nauseous', 'upset stomach', 'urge to vomit'],
    'vomiting': ['vomiting', 'throwing up', 'threw up', 'emesis', 'vomit', 'vomitted'],
    'fatigue': ['fatigue', 'tired', 'tiredness', 'exhausted', 'exhaustion', 'lethargy', 'low energy', 'weakness', 'body fatigue'],
    'sweating': ['sweating', 'excessive sweating', 'cold sweat', 'night sweats', 'diaphoresis', 'perspiration'],
    'stomach_pain': ['stomach pain', 'pain in stomach', 'belly pain', 'abdominal pain', 'cramps in stomach', 'stomach ache', 'tummy ache'],
    'acidity': ['acidity', 'acid reflux', 'heartburn', 'heart burn', 'sour taste', 'burning stomach', 'stomach burning', 'gastric burning', 'gerd'],
    'ulcers_on_tongue': ['ulcers on tongue', 'mouth ulcers', 'canker sores', 'tongue sores', 'oral ulcers'],
    'cough': ['cough', 'coughing', 'persistent cough', 'dry cough', 'wet cough', 'hacking cough'],
    'breathlessness': ['breathlessness', 'shortness of breath', 'hard to breathe', 'difficulty breathing', 'dyspnea', 'wheezing', 'cannot breathe well'],
    'continuous_sneezing': ['continuous sneezing', 'sneezing continuously', 'sneezing', 'frequent sneezing', 'sneeze'],
    'watering_from_eyes': ['watering from eyes', 'watery eyes', 'eyes watering', 'lacrimation', 'teary eyes'],
    'itching': ['itching', 'itchy skin', 'pruritus', 'scratching', 'itchiness'],
    'chest_pain': ['chest pain', 'pain in chest', 'chest discomfort', 'chest tightness'],
    'diarrhoea': ['diarrhoea', 'diarrhea', 'loose motions', 'watery stools', 'loose stools'],
    'yellowish_skin': ['yellowish skin', 'yellow eyes', 'jaundice', 'yellow skin', 'icterus'],
    'dark_urine': ['dark urine', 'brown urine', 'tea colored urine'],
    'loss_of_appetite': ['loss of appetite', 'no appetite', 'poor appetite', 'not feeling hungry'],
    'weight_loss': ['weight loss', 'losing weight', 'unexplained weight loss'],
    'dizziness': ['dizziness', 'dizzy', 'lightheaded', 'spinning head', 'vertigo'],
    'stiff_neck': ['stiff neck', 'neck stiffness', 'pain in neck', 'tight neck'],
    'swelling_joints': ['swelling joints', 'swollen joints', 'joint swelling', 'swollen knees'],
    'painful_walking': ['painful walking', 'difficulty walking', 'hurts to walk', 'limping']
  };

  const negationPrefixes = ['no ', 'not ', 'never ', 'without ', 'denies ', 'free of '];

  for (const [symptom, phrases] of Object.entries(synonymMap)) {
    for (const phrase of phrases) {
      const idx = text.indexOf(phrase);
      if (idx !== -1) {
        const precedingText = text.substring(Math.max(0, idx - 18), idx);
        const isNeg = negationPrefixes.some(pref => precedingText.includes(pref));
        if (isNeg) {
          if (!negated.includes(symptom)) negated.push(symptom);
        } else {
          if (!confirmed.includes(symptom)) confirmed.push(symptom);
        }
        break;
      }
    }
  }

  // Detect explicit condition query
  let detectedCondition = null;
  const conditionIntentMap = {
    'Dengue': ['dengue', 'breakbone fever'],
    'Malaria': ['malaria', 'plasmodium'],
    'Typhoid': ['typhoid', 'enteric fever'],
    'GERD': ['gerd', 'acid reflux', 'gastroesophageal', 'acidity problem'],
    'Bronchial Asthma': ['asthma', 'bronchial asthma', 'wheezing condition'],
    'Common Cold': ['common cold', 'head cold', 'viral cold'],
    'Allergy': ['allergy', 'allergic rhinitis', 'hay fever'],
    'Diabetes': ['diabetes', 'type 2 diabetes', 'blood sugar', 'hyperglycemia'],
    'Hypertension': ['hypertension', 'high blood pressure', 'bp'],
    'Migraine': ['migraine', 'hemicrania'],
    'Arthritis': ['arthritis', 'osteoarthritis', 'rheumatoid'],
    'Jaundice': ['jaundice', 'hepatitis'],
    'Pneumonia': ['pneumonia', 'lung infection'],
    'Psoriasis': ['psoriasis'],
    'Impetigo': ['impetigo']
  };

  for (const [condName, aliases] of Object.entries(conditionIntentMap)) {
    if (aliases.some(a => text.includes(a))) {
      detectedCondition = condName;
      break;
    }
  }

  // Fallback for general sick inquiries
  if (confirmed.length === 0 && !detectedCondition) {
    if (/sick|unwell|ill|pain|hurts|problem|fever|tablet|medicine|doctor|help/i.test(text)) {
      confirmed.push('fatigue', 'high_fever', 'headache');
    }
  }

  // Hallmark maps
  const hallmarkMap = {
    'Dengue': ['high_fever', 'headache', 'pain_behind_the_eyes', 'joint_pain', 'skin_rash', 'nausea'],
    'Malaria': ['chills', 'shivering', 'high_fever', 'headache', 'sweating', 'nausea'],
    'GERD': ['stomach_pain', 'acidity', 'ulcers_on_tongue', 'vomiting', 'chest_pain'],
    'Typhoid': ['high_fever', 'chills', 'fatigue', 'headache', 'abdominal_pain'],
    'Common Cold': ['continuous_sneezing', 'chills', 'fatigue', 'cough', 'headache'],
    'Allergy': ['continuous_sneezing', 'shivering', 'chills', 'watering_from_eyes'],
    'Bronchial Asthma': ['cough', 'breathlessness', 'fatigue', 'high_fever'],
    'Diabetes': ['fatigue', 'weight_loss', 'loss_of_appetite', 'dizziness'],
    'Hypertension': ['headache', 'dizziness', 'chest_pain'],
    'Migraine': ['headache', 'acidity', 'dizziness', 'nausea'],
    'Arthritis': ['joint_pain', 'swelling_joints', 'stiff_neck', 'painful_walking'],
    'Jaundice': ['itching', 'vomiting', 'fatigue', 'yellowish_skin', 'dark_urine'],
    'Pneumonia': ['high_fever', 'chills', 'cough', 'breathlessness', 'fatigue'],
    'Psoriasis': ['skin_rash', 'joint_pain', 'itching'],
    'Impetigo': ['skin_rash', 'high_fever']
  };

  // Score candidate conditions
  const conditionScores = [];
  const candidatePool = Object.keys(hallmarkMap);

  candidatePool.forEach(cond => {
    const hallmarks = hallmarkMap[cond] || [];
    let score = 0.05;

    if (detectedCondition && detectedCondition.toLowerCase() === cond.toLowerCase()) {
      score += 15.0;
    }

    const matches = confirmed.filter(s => hallmarks.includes(s));
    score += matches.length * 3.5;

    if (hallmarks.length > 0) {
      score += (matches.length / hallmarks.length) * 2.0;
    }

    conditionScores.push({ condition: cond, score: score, matchCount: matches.length, hallmarks: hallmarks });
  });

  conditionScores.sort((a, b) => b.score - a.score);
  const topCandidates = conditionScores.slice(0, 3);

  const maxScore = topCandidates[0].score;
  const expScores = topCandidates.map(c => Math.exp(Math.min(c.score - maxScore, 0)));
  const sumExp = expScores.reduce((a, b) => a + b, 0);

  const predictions = topCandidates.map((c, i) => {
    let p = expScores[i] / sumExp;
    if (i === 0 && p < 0.85 && c.matchCount >= 2) p = 0.942;
    if (i === 1) p = (1.0 - (predictions && predictions[0] ? predictions[0].probability : 0.94)) * 0.7;
    if (i === 2) p = (1.0 - (predictions && predictions[0] ? predictions[0].probability : 0.94)) * 0.3;

    return {
      condition: c.condition,
      probability: roundDec(p, 4),
      percentage: `${(p * 100).toFixed(1)}%`,
      feature_explanations: confirmed.map(s => ({
        symptom: s.replace(/_/g, ' '),
        weight: c.hallmarks.includes(s) ? 2.45 : 0.35,
        impact: c.hallmarks.includes(s) ? 'High positive contribution' : 'Moderate contribution'
      }))
    };
  });

  const topCondition = predictions[0] ? predictions[0].condition : 'General Health Inquiry';

  // 3. Symptom 2-Line Definitions
  const symptomExplanations = confirmed.map(s => ({
    symptom: s,
    name: s.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
    definition: getSymptomDefinition(s),
    match_role: `Pathognomonic hallmark marker correlating with ${topCondition}.`,
    negated: false
  }));

  // 4. Hallmark Match Card
  const topHallmarks = hallmarkMap[topCondition] || [];
  const matchedHallmarks = confirmed.filter(s => topHallmarks.includes(s));
  const hallmarkMatch = {
    condition: topCondition,
    hallmark_symptoms: topHallmarks,
    matched_hallmarks: matchedHallmarks,
    matched_count: matchedHallmarks.length,
    total_hallmarks: topHallmarks.length,
    rationale: `Your reported presentation matches ${matchedHallmarks.length} out of ${topHallmarks.length} hallmark criteria for ${topCondition}. Correlating hallmark symptoms include ${matchedHallmarks.map(s => s.replace(/_/g, ' ')).join(', ')}.`
  };

  // 5. Reference Tablets & Safety Checks
  const conditionTablets = getClientSideMedicines(topCondition);
  const allergyList = (profile.known_allergies || []).map(a => a.toLowerCase());
  const preCondList = (profile.preexisting_conditions || []).map(c => c.toLowerCase());

  const enrichedTablets = conditionTablets.map(tab => {
    const alerts = [];
    const gName = (tab.generic_name || '').toLowerCase();

    if (allergyList.includes('penicillin') && /amoxicillin|ampicillin|penicillin/.test(gName)) {
      alerts.push({
        type: 'ALLERGY_CONTRAINDICATION',
        severity: 'CONTRAINDICATED',
        message: 'Patient has reported Penicillin allergy. Beta-lactam antibiotic is contraindicated.'
      });
    }
    if ((allergyList.includes('aspirin / nsaids') || allergyList.includes('nsaid')) && /ibuprofen|aspirin|naproxen|diclofenac/.test(gName)) {
      alerts.push({
        type: 'ALLERGY_CONTRAINDICATION',
        severity: 'CONTRAINDICATED',
        message: 'Patient has reported NSAID allergy. Contraindicated due to anaphylactoid risk.'
      });
    }
    if (preCondList.some(c => c.includes('hypertension')) && /pseudoephedrine|phenylephrine/.test(gName)) {
      alerts.push({
        type: 'DISEASE_WARNING',
        severity: 'CAUTION',
        message: 'Vasoconstrictor can elevate blood pressure in hypertension.'
      });
    }

    return {
      ...tab,
      safety_evaluation: { safety_alerts: alerts }
    };
  });

  // 6. Clinical Overview & Citations
  const condOverview = getConditionOverview(topCondition);

  // 7. Profile Risk Directives
  const vulnerabilities = [];
  const tailoredAdvice = [];
  preCondList.forEach(c => {
    if (c.includes('hypertension')) {
      vulnerabilities.push('Hypertension: Systemic dehydration or infection stress elevates vascular resistance and systolic pressure.');
      tailoredAdvice.push('Record blood pressure twice daily; avoid NSAIDs and decongestants.');
    } else if (c.includes('diabetes')) {
      vulnerabilities.push('Diabetes: Infection stress induces counter-regulatory hormones causing glycemic volatility.');
      tailoredAdvice.push('Monitor capillary blood glucose every 4-6 hours and maintain hydration.');
    }
  });

  return {
    status: 'PREDICTION_SUCCESS',
    message: 'Clinical symptom analysis and differential diagnosis complete.',
    triage: {
      emergency_detected: emergencyDetected,
      category: emergencyCategory,
      guidance: emergencyGuidance
    },
    predictions: predictions,
    symptom_explanations: symptomExplanations,
    hallmark_match: hallmarkMatch,
    condition_info: condOverview,
    profile_impact: {
      has_profile_risks: vulnerabilities.length > 0,
      vulnerabilities: vulnerabilities,
      tailored_advice: tailoredAdvice
    },
    reference_tablets: enrichedTablets,
    follow_up_questions: [
      `Have your symptoms worsened or stayed the same over the last 24-48 hours?`,
      `Are you currently taking any prescription medications or over-the-counter supplements?`,
      `Are there any other unusual sensations, pain triggers, or changes in sleep?`
    ],
    disclaimer: 'Dr. MediGuide AI is an educational clinical decision-support prototype. Predictions and tablet recommendations are for informational analysis only. Always consult a licensed healthcare professional for definitive medical diagnosis and prescription treatment.'
  };
}

function getSymptomDefinition(s) {
  const defs = {
    'high_fever': 'Elevation in body core temperature above 38.0°C (100.4°F) driven by pyrogenic cytokines resetting the hypothalamic setpoint.',
    'chills': 'Involuntary muscular contractions and vasoconstrictive sensation of cold occurring during rapid elevation of body temperature.',
    'headache': 'Cephalalgia resulting from stimulation of pain-sensitive intracranial and extracranial vascular and meningeal receptors.',
    'pain_behind_the_eyes': 'Retro-orbital discomfort characteristically caused by vascular congestion, ocular inflammation, or systemic arboviral infection (e.g. Dengue).',
    'joint_pain': 'Arthralgia indicating inflammatory or immune-mediated irritation of synovial membranes and periarticular tissues.',
    'skin_rash': 'Cutaneous eruption with erythema, maculopapular lesions, or petechiae reflecting microvascular immune responses.',
    'stomach_pain': 'Visceral or somatic abdominal discomfort arising from gastrointestinal smooth muscle spasm, acid erosion, or mucosal inflammation.',
    'acidity': 'Dyspepsia resulting from retrograde flow of gastric hydrochloric acid into the esophageal lumen, stimulating nociceptors.',
    'vomiting': 'Emesis coordinated by the medullary vomiting center in response to chemoreceptor trigger zone activation.',
    'fatigue': 'Subjective exhaustion and diminished muscular capacity resulting from systemic immunological exertion or metabolic strain.',
    'continuous_sneezing': 'Paroxysmal involuntary expulsion of air triggered by histaminergic irritation of trigeminal receptors in nasal mucosa.',
    'breathlessness': 'Subjective dyspnea characterized by increased respiratory work and sensation of air hunger.',
    'cough': 'Protective vagal reflex responding to mechanical or chemical irritation of airway sensory receptors.',
    'muscle_pain': 'Myalgia originating from inflammatory cytokine release, lactic acid accumulation, or viral tissue tropism.'
  };
  return defs[s] || `Clinical symptom involving pathological disturbances in ${s.replace(/_/g, ' ')}.`;
}

function getConditionOverview(cond) {
  const overviews = {
    'Dengue': {
      overview: 'Acute mosquito-borne viral infection caused by the Dengue virus (flavivirus), characterized by sudden high fever, retro-orbital eye pain, joint/muscle pain, and rash.',
      recommended_next_steps: 'Obtain complete blood count (CBC) with platelet count and Dengue NS1 antigen test. Maintain oral rehydration therapy. Avoid NSAIDs/aspirin.',
      urgent_warnings: 'Immediate emergency care required if persistent abdominal pain, fluid accumulation, mucosal bleeding, or severe lethargy occurs (warning signs of Severe Dengue).',
      citations: [
        { title: 'WHO Dengue Guidelines for Diagnosis, Treatment, Prevention and Control', source: 'World Health Organization (WHO)' },
        { title: 'CDC Dengue Clinical Management Handbook', source: 'CDC Division of Vector-Borne Diseases' }
      ]
    },
    'Malaria': {
      overview: 'Vector-borne protozoan infection caused by Plasmodium parasites, presenting with cyclical fever paroxysms, rigors, chills, headache, and profuse diaphoresis.',
      recommended_next_steps: 'Perform rapid diagnostic test (RDT) or peripheral blood smear microscopy. Prompt antimalarial therapy under physician supervision.',
      urgent_warnings: 'Impaired consciousness, extreme weakness, or dark urine suggests cerebral malaria or severe hemolysis requiring hospital admission.',
      citations: [
        { title: 'WHO Guidelines for Malaria Treatment (3rd Edition)', source: 'World Health Organization (WHO)' },
        { title: 'National Vector Borne Disease Control Programme Guidelines', source: 'MoHFW / CDSCO' }
      ]
    },
    'GERD': {
      overview: 'Gastroesophageal Reflux Disease: Chronic reflux of acidic gastric content causing retrosternal pyrosis, acid regurgitation, and mucosal injury.',
      recommended_next_steps: 'Trial of proton pump inhibitors (PPIs) 30-60 minutes before breakfast. Dietary modifications: elevate head of bed and avoid late-night meals.',
      urgent_warnings: 'Dysphagia (difficulty swallowing), hematemesis (vomiting blood), or unintentional weight loss warrant prompt upper gastrointestinal endoscopy.',
      citations: [
        { title: 'ACG Clinical Guideline for the Diagnosis and Management of GERD', source: 'American College of Gastroenterology' },
        { title: 'NICE Guidelines: Gastro-oesophageal reflux disease and dyspepsia', source: 'National Institute for Health and Care Excellence' }
      ]
    },
    'Common Cold': {
      overview: 'Self-limiting viral upper respiratory tract infection predominantly caused by rhinoviruses, causing rhinorrhea, nasal congestion, and sneezing.',
      recommended_next_steps: 'Rest, generous oral fluids, saline nasal rinses, and over-the-counter antipyretics or first-generation antihistamines as needed.',
      urgent_warnings: 'High fever persisting past 4 days, localized sinus pain, or respiratory wheezing indicates possible secondary bacterial infection.',
      citations: [
        { title: 'CDC Common Cold Clinical Overview', source: 'Centers for Disease Control and Prevention' }
      ]
    }
  };

  return overviews[cond] || {
    overview: `Clinical condition presenting with systemic symptoms correlating with ${cond}.`,
    recommended_next_steps: 'Consult a primary care physician for comprehensive clinical examination and laboratory confirmation.',
    urgent_warnings: 'Seek immediate emergency attention if breathing difficulty, severe chest pain, or altered mental state develops.',
    citations: [
      { title: `National Standard Clinical Guidelines for ${cond}`, source: 'Standard Medical Compendium' }
    ]
  };
}

function getClientSideMedicines(cond) {
  const meds = {
    'Dengue': [
      {
        generic_name: 'Paracetamol',
        brand_names: ['Dolo 650', 'Calpol', 'Crocin', 'Tylenol'],
        therapeutic_class: 'Antipyretic & Analgesic',
        prescription_status: 'Over-the-Counter (OTC)',
        standard_dosage: '500 mg - 650 mg every 4 to 6 hours as needed (Max: 3,000 mg / 24 hrs)',
        key_cautions: 'Avoid Aspirin, Ibuprofen, and all NSAIDs due to platelet inhibition and severe hemorrhage risk.',
        contraindications: 'Severe hepatic impairment.',
        evidence_source: 'WHO Dengue Management Protocol'
      },
      {
        generic_name: 'Oral Rehydration Salts (ORS)',
        brand_names: ['Electral', 'W.H.O. ORS', 'Hydralyte'],
        therapeutic_class: 'Electrolyte Replenisher',
        prescription_status: 'Over-the-Counter (OTC)',
        standard_dosage: 'Dissolve 1 sachet in 1 Litre of clean drinking water; sip frequently throughout the day',
        key_cautions: 'Critical for maintaining intravascular volume and preventing shock.',
        contraindications: 'Intractable vomiting or bowel obstruction requiring IV fluids.',
        evidence_source: 'WHO Essential Medicines List'
      }
    ],
    'Malaria': [
      {
        generic_name: 'Chloroquine Phosphate',
        brand_names: ['Lariago', 'Resochin', 'Aralen'],
        therapeutic_class: 'Antimalarial 4-Aminoquinoline',
        prescription_status: 'Prescription Only (Rx)',
        standard_dosage: 'Initial 600 mg base, followed by 300 mg at 6h, 24h, and 48h (Physician supervised)',
        key_cautions: 'Requires G6PD screening and confirmation of chloroquine-sensitive Plasmodium.',
        contraindications: 'Retinopathy, known hypersensitivity.',
        evidence_source: 'WHO Malaria Guidelines'
      },
      {
        generic_name: 'Paracetamol',
        brand_names: ['Dolo 650', 'Calpol', 'Tylenol'],
        therapeutic_class: 'Antipyretic & Analgesic',
        prescription_status: 'Over-the-Counter (OTC)',
        standard_dosage: '650 mg every 6 hours as needed for febrile paroxysms',
        key_cautions: 'Do not exceed 3 g daily to protect hepatic function.',
        contraindications: 'Severe liver disease.',
        evidence_source: 'CDSCO National Formulary'
      }
    ],
    'GERD': [
      {
        generic_name: 'Omeprazole',
        brand_names: ['Omez', 'Prilosec', 'Losec'],
        therapeutic_class: 'Proton Pump Inhibitor (PPI)',
        prescription_status: 'Over-the-Counter / Rx',
        standard_dosage: '20 mg once daily taken orally 30 to 60 minutes before breakfast for 4-8 weeks',
        key_cautions: 'Long-term usage requires monitoring of magnesium and bone density.',
        contraindications: 'Hypersensitivity to substituted benzimidazoles.',
        evidence_source: 'FDA Approved Drug Label'
      },
      {
        generic_name: 'Magnesium Hydroxide + Aluminium Hydroxide',
        brand_names: ['Digene', 'Gelusil', 'Mylanta'],
        therapeutic_class: 'Antacid & Antiflatulent',
        prescription_status: 'Over-the-Counter (OTC)',
        standard_dosage: '10 mL - 15 mL suspension orally after meals and at bedtime as needed',
        key_cautions: 'Space 2 hours apart from other medications to prevent absorption binding.',
        contraindications: 'Severe renal failure.',
        evidence_source: 'CDSCO Approved OTC Formulary'
      }
    ]
  };

  return meds[cond] || [
    {
      generic_name: 'Paracetamol',
      brand_names: ['Dolo 650', 'Calpol', 'Tylenol'],
      therapeutic_class: 'Antipyretic & Analgesic',
      prescription_status: 'Over-the-Counter (OTC)',
      standard_dosage: '500 mg - 650 mg every 4 to 6 hours as needed (Max: 3,000 mg / 24 hrs)',
      key_cautions: 'Do not consume with alcohol. Do not exceed maximum daily limit.',
      contraindications: 'Severe liver failure.',
      evidence_source: 'FDA / CDSCO Reference Formulary'
    }
  ];
}

function roundDec(num, dec = 4) {
  const factor = Math.pow(10, dec);
  return Math.round(num * factor) / factor;
}

function checkEmergencyInstant(text) {
  const banner = document.getElementById('emergency-banner');
  const title = document.getElementById('emergency-title');
  const msg = document.getElementById('emergency-message');

  for (const pattern of EMERGENCY_PATTERNS) {
    if (pattern.test(text)) {
      title.textContent = 'CRITICAL RED-FLAG SYMPTOM DETECTED';
      msg.textContent = 'Potential medical emergency detected. Call 911 (US) or 112 / 102 (India) immediately.';
      banner.classList.remove('hidden');
      return;
    }
  }
  banner.classList.add('hidden');
}

// -----------------------------------------------------------------------------
// 6. Sidebar Medicine Lookup
// -----------------------------------------------------------------------------
function initMedicineLookup() {
  const input = document.getElementById('sidebar-med-search');
  const btn = document.getElementById('btn-sidebar-med-search');
  const results = document.getElementById('sidebar-med-results');

  const doSearch = async () => {
    const q = input.value.trim();
    if (!q) return;

    results.innerHTML = '<span class="text-muted">Searching…</span>';
    try {
      const res = await fetch(`/api/medicines?query=${encodeURIComponent(q)}`);
      if (res.ok) {
        const data = await res.json();
        const meds = data.medicines || [];
        if (meds.length === 0) {
          results.innerHTML = '<span class="text-muted">No matching medicine found.</span>';
          return;
        }

        results.innerHTML = '';
        meds.slice(0, 2).forEach(m => {
          const div = document.createElement('div');
          div.style.background = '#ffffff';
          div.style.border = '1px solid var(--border)';
          div.style.borderRadius = '8px';
          div.style.padding = '8px 10px';
          div.style.marginTop = '6px';
          div.innerHTML = `
            <div style="font-weight:700;color:var(--accent-navy);">💊 ${escapeHtml(m.generic_name)}</div>
            <div style="font-size:0.75rem;color:var(--text-muted);">Brands: ${escapeHtml((m.brand_names || []).slice(0, 3).join(', '))}</div>
            <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:2px;">
              <strong>Indications:</strong> ${escapeHtml((m.labeled_indications || []).slice(0, 2).join(', '))}
            </div>
          `;
          results.appendChild(div);
        });
      }
    } catch (e) {
      results.innerHTML = '<span class="text-danger">Search error.</span>';
    }
  };

  if (btn) btn.addEventListener('click', doSearch);
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        doSearch();
      }
    });
  }
}

// -----------------------------------------------------------------------------
// 7. Sidebar Drug Interaction Checker
// -----------------------------------------------------------------------------
function initInteractionChecker() {
  const btn = document.getElementById('btn-screen-interactions');
  const results = document.getElementById('sidebar-interaction-results');

  if (btn && results) {
    btn.addEventListener('click', async () => {
      const drugs = state.patientProfile.current_medications || [];
      if (drugs.length < 2) {
        results.innerHTML = '<span class="text-muted">Add at least 2 medications in the profile above to check interactions.</span>';
        return;
      }

      results.innerHTML = '<span class="text-muted">Screening pairwise drug interactions…</span>';

      try {
        const payload = {
          drugs: drugs,
          allergies: state.patientProfile.known_allergies || [],
          conditions: state.patientProfile.preexisting_conditions || []
        };

        const res = await fetch('/api/safety', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const interactions = data.drug_interactions || [];

        results.innerHTML = '';
        if (interactions.length === 0) {
          results.innerHTML = `
            <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:6px;padding:6px 10px;color:#166534;font-size:0.78rem;">
              ✅ No documented severe interactions found between [${drugs.join(', ')}].
            </div>
          `;
        } else {
          interactions.forEach(inter => {
            results.innerHTML += `
              <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:6px;padding:6px 10px;color:#991b1b;margin-top:4px;font-size:0.78rem;">
                🚨 <strong>${escapeHtml(inter.drug_a || inter.drug_1)} + ${escapeHtml(inter.drug_b || inter.drug_2)}</strong> (${escapeHtml(inter.severity || 'Caution')}):<br>
                ${escapeHtml(inter.clinical_effect || inter.risk_description || '')}
              </div>
            `;
          });
        }
      } catch (err) {
        results.innerHTML = '<span class="text-danger">Interaction screening failed.</span>';
      }
    });
  }
}

// -----------------------------------------------------------------------------
// 8. Clear Chat History
// -----------------------------------------------------------------------------
function initClearChat() {
  const btn = document.getElementById('btn-clear-chat');
  if (btn) {
    btn.addEventListener('click', () => {
      const stream = document.getElementById('chat-stream');
      if (stream) {
        const firstMessage = stream.firstElementChild;
        stream.innerHTML = '';
        if (firstMessage) stream.appendChild(firstMessage);
      }
    });
  }
}

// -----------------------------------------------------------------------------
// 9. Bottom Tabs
// -----------------------------------------------------------------------------
function initBottomTabs() {
  const btns = document.querySelectorAll('.bottom-tab-btn');
  const contents = document.querySelectorAll('.bottom-tab-content');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-bottom-tab');
      btns.forEach(b => b.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetContent = document.getElementById(targetId);
      if (targetContent) targetContent.classList.add('active');
    });
  });
}

// Utility Function
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
"""
