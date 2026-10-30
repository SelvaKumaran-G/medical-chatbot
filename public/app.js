/**
 * Dr. MediGuide AI — Client Application Script
 * Streamlit Parity: Left Sidebar Patient Clinical Profile + Interactive Clinical Chatbot.
 */

// Global State
const state = {
  theme: localStorage.getItem('mediguide_theme') || 'light',
  patientProfile: JSON.parse(localStorage.getItem('mediguide_profile') || JSON.stringify({
    name: 'Patient',
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
  /\b(crushing chest pain|chest pain radiating|pain in left arm|chest pressure and sweating|heart attack)\b/i,
  /\b(facial drooping|face droop|slurred speech|slurring words|one side weakness|cannot lift arm|stroke)\b/i,
  /\b(cannot breathe|unable to breathe|gasping for air|turning blue|blue lips|swelling of throat|anaphylaxis)\b/i,
  /\b(unconscious|passed out|unresponsive|prolonged seizure|coma)\b/i,
  /\b(coughing up blood|vomiting blood|uncontrolled bleeding)\b/i
];

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebarProfile();
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

  // Sidebar toggle for mobile
  const sidebarBtn = document.getElementById('btn-sidebar-toggle');
  const sidebar = document.getElementById('app-sidebar');
  if (sidebarBtn && sidebar) {
    sidebarBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
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
  // Append user message bubble
  appendUserMessage(text);

  // Append typing indicator bubble
  const typingBubbleId = appendTypingIndicator();

  try {
    const payload = {
      text: text,
      patient_profile: state.patientProfile
    };

    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    removeTypingIndicator(typingBubbleId);
    appendAssistantResponse(data);
  } catch (err) {
    console.error('API Error:', err);
    removeTypingIndicator(typingBubbleId);
    appendAssistantErrorBubble('Could not complete analysis right now. Please ensure the local server is running.');
  }
}

function appendUserMessage(text) {
  const stream = document.getElementById('chat-stream');
  if (!stream) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = 'chat-message user';
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  msgDiv.innerHTML = `
    <div class="chat-avatar-col">
      <div class="chat-avatar-placeholder">🧑‍💼</div>
    </div>
    <div class="chat-bubble">
      <div class="chat-bubble-header">
        <span class="chat-sender-name">You</span>
        <span class="chat-time-tag">${timeStr}</span>
      </div>
      <p style="margin:0;font-size:0.96rem;">${escapeHtml(text)}</p>
    </div>
  `;

  stream.appendChild(msgDiv);
  msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
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
      <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\'chat-avatar-placeholder\'>👨‍⚕️</div>'">
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
      <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\'chat-avatar-placeholder\'>👨‍⚕️</div>'">
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
      <img src="assets/doctor_avatar.png" class="chat-avatar-img" alt="Dr. MediGuide AI" onerror="this.outerHTML='<div class=\'chat-avatar-placeholder\'>👨‍⚕️</div>'">
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
  msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
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
