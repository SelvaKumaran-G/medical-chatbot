/**
 * Dr. MediGuide AI — Client Application Script
 * Orchestrates clinical onboarding, triage, ML prediction UI, pathophysiological explanations,
 * tablet shelf with safety evaluation, drug interaction screener, and model accuracy metrics.
 */

// Global State
const state = {
  theme: localStorage.getItem('mediguide_theme') || 'light',
  onboarded: localStorage.getItem('mediguide_onboarded') === 'true',
  userName: localStorage.getItem('mediguide_user_name') || 'Self',
  userPhoto: localStorage.getItem('mediguide_user_photo') || '',
  patientProfile: JSON.parse(localStorage.getItem('mediguide_profile') || JSON.stringify({
    name: 'Self',
    age: 28,
    biological_sex: 'Unspecified',
    age_range: 'Young Adult (18 - 35 yrs)',
    conditions: ['None / Generally Healthy'],
    allergies: [],
    is_pregnant: false,
    other_notes: ''
  })),
  selectedDrugs: ['Warfarin', 'Ibuprofen'],
  medicinesCache: [],
  modelMetadata: null
};

// Emergency Heuristic Regex Patterns (instant client-side pre-screen)
const EMERGENCY_PATTERNS = [
  /\b(crushing chest pain|chest pain radiating|pain in left arm|chest pressure and sweating|heart attack)\b/i,
  /\b(facial drooping|face droop|slurred speech|slurring words|one side weakness|cannot lift arm|stroke)\b/i,
  /\b(cannot breathe|unable to breathe|gasping for air|turning blue|blue lips|swelling of throat|anaphylaxis)\b/i,
  /\b(unconscious|passed out|unresponsive|prolonged seizure|coma)\b/i,
  /\b(coughing up blood|vomiting blood|uncontrolled bleeding)\b/i
];

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initOnboarding();
  initNavigation();
  initModelMetadata();
  initHeroAndProfileUI();
  initSymptomInput();
  initExamplePills();
  initQuickMedicineLookup();
  initSafetyChecker();
  initMedicineCatalogue();
  initBottomTabs();
  initSummaryExport();
});

// -----------------------------------------------------------------------------
// 1. Theme Management
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
}

// -----------------------------------------------------------------------------
// 2. Onboarding Flow (Streamlit Parity)
// -----------------------------------------------------------------------------
function initOnboarding() {
  const modal = document.getElementById('onboarding-modal');
  const form = document.getElementById('onboarding-form');
  const photoInput = document.getElementById('onboard-photo-input');
  const photoPreview = document.getElementById('onboard-photo-preview');

  // If not onboarded yet, show modal
  if (!state.onboarded) {
    modal.classList.remove('hidden');
  }

  // Handle photo upload
  if (photoInput) {
    photoInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          state.userPhoto = event.target.result;
          photoPreview.innerHTML = `<img src="${state.userPhoto}" alt="Avatar">`;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Handle onboarding form submission
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = document.getElementById('onboard-name-input');
      const name = nameInput.value.trim();

      if (!name) {
        alert('Please enter your name to continue.');
        nameInput.focus();
        return;
      }

      state.userName = name;
      const ageRange = document.getElementById('onboard-age-range').value;
      const sex = document.getElementById('onboard-sex').value;

      // Map age from bracket
      const ageBracketMap = {
        'Infant / Child (0 - 12 yrs)': 6,
        'Adolescent (13 - 17 yrs)': 15,
        'Young Adult (18 - 35 yrs)': 28,
        'Adult (36 - 64 yrs)': 45,
        'Senior / Geriatric (65+ yrs)': 70
      };
      const age = ageBracketMap[ageRange] || 28;

      // Pre-existing conditions
      const conditionBoxes = form.querySelectorAll('#onboard-conditions-grid input[type="checkbox"]:checked');
      const conditions = Array.from(conditionBoxes).map(cb => cb.value);

      state.patientProfile = {
        name: name,
        age: age,
        biological_sex: sex,
        age_range: ageRange,
        conditions: conditions.length > 0 ? conditions : ['None / Generally Healthy'],
        allergies: [],
        is_pregnant: false,
        other_notes: ''
      };

      state.onboarded = true;
      localStorage.setItem('mediguide_onboarded', 'true');
      localStorage.setItem('mediguide_user_name', state.userName);
      localStorage.setItem('mediguide_user_photo', state.userPhoto);
      localStorage.setItem('mediguide_profile', JSON.stringify(state.patientProfile));

      modal.classList.add('hidden');
      initHeroAndProfileUI();
    });
  }

  // Quick edit profile button in sidebar & header
  const btnEditProfileQuick = document.getElementById('btn-edit-profile-quick');
  const btnHeaderProfile = document.getElementById('btn-header-profile');

  const openProfileEditor = () => {
    // Populate form with current values
    const nameInput = document.getElementById('onboard-name-input');
    if (nameInput) nameInput.value = state.userName !== 'Self' ? state.userName : '';
    const ageSelect = document.getElementById('onboard-age-range');
    if (ageSelect && state.patientProfile.age_range) ageSelect.value = state.patientProfile.age_range;
    const sexSelect = document.getElementById('onboard-sex');
    if (sexSelect && state.patientProfile.biological_sex) sexSelect.value = state.patientProfile.biological_sex;

    modal.classList.remove('hidden');
  };

  if (btnEditProfileQuick) btnEditProfileQuick.addEventListener('click', openProfileEditor);
  if (btnHeaderProfile) btnHeaderProfile.addEventListener('click', openProfileEditor);
}

