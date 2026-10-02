/**
 * FitBuddy AI - Advanced Frontend Client Suite
 */

// Application State
const state = {
  currentPlanId: null,
  currentPlanData: null,
  currentNutritionData: null,
  currentUserData: null,
  checkedExercises: new Set(),
  unitSystem: 'metric', // 'metric' or 'imperial'
  activeDayFilter: 'all',
  timer: {
    interval: null,
    secondsRemaining: 60,
    isRunning: false,
    duration: 60
  }
};

// -----------------------------------------------------------------------------
// Toast Notification Engine
// -----------------------------------------------------------------------------
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  const bgClasses = {
    info: 'bg-slate-900 dark:bg-slate-800 text-white border-slate-700',
    success: 'bg-emerald-600 text-white border-emerald-500',
    error: 'bg-rose-600 text-white border-rose-500',
    warning: 'bg-amber-600 text-white border-amber-500'
  };

  toast.className = `flex items-center gap-2 px-4 py-3 rounded-2xl shadow-xl border text-xs font-semibold transform transition-all duration-300 translate-y-4 opacity-0 ${bgClasses[type] || bgClasses.info}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-4', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// -----------------------------------------------------------------------------
// Theme Engine (Dark / Light Mode)
// -----------------------------------------------------------------------------
const ThemeManager = {
  init() {
    const savedTheme = localStorage.getItem('fitbuddy_theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      this.setTheme('dark');
    } else {
      this.setTheme('light');
    }
  },
  toggle() {
    const isDark = document.documentElement.classList.contains('dark');
    this.setTheme(isDark ? 'light' : 'dark');
  },
  setTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('fitbuddy_theme', 'dark');
      const icon = document.getElementById('themeToggleIcon');
      if (icon) icon.textContent = '☀️';
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('fitbuddy_theme', 'light');
      const icon = document.getElementById('themeToggleIcon');
      if (icon) icon.textContent = '🌙';
    }
  }
};

// -----------------------------------------------------------------------------
// Unit Converter (Metric / Imperial)
// -----------------------------------------------------------------------------
const UnitManager = {
  setSystem(sys) {
    if (state.unitSystem === sys) return;
    state.unitSystem = sys;

    const wInput = document.getElementById('f-weight');
    const hInput = document.getElementById('f-height');
    const wLabel = document.getElementById('weightLabel');
    const hLabel = document.getElementById('heightLabel');

    const btnMetric = document.getElementById('btnMetric');
    const btnImperial = document.getElementById('btnImperial');

    if (sys === 'imperial') {
      btnImperial.classList.add('bg-brand-600', 'text-white');
      btnImperial.classList.remove('text-slate-600', 'dark:text-slate-400');
      btnMetric.classList.remove('bg-brand-600', 'text-white');
      btnMetric.classList.add('text-slate-600', 'dark:text-slate-400');

      wLabel.textContent = 'Weight (lbs)';
      hLabel.textContent = 'Height (inches)';

      // Convert values if present
      if (wInput.value) {
        wInput.value = (parseFloat(wInput.value) * 2.20462).toFixed(1);
      }
      if (hInput.value) {
        hInput.value = (parseFloat(hInput.value) / 2.54).toFixed(1);
      }
      wInput.placeholder = "165";
      hInput.placeholder = "70";
    } else {
      btnMetric.classList.add('bg-brand-600', 'text-white');
      btnMetric.classList.remove('text-slate-600', 'dark:text-slate-400');
      btnImperial.classList.remove('bg-brand-600', 'text-white');
      btnImperial.classList.add('text-slate-600', 'dark:text-slate-400');

      wLabel.textContent = 'Weight (kg)';
      hLabel.textContent = 'Height (cm)';

      if (wInput.value) {
        wInput.value = (parseFloat(wInput.value) / 2.20462).toFixed(1);
      }
      if (hInput.value) {
        hInput.value = (parseFloat(hInput.value) * 2.54).toFixed(1);
      }
      wInput.placeholder = "75";
      hInput.placeholder = "178";
    }
    updateBmiChip();
  },
  getMetricValues() {
    let w = parseFloat(document.getElementById('f-weight').value);
    let h = parseFloat(document.getElementById('f-height').value);

    if (state.unitSystem === 'imperial') {
      w = w / 2.20462;
      h = h * 2.54;
    }
    return {
      weightKg: Math.round(w * 10) / 10,
      heightCm: Math.round(h)
    };
  }
};

// -----------------------------------------------------------------------------
// Interactive Intake Form Helpers
// -----------------------------------------------------------------------------
function updateBmiChip() {
  const { weightKg, heightCm } = UnitManager.getMetricValues();
  const chip = document.getElementById('bmiChip');
  if (!chip) return;

  if (weightKg > 30 && heightCm > 100) {
    const hM = heightCm / 100;
    const bmi = (weightKg / (hM * hM)).toFixed(1);
    let label = 'Normal';
    let color = 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200';

    if (bmi < 18.5) {
      label = 'Underweight';
      color = 'bg-sky-50 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300 border-sky-200';
    } else if (bmi >= 25 && bmi < 30) {
      label = 'Overweight';
      color = 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200';
    } else if (bmi >= 30) {
      label = 'Obese';
      color = 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200';
    }

    chip.textContent = `BMI: ${bmi} (${label})`;
    chip.className = `text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${color}`;
    chip.classList.remove('hidden');
  } else {
    chip.classList.add('hidden');
  }
}

function selectChip(groupClass, activeBtn, inputId, value) {
  document.querySelectorAll('.' + groupClass).forEach(btn => {
    btn.classList.remove('border-brand-600', 'bg-brand-50/70', 'dark:bg-brand-950/40', 'border-2');
    btn.classList.add('border-slate-200', 'dark:border-slate-800', 'border');
  });

  activeBtn.classList.remove('border-slate-200', 'dark:border-slate-800', 'border');
  activeBtn.classList.add('border-brand-600', 'bg-brand-50/70', 'dark:bg-brand-950/40', 'border-2');

  const inputEl = document.getElementById(inputId);
  if (inputEl) inputEl.value = value;
}

function selectSegment(groupClass, activeBtn, inputId, value) {
  document.querySelectorAll('.' + groupClass).forEach(btn => {
    btn.classList.remove('bg-white', 'dark:bg-slate-700', 'text-slate-900', 'dark:text-white', 'shadow-sm');
    btn.classList.add('text-slate-600', 'dark:text-slate-400');
  });

  activeBtn.classList.add('bg-white', 'dark:bg-slate-700', 'text-slate-900', 'dark:text-white', 'shadow-sm');
  activeBtn.classList.remove('text-slate-600', 'dark:text-slate-400');

  const inputEl = document.getElementById(inputId);
  if (inputEl) inputEl.value = value;
}

// -----------------------------------------------------------------------------
// Generation & Plan Rendering
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();

  // Load saved state
  const savedChecks = localStorage.getItem('fitbuddy_checked_exercises');
  if (savedChecks) {
    try {
      state.checkedExercises = new Set(JSON.parse(savedChecks));
    } catch(e) {}
  }

  const savedPlan = localStorage.getItem('fitbuddy_plan');
  const savedPlanId = localStorage.getItem('fitbuddy_plan_id');
  const savedNutri = localStorage.getItem('fitbuddy_nutrition');
  const savedUser = localStorage.getItem('fitbuddy_user');

  // Check if URL has ?load_plan=ID
  const urlParams = new URLSearchParams(window.location.search);
  const loadPlanIdParam = urlParams.get('load_plan');
  if (loadPlanIdParam) {
    loadPlanById(parseInt(loadPlanIdParam));
  } else if (savedPlan && savedPlanId) {
    try {
      state.currentPlanData = JSON.parse(savedPlan);
      state.currentPlanId = parseInt(savedPlanId);
      state.currentNutritionData = savedNutri ? JSON.parse(savedNutri) : null;
      state.currentUserData = savedUser ? JSON.parse(savedUser) : null;

      displayPlanSuite(state.currentPlanData, state.currentNutritionData, state.currentUserData);
      const topBtn = document.getElementById('viewActivePlanBtn');
      if (topBtn) topBtn.classList.remove('hidden');
    } catch(e) {
      console.warn("Storage recovery skipped:", e);
    }
  }

  // Setup form submission
  const form = document.getElementById('generateForm');
  if (form) {
    form.addEventListener('submit', handleGeneratePlan);
  }
});

async function handleGeneratePlan(e) {
  e.preventDefault();

  const { weightKg, heightCm } = UnitManager.getMetricValues();

  const payload = {
    name: document.getElementById('f-name').value.trim(),
    age: parseInt(document.getElementById('f-age').value),
    weight: weightKg,
    height: heightCm,
    gender: document.getElementById('f-gender').value,
    goal: document.getElementById('f-goal').value,
    intensity: document.getElementById('f-intensity').value,
    equipment: document.getElementById('f-equipment').value,
    dietary_preference: document.getElementById('f-dietary').value,
    injuries: document.getElementById('f-injuries').value.trim() || 'None',
    session_duration: parseInt(document.getElementById('f-duration').value || '45'),
    days_per_week: parseInt(document.getElementById('f-days').value || '7')
  };

  setButtonLoading(true, 'Synthesizing 7-Day Protocol...');
  hideError('generateError');

  try {
    const response = await fetch('/api/plans/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to generate plan.');
    }

    // Update State
    state.currentPlanId = data.plan_id;
    state.currentPlanData = data.plan;
    state.currentNutritionData = data.nutrition;
    state.currentUserData = data.user;

    // Cache to LocalStorage
    localStorage.setItem('fitbuddy_plan', JSON.stringify(data.plan));
    localStorage.setItem('fitbuddy_plan_id', data.plan_id);
    if (data.nutrition) localStorage.setItem('fitbuddy_nutrition', JSON.stringify(data.nutrition));
    if (data.user) localStorage.setItem('fitbuddy_user', JSON.stringify(data.user));

    displayPlanSuite(data.plan, data.nutrition, data.user, data.tip);

    showToast('7-Day Routine generated successfully!', 'success');
    const planSec = document.getElementById('planSection');
    planSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const topBtn = document.getElementById('viewActivePlanBtn');
    if (topBtn) topBtn.classList.remove('hidden');

  } catch (err) {
    showError('generateError', err.message);
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(false, 'Generate Personalized Routine ✨');
  }
}

function displayPlanSuite(plan, nutrition, user, tip) {
  // Update Plan Header
  if (state.currentPlanId) {
    const badge = document.getElementById('planBadgeId');
    if (badge) badge.textContent = '#' + state.currentPlanId;
  }

  if (user) {
    const title = document.getElementById('planOwnerTitle');
    if (title) title.textContent = `${user.name}'s 7-Day Performance Blueprint`;

    const summary = document.getElementById('planStatsSummary');
    if (summary) {
      summary.textContent = `Goal: ${user.goal} • Intensity: ${user.intensity.toUpperCase()} • Equipment: ${user.equipment} • Diet: ${user.dietary_preference || 'Balanced'}`;
    }
  }

  // Update Nutrition & Macro Fuel Deck
  if (nutrition) {
    document.getElementById('targetCaloriesVal').textContent = `${nutrition.target_calories} kcal`;
    document.getElementById('targetProteinVal').textContent = `${nutrition.protein_g}g`;
    document.getElementById('targetCarbsVal').textContent = `${nutrition.carbs_g}g`;
    document.getElementById('targetFatVal').textContent = `${nutrition.fat_g}g`;

    if (nutrition.macro_split) {
      document.getElementById('macroBarProtein').style.width = `${nutrition.macro_split.protein_pct}%`;
      document.getElementById('macroBarCarbs').style.width = `${nutrition.macro_split.carbs_pct}%`;
      document.getElementById('macroBarFat').style.width = `${nutrition.macro_split.fat_pct}%`;
      document.getElementById('macroRatioLabels').textContent = `Ratio: ${nutrition.macro_split.protein_pct}% Protein | ${nutrition.macro_split.carbs_pct}% Carbs | ${nutrition.macro_split.fat_pct}% Fat`;
    }

    if (nutrition.hydration_liters) {
      document.getElementById('hydrationTargetVal').textContent = `${nutrition.hydration_liters} L/day`;
    }
    if (nutrition.goal_type) {
      document.getElementById('goalTypeBadge').textContent = nutrition.goal_type;
    }
  }

  if (tip) {
    document.getElementById('nutritionTipText').textContent = tip;
  }

  renderPlanGrid(plan);

  const planSec = document.getElementById('planSection');
  if (planSec) planSec.classList.remove('hidden');
}

