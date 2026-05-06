/**
 * ArmaraOS Pump.fun Chat Controller
 * 
 * Listens to pump.fun chat for "probe bot <prompt>" commands
 * and routes them to ArmaraOS at localhost:4200.
 * 
 * Usage: node bot.js
 */

const WebSocket = require('ws');

// ─── CONFIG ────────────────────────────────────────────────────────────────────
const CONTRACT = '56hrCR3n7danhHNjWaU4VeUHpE1eRE9VRBWpHRPKpump';
const ARMARAOS_URL = 'http://localhost:4200';
const COMMAND_PREFIX = 'probe bot';

// How many seconds a user must wait before sending another command
const COOLDOWN_SECONDS = 15;

// Max prompt length (chars) to prevent abuse
const MAX_PROMPT_LENGTH = 300;

// Blocked keywords — any prompt containing these is rejected
const BLOCKLIST = [
  'buy', 'sell', 'send', 'transfer', 'wallet', 'withdraw', 'deposit',
  'private key', 'seed phrase', 'mnemonic', 'sign transaction',
  'solana', 'sol', 'lamport', 'pump.fun', 'swap', 'bridge',
  'rm -rf', 'del /f', 'format', 'shutdown', 'reboot',
  'password', 'api key', 'secret', 'token', '.env',
];

// ─── STATE ─────────────────────────────────────────────────────────────────────
const cooldowns = new Map(); // username → last command timestamp
let armaraAgentId = null;    // cached agent ID from ArmaraOS
let queueDepth = 0;
const MAX_QUEUE_DEPTH = 3;   // ignore commands if too many are in flight

// ─── OVERLAY ───────────────────────────────────────────────────────────────────
// Writes current status to overlay.json — read by the OBS browser source (overlay.html)
const fs = require('fs');
function updateOverlay(data) {
  try {
    fs.writeFileSync('overlay.json', JSON.stringify({ ...data, ts: Date.now() }, null, 2));
  } catch (_) {}
}

// ─── BLOCKLIST CHECK ───────────────────────────────────────────────────────────
function isBlocked(prompt) {
  const lower = prompt.toLowerCase();
  return BLOCKLIST.some(word => lower.includes(word));
}

// ─── ARMARAOS API ──────────────────────────────────────────────────────────────
async function getOrCreateAgent() {
  if (armaraAgentId) return armaraAgentId;

  try {
    // Try listing agents first
    const listRes = await fetch(`${ARMARAOS_URL}/api/agents`);
    if (listRes.ok) {
      const agents = await listRes.json();
      const list = Array.isArray(agents) ? agents : (agents.agents || agents.data || []);
      if (list.length > 0) {
        armaraAgentId = list[0].id;
        console.log(`[ArmaraOS] Using existing agent: ${armaraAgentId}`);
        return armaraAgentId;
      }
    }
  } catch (e) {
    console.error('[ArmaraOS] Failed to list agents:', e.message);
  }

  return null; // Will fall back to direct chat endpoint
}

async function sendToArmaraOS(prompt, username) {
  const agentId = await getOrCreateAgent();

  // Try agent chat endpoint first, fall back to generic chat
  const endpoints = agentId
    ? [
        { url: `${ARMARAOS_URL}/api/agents/${agentId}/chat`, body: { message: prompt } },
        { url: `${ARMARAOS_URL}/api/chat`, body: { message: prompt, agent_id: agentId } },
      ]
    : [
        { url: `${ARMARAOS_URL}/api/chat`, body: { message: prompt } },
        { url: `${ARMARAOS_URL}/v1/chat/completions`, body: { messages: [{ role: 'user', content: prompt }] } },
      ];

  for (const endpoint of endpoints) {
    try {
      const res = await fetch(endpoint.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(endpoint.body),
        signal: AbortSignal.timeout(30000),
      });

      if (res.ok) {
        const data = await res.json();
        // Extract response text from various response shapes
        const reply =
          data.reply ||
          data.response ||
          data.message ||
          data.content ||
          data?.choices?.[0]?.message?.content ||
          JSON.stringify(data).slice(0, 200);
        return reply;
      }
    } catch (e) {
      // Try next endpoint
    }
  }

  throw new Error('ArmaraOS did not respond on any known endpoint');
}

