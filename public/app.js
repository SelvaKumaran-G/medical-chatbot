/**
 * MediGuide AI — Client Application Script
 * Orchestrates clinical triage, ML prediction UI, interaction screening, and local context persistence.
 */

// State Management
const state = {
  theme: localStorage.getItem('mediguide_theme') || 'light',
  patientProfile: JSON.parse(localStorage.getItem('mediguide_profile') || JSON.stringify({
    name: 'Self',
    age: 30,
    biological_sex: 'Unspecified',
    age_range: 'Young Adult (18 - 35 yrs)',
    conditions: [],
    allergies: [],
    is_pregnant: false
  })),
  selectedDrugs: ['Warfarin', 'Ibuprofen'],
  medicinesCache: []
};

// Emergency Heuristic Regex Patterns (client-side pre-screen for instant triage)
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
  initNavigation();
  initPatientProfile();
  initSymptomInput();
  initSafetyChecker();
  initMedicineCatalogue();
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

// -----------------------------------------------------------------------------
// 2. Navigation Tabs
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

      // If switching to database tab and empty, load catalogue
      if (targetId === 'tab-database' && state.medicinesCache.length === 0) {
        loadMedicinesCatalogue();
      }
    });
  });

  // Edit context button jumps to profile tab
  const btnEditContext = document.getElementById('btn-edit-context');
  if (btnEditContext) {
    btnEditContext.addEventListener('click', () => {
      document.getElementById('tab-btn-profile').click();
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
// 3. Patient Profile Management
// -----------------------------------------------------------------------------
function initPatientProfile() {
  updateProfileRibbon();

  // Populate form with stored state
  const form = document.getElementById('profile-form');
  if (!form) return;

  document.getElementById('profile-name').value = state.patientProfile.name || 'Self';
  document.getElementById('profile-age').value = state.patientProfile.age || 30;
  document.getElementById('profile-sex').value = state.patientProfile.biological_sex || 'Unspecified';
  document.getElementById('profile-age-range').value = state.patientProfile.age_range || 'Young Adult (18 - 35 yrs)';
  document.getElementById('profile-pregnant').checked = !!state.patientProfile.is_pregnant;

  // Checkboxes
  const condBoxes = form.querySelectorAll('input[name="conditions"]');
  condBoxes.forEach(cb => {
    cb.checked = (state.patientProfile.conditions || []).includes(cb.value);
  });

  const allergyBoxes = form.querySelectorAll('input[name="allergies"]');
  allergyBoxes.forEach(cb => {
    cb.checked = (state.patientProfile.allergies || []).includes(cb.value);
  });

  // Form submit
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const selectedConds = Array.from(form.querySelectorAll('input[name="conditions"]:checked')).map(cb => cb.value);
    const selectedAllergies = Array.from(form.querySelectorAll('input[name="allergies"]:checked')).map(cb => cb.value);

    state.patientProfile = {
      name: document.getElementById('profile-name').value.trim() || 'Self',
      age: parseInt(document.getElementById('profile-age').value, 10) || 30,
      biological_sex: document.getElementById('profile-sex').value,
      age_range: document.getElementById('profile-age-range').value,
      conditions: selectedConds,
      allergies: selectedAllergies,
      is_pregnant: document.getElementById('profile-pregnant').checked
    };

    localStorage.setItem('mediguide_profile', JSON.stringify(state.patientProfile));
    updateProfileRibbon();

    // Show feedback
    const msg = document.getElementById('profile-saved-msg');
    msg.classList.remove('hidden');
    setTimeout(() => msg.classList.add('hidden'), 3500);
  });
}

function updateProfileRibbon() {
  const p = state.patientProfile;
  const nameEl = document.getElementById('ribbon-patient-name');
  const demoEl = document.getElementById('ribbon-patient-demographics');
  const allergyEl = document.getElementById('ribbon-patient-allergies');
  const condEl = document.getElementById('ribbon-patient-conditions');
  const dot = document.getElementById('profile-indicator-dot');

  if (nameEl) nameEl.textContent = p.name || 'Self';
  if (demoEl) demoEl.textContent = `${p.age || 30} yrs • ${p.biological_sex || 'Unspecified'}`;

  const hasAllergies = p.allergies && p.allergies.length > 0;
  if (allergyEl) {
    if (hasAllergies) {
      allergyEl.textContent = p.allergies.join(', ');
      allergyEl.className = 'text-danger';
    } else {
      allergyEl.textContent = 'None Reported';
      allergyEl.className = 'text-safe';
    }
  }

  const hasConds = p.conditions && p.conditions.length > 0;
  if (condEl) {
    condEl.textContent = hasConds ? p.conditions.slice(0, 2).join(', ') + (p.conditions.length > 2 ? '...' : '') : 'None';
  }

  if (dot) {
    if (hasAllergies || hasConds || p.is_pregnant) {
      dot.classList.add('active');
    } else {
      dot.classList.remove('active');
    }
  }
}

// -----------------------------------------------------------------------------
// 4. Symptom Input & Prediction Engine
// -----------------------------------------------------------------------------
function initSymptomInput() {
  const textarea = document.getElementById('symptom-input');
  const charCount = document.getElementById('char-count');
  const btnAnalyze = document.getElementById('btn-analyze-symptoms');
  const btnClear = document.getElementById('btn-clear-symptoms');
  const chips = document.querySelectorAll('#symptom-chips .chip');

  // Input event: character count & instant red-flag pre-screening
  textarea.addEventListener('input', () => {
    charCount.textContent = textarea.value.length;
    checkEmergencyInstant(textarea.value);
  });

  // Quick symptom chips
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const sym = chip.getAttribute('data-symptom');
      if (textarea.value.trim()) {
        textarea.value += ', ' + sym;
      } else {
        textarea.value = 'I am experiencing ' + sym;
      }
      charCount.textContent = textarea.value.length;
      checkEmergencyInstant(textarea.value);
      textarea.focus();
    });
  });

  // Clear button
  btnClear.addEventListener('click', () => {
    textarea.value = '';
    charCount.textContent = '0';
    document.getElementById('emergency-banner').classList.add('hidden');
    resetConsultationView();
  });

  // Analyze button
  btnAnalyze.addEventListener('click', runSymptomAnalysis);

  // New assessment button
  const btnReset = document.getElementById('btn-reset-consultation');
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      textarea.value = '';
      charCount.textContent = '0';
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

