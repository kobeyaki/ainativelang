#!/usr/bin/env node
// AINL Holder Hub — Token-gated verification API, image gen, leaderboard
require('dotenv').config({ path: __dirname + '/.env' });
const express = require('express');
const nacl = require('tweetnacl');
const bs58 = require('bs58');
const path = require('path');
const fs = require('fs');
const { Connection, PublicKey } = require('@solana/web3.js');
const { verifyHolder, TIERS, DECIMALS } = require('./verify');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/generated', express.static(path.join(__dirname, 'generated')));

// === VERIFICATION ===

app.post('/api/verify', async (req, res) => {
  try {
    const { wallet, signature, message } = req.body;
    if (!wallet || !signature || !message) {
      return res.status(400).json({ error: 'Missing wallet, signature, or message' });
    }
    const messageBytes = new TextEncoder().encode(message);
    const signatureBytes = bs58.decode(signature);
    const publicKeyBytes = bs58.decode(wallet);
    const valid = nacl.sign.detached.verify(messageBytes, signatureBytes, publicKeyBytes);
    if (!valid) return res.status(401).json({ error: 'Invalid signature' });
    const result = await verifyHolder(wallet);
    res.json(result);
  } catch (e) {
    console.error('Verify error:', e.message);
    res.status(500).json({ error: 'Verification failed' });
  }
});

app.get('/api/balance/:wallet', async (req, res) => {
  try {
    const result = await verifyHolder(req.params.wallet);
    res.json(result);
  } catch (e) {
    console.error('Balance error:', e.message);
    res.status(500).json({ error: 'Balance check failed' });
  }
});

app.get('/api/token', (req, res) => {
  res.json({
    name: 'AINL', symbol: 'AINL',
    mint: process.env.AINL_TOKEN_MINT, chain: 'solana',
    tiers: {
      basic: { min: process.env.TIER_BASIC, emoji: '🤖', perks: ['Holder dashboard access', 'Basic AI agent access'] },
      pro: { min: process.env.TIER_PRO, emoji: '⭐', perks: ['Everything in Basic', 'AINL image generator', 'Alpha channel'] },
      whale: { min: process.env.TIER_WHALE, emoji: '🐋', perks: ['Everything in Pro', 'Unlimited image gen', 'Custom styles', 'Governance votes'] },
    },
  });
});

// === IMAGE GENERATOR (token-gated) ===

const GENERATED_DIR = path.join(__dirname, 'generated');
if (!fs.existsSync(GENERATED_DIR)) fs.mkdirSync(GENERATED_DIR, { recursive: true });

// Rate limit tracking
const genLimits = new Map(); // wallet -> { count, resetAt }

function checkGenLimit(wallet, tier) {
  const limits = { basic: 3, pro: 10, whale: 50 }; // per day
  const max = limits[tier] || 0;
  if (max === 0) return false;

  const now = Date.now();
  const entry = genLimits.get(wallet) || { count: 0, resetAt: now + 86400000 };
  if (now > entry.resetAt) { entry.count = 0; entry.resetAt = now + 86400000; }
  if (entry.count >= max) return false;
  entry.count++;
  genLimits.set(wallet, entry);
  return true;
}

app.post('/api/generate', async (req, res) => {
  try {
    const { wallet, prompt } = req.body;
    if (!wallet || !prompt) return res.status(400).json({ error: 'Missing wallet or prompt' });

    // Verify holder status
    const holder = await verifyHolder(wallet);
    if (holder.tier === 'none') {
      return res.status(403).json({ error: 'Hold at least 100K $AINL to use the image generator' });
    }

    // Check rate limit
    if (!checkGenLimit(wallet, holder.tier)) {
      return res.status(429).json({ error: 'Daily generation limit reached. Upgrade your tier for more.' });
    }

    // Enforce AINL branding in prompt
    const brandedPrompt = `Kawaii cartoon style, cute glossy orange-red starfish mascot character with big shiny black eyes and happy smile, pure black background, vibrant orange-red color palette, glossy cartoon vector art style. Scene: ${prompt}`;

    const OpenAI = require('openai');
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

    const response = await openai.images.generate({
      model: 'gpt-image-1',
      prompt: brandedPrompt,
      n: 1,
      size: '1024x1024',
      quality: 'medium',
    });

    // Save image
    const imageData = response.data[0].b64_json;
    const filename = `ainl-${Date.now()}-${Math.random().toString(36).slice(2, 8)}.png`;
    const filepath = path.join(GENERATED_DIR, filename);

    if (imageData) {
      fs.writeFileSync(filepath, Buffer.from(imageData, 'base64'));
    }

    const imageUrl = response.data[0].url || `/generated/${filename}`;

    res.json({
      success: true,
      imageUrl,
      tier: holder.tier,
      remaining: getRemainingGens(wallet, holder.tier),
    });
  } catch (e) {
    console.error('Generate error:', e.message);
    res.status(500).json({ error: 'Image generation failed: ' + e.message });
  }
});

function getRemainingGens(wallet, tier) {
  const limits = { basic: 3, pro: 10, whale: 50 };
  const max = limits[tier] || 0;
  const entry = genLimits.get(wallet);
  if (!entry) return max;
  if (Date.now() > entry.resetAt) return max;
  return Math.max(0, max - entry.count);
}

// === LEADERBOARD ===

// Top holders cache (refreshes every 10 minutes)
let leaderboardCache = { data: [], updatedAt: 0 };
const LEADERBOARD_TTL = 600000; // 10 min

app.get('/api/leaderboard', async (req, res) => {
  try {
    const now = Date.now();
    if (now - leaderboardCache.updatedAt < LEADERBOARD_TTL && leaderboardCache.data.length > 0) {
      return res.json(leaderboardCache.data);
    }

    const connection = new Connection(process.env.SOLANA_RPC, 'confirmed');
    const mint = new PublicKey(process.env.AINL_TOKEN_MINT);
    const TOKEN_2022 = new PublicKey('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb');

    // Get largest token accounts
    const largest = await connection.getTokenLargestAccounts(mint);

    const holders = [];
    for (const acct of largest.value.slice(0, 20)) {
      const info = await connection.getParsedAccountInfo(acct.address);
      const parsed = info.value?.data?.parsed;
      if (parsed) {
        const owner = parsed.info.owner;
        const amount = BigInt(parsed.info.tokenAmount.amount);
        const multiplier = BigInt(10 ** DECIMALS);
        const formatted = (amount / multiplier).toLocaleString();
        const tier = amount >= TIERS.whale ? '🐋' : amount >= TIERS.pro ? '⭐' : amount >= TIERS.basic ? '🤖' : '👀';
        holders.push({
          wallet: owner,
          walletShort: owner.slice(0, 4) + '...' + owner.slice(-4),
          balance: amount.toString(),
          balanceFormatted: formatted,
          tier,
        });
      }
    }

    holders.sort((a, b) => {
      const ba = BigInt(a.balance);
      const bb = BigInt(b.balance);
      return bb > ba ? 1 : bb < ba ? -1 : 0;
    });

    leaderboardCache = { data: holders, updatedAt: now };
    res.json(holders);
  } catch (e) {
    console.error('Leaderboard error:', e.message);
    res.status(500).json({ error: 'Failed to load leaderboard' });
  }
});

// Force port from .env (override system PORT)
const dotenvConfig = require('dotenv').parse(require('fs').readFileSync(__dirname + '/.env'));
const PORT = dotenvConfig.PORT || 3456;
app.listen(PORT, '0.0.0.0', () => console.log(`AINL Holder Hub running on :${PORT}`));