// ─── COMMAND HANDLER ───────────────────────────────────────────────────────────
async function handleCommand(username, prompt) {
  const now = Date.now();

  // Cooldown check
  const lastRun = cooldowns.get(username) || 0;
  const elapsed = (now - lastRun) / 1000;
  if (elapsed < COOLDOWN_SECONDS) {
    const wait = Math.ceil(COOLDOWN_SECONDS - elapsed);
    console.log(`[COOLDOWN] ${username} must wait ${wait}s`);
    updateOverlay({ status: 'cooldown', user: username, wait });
    return;
  }

  // Queue depth check
  if (queueDepth >= MAX_QUEUE_DEPTH) {
    console.log(`[QUEUE] Too many in-flight commands, dropping from ${username}`);
    updateOverlay({ status: 'busy', user: username });
    return;
  }

  // Length check
  if (prompt.length > MAX_PROMPT_LENGTH) {
    console.log(`[BLOCKED] Prompt too long from ${username}`);
    return;
  }

  // Blocklist check
  if (isBlocked(prompt)) {
    console.log(`[BLOCKED] Prompt from ${username} matched blocklist: "${prompt}"`);
    updateOverlay({ status: 'blocked', user: username, reason: 'Blocked keyword' });
    return;
  }

  // Accept
  cooldowns.set(username, now);
  queueDepth++;

  console.log(`\n[CMD] ${username}: ${prompt}`);
  updateOverlay({ status: 'executing', user: username, prompt });

  try {
    const reply = await sendToArmaraOS(prompt, username);
    const short = reply.length > 200 ? reply.slice(0, 200) + '…' : reply;
    console.log(`[REPLY] ${short}`);
    updateOverlay({ status: 'replied', user: username, prompt, reply: short });
  } catch (e) {
    console.error(`[ERROR] ArmaraOS call failed: ${e.message}`);
    updateOverlay({ status: 'error', user: username, error: e.message });
  } finally {
    queueDepth--;
  }
}

// ─── PUMP.FUN WEBSOCKET ────────────────────────────────────────────────────────
function connect() {
  // pump.fun uses socket.io — we connect to the underlying engine.io transport
  const WS_URL = `wss://frontend-api.pump.fun/socket.io/?EIO=4&transport=websocket`;

  console.log('[pump.fun] Connecting...');
  const ws = new WebSocket(WS_URL, {
    headers: {
      'Origin': 'https://pump.fun',
      'User-Agent': 'Mozilla/5.0',
    }
  });

  ws.on('open', () => {
    console.log('[pump.fun] Connected');
    // socket.io handshake — send connect packet then subscribe to coin chat
    ws.send('40');
  });

  ws.on('message', (raw) => {
    const msg = raw.toString();

    // socket.io ping/pong
    if (msg === '2') { ws.send('3'); return; }

    // Parse socket.io event packets (42[...])
    if (!msg.startsWith('42')) return;

    let event, data;
    try {
      const parsed = JSON.parse(msg.slice(2));
      [event, data] = parsed;
    } catch (_) { return; }

    // Subscribe to coin chat after connect ack
    if (event === 'connect' || msg === '40{}') {
      console.log(`[pump.fun] Subscribing to coin: ${CONTRACT}`);
      ws.send(`42["subscribeNewToken",{}]`);
      ws.send(`42["subscribeCoinTrade",{"mint":"${CONTRACT}"}]`);
      ws.send(`42["subscribeCoinChat",{"mint":"${CONTRACT}"}]`);
    }

    // Chat message event — pump.fun uses various event names
    if (['chatMessage', 'newChatMessage', 'message', 'chat'].includes(event)) {
      const username = data?.username || data?.user || data?.sender || 'anon';
      const text = (data?.message || data?.text || data?.content || '').trim();

      if (!text) return;
      console.log(`[chat] ${username}: ${text}`);

      // Check for "probe bot <prompt>"
      const lower = text.toLowerCase();
      if (lower.startsWith(COMMAND_PREFIX)) {
        const prompt = text.slice(COMMAND_PREFIX.length).trim();
        if (prompt) handleCommand(username, prompt);
      }
    }
  });

  ws.on('close', (code) => {
    console.log(`[pump.fun] Disconnected (${code}). Reconnecting in 5s...`);
    updateOverlay({ status: 'disconnected' });
    setTimeout(connect, 5000);
  });

  ws.on('error', (e) => {
    console.error('[pump.fun] WS error:', e.message);
  });
}

// ─── STARTUP ───────────────────────────────────────────────────────────────────
console.log('╔═══════════════════════════════════════════╗');
console.log('║   ArmaraOS × Pump.fun Chat Controller    ║');
console.log('╚═══════════════════════════════════════════╝');
console.log(`Token:    ${CONTRACT}`);
console.log(`ArmaraOS: ${ARMARAOS_URL}`);
console.log(`Trigger:  "${COMMAND_PREFIX} <prompt>"`);
console.log(`Cooldown: ${COOLDOWN_SECONDS}s per user\n`);

updateOverlay({ status: 'starting' });

// Verify ArmaraOS is reachable
fetch(`${ARMARAOS_URL}/api/agents`)
  .then(r => {
    if (r.ok) console.log('[ArmaraOS] ✓ Reachable');
    else console.warn(`[ArmaraOS] ⚠ Responded with ${r.status} — check it's running`);
  })
  .catch(() => console.warn('[ArmaraOS] ⚠ Not reachable at localhost:4200 — is it running?'));

connect();