function renderPlanGrid(plan) {
  const grid = document.getElementById('planGrid');
  if (!grid) return;
  grid.innerHTML = '';

  let totalExercises = 0;
  let completedExercises = 0;

  for (const [dayKey, dayData] of Object.entries(plan)) {
    const exercises = dayData.exercises || [];
    const isRest = exercises.length === 0 ||
                   dayData.focus.toLowerCase().includes('rest') ||
                   dayData.focus.toLowerCase().includes('recovery');

    let exercisesHtml = '';
    if (isRest && exercises.length === 0) {
      exercisesHtml = `
        <div class="py-8 text-center text-slate-400 dark:text-slate-500 space-y-2">
          <span class="text-3xl block">🧘</span>
          <p class="text-xs font-bold text-slate-700 dark:text-slate-300">Active Rest & Muscle Restoration</p>
          <p class="text-[11px]">Hydrate, perform gentle mobility stretches, and prioritize restorative sleep.</p>
        </div>
      `;
    } else {
      exercisesHtml = exercises.map((ex, idx) => {
        totalExercises++;
        const itemKey = `${state.currentPlanId || 'plan'}_${dayKey}_${idx}`;
        const isChecked = state.checkedExercises.has(itemKey);
        if (isChecked) completedExercises++;

        const youtubeQuery = encodeURIComponent(`how to do ${ex.name} exercise proper form`);
        const restSec = ex.rest_sec || 60;

        return `
          <li class="p-3.5 rounded-2xl border ${isChecked ? 'bg-emerald-50/70 border-emerald-300/80 dark:bg-emerald-950/30 dark:border-emerald-800/50' : 'bg-slate-50/80 border-slate-200/80 dark:bg-slate-800/50 dark:border-slate-700/60'} transition-all space-y-2">
            <div class="flex items-start justify-between gap-3">
              <label class="flex items-start gap-3 cursor-pointer flex-grow select-none">
                <input type="checkbox" onchange="toggleExerciseCheck('${itemKey}', this)" ${isChecked ? 'checked' : ''} class="exercise-checkbox mt-1 h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" />
                <div class="space-y-0.5">
                  <span class="exercise-title text-xs font-bold text-slate-900 dark:text-white leading-snug block">${ex.name}</span>
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="text-[11px] font-bold text-brand-600 dark:text-brand-400">${ex.sets} sets × ${ex.reps}</span>
                    <button type="button" onclick="startTimerFor(${restSec})" class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-200/70 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-brand-50 hover:text-brand-600 transition flex items-center gap-1">
                      ⏱️ ${restSec}s rest
                    </button>
                  </div>
                </div>
              </label>
              <a href="https://www.youtube.com/results?search_query=${youtubeQuery}" target="_blank" rel="noopener noreferrer" title="Watch Form Demo on YouTube" class="no-print p-1.5 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 transition">
                <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
              </a>
            </div>
            ${ex.notes ? `<p class="text-[11px] text-slate-500 dark:text-slate-400 pl-7 leading-tight">${ex.notes}</p>` : ''}
          </li>
        `;
      }).join('');
    }

    grid.innerHTML += `
      <div class="fit-card day-card rounded-3xl p-5 space-y-4 hover:shadow-lg transition-all flex flex-col justify-between" data-day="${dayKey}">
        <div class="space-y-3">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <span class="text-xs font-black uppercase tracking-wider text-brand-600 dark:text-brand-400">${dayKey}</span>
            <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full ${isRest ? 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800' : 'bg-brand-50 dark:bg-brand-950/50 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800'}">
              ${dayData.focus || 'Workout'}
            </span>
          </div>

          ${dayData.warmup ? `
            <div class="text-[11px] text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-xl border border-slate-200/60 dark:border-slate-700/60 flex items-start gap-2">
              <span class="font-extrabold text-brand-600 dark:text-brand-400">Warmup:</span>
              <span>${dayData.warmup}</span>
            </div>
          ` : ''}

          <ul class="space-y-2.5">
            ${exercisesHtml}
          </ul>
        </div>

        ${dayData.cooldown ? `
          <div class="text-[11px] text-slate-400 dark:text-slate-500 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-start gap-1.5">
            <span class="font-bold text-slate-600 dark:text-slate-400">Cooldown:</span>
            <span>${dayData.cooldown}</span>
          </div>
        ` : ''}
      </div>
    `;
  }

  updateWeeklyProgressBar(completedExercises, totalExercises);
  filterDayView(state.activeDayFilter);
}

