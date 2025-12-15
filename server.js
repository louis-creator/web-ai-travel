const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
require('dotenv').config();

const app = express();
const PORT = 3000;

app.use(express.static('public'));
app.use(bodyParser.json());

/* ===================== API KEY POOL ===================== */

const COOLDOWN_MS = 15 * 60 * 1000; // 15 phút
const MAX_RETRY = 4;

class ApiKeyPool {
  constructor(keys) {
    this.keys = keys.map(k => ({
      key: k,
      cooldownUntil: 0
    }));
    this.pointer = 0;
  }

  getAvailableKey() {
    const now = Date.now();
    const n = this.keys.length;

    for (let i = 0; i < n; i++) {
      const idx = (this.pointer + i) % n;
      const slot = this.keys[idx];

      if (slot.cooldownUntil <= now) {
        this.pointer = (idx + 1) % n; // round-robin
        return slot;
      }
    }
    return null;
  }

  markCooldown(slot) {
    slot.cooldownUntil = Date.now() + COOLDOWN_MS;
  }
}

function isQuotaError(text = '') {
  const t = text.toUpperCase();
  return (
    t.includes('429') ||
    t.includes('QUOTA') ||
    t.includes('RATE') ||
    t.includes('RESOURCE_EXHAUSTED') ||
    t.includes('TOO MANY REQUESTS')
  );
}

const keys = (process.env.GEMINI_API_KEYS || '')
  .split(',')
  .map(k => k.trim())
  .filter(Boolean);

const keyPool = new ApiKeyPool(keys);

/* ===================== AI1 ===================== */

app.post('/api/recommend', (req, res) => {
  const { tags, budget } = req.body;
  const tagsString = (tags || []).join(',');

  const py = spawn('python', ['ai1.py', tagsString, budget]);
  let out = '';

  py.stdout.on('data', d => out += d.toString());
  py.stderr.on('data', d => console.error(`AI1 Error: ${d}`));

  py.on('close', () => {
    try {
      res.json({ success: true, data: JSON.parse(out) });
    } catch {
      res.json({ success: false, error: 'AI1 failed' });
    }
  });
});

/* ===================== AI2 (ROTATE KEY) ===================== */

function runAi2Once({ startTime, endTime, priorityString, apiKey }) {
  return new Promise(resolve => {
    const py = spawn(
      'python',
      ['ai2.py', startTime, endTime, priorityString],
      { env: { ...process.env, GEMINI_API_KEY: apiKey } }
    );

    let out = '';
    let err = '';

    py.stdout.on('data', d => out += d.toString());
    py.stderr.on('data', d => err += d.toString());

    py.on('close', () => {
      let parsed = null;
      try { parsed = JSON.parse(out); } catch {}
      resolve({ parsed, out, err });
    });
  });
}

app.post('/api/plan', async (req, res) => {
  const { startTime, endTime, priorityLocations } = req.body;
  const priorityString = (priorityLocations || []).join('|');

  if (!keys.length) {
    return res.json({ success: false, error: 'No Gemini API keys configured' });
  }

  for (let attempt = 1; attempt <= MAX_RETRY; attempt++) {
    const slot = keyPool.getAvailableKey();

    if (!slot) {
      return res.json({
        success: false,
        error: 'All API keys are cooling down. Try again later.'
      });
    }

    const r = await runAi2Once({
      startTime,
      endTime,
      priorityString,
      apiKey: slot.key
    });

    if (r.parsed && !r.parsed.error) {
      return res.json({ success: true, data: r.parsed });
    }

    const errText = r.parsed?.error || r.err || r.out || '';

    if (isQuotaError(errText)) {
      console.warn('Quota hit → cooldown key');
      keyPool.markCooldown(slot);
      continue;
    }

    return res.json({ success: false, error: errText || 'Gemini error' });
  }

  res.json({
    success: false,
    error: 'AI2 failed after retries (quota)'
  });
});

/* ===================== START ===================== */

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