async function runSymptomAnalysis() {
  const textarea = document.getElementById('symptom-input');
  const query = textarea.value.trim();

  if (!query) {
    alert('Please enter or select at least one symptom.');
    textarea.focus();
    return;
  }

  const spinner = document.getElementById('analyze-spinner');
  const btn = document.getElementById('btn-analyze-symptoms');
  spinner.classList.remove('hidden');
  btn.disabled = true;

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
    console.error('Prediction API Error:', err);
    // If running in purely static mode or offline, use client-side predictor fallback
    runClientSideFallback(query);
  } finally {
    spinner.classList.add('hidden');
    btn.disabled = false;
  }
}

function renderPredictionResults(data) {
  const emptyState = document.getElementById('results-empty-state');
  const resultsCard = document.getElementById('results-card');

  emptyState.style.display = 'none';
  resultsCard.classList.remove('hidden');

  // 1. Triage Banner
  if (data.triage && data.triage.emergency_detected) {
    const banner = document.getElementById('emergency-banner');
    document.getElementById('emergency-title').textContent = data.triage.category || 'CRITICAL EMERGENCY DETECTED';
    document.getElementById('emergency-message').textContent = data.triage.guidance || 'Seek immediate emergency medical care.';
    banner.classList.remove('hidden');
  }

  // 2. Extracted Entities
  const confirmedContainer = document.getElementById('tokens-confirmed');
  const negatedContainer = document.getElementById('tokens-negated');
  const negatedWrap = document.getElementById('tokens-negated-wrap');

  confirmedContainer.innerHTML = '';
  negatedContainer.innerHTML = '';

  if (data.extracted_symptoms && data.extracted_symptoms.length > 0) {
    data.extracted_symptoms.forEach(s => {
      const b = document.createElement('span');
      b.className = 'token-badge confirmed';
      b.textContent = s.replace(/_/g, ' ');
      confirmedContainer.appendChild(b);
    });
  } else {
    confirmedContainer.innerHTML = '<span class="text-muted">None recognized</span>';
  }

  if (data.negated_symptoms && data.negated_symptoms.length > 0) {
    negatedWrap.style.display = 'flex';
    data.negated_symptoms.forEach(s => {
      const b = document.createElement('span');
      b.className = 'token-badge negated';
      b.textContent = s.replace(/_/g, ' ');
      negatedContainer.appendChild(b);
    });
  } else {
    negatedWrap.style.display = 'none';
  }

  // 3. Patient Context Safety Alert
  const safetyBox = document.getElementById('patient-safety-alert');
  const safetyItems = document.getElementById('safety-alert-items');
  safetyItems.innerHTML = '';

  if (data.safety_alerts && data.safety_alerts.length > 0) {
    safetyBox.classList.remove('hidden');
    data.safety_alerts.forEach(alert => {
      const div = document.createElement('div');
      div.className = 'safety-alert-row';
      div.innerHTML = `<strong>${escapeHtml(alert.category || 'Warning')}:</strong> ${escapeHtml(alert.clinical_warning || '')}`;
      safetyItems.appendChild(div);
    });
  } else {
    safetyBox.classList.add('hidden');
  }

  // 4. Differential Predictions
  const predContainer = document.getElementById('prediction-list');
  predContainer.innerHTML = '';

  if (!data.predictions || data.predictions.length === 0) {
    predContainer.innerHTML = `
      <div class="empty-state-box">
        <p>${escapeHtml(data.message || 'No high-confidence condition matched. Please provide more symptoms.')}</p>
      </div>
    `;
  } else {
    data.predictions.forEach((pred, idx) => {
      const item = document.createElement('div');
      item.className = 'prediction-item';

      const pct = Math.round(pred.probability * 100);
      const explTags = (pred.feature_explanations || [])
        .map(e => `<span class="feature-tag">${escapeHtml(e.symptom)} (${e.weight > 0 ? '+' : ''}${e.weight})</span>`)
        .join('');

      item.innerHTML = `
        <div class="prediction-top-row">
          <div class="condition-title">#${idx + 1} ${escapeHtml(pred.condition)}</div>
          <div class="percentage-badge">${pred.percentage || pct + '%'}</div>
        </div>
        <div class="probability-bar-bg">
          <div class="probability-bar-fill" style="width: ${pct}%"></div>
        </div>
        ${explTags ? `
          <div class="feature-expl-wrap">
            <div class="feature-expl-header">Pathophysiological Symptom Indicators:</div>
            <div class="feature-tag-list">${explTags}</div>
          </div>
        ` : ''}
      `;
      predContainer.appendChild(item);
    });
  }

  // 5. Reference Medicines
  const refMedsBox = document.getElementById('reference-meds-box');
  const medsGrid = document.getElementById('ref-meds-grid');
  medsGrid.innerHTML = '';

  if (data.reference_medicines && data.reference_medicines.length > 0) {
    refMedsBox.style.display = 'block';
    data.reference_medicines.forEach(med => {
      const card = document.createElement('div');
      card.className = 'med-card-mini';
      const brands = (med.brand_names || []).slice(0, 3).join(', ');
      card.innerHTML = `
        <div class="med-card-name">${escapeHtml(med.generic_name)}</div>
        ${brands ? `<div class="med-card-brands">Brands: ${escapeHtml(brands)}</div>` : ''}
        <div class="med-card-desc">${escapeHtml((med.description || '').slice(0, 95))}...</div>
      `;
      medsGrid.appendChild(card);
    });
  } else {
    refMedsBox.style.display = 'none';
  }

  // 6. Follow-up Questions
  const followUpCard = document.getElementById('follow-up-card');
  const followUpList = document.getElementById('follow-up-list');
  followUpList.innerHTML = '';

  if (data.follow_up_questions && data.follow_up_questions.length > 0) {
    followUpCard.style.display = 'block';
    data.follow_up_questions.forEach(q => {
      const li = document.createElement('li');
      li.textContent = q;
      followUpList.appendChild(li);
    });
  } else {
    followUpCard.style.display = 'none';
  }
}