function toggleExerciseCheck(itemKey, checkbox) {
  if (checkbox.checked) {
    state.checkedExercises.add(itemKey);
  } else {
    state.checkedExercises.delete(itemKey);
  }
  localStorage.setItem('fitbuddy_checked_exercises', JSON.stringify(Array.from(state.checkedExercises)));

  if (state.currentPlanData) {
    renderPlanGrid(state.currentPlanData);
  }
}

function updateWeeklyProgressBar(completed, total) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const bar = document.getElementById('progressBarFill');
  const text = document.getElementById('progressStatusText');
  if (bar) bar.style.width = `${percentage}%`;
  if (text) text.textContent = `${completed} of ${total} exercises completed (${percentage}%)`;

  if (percentage === 100 && total > 0) {
    showToast('🏆 Incredible work! You conquered this 7-day routine!', 'success');
  }
}

function filterDayView(day, tabEl) {
  state.activeDayFilter = day;

  document.querySelectorAll('.day-tab').forEach(t => {
    t.classList.remove('bg-brand-600', 'text-white');
    t.classList.add('bg-white', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
  });

  if (tabEl) {
    tabEl.classList.remove('bg-white', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
    tabEl.classList.add('bg-brand-600', 'text-white');
  }

  document.querySelectorAll('.day-card').forEach(card => {
    if (day === 'all' || card.getAttribute('data-day') === day) {
      card.classList.remove('hidden');
    } else {
      card.classList.add('hidden');
    }
  });
}

// -----------------------------------------------------------------------------
// AI Routine Refiner
// -----------------------------------------------------------------------------
function setQuickRefine(text) {
  const input = document.getElementById('feedbackInput');
  if (input) {
    input.value = text;
    input.focus();
  }
}

async function refinePlan() {
  const input = document.getElementById('feedbackInput');
  const feedback = input ? input.value.trim() : '';

  if (!feedback) {
    showError('refineError', 'Please describe the tweak you want to make.');
    return;
  }
  if (!state.currentPlanId) {
    showError('refineError', 'No active plan loaded to tweak.');
    return;
  }

  setRefineLoading(true);
  hideError('refineError');

  try {
    const res = await fetch('/api/plans/refine', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan_id: state.currentPlanId,
        feedback: feedback
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Could not update plan.');

    state.currentPlanData = data.plan;
    localStorage.setItem('fitbuddy_plan', JSON.stringify(data.plan));

    renderPlanGrid(data.plan);
    input.value = '';
    showToast('Plan adjusted by Gemini 2.0 Flash!', 'success');

    const grid = document.getElementById('planGrid');
    if (grid) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch(err) {
    showError('refineError', err.message);
    showToast(err.message, 'error');
  } finally {
    setRefineLoading(false);
  }
}

// -----------------------------------------------------------------------------
// Synthesized Acoustic Stopwatch Chime & Timer
// -----------------------------------------------------------------------------
function playSynthesizedChime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(880, ctx.currentTime); // A5 note
    osc.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.3);

    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.7);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.7);
  } catch(e) {
    console.warn("Audio chime prevented:", e);
  }
}