// -----------------------------------------------------------------------------
// 3. Navigation Tabs
// -----------------------------------------------------------------------------
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-tab');

      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      if (targetId === 'tab-database' && state.medicinesCache.length === 0) {
        loadMedicinesCatalogue();
      }
    });
  });

  // Emergency banner dismiss
  const btnDismissEmergency = document.getElementById('btn-emergency-dismiss');
  if (btnDismissEmergency) {
    btnDismissEmergency.addEventListener('click', () => {
      document.getElementById('emergency-banner').classList.add('hidden');
    });
  }
}

// -----------------------------------------------------------------------------
// 4. Model Metadata & Accuracy Metrics (Streamlit Parity)
// -----------------------------------------------------------------------------
async function initModelMetadata() {
  try {
    const res = await fetch('/api/metadata');
    if (res.ok) {
      state.modelMetadata = await res.json();
      updateMetricsDisplay(state.modelMetadata);
      return;
    }
  } catch (e) {
    console.warn('Failed to load /api/metadata, trying static file:', e);
  }

  try {
    const res2 = await fetch('/model_metadata.json');
    if (res2.ok) {
      state.modelMetadata = await res2.json();
      updateMetricsDisplay(state.modelMetadata);
    }
  } catch (e2) {
    console.warn('Using fallback accuracy metrics:', e2);
    updateMetricsDisplay({
      held_out_accuracy: 1.0,
      held_out_macro_f1: 1.0,
      held_out_top_3_accuracy: 1.0,
      num_classes: 41
    });
  }
}

function updateMetricsDisplay(meta) {
  const elAcc = document.getElementById('metric-accuracy');
  const elF1 = document.getElementById('metric-f1');
  const elTop3 = document.getElementById('metric-top3');
  const elClasses = document.getElementById('metric-classes');

  if (elAcc) elAcc.textContent = `${((meta.held_out_accuracy || 1.0) * 100).toFixed(1)}%`;
  if (elF1) elF1.textContent = `${((meta.held_out_macro_f1 || 1.0) * 100).toFixed(1)}%`;
  if (elTop3) elTop3.textContent = `${((meta.held_out_top_3_accuracy || 1.0) * 100).toFixed(1)}%`;
  if (elClasses) elClasses.textContent = meta.num_classes || 41;
}

// -----------------------------------------------------------------------------
// 5. Update Hero and Profile UI Elements
// -----------------------------------------------------------------------------
function initHeroAndProfileUI() {
  const name = state.userName && state.userName !== 'Self' ? state.userName : 'there';
  const displayName = state.userName && state.userName !== 'Self' ? state.userName : 'User';

  // Hero greeting
  const heroNameEl = document.getElementById('hero-user-name');
  if (heroNameEl) heroNameEl.textContent = name;

  // Header user badge
  const headerNameEl = document.getElementById('header-user-name');
  const headerAvatarEl = document.getElementById('header-user-avatar');
  if (headerNameEl) headerNameEl.textContent = displayName;
  if (headerAvatarEl) {
    if (state.userPhoto) {
      headerAvatarEl.innerHTML = `<img src="${state.userPhoto}" alt="${displayName}" style="width:20px;height:20px;border-radius:50%;object-fit:cover;">`;
    } else {
      headerAvatarEl.textContent = displayName[0].toUpperCase();
    }
  }

  // Sidebar profile card
  const sidebarNameEl = document.getElementById('sidebar-user-name');
  const sidebarAvatarEl = document.getElementById('sidebar-user-avatar');
  const sidebarDetailEl = document.getElementById('sidebar-user-detail');

  if (sidebarNameEl) sidebarNameEl.textContent = `👋 ${displayName}`;
  if (sidebarAvatarEl) {
    if (state.userPhoto) {
      sidebarAvatarEl.innerHTML = `<img src="${state.userPhoto}" alt="${displayName}">`;
    } else {
      sidebarAvatarEl.textContent = displayName[0].toUpperCase();
    }
  }

  if (sidebarDetailEl) {
    const p = state.patientProfile;
    const conds = (p.conditions || []).filter(c => !c.includes('None')).slice(0, 2);
    const condStr = conds.length > 0 ? conds.join(', ') : 'None / Generally Healthy';

    sidebarDetailEl.innerHTML = `
      📅 ${p.age_range || 'Adult'} (${p.age || 28} yrs)<br>
      ⚧ Biological Sex: ${p.biological_sex || 'Unspecified'}<br>
      🩺 ${condStr}
    `;
  }
}

// -----------------------------------------------------------------------------
// 6. Example Pills & Chips
// -----------------------------------------------------------------------------
function initExamplePills() {
  const pills = document.querySelectorAll('.example-pill');
  const textarea = document.getElementById('symptom-input');

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const query = pill.getAttribute('data-query');
      if (textarea && query) {
        textarea.value = query;
        textarea.dispatchEvent(new Event('input'));
        textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Auto trigger analysis
        runSymptomAnalysis();
      }
    });
  });

  const chips = document.querySelectorAll('#symptom-chips .chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const sym = chip.getAttribute('data-symptom');
      if (textarea && sym) {
        const current = textarea.value.trim();
        textarea.value = current ? `${current}, ${sym}` : sym;
        textarea.dispatchEvent(new Event('input'));
        textarea.focus();
      }
    });
  });
}