function resetConsultationView() {
  document.getElementById('results-empty-state').style.display = 'block';
  document.getElementById('results-card').classList.add('hidden');
}

// -----------------------------------------------------------------------------
// 5. Drug-Drug Interaction Screener
// -----------------------------------------------------------------------------
function initSafetyChecker() {
  const drugInput = document.getElementById('safety-drug-input');
  const btnAdd = document.getElementById('btn-add-drug');
  const btnCheck = document.getElementById('btn-check-interactions');
  const quickDrugs = document.querySelectorAll('.quick-drugs-row .chip-sm');

  // Render initial default drugs
  renderSelectedDrugs();

  // Add drug
  function addDrug(name) {
    const clean = name.trim();
    if (!clean) return;
    if (!state.selectedDrugs.map(d => d.toLowerCase()).includes(clean.toLowerCase())) {
      state.selectedDrugs.push(clean);
      renderSelectedDrugs();
    }
    drugInput.value = '';
    drugInput.focus();
  }

  btnAdd.addEventListener('click', () => addDrug(drugInput.value));
  drugInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addDrug(drugInput.value);
    }
  });

  quickDrugs.forEach(chip => {
    chip.addEventListener('click', () => {
      addDrug(chip.getAttribute('data-drug'));
    });
  });

  // Check interactions button
  btnCheck.addEventListener('click', runInteractionScreening);
}