function formatTimerDigits(sec) {
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = (sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function setRestTime(seconds) {
  clearInterval(state.timer.interval);
  state.timer.isRunning = false;
  state.timer.secondsRemaining = seconds;
  state.timer.duration = seconds;

  const display = document.getElementById('timerDisplay');
  if (display) display.textContent = formatTimerDigits(seconds);

  const btn = document.getElementById('timerToggleBtn');
  if (btn) {
    btn.textContent = 'Start';
    btn.classList.remove('bg-emerald-600');
    btn.classList.add('bg-slate-900', 'dark:bg-brand-600');
  }
}

function startTimerFor(seconds) {
  setRestTime(seconds);
  toggleTimer();
  const widget = document.getElementById('restTimerWidget');
  if (widget) widget.scrollIntoView({ behavior: 'smooth', block: 'center' });
  showToast(`Rest timer set for ${seconds}s`, 'info');
}

function toggleTimer() {
  const btn = document.getElementById('timerToggleBtn');

  if (state.timer.isRunning) {
    clearInterval(state.timer.interval);
    state.timer.isRunning = false;
    if (btn) btn.textContent = 'Resume';
  } else {
    state.timer.isRunning = true;
    if (btn) btn.textContent = 'Pause';

    state.timer.interval = setInterval(() => {
      if (state.timer.secondsRemaining > 0) {
        state.timer.secondsRemaining--;
        const display = document.getElementById('timerDisplay');
        if (display) display.textContent = formatTimerDigits(state.timer.secondsRemaining);
      } else {
        clearInterval(state.timer.interval);
        state.timer.isRunning = false;
        playSynthesizedChime();

        const display = document.getElementById('timerDisplay');
        if (display) display.textContent = "00:00";
        if (btn) {
          btn.textContent = 'Set Finished!';
          btn.classList.add('bg-emerald-600');
        }
        showToast('Rest interval complete! Time for the next set.', 'success');
      }
    }, 1000);
  }
}

function resetTimer() {
  setRestTime(60);
}

// -----------------------------------------------------------------------------
// Export Routines (.ics Calendar, JSON, Clipboard)
// -----------------------------------------------------------------------------
function downloadCalendar() {
  if (!state.currentPlanId) {
    showToast('Please generate a plan before exporting to Calendar.', 'warning');
    return;
  }
  window.location.href = `/api/export/${state.currentPlanId}/calendar`;
  showToast('Downloading iCalendar (.ics) schedule...', 'info');
}

function downloadJson() {
  if (!state.currentPlanId) {
    showToast('Please generate a plan before exporting JSON.', 'warning');
    return;
  }
  window.location.href = `/api/export/${state.currentPlanId}/json`;
  showToast('Downloading plan JSON file...', 'info');
}

function copyPlanToClipboard() {
  if (!state.currentPlanData) {
    showToast('No active routine to copy.', 'warning');
    return;
  }

  let text = "🏋️ FITBUDDY 7-DAY WORKOUT SCHEDULE\n=================================\n\n";
  for (const [day, d] of Object.entries(state.currentPlanData)) {
    text += `[${day} - ${d.focus}]\n`;
    if (d.warmup) text += `Warmup: ${d.warmup}\n`;
    (d.exercises || []).forEach(ex => {
      text += ` • ${ex.name}: ${ex.sets} sets x ${ex.reps}${ex.notes ? ' (' + ex.notes + ')' : ''} [Rest: ${ex.rest_sec || 60}s]\n`;
    });
    if (d.cooldown) text += `Cooldown: ${d.cooldown}\n`;
    text += "\n";
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast('Workout schedule copied to clipboard!', 'success');
  }).catch(() => {
    alert("Could not copy. Please use print or download options.");
  });
}

// -----------------------------------------------------------------------------
// History Drawer Engine
// -----------------------------------------------------------------------------
async function openHistoryDrawer() {
  const drawer = document.getElementById('historyDrawer');
  const list = document.getElementById('historyList');
  if (!drawer || !list) return;

  drawer.classList.remove('hidden');
  list.innerHTML = `
    <div class="py-12 text-center text-slate-400">
      <svg class="animate-spin h-6 w-6 mx-auto mb-2 text-brand-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Loading saved routines...
    </div>
  `;

  try {
    const res = await fetch('/api/plans?limit=25');
    const plans = await res.json();

    if (!plans || plans.length === 0) {
      list.innerHTML = `
        <div class="py-12 text-center text-slate-400 space-y-2">
          <span class="text-3xl block">📋</span>
          <p class="text-sm font-bold text-slate-600 dark:text-slate-300">No saved routines yet</p>
          <p class="text-xs">Create your first 7-day routine above!</p>
        </div>
      `;
      return;
    }

    list.innerHTML = plans.map(p => `
      <div class="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800/80 shadow-sm hover:border-brand-500 transition-all flex items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-slate-900 dark:text-white">${p.user_name}</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-300">#${p.id}</span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400">${p.user_goal} • ${p.equipment}</p>
          <div class="text-[10px] text-slate-400">${new Date(p.created_at).toLocaleDateString()}</div>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="loadPlanById(${p.id})" class="px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold transition shadow-sm">
            Load
          </button>
          <button onclick="deletePlanById(${p.id}, this)" class="p-1.5 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition">
            ✕
          </button>
        </div>
      </div>
    `).join('');

  } catch(e) {
    list.innerHTML = `<div class="p-4 text-xs text-rose-500">Failed to load history: ${e.message}</div>`;
  }
}

function closeHistoryDrawer() {
  const drawer = document.getElementById('historyDrawer');
  if (drawer) drawer.classList.add('hidden');
}

async function loadPlanById(planId) {
  try {
    showToast(`Loading routine #${planId}...`, 'info');
    const res = await fetch(`/api/plans/${planId}`);
    if (!res.ok) throw new Error('Routine not found.');
    const data = await res.json();

    state.currentPlanId = data.plan_id;
    state.currentPlanData = data.plan;
    state.currentNutritionData = data.nutrition;
    state.currentUserData = data.user;

    localStorage.setItem('fitbuddy_plan', JSON.stringify(data.plan));
    localStorage.setItem('fitbuddy_plan_id', data.plan_id);
    if (data.nutrition) localStorage.setItem('fitbuddy_nutrition', JSON.stringify(data.nutrition));
    if (data.user) localStorage.setItem('fitbuddy_user', JSON.stringify(data.user));

    displayPlanSuite(data.plan, data.nutrition, data.user, data.tip);
    closeHistoryDrawer();

    const planSec = document.getElementById('planSection');
    if (planSec) planSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast(`Routine #${planId} loaded!`, 'success');

  } catch(err) {
    showToast(err.message, 'error');
  }
}

async function deletePlanById(planId, btnEl) {
  if (!confirm(`Are you sure you want to delete routine #${planId}?`)) return;

  try {
    const res = await fetch(`/api/plans/${planId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Could not delete plan');

    if (state.currentPlanId === planId) {
      localStorage.removeItem('fitbuddy_plan');
      localStorage.removeItem('fitbuddy_plan_id');
      state.currentPlanId = null;
      state.currentPlanData = null;
    }

    const parentCard = btnEl.closest('.p-4');
    if (parentCard) parentCard.remove();
    showToast(`Routine #${planId} deleted`, 'info');

  } catch(e) {
    showToast(e.message, 'error');
  }
}

// -----------------------------------------------------------------------------
// UI Utilities
// -----------------------------------------------------------------------------
function setButtonLoading(loading, text) {
  const btn = document.getElementById('generateBtn');
  const btnText = document.getElementById('generateBtnText');
  const spinner = document.getElementById('generateSpinner');

  if (btn) btn.disabled = loading;
  if (btnText) btnText.textContent = text;
  if (spinner) spinner.classList.toggle('hidden', !loading);
}

function setRefineLoading(loading) {
  const btn = document.getElementById('refineBtn');
  const btnText = document.getElementById('refineBtnText');
  const spinner = document.getElementById('refineSpinner');

  if (btn) btn.disabled = loading;
  if (btnText) btnText.textContent = loading ? 'Fine-Tuning...' : 'Apply Adjustments';
  if (spinner) spinner.classList.toggle('hidden', !loading);
}

function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = msg;
    el.classList.remove('hidden');
  }
}