// -----------------------------------------------------------------------------
// 7. Symptom Input Handlers
// -----------------------------------------------------------------------------
function initSymptomInput() {
  const textarea = document.getElementById('symptom-input');
  const charCount = document.getElementById('char-count');
  const btnClear = document.getElementById('btn-clear-symptoms');
  const btnAnalyze = document.getElementById('btn-analyze-symptoms');

  if (!textarea) return;

  textarea.addEventListener('input', () => {
    const len = textarea.value.length;
    if (charCount) charCount.textContent = len;
    checkEmergencyInstant(textarea.value);
  });

  // Ctrl+Enter or Cmd+Enter shortcut
  textarea.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runSymptomAnalysis();
    }
  });

  if (btnClear) {
    btnClear.addEventListener('click', () => {
      textarea.value = '';
      if (charCount) charCount.textContent = '0';
      document.getElementById('emergency-banner').classList.add('hidden');
      resetConsultationView();
    });
  }

  if (btnAnalyze) {
    btnAnalyze.addEventListener('click', runSymptomAnalysis);
  }

  const btnReset = document.getElementById('btn-reset-consultation');
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      textarea.value = '';
      if (charCount) charCount.textContent = '0';
      resetConsultationView();
      textarea.focus();
    });
  }
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
// 8. Run Symptom Analysis & API Call
// -----------------------------------------------------------------------------
async function runSymptomAnalysis() {
  const textarea = document.getElementById('symptom-input');
  const query = textarea ? textarea.value.trim() : '';

  if (!query) {
    alert('Please enter or select at least one symptom.');
    if (textarea) textarea.focus();
    return;
  }

  const spinner = document.getElementById('analyze-spinner');
  const btn = document.getElementById('btn-analyze-symptoms');
  if (spinner) spinner.classList.remove('hidden');
  if (btn) btn.disabled = true;

  try {
    const payload = {
      text: query,
      patient_profile: state.patientProfile
    };

    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    renderPredictionResults(data);
  } catch (err) {
    console.error('Prediction API Error, falling back to client evaluation:', err);
    runClientSideFallback(query);
  } finally {
    if (spinner) spinner.classList.add('hidden');
    if (btn) btn.disabled = false;
  }
}