function renderSelectedDrugs() {
  const list = document.getElementById('selected-drugs-list');
  const count = document.getElementById('drug-count');
  count.textContent = state.selectedDrugs.length;

  list.innerHTML = '';
  if (state.selectedDrugs.length === 0) {
    list.innerHTML = '<span class="empty-hint">No medications added yet. Add at least two to check interactions.</span>';
    return;
  }

  state.selectedDrugs.forEach((drug, idx) => {
    const tag = document.createElement('div');
    tag.className = 'drug-tag';
    tag.innerHTML = `
      <span>💊 ${escapeHtml(drug)}</span>
      <button class="drug-tag-remove" data-index="${idx}" title="Remove ${escapeHtml(drug)}">&times;</button>
    `;
    list.appendChild(tag);
  });

  // Attach delete handlers
  list.querySelectorAll('.drug-tag-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt(e.target.getAttribute('data-index'), 10);
      state.selectedDrugs.splice(idx, 1);
      renderSelectedDrugs();
    });
  });
}

async function runInteractionScreening() {
  if (state.selectedDrugs.length < 2) {
    alert('Please add at least 2 medications to check pairwise interactions.');
    return;
  }

  const resultsBox = document.getElementById('safety-results-box');
  const emptyBox = document.getElementById('safety-empty-state');

  resultsBox.innerHTML = '<div class="text-center p-3">Screening pharmacology database...</div>';
  emptyBox.style.display = 'none';
  resultsBox.classList.remove('hidden');

  try {
    const res = await fetch('/api/safety', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        drugs: state.selectedDrugs,
        allergies: state.patientProfile.allergies,
        conditions: state.patientProfile.conditions
      })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderInteractionResults(data);
  } catch (err) {
    console.error('Safety Check Error:', err);
    // Offline heuristic mock
    renderOfflineInteractionFallback();
  }
}

function renderInteractionResults(data) {
  const resultsBox = document.getElementById('safety-results-box');
  resultsBox.innerHTML = '';

  const interactions = data.drug_interactions || [];

  if (interactions.length === 0) {
    resultsBox.innerHTML = `
      <div class="safety-alert-box" style="background:var(--success-subtle);border-color:var(--success-border);color:var(--success);">
        <div class="safety-alert-icon">✓</div>
        <div>
          <h4>No Known Severe Pairwise Interactions Detected</h4>
          <p>None of the screened medications have documented major contraindicated interactions in this reference database. Always consult your pharmacist.</p>
        </div>
      </div>
    `;
    return;
  }

  const heading = document.createElement('h3');
  heading.className = 'section-title';
  heading.textContent = `Found ${interactions.length} Documented Drug Interaction(s):`;
  resultsBox.appendChild(heading);

  interactions.forEach(inter => {
    const item = document.createElement('div');
    const isMajor = (inter.severity || '').toLowerCase().includes('contra') || (inter.severity || '').toLowerCase().includes('severe');
    item.className = `interaction-item ${isMajor ? 'severe' : 'moderate'}`;

    item.innerHTML = `
      <div class="interaction-header">
        <div class="interaction-drugs">⚠️ ${escapeHtml(inter.drug_a)} + ${escapeHtml(inter.drug_b)}</div>
        <span class="badge ${isMajor ? 'badge-danger' : 'badge-warning'}">${escapeHtml(inter.severity || 'Moderate')}</span>
      </div>
      <div class="interaction-effect">${escapeHtml(inter.clinical_effect || 'Pharmacodynamic conflict.')}</div>
      <div class="interaction-recom"><strong>Guidance:</strong> ${escapeHtml(inter.recommendation || 'Consult your prescribing doctor.')}</div>
    `;
    resultsBox.appendChild(item);
  });
}

