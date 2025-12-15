/*************************
 * GLOBAL STATE
 *************************/
let ai1Results = [];          // full AI1 results
let ai1SelectedNames = [];    // user-selected names
let ai2PriorityList = [];     // final list for AI2

/*************************
 * UI HELPERS
 *************************/
function setAI2Enabled(enabled) {
    const btn = document.getElementById('btnAI2');
    if (btn) btn.disabled = !enabled;
}

function updateSelectedUI() {
    const countEl = document.getElementById('selectedCount');
    const btnUse = document.getElementById('btnUseSelected');

    if (countEl) countEl.textContent = `Selected: ${ai1SelectedNames.length}`;
    if (btnUse) btnUse.disabled = false; // luôn cho bấm
}

/*************************
 * INPUT VALIDATION
 *************************/
function parseBudgetOrDefault(value, def = 500000) {
    const n = Number(String(value || '').trim());
    if (!Number.isFinite(n) || n <= 0) return def;
    return Math.round(n);
}

function timeToMinutes(t) {
    if (!t || !/^\d{2}:\d{2}$/.test(t)) return null;
    const [h, m] = t.split(':').map(Number);
    return h * 60 + m;
}

function validateOrDefaultTime(startRaw, endRaw) {
    const start = startRaw?.trim() || '08:00';
    const end = endRaw?.trim() || '17:00';

    const s = timeToMinutes(start);
    const e = timeToMinutes(end);

    if (s === null || e === null) {
        return { ok: false, msg: 'Invalid time format (HH:MM).' };
    }
    if (e <= s) {
        return { ok: false, msg: 'End time must be after start time.' };
    }
    if (e - s < 120) {
        return { ok: false, msg: 'Trip duration must be at least 2 hours.' };
    }
    return { ok: true, start, end };
}

/*************************
 * AI1
 *************************/
async function runAI1() {
    ai1Results = [];
    ai1SelectedNames = [];
    ai2PriorityList = [];
    setAI2Enabled(false);
    updateSelectedUI();

    const budgetInput = document.getElementById('budgetInput');
    const budget = parseBudgetOrDefault(budgetInput.value);
    budgetInput.value = budget;

    const checked = document.querySelectorAll('input[type="checkbox"]:checked');
    const tags = Array.from(checked).map(cb => cb.value);

    if (tags.length === 0) {
        alert('Please select at least one interest.');
        return;
    }

    const container = document.getElementById('ai1-result');
    container.innerHTML = '<p>Loading AI1...</p>';

    try {
        const res = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tags, budget })
        });
        const json = await res.json();

        if (!json.success) {
            container.innerHTML = '<p style="color:red">AI1 failed.</p>';
            return;
        }

        ai1Results = json.data || [];
        renderCardsSelectable(ai1Results, container);
        updateSelectedUI();

    } catch {
        container.innerHTML = '<p style="color:red">Connection error.</p>';
    }
}

/*************************
 * AI1 RENDER (SELECTABLE)
 *************************/
function renderCardsSelectable(data, container) {
    if (!data.length) {
        container.innerHTML = '<p>No places found.</p>';
        return;
    }

    let html = '';
    data.forEach((item, i) => {
        const price = new Intl.NumberFormat('vi-VN', {
            style: 'currency', currency: 'VND'
        }).format(item.price);

        html += `
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="place-title">${i + 1}. ${item.name}</div>
                <input type="checkbox"
                    data-name="${encodeURIComponent(item.name)}"
                    onchange="onPickChanged(this)">
            </div>
            <div class="info">${price}</div>
            <div class="info">${item.opening_hours}</div>
            <div class="info">${item.address}</div>
            <a href="${item.map_link}" target="_blank">Map</a>
        </div>`;
    });

    container.innerHTML = html;
}

/*************************
 * SELECTION HANDLERS
 *************************/
window.onPickChanged = function (cb) {
    const name = decodeURIComponent(cb.dataset.name || '');
    if (!name) return;

    if (cb.checked) {
        if (!ai1SelectedNames.includes(name)) ai1SelectedNames.push(name);
    } else {
        ai1SelectedNames = ai1SelectedNames.filter(n => n !== name);
    }
    updateSelectedUI();
};

window.useSelectedForAI2 = function () {
    // Nếu không chọn gì → dùng ALL AI1
    if (ai1SelectedNames.length === 0) {
        ai2PriorityList = ai1Results.map(p => p.name);
        alert(`No selection detected. Using all ${ai2PriorityList.length} places for AI2.`);
    } else {
        ai2PriorityList = [...ai1SelectedNames];
        alert(`Selected ${ai2PriorityList.length} place(s) for AI2.`);
    }
    setAI2Enabled(true);
};

/*************************
 * AI2
 *************************/
async function runAI2() {
    const container = document.getElementById('ai2-result');

    // Fallback an toàn: chưa xác nhận chọn → dùng ALL AI1
    if (!ai2PriorityList.length && ai1Results.length > 0) {
        ai2PriorityList = ai1Results.map(p => p.name);
    }

    if (!ai2PriorityList.length) {
        container.innerHTML = '<p style="color:red">Please run AI1 first.</p>';
        return;
    }

    const startEl = document.getElementById('startTime');
    const endEl = document.getElementById('endTime');

    const check = validateOrDefaultTime(startEl.value, endEl.value);
    if (!check.ok) {
        alert(check.msg);
        startEl.value = '08:00';
        endEl.value = '17:00';
        return;
    }

    startEl.value = check.start;
    endEl.value = check.end;

    container.innerHTML = '<p>Planning itinerary...</p>';

    try {
        const res = await fetch('/api/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                startTime: check.start,
                endTime: check.end,
                priorityLocations: ai2PriorityList
            })
        });

        const json = await res.json();
        if (!json.success) {
            container.innerHTML = `<p style="color:red">${json.error}</p>`;
            return;
        }

        renderTimeline(json.data, container);

    } catch {
        container.innerHTML = '<p style="color:red">Connection error.</p>';
    }
}

/*************************
 * AI2 RENDER
 *************************/
function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderTimeline(data, container) {
  if (!data || !Array.isArray(data.timeline) || data.timeline.length === 0) {
    container.innerHTML = '<p>No itinerary generated.</p>';
    return;
  }

  let html = '';

  // Note (nếu AI trả về)
  if (data.note) {
    html += `
      <div class="ai2-note">
        <i class="fas fa-lightbulb"></i>
        <span>${escapeHtml(data.note)}</span>
      </div>
    `;
  }

  html += `<div class="timeline-wrapper">`;

  data.timeline.forEach((item) => {
    const icon = item.icon || "visit"; // visit | move | food
    const cls = icon === "move" ? "timeline-move" : (icon === "food" ? "timeline-food" : "timeline-visit");
    const fa = icon === "move" ? "fa-route" : (icon === "food" ? "fa-utensils" : "fa-map-marker-alt");

    html += `
      <div class="timeline-item ${cls}">
        <div class="time-col">${escapeHtml(item.time || "")}</div>

        <div class="marker-col">
          <div class="marker"><i class="fas ${fa}"></i></div>
          <div class="line"></div>
        </div>

        <div class="content-col">
          <div class="activity-title">${escapeHtml(item.activity || "")}</div>
          ${item.detail ? `<div class="activity-note">${escapeHtml(item.detail)}</div>` : ""}
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}