function hideError(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

function scrollToActivePlan() {
  const planSec = document.getElementById('planSection');
  if (planSec) planSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function scrollToRefine() {
  const refine = document.getElementById('refineSection');
  if (refine) {
    refine.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const input = document.getElementById('feedbackInput');
    if (input) input.focus();
  }
}

function resetPlanner() {
  const intake = document.getElementById('intakeSection');
  if (intake) {
    intake.scrollIntoView({ behavior: 'smooth', block: 'start' });
    const nameInput = document.getElementById('f-name');
    if (nameInput) nameInput.focus();
  }
}

// -----------------------------------------------------------------------------
// Interactive BMI & Body Composition Calculator Engine
// -----------------------------------------------------------------------------
const BmiCalculator = {
  unit: 'metric', // 'metric' or 'imperial'
  heightCm: 175,
  weightKg: 72,
  age: 26,
  gender: 'other',

  openModal() {
    const modal = document.getElementById('bmiModal');
    if (!modal) return;
    
    // Sync current values from intake form if available
    const formW = parseFloat(document.getElementById('f-weight')?.value);
    const formH = parseFloat(document.getElementById('f-height')?.value);
    const formAge = parseInt(document.getElementById('f-age')?.value);
    const formGen = document.getElementById('f-gender')?.value;

    if (formW && formW > 30) this.weightKg = formW;
    if (formH && formH > 100) this.heightCm = formH;
    if (formAge && formAge > 12) this.age = formAge;
    if (formGen) this.gender = formGen;

    this.render();
    modal.classList.remove('hidden');
  },

  closeModal() {
    const modal = document.getElementById('bmiModal');
    if (modal) modal.classList.add('hidden');
  },

  setUnit(u) {
    if (this.unit === u) return;
    this.unit = u;

    const btnM = document.getElementById('bmiUnitMetric');
    const btnI = document.getElementById('bmiUnitImperial');
    const hLabel = document.getElementById('bmiHeightLabel');
    const wLabel = document.getElementById('bmiWeightLabel');

    if (u === 'imperial') {
      btnI?.classList.add('bg-brand-600', 'text-white', 'shadow-sm');
      btnI?.classList.remove('text-slate-600', 'dark:text-slate-400');
      btnM?.classList.remove('bg-brand-600', 'text-white', 'shadow-sm');
      btnM?.classList.add('text-slate-600', 'dark:text-slate-400');

      if (hLabel) hLabel.textContent = 'Height (inches)';
      if (wLabel) wLabel.textContent = 'Weight (lbs)';
    } else {
      btnM?.classList.add('bg-brand-600', 'text-white', 'shadow-sm');
      btnM?.classList.remove('text-slate-600', 'dark:text-slate-400');
      btnI?.classList.remove('bg-brand-600', 'text-white', 'shadow-sm');
      btnI?.classList.add('text-slate-600', 'dark:text-slate-400');

      if (hLabel) hLabel.textContent = 'Height (cm)';
      if (wLabel) wLabel.textContent = 'Weight (kg)';
    }
    this.render();
  },

  onHeightChange(val) {
    let h = parseFloat(val);
    this.heightCm = this.unit === 'imperial' ? h * 2.54 : h;
    this.render();
  },

  onWeightChange(val) {
    let w = parseFloat(val);
    this.weightKg = this.unit === 'imperial' ? w / 2.20462 : w;
    this.render();
  },

  onAgeChange(val) {
    this.age = parseInt(val) || 25;
    this.render();
  },

  onSexChange(val) {
    this.gender = val;
    this.render();
  },

  render() {
    const hM = this.heightCm / 100;
    const bmi = (this.weightKg / (hM * hM)).toFixed(1);

    // Update displays
    const hDisp = document.getElementById('bmiHeightDisplay');
    const wDisp = document.getElementById('bmiWeightDisplay');
    const aDisp = document.getElementById('bmiAgeDisplay');
    const hSlider = document.getElementById('bmiHeightSlider');
    const wSlider = document.getElementById('bmiWeightSlider');
    const aSlider = document.getElementById('bmiAgeSlider');
    const sexSelect = document.getElementById('bmiSexSelect');

    if (this.unit === 'imperial') {
      const hInches = Math.round(this.heightCm / 2.54);
      const wLbs = Math.round(this.weightKg * 2.20462 * 10) / 10;
      if (hDisp) hDisp.textContent = `${hInches} in`;
      if (wDisp) wDisp.textContent = `${wLbs} lbs`;
      if (hSlider) { hSlider.min = "48"; hSlider.max = "90"; hSlider.value = hInches; }
      if (wSlider) { wSlider.min = "80"; wSlider.max = "390"; wSlider.value = wLbs; }
    } else {
      if (hDisp) hDisp.textContent = `${Math.round(this.heightCm)} cm`;
      if (wDisp) wDisp.textContent = `${Math.round(this.weightKg * 10) / 10} kg`;
      if (hSlider) { hSlider.min = "120"; hSlider.max = "230"; hSlider.value = Math.round(this.heightCm); }
      if (wSlider) { wSlider.min = "35"; wSlider.max = "180"; wSlider.value = Math.round(this.weightKg * 10) / 10; }
    }

    if (aDisp) aDisp.textContent = `${this.age} yrs`;
    if (aSlider) aSlider.value = this.age;
    if (sexSelect) sexSelect.value = this.gender;

    // Body fat formula (Deurenberg)
    const sexFactor = this.gender === 'male' ? 1.0 : (this.gender === 'female' ? 0.0 : 0.5);
    let bodyFat = (1.20 * parseFloat(bmi)) + (0.23 * this.age) - (10.8 * sexFactor) - 5.4;
    bodyFat = Math.max(5.0, Math.min(bodyFat, 55.0)).toFixed(1);

    // Healthy weight window (BMI 18.5 - 24.9)
    const minW = (18.5 * (hM * hM)).toFixed(1);
    const maxW = (24.9 * (hM * hM)).toFixed(1);

    let category = "Normal Weight";
    let badgeClass = "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800";
    let deltaText = "In optimal range (0 kg)";
    let deltaClass = "text-emerald-600 dark:text-emerald-400";
    let advice = "Optimal healthy range. Maintain your current weight with progressive strength training and conditioning.";

    if (parseFloat(bmi) < 18.5) {
      category = "Underweight";
      badgeClass = "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300 border-sky-300 dark:border-sky-800";
      const diff = (minW - this.weightKg).toFixed(1);
      deltaText = `Need +${diff} kg for optimal zone`;
      deltaClass = "text-sky-600 dark:text-sky-400";
      advice = `Your BMI is below standard. A caloric surplus focused on whole proteins and progressive resistance training will help build healthy muscle mass.`;
    } else if (parseFloat(bmi) >= 25.0 && parseFloat(bmi) < 30.0) {
      category = "Overweight";
      badgeClass = "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800";
      const diff = (this.weightKg - maxW).toFixed(1);
      deltaText = `Exceeds by +${diff} kg`;
      deltaClass = "text-amber-600 dark:text-amber-400";
      advice = `Your BMI indicates surplus body mass. A gentle caloric deficit (350-500 kcal) with daily cardio & resistance training will optimize your health markers.`;
    } else if (parseFloat(bmi) >= 30.0) {
      category = "Obesity Range";
      badgeClass = "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-300 dark:border-rose-800";
      const diff = (this.weightKg - maxW).toFixed(1);
      deltaText = `Exceeds by +${diff} kg`;
      deltaClass = "text-rose-600 dark:text-rose-400";
      advice = `Your BMI is in the elevated obesity tier. Prioritize low-impact aerobic conditioning, joint protection, and structured deficit nutrition.`;
    }

    // Update DOM results
    const scoreVal = document.getElementById('bmiScoreVal');
    const badge = document.getElementById('bmiCategoryBadge');
    const fatVal = document.getElementById('bmiBodyFatVal');
    const rangeVal = document.getElementById('bmiHealthyRangeVal');
    const deltaVal = document.getElementById('bmiDeltaVal');
    const adviceText = document.getElementById('bmiAdviceText');

    if (scoreVal) scoreVal.textContent = bmi;
    if (badge) {
      badge.textContent = category;
      badge.className = `text-xs font-extrabold px-3 py-1 rounded-full border ${badgeClass}`;
    }
    if (fatVal) fatVal.textContent = `${bodyFat}%`;
    if (rangeVal) {
      if (this.unit === 'imperial') {
        const minLbs = Math.round(minW * 2.20462);
        const maxLbs = Math.round(maxW * 2.20462);
        rangeVal.textContent = `${minLbs} lbs – ${maxLbs} lbs`;
      } else {
        rangeVal.textContent = `${minW} kg – ${maxW} kg`;
      }
    }
    if (deltaVal) {
      deltaVal.textContent = deltaText;
      deltaVal.className = `font-extrabold ${deltaClass}`;
    }
    if (adviceText) adviceText.textContent = advice;
  },

  applyToPlanner() {
    const wInput = document.getElementById('f-weight');
    const hInput = document.getElementById('f-height');
    const aInput = document.getElementById('f-age');
    const gSelect = document.getElementById('f-gender');

    if (wInput) wInput.value = Math.round(this.weightKg * 10) / 10;
    if (hInput) hInput.value = Math.round(this.heightCm);
    if (aInput) aInput.value = this.age;
    if (gSelect) gSelect.value = this.gender;

    // Auto-align recommended goal based on BMI
    const hM = this.heightCm / 100;
    const bmi = parseFloat((this.weightKg / (hM * hM)).toFixed(1));

    if (bmi >= 25.0) {
      // Recommend Fat Loss
      const fatLossBtn = document.querySelector('[onclick*="Fat Loss"]');
      if (fatLossBtn) selectChip('goal-chip', fatLossBtn, 'f-goal', 'Fat Loss & Lean Shred');
    } else if (bmi < 20.0) {
      // Recommend Muscle Gain
      const muscleBtn = document.querySelector('[onclick*="Muscle Hypertrophy"]');
      if (muscleBtn) selectChip('goal-chip', muscleBtn, 'f-goal', 'Muscle Hypertrophy & Bulk');
    }

    updateBmiChip();
    this.closeModal();

    const intake = document.getElementById('intakeSection');
    if (intake) intake.scrollIntoView({ behavior: 'smooth', block: 'start' });

    showToast(`Stats loaded! BMI: ${bmi} applied to Workout Planner.`, 'success');
  }
};