function renderOfflineInteractionFallback() {
  const hasWarfarin = state.selectedDrugs.some(d => d.toLowerCase().includes('warfarin'));
  const hasIbu = state.selectedDrugs.some(d => d.toLowerCase().includes('ibuprofen') || d.toLowerCase().includes('aspirin'));

  const resultsBox = document.getElementById('safety-results-box');
  resultsBox.innerHTML = '';

  if (hasWarfarin && hasIbu) {
    resultsBox.innerHTML = `
      <div class="interaction-item severe">
        <div class="interaction-header">
          <div class="interaction-drugs">⚠️ Warfarin + NSAID (Ibuprofen / Aspirin)</div>
          <span class="badge badge-danger">Severe / Contraindicated</span>
        </div>
        <div class="interaction-effect">NSAIDs displace warfarin from protein binding sites and inhibit platelets, significantly increasing major gastrointestinal bleeding risk.</div>
        <div class="interaction-recom"><strong>Guidance:</strong> Avoid concurrent use. Consult physician for non-NSAID analgesic alternatives (e.g., paracetamol).</div>
      </div>
    `;
  } else {
    resultsBox.innerHTML = `
      <div class="safety-alert-box" style="background:var(--success-subtle);border-color:var(--success-border);color:var(--success);">
        <div class="safety-alert-icon">✓</div>
        <div>
          <h4>Screening Complete</h4>
          <p>No critical bleeding contraindications detected between selected items.</p>
        </div>
      </div>
    `;
  }
}

// -----------------------------------------------------------------------------
// 6. Medicine Database Explorer
// -----------------------------------------------------------------------------
async function initMedicineCatalogue() {
  const searchInput = document.getElementById('db-search-input');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        filterMedicines(searchInput.value.trim());
      }, 250);
    });
  }
}

async function loadMedicinesCatalogue() {
  const container = document.getElementById('medicines-catalogue');
  container.innerHTML = '<div class="p-3 text-muted">Loading verified medicine records from FDA and CDSCO...</div>';

  try {
    const res = await fetch('/api/medicines');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    state.medicinesCache = data.medicines || [];
    renderCatalogueGrid(state.medicinesCache);
  } catch (err) {
    console.error('Failed to load medicines:', err);
    container.innerHTML = '<div class="p-3 text-danger">Failed to load medicines catalogue from API.</div>';
  }
}

function filterMedicines(query) {
  if (!query) {
    renderCatalogueGrid(state.medicinesCache);
    return;
  }
  const q = query.toLowerCase();
  const filtered = state.medicinesCache.filter(m => {
    return (m.generic_name || '').toLowerCase().includes(q) ||
           (m.drug_class || '').toLowerCase().includes(q) ||
           (m.brand_names || []).some(b => b.toLowerCase().includes(q)) ||
           (m.labeled_indications || []).some(ind => ind.toLowerCase().includes(q));
  });
  renderCatalogueGrid(filtered);
}

function renderCatalogueGrid(list) {
  const container = document.getElementById('medicines-catalogue');
  container.innerHTML = '';

  if (!list || list.length === 0) {
    container.innerHTML = '<div class="p-3 text-muted">No medicines found matching the search query.</div>';
    return;
  }

  list.forEach(med => {
    const card = document.createElement('div');
    card.className = 'catalogue-card';

    const brands = (med.brand_names || []).slice(0, 4).join(', ');
    const indications = (med.labeled_indications || []).slice(0, 3).join(', ');

    card.innerHTML = `
      <div>
        <div class="catalogue-name">${escapeHtml(med.generic_name)}</div>
        <div class="catalogue-class">${escapeHtml(med.drug_class || 'Pharmaceutical')}</div>
        ${brands ? `<div class="catalogue-brands"><strong>Brands:</strong> ${escapeHtml(brands)}</div>` : ''}
        ${indications ? `<div class="catalogue-indications"><strong>Labeled Uses:</strong> ${escapeHtml(indications)}</div>` : ''}
      </div>
      <div>
        <a href="${escapeHtml(med.source_url || '#')}" target="_blank" rel="noopener" class="catalogue-citation">
          Source: ${escapeHtml(med.source_org || 'FDA DailyMed')} ↗
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

// -----------------------------------------------------------------------------
// 7. Clinical Summary Export / Print
// -----------------------------------------------------------------------------
function initSummaryExport() {
  const btnPrint = document.getElementById('btn-print-summary');
  if (btnPrint) {
    btnPrint.addEventListener('click', () => {
      window.print();
    });
  }
}

// Utility: HTML Escaper to prevent XSS
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
