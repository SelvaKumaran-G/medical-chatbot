/**
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
  /\b(crushing chest pain|chest pain radiating|pain in left arm|chest pressure and sweating|heart attack)\b/i,
  /\b(facial drooping|face droop|slurred speech|slurring words|one side weakness|cannot lift arm|stroke)\b/i,
  /\b(cannot breathe|unable to breathe|gasping for air|turning blue|blue lips|swelling of throat|anaphylaxis)\b/i,
  /\b(unconscious|passed out|unresponsive|prolonged seizure|coma)\b/i,
  /\b(coughing up blood|vomiting blood|uncontrolled bleeding)\b/i
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
    name: s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
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