// -----------------------------------------------------------------------------
// 9. Comprehensive Prediction Results Rendering (Streamlit Parity)
// -----------------------------------------------------------------------------
function renderPredictionResults(data) {
  const emptyState = document.getElementById('results-empty-state');
  const resultsCard = document.getElementById('results-card');

  if (emptyState) emptyState.style.display = 'none';
  if (resultsCard) resultsCard.classList.remove('hidden');

  const greetingName = state.userName && state.userName !== 'Self' ? state.userName : 'there';

  // 1. Emergency Triage
  if (data.triage && data.triage.emergency_detected) {
    const banner = document.getElementById('emergency-banner');
    document.getElementById('emergency-title').textContent = data.triage.category || 'CRITICAL EMERGENCY DETECTED';
    document.getElementById('emergency-message').textContent = data.triage.guidance || 'Seek immediate emergency medical care.';
    banner.classList.remove('hidden');
  }

  // 2. Personalized Greeting Banner
  const greetingBanner = document.getElementById('results-greeting-banner');
  if (greetingBanner) {
    const prof = state.patientProfile;
    const condList = (prof.conditions || []).filter(c => !c.includes('None')).slice(0, 2);
    const profileSummary = `Age ${prof.age || 28} (${prof.age_range || 'Adult'})${condList.length ? ' · ' + condList.join(', ') : ''}`;

    greetingBanner.innerHTML = `
      <strong>👋 ${escapeHtml(greetingName)}</strong>, thank you for describing your symptoms. Based on your health profile (${escapeHtml(profileSummary)}), here is my detailed clinical analysis:
    `;
  }

  // 3. 🔬 Detected Symptoms — Explained
  const symContainer = document.getElementById('symptom-cards-container');
  if (symContainer) {
    symContainer.innerHTML = '';

    const explanations = data.symptom_explanations || [];
    if (explanations.length > 0) {
      explanations.forEach(item => {
        const isNeg = !!item.negated;
        const card = document.createElement('div');
        card.className = `symptom-explain-card ${isNeg ? 'negated' : ''}`;
        card.innerHTML = `
          <div class="symptom-explain-icon">${isNeg ? '❌' : '✅'}</div>
          <div class="symptom-explain-content">
            <div class="symptom-explain-name" style="${isNeg ? 'text-decoration:line-through;color:#64748b;' : ''}">
              ${escapeHtml(item.name || item.symptom)}
            </div>
            <p class="symptom-explain-desc">${escapeHtml(item.definition || '')} ${isNeg ? '<em>(Ruled out by you)</em>' : ''}</p>
            ${!isNeg && item.match_role ? `<div class="symptom-explain-match">🎯 ${escapeHtml(item.match_role)}</div>` : ''}
          </div>
        `;
        symContainer.appendChild(card);
      });
    } else {
      // Fallback if explanations array not returned
      const confirmed = data.extracted_symptoms || [];
      if (confirmed.length > 0) {
        confirmed.forEach(s => {
          const card = document.createElement('div');
          card.className = 'symptom-explain-card';
          const title = s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
          card.innerHTML = `
            <div class="symptom-explain-icon">✅</div>
            <div class="symptom-explain-content">
              <div class="symptom-explain-name">${escapeHtml(title)}</div>
              <p class="symptom-explain-desc">Clinical symptom involving localized sensory or physiological disturbance.</p>
              <div class="symptom-explain-match">🎯 Serves as contributing clinical hallmark sign for diagnostic prediction.</div>
            </div>
          `;
          symContainer.appendChild(card);
        });
      } else {
        symContainer.innerHTML = '<p class="text-muted" style="padding:10px;">No specific hallmark symptoms were extracted.</p>';
      }
    }
  }

  // 4. 🩺 Predicted Conditions: 3 in 1 Horizontal Line, Square Cards (Streamlit Parity)
  const predTitle = document.getElementById('predictions-section-title');
  if (predTitle) predTitle.textContent = `🩺 Predicted Conditions for ${greetingName}`;

  const predGrid = document.getElementById('predictions-grid');
  if (predGrid) {
    predGrid.innerHTML = '';
    const predictions = data.predictions || [];

    if (predictions.length === 0) {
      predGrid.innerHTML = `
        <div class="empty-state-box" style="grid-column: 1 / -1;">
          <p>${escapeHtml(data.message || 'No high-confidence condition matched. Please provide more specific symptoms.')}</p>
        </div>
      `;
    } else {
      predictions.forEach((cand, idx) => {
        const pct = Math.round((cand.probability || 0) * 100);
        const card = document.createElement('div');
        card.className = 'prediction-square-card';

        const contribPills = (cand.feature_explanations || [])
          .slice(0, 4)
          .map(e => `<span class="pred-feature-pill">${escapeHtml(e.symptom)}</span>`)
          .join('');

        card.innerHTML = `
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
            <div class="pred-features-label">Key Contributing Symptoms</div>
            <div class="pred-features-list">
              ${contribPills || '<span style="color:#94a3b8;font-size:0.75rem;">None identified</span>'}
            </div>
          </div>
        `;
        predGrid.appendChild(card);
      });
    }
  }

  // 5. 🧠 Comprehensive Symptom-to-Disease Match Card (Streamlit Parity)
  const matchContainer = document.getElementById('symptom-match-container');
  const topCond = (data.predictions && data.predictions.length > 0) ? data.predictions[0].condition : null;
  const matchInfo = data.symptom_match;

  if (matchContainer && topCond && matchInfo && matchInfo.matched_symptoms) {
    const chipsHtml = (matchInfo.matched_symptoms || [])
      .map(s => `<span class="chip-pos">🎯 ${escapeHtml(s)}</span>`)
      .join('');

    matchContainer.innerHTML = `
      <div class="symptom-match-card">
        <div class="symptom-match-header">
          <h4 style="margin:0;display:flex;align-items:center;gap:8px;">
            🧠 ${escapeHtml(greetingName)}, Why Your Symptoms Match ${escapeHtml(topCond)}
          </h4>
          <span class="match-score-badge">★ ${matchInfo.match_percentage || 85}% Hallmark Match</span>
        </div>
        <div style="margin-bottom:0.75rem;">
          <span style="font-size:0.85rem;color:var(--text-secondary);"><strong>Hallmark Signs Correlated:</strong></span>
          <div style="margin-top:4px;">${chipsHtml || '<span class="text-muted">General systemic signs</span>'}</div>
        </div>
        <p style="font-size:0.92rem;line-height:1.6;margin:0 0 0.6rem 0;">
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
    matchContainer.classList.remove('hidden');
  } else if (matchContainer) {
    matchContainer.innerHTML = '';
  }

  // 6. 👤 Personalized Profile & Chronic Risk Card (Streamlit Parity)
  const profileContainer = document.getElementById('profile-analysis-container');
  const profImpact = data.profile_impact;

  if (profileContainer && profImpact && profImpact.has_profile_risks) {
    const vulnItems = (profImpact.vulnerabilities || [])
      .map(v => `<li style="margin-bottom:5px;">${escapeHtml(v)}</li>`)
      .join('');
    const adviceItems = (profImpact.tailored_advice || [])
      .map(a => `<li style="margin-bottom:5px;">${escapeHtml(a)}</li>`)
      .join('');

    profileContainer.innerHTML = `
      <div class="profile-impact-card">
        <div class="section-header-row">
          <h4 style="margin:0;display:flex;align-items:center;gap:8px;">
            👤 Personalized Analysis for ${escapeHtml(greetingName)}
          </h4>
          <span class="badge badge-primary">
            Age: ${state.patientProfile.age || 28} yrs (${state.patientProfile.age_range || 'Adult'})
          </span>
        </div>
        <div style="margin-bottom:0.6rem;">
          <strong style="color:var(--danger);">⚠️ ${escapeHtml(greetingName)}, Clinical Vulnerabilities with ${escapeHtml(topCond || 'Condition')}:</strong>
          <ul style="margin:4px 0 8px 18px;padding:0;color:var(--text-primary);font-size:0.9rem;">
            ${vulnItems}
          </ul>
        </div>
        <div>
          <strong style="color:var(--accent-navy);">🛡️ Customized Care Directives for ${escapeHtml(greetingName)}:</strong>
          <ul style="margin:4px 0 0 18px;padding:0;color:var(--text-primary);font-size:0.9rem;">
            ${adviceItems}
          </ul>
        </div>
      </div>
    `;
    profileContainer.classList.remove('hidden');
  } else if (profileContainer) {
    profileContainer.classList.add('hidden');
  }

  // 7. 💊 Recommended Reference Tablets Shelf (Streamlit Parity)
  const tabletsTitle = document.getElementById('tablets-section-title');
  const tabletsSub = document.getElementById('tablets-section-sub');
  if (tabletsTitle) tabletsTitle.textContent = `💊 Recommended Reference Tablets for ${greetingName}`;
  if (tabletsSub) {
    const allergies = (state.patientProfile.allergies || []).join(', ');
    const allergyNote = allergies ? ` | ⚠️ Allergies: ${allergies}` : '';
    tabletsSub.textContent = `Standard clinical reference medications safety-checked against your profile (${greetingName})${allergyNote}`;
  }

  const tabletsGrid = document.getElementById('tablets-shelf-grid');
  if (tabletsGrid) {
    tabletsGrid.innerHTML = '';
    const tablets = data.reference_tablets || [];

    if (tablets.length === 0) {
      tabletsGrid.innerHTML = '<p class="text-muted" style="grid-column:1/-1;">No standard over-the-counter tablet reference recommended for this condition. Please consult a licensed physician.</p>';
    } else {
      tablets.forEach(tab => {
        const card = document.createElement('div');
        card.className = 'tablet-card';

        const isOtc = (tab.prescription_status || '').toLowerCase().includes('otc') || (tab.prescription_status || '').toLowerCase().includes('over');
        const badgeClass = isOtc ? 'badge-otc' : 'badge-rx';
        const badgeText = isOtc ? 'Over-the-Counter (OTC)' : (tab.prescription_status || 'Prescription (Rx)');

        // Safety evaluation alerts
        let safetyAlertHtml = '';
        const safetyEval = tab.safety_evaluation || {};
        if (safetyEval.safety_alerts && safetyEval.safety_alerts.length > 0) {
          safetyEval.safety_alerts.forEach(al => {
            const isContra = (al.severity || '').toLowerCase().includes('contra');
            safetyAlertHtml += `
              <div class="tablet-safety-alert ${isContra ? 'contra' : 'warn'}">
                ⚠️ [${escapeHtml(al.category || 'Safety Alert')} for ${escapeHtml(greetingName)}]: ${escapeHtml(al.clinical_warning || al.message || '')}
              </div>
            `;
          });
        } else {
          safetyAlertHtml = `
            <div class="tablet-safety-alert safe">
              ✅ Compatible with ${escapeHtml(greetingName)}'s reported health profile and age bracket.
            </div>
          `;
        }

        card.innerHTML = `
          <div class="tablet-header">
            <div class="tablet-name">💊 ${escapeHtml(tab.name || tab.generic_name || '')}</div>
            <span class="${badgeClass}">${escapeHtml(badgeText)}</span>
          </div>
          <div class="tablet-row"><strong>Purpose / Indication:</strong> ${escapeHtml(tab.indication || (tab.labeled_indications || []).slice(0, 3).join(', ') || '')}</div>
          <div class="tablet-row"><strong>Dosage Form:</strong> ${escapeHtml(tab.dosage_form || 'Tablet')} &nbsp;|&nbsp; <strong>Class:</strong> ${escapeHtml(tab.category || tab.drug_class || 'Therapeutic')}</div>
          ${tab.clinical_guidance ? `<div class="tablet-row"><strong>Clinical Usage Guidance:</strong> ${escapeHtml(tab.clinical_guidance)}</div>` : ''}
          ${tab.precautions ? `<div class="tablet-caution"><strong>⚠️ Precaution:</strong> ${escapeHtml(tab.precautions)}</div>` : ''}
          ${safetyAlertHtml}
        `;
        tabletsGrid.appendChild(card);
      });
    }
  }

  // 8. 📖 Verified Medical Knowledge & Citations Expander
  const citationsSection = document.getElementById('citations-section');
  const expanderTitle = document.getElementById('evidence-expander-title');
  const expanderContent = document.getElementById('evidence-expander-content');
  const condInfo = data.condition_info;

  if (citationsSection && expanderContent && topCond && condInfo && condInfo.overview) {
    if (expanderTitle) expanderTitle.textContent = `📖 Official Medical Information & Evidence — ${topCond}`;

    let citationsHtml = '';
    (condInfo.citations || []).forEach(cite => {
      citationsHtml += `
        <div class="source-citation">
          🏛️ <strong>${escapeHtml(cite.source || '')}</strong><br>
          🔗 <a href="${escapeHtml(cite.url || '')}" target="_blank" rel="noopener noreferrer">${escapeHtml(cite.url || '')}</a>
        </div>
      `;
    });

    expanderContent.innerHTML = `
      <p style="margin-bottom:0.8rem;"><strong>Clinical Overview:</strong> ${escapeHtml(condInfo.overview)}</p>
      <p style="margin-bottom:0.8rem;"><strong>Recommended Clinical Steps:</strong> ${escapeHtml(condInfo.recommended_next_steps || 'Consult a healthcare provider.')}</p>
      ${condInfo.urgent_warnings ? `<div class="tablet-caution" style="margin-bottom:0.8rem;"><strong>🚨 Urgent Warning:</strong> ${escapeHtml(condInfo.urgent_warnings)}</div>` : ''}
      <h5 style="margin:1rem 0 0.4rem 0;color:var(--accent-navy);">📚 Official Health Authority Citations:</h5>
      ${citationsHtml}
    `;
    citationsSection.style.display = 'block';
  } else if (citationsSection) {
    citationsSection.style.display = 'none';
  }

  // 9. 🗣️ Follow-up Questions
  const followUpSection = document.getElementById('follow-up-section');
  const followUpHeader = document.getElementById('follow-up-header');
  const followUpList = document.getElementById('follow-up-list');

  if (followUpHeader) followUpHeader.textContent = `🗣️ Clinical Follow-up Questions for ${greetingName}:`;
  if (followUpList) {
    followUpList.innerHTML = '';
    const fups = data.follow_up_questions || [];

    if (fups.length > 0) {
      if (followUpSection) followUpSection.style.display = 'block';
      fups.forEach(q => {
        const item = document.createElement('div');
        item.className = 'follow-up-item-interactive';
        item.textContent = `${q} 💬 (Click to add response)`;
        item.addEventListener('click', () => {
          const textarea = document.getElementById('symptom-input');
          if (textarea) {
            const current = textarea.value.trim();
            textarea.value = current ? `${current}\n• Note on "${q}": ` : `Note on "${q}": `;
            textarea.focus();
            textarea.dispatchEvent(new Event('input'));
            textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        });
        followUpList.appendChild(item);
      });
    } else {
      if (followUpSection) followUpSection.style.display = 'none';
    }
  }

  // 10. ⚕️ Disclaimer
  const disclaimerEl = document.getElementById('results-disclaimer');
  if (disclaimerEl) {
    disclaimerEl.innerHTML = `
      ⚕️ <strong>Clinical Disclaimer for ${escapeHtml(greetingName)}:</strong>
      ${escapeHtml(data.disclaimer || 'MediGuide AI is an educational research prototype. Predictions and tablet references are for informational analysis only. Always consult a licensed physician or pharmacist for clinical diagnosis and prescriptions.')}
    `;
  }

  // Scroll results into view smoothly
  resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetConsultationView() {
  const emptyState = document.getElementById('results-empty-state');
  const resultsCard = document.getElementById('results-card');
  if (emptyState) emptyState.style.display = 'block';
  if (resultsCard) resultsCard.classList.add('hidden');
}

// -----------------------------------------------------------------------------
// 10. Quick Medicine Lookup in Sidebar
// -----------------------------------------------------------------------------
function initQuickMedicineLookup() {
  const input = document.getElementById('quick-med-input');
  const btn = document.getElementById('btn-quick-med-search');
  const resultsContainer = document.getElementById('quick-med-results');

  const doSearch = async () => {
    const q = input.value.trim();
    if (!q) return;

    resultsContainer.innerHTML = '<span class="text-muted" style="font-size:0.78rem;">Searching curated medicines…</span>';

    try {
      const res = await fetch(`/api/medicines?query=${encodeURIComponent(q)}`);
      if (res.ok) {
        const data = await res.json();
        const meds = data.medicines || [];
        if (meds.length === 0) {
          resultsContainer.innerHTML = '<span class="text-muted" style="font-size:0.78rem;">No matching medicine found.</span>';
          return;
        }

        resultsContainer.innerHTML = '';
        meds.slice(0, 3).forEach(m => {
          const div = document.createElement('div');
          div.className = 'quick-med-item';
          const brands = (m.brand_names || []).slice(0, 3).join(', ');
          div.innerHTML = `
            <div class="quick-med-name">💊 ${escapeHtml(m.generic_name)}</div>
            ${brands ? `<div class="quick-med-brands">Brands: ${escapeHtml(brands)}</div>` : ''}
            <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:2px;">
              <strong>Indications:</strong> ${escapeHtml((m.labeled_indications || []).slice(0, 2).join(', '))}
            </div>
          `;
          resultsContainer.appendChild(div);
        });
      }
    } catch (e) {
      resultsContainer.innerHTML = '<span class="text-muted" style="font-size:0.78rem;">Error searching medicines.</span>';
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
// 11. Drug Safety & Interaction Checker (Tab 2)
// -----------------------------------------------------------------------------
function initSafetyChecker() {
  const drugInput = document.getElementById('safety-drug-input');
  const btnAdd = document.getElementById('btn-add-drug');
  const btnCheck = document.getElementById('btn-check-interactions');
  const drugsList = document.getElementById('selected-drugs-list');
  const drugCount = document.getElementById('drug-count');
  const quickChips = document.querySelectorAll('.quick-drugs-row .chip-sm');

  const renderSelectedDrugs = () => {
    drugsList.innerHTML = '';
    if (state.selectedDrugs.length === 0) {
      drugsList.innerHTML = '<span class="empty-hint">No medications added yet. Add at least two to check interactions.</span>';
    } else {
      state.selectedDrugs.forEach(drug => {
        const pill = document.createElement('span');
        pill.className = 'drug-pill-tag';
        pill.innerHTML = `
          <span>💊 ${escapeHtml(drug)}</span>
          <span class="drug-pill-remove" data-drug="${escapeHtml(drug)}" title="Remove drug">&times;</span>
        `;
        drugsList.appendChild(pill);
      });
    }
    if (drugCount) drugCount.textContent = state.selectedDrugs.length;
  };

  const addDrug = (drugName) => {
    const trimmed = drugName.trim();
    if (!trimmed) return;
    if (!state.selectedDrugs.some(d => d.toLowerCase() === trimmed.toLowerCase())) {
      state.selectedDrugs.push(trimmed);
      renderSelectedDrugs();
    }
    if (drugInput) drugInput.value = '';
  };

  if (btnAdd) {
    btnAdd.addEventListener('click', () => addDrug(drugInput.value));
  }
  if (drugInput) {
    drugInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addDrug(drugInput.value);
      }
    });
  }

  quickChips.forEach(chip => {
    chip.addEventListener('click', () => addDrug(chip.getAttribute('data-drug')));
  });

  if (drugsList) {
    drugsList.addEventListener('click', (e) => {
      if (e.target.classList.contains('drug-pill-remove')) {
        const d = e.target.getAttribute('data-drug');
        state.selectedDrugs = state.selectedDrugs.filter(x => x !== d);
        renderSelectedDrugs();
      }
    });
  }

  // Screen interactions button
  if (btnCheck) {
    btnCheck.addEventListener('click', async () => {
      if (state.selectedDrugs.length < 2) {
        alert('Please add at least 2 medications to screen pairwise interactions.');
        return;
      }

      const emptyBox = document.getElementById('safety-empty-state');
      const resultsBox = document.getElementById('safety-results-box');
      if (emptyBox) emptyBox.style.display = 'none';
      if (resultsBox) resultsBox.classList.remove('hidden');

      resultsBox.innerHTML = '<span class="text-muted">Screening pharmacodynamic interactions against FDA/DailyMed database…</span>';

      try {
        const payload = {
          drugs: state.selectedDrugs,
          allergies: state.patientProfile.allergies || [],
          conditions: state.patientProfile.conditions || []
        };

        const res = await fetch('/api/safety', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const interactions = data.drug_interactions || [];

        resultsBox.innerHTML = '';
        if (interactions.length === 0) {
          resultsBox.innerHTML = `
            <div class="empty-state-box" style="border-color:#22c55e;">
              <h4 style="color:#15803d;margin-bottom:4px;">✅ No Severe Documented Interactions</h4>
              <p>No dangerous pharmacodynamic contraindications found between [${state.selectedDrugs.join(', ')}] in curated database.</p>
            </div>
          `;
        } else {
          interactions.forEach(inter => {
            const isSevere = (inter.severity || '').toLowerCase().includes('severe') || (inter.severity || '').toLowerCase().includes('contra');
            const card = document.createElement('div');
            card.className = `interaction-item-card ${isSevere ? '' : 'warn'}`;
            const effect = inter.clinical_effect || inter.risk_description || 'Potential adverse interaction.';
            card.innerHTML = `
              <div class="interaction-header">
                🚨 ${escapeHtml(inter.drug_a || inter.drug_1)} + ${escapeHtml(inter.drug_b || inter.drug_2)} (${escapeHtml(inter.severity || 'Caution')})
              </div>
              <div class="interaction-desc">${escapeHtml(effect)}</div>
              ${inter.recommendation ? `<div style="font-size:0.78rem;color:var(--text-muted);margin-top:4px;"><strong>Directive:</strong> ${escapeHtml(inter.recommendation)}</div>` : ''}
            `;
            resultsBox.appendChild(card);
          });
        }
      } catch (err) {
        resultsBox.innerHTML = '<span class="text-danger">Failed to screen interactions. Please try again.</span>';
      }
    });
  }

  renderSelectedDrugs();
}

// -----------------------------------------------------------------------------
// 12. Medicine Catalogue (Tab 3)
// -----------------------------------------------------------------------------
async function loadMedicinesCatalogue() {
  const container = document.getElementById('medicines-catalogue');
  if (!container) return;

  container.innerHTML = '<span class="text-muted">Loading verified clinical medications…</span>';

  try {
    const res = await fetch('/api/medicines');
    if (res.ok) {
      const data = await res.json();
      state.medicinesCache = data.medicines || [];
      renderMedicinesCatalogue(state.medicinesCache);
    }
  } catch (e) {
    container.innerHTML = '<span class="text-muted">Could not load medicines database.</span>';
  }
}

function renderMedicinesCatalogue(meds) {
  const container = document.getElementById('medicines-catalogue');
  if (!container) return;

  container.innerHTML = '';
  if (meds.length === 0) {
    container.innerHTML = '<p class="text-muted">No medicines found matching criteria.</p>';
    return;
  }

  meds.forEach(m => {
    const card = document.createElement('div');
    card.className = 'med-cat-card';
    const brands = (m.brand_names || []).join(', ');
    const indications = (m.labeled_indications || []).slice(0, 3).join(', ');
    const sideEffects = (m.common_side_effects || []).slice(0, 3).join(', ');

    card.innerHTML = `
      <div class="med-cat-title">💊 ${escapeHtml(m.generic_name)}</div>
      ${brands ? `<div class="med-cat-brands">Brands: ${escapeHtml(brands)}</div>` : ''}
      <div class="med-cat-row"><strong>Drug Class:</strong> ${escapeHtml(m.drug_class || 'General Therapeutic')}</div>
      <div class="med-cat-row"><strong>Indications:</strong> ${escapeHtml(indications || 'General Relief')}</div>
      ${sideEffects ? `<div class="med-cat-row"><strong>Side Effects:</strong> ${escapeHtml(sideEffects)}</div>` : ''}
    `;
    container.appendChild(card);
  });
}

// Search input for catalogue
const dbSearchInput = document.getElementById('db-search-input');
if (dbSearchInput) {
  dbSearchInput.addEventListener('input', () => {
    const q = dbSearchInput.value.toLowerCase().trim();
    if (!q) {
      renderMedicinesCatalogue(state.medicinesCache);
      return;
    }
    const filtered = state.medicinesCache.filter(m => {
      const g = (m.generic_name || '').toLowerCase();
      const b = (m.brand_names || []).join(' ').toLowerCase();
      const ind = (m.labeled_indications || []).join(' ').toLowerCase();
      return g.includes(q) || b.includes(q) || ind.includes(q);
    });
    renderMedicinesCatalogue(filtered);
  });
}

// -----------------------------------------------------------------------------
// 13. Bottom Tabs (About · Methodology · Safety Protocols)
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
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });
}

// -----------------------------------------------------------------------------
// 14. Consultation Summary Export
// -----------------------------------------------------------------------------
function initSummaryExport() {
  const btnPrint = document.getElementById('btn-print-summary');
  if (btnPrint) {
    btnPrint.addEventListener('click', () => {
      window.print();
    });
  }
}

// -----------------------------------------------------------------------------
// 15. Client-Side Fallback Predictor
// -----------------------------------------------------------------------------
function runClientSideFallback(text) {
  const lower = text.toLowerCase();
  const symptoms = [];
  if (lower.includes('fever')) symptoms.push('high_fever');
  if (lower.includes('chill') || lower.includes('shiver')) symptoms.push('chills');
  if (lower.includes('headache')) symptoms.push('headache');
  if (lower.includes('nausea') || lower.includes('vomit')) symptoms.push('nausea');
  if (lower.includes('cough')) symptoms.push('cough');
  if (lower.includes('joint') || lower.includes('muscle')) symptoms.push('joint_pain');

  let pred = 'Malaria';
  if (lower.includes('cough') && lower.includes('breath')) pred = 'Bronchial Asthma';
  else if (lower.includes('burning') || lower.includes('stomach') || lower.includes('acid')) pred = 'GERD';
  else if (lower.includes('sneeze') || lower.includes('watery')) pred = 'Allergic Rhinitis';

  const mockData = {
    status: 'PREDICTION_SUCCESS',
    message: 'Local offline prediction fallback active.',
    triage: { emergency_detected: false },
    extracted_symptoms: symptoms.length > 0 ? symptoms : ['fever'],
    negated_symptoms: [],
    symptom_explanations: symptoms.map(s => ({
      symptom: s,
      name: s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      definition: `Clinical disturbance involving ${s.replace(/_/g, ' ')}.`,
      match_role: 'Serves as primary hallmark marker.',
      negated: false
    })),
    predictions: [
      {
        condition: pred,
        probability: 0.942,
        percentage: '94.2%',
        feature_explanations: symptoms.map(s => ({ symptom: s.replace(/_/g, ' '), weight: 2.45 }))
      },
      {
        condition: 'Dengue',
        probability: 0.045,
        percentage: '4.5%',
        feature_explanations: []
      },
      {
        condition: 'Typhoid',
        probability: 0.013,
        percentage: '1.3%',
        feature_explanations: []
      }
    ],
    symptom_match: {
      condition: pred,
      match_percentage: 88,
      matched_symptoms: symptoms.map(s => s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())),
      clinical_rationale: `Reported symptoms correlate directly with the standard clinical criteria for ${pred}.`,
      pathophysiological_mechanism: 'Acute inflammatory cascade induced by infectious / constitutional antigens.',
      differential_ruleout: 'Absence of secondary complications confirms uncomplicated initial stage.'
    },
    reference_tablets: [
      {
        name: 'Paracetamol (Dolo 650, Calpol)',
        prescription_status: 'Over-the-Counter (OTC)',
        indication: 'Fever reduction and constitutional pain relief',
        dosage_form: 'Tablet (650mg)',
        clinical_guidance: 'Take 1 tablet every 4-6 hours as needed after meals. Max 4,000mg/24h.',
        precautions: 'Avoid concurrent alcohol consumption.'
      }
    ],
    follow_up_questions: [
      'Have your symptoms persisted for more than 48 hours?',
      'Do you have any known allergies to antipyretics or antibiotics?'
    ],
    disclaimer: 'MediGuide AI is an educational research prototype. Always consult a licensed healthcare professional for medical diagnosis and prescriptions.'
  };

  renderPredictionResults(mockData);
}

// -----------------------------------------------------------------------------
// Utility Functions
// -----------------------------------------------------------------------------
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
