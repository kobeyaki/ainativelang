const fs = require('fs');
const path = require('path');
const https = require('https');
const FormData = require('form-data');

const BOT_TOKEN = '8081605621:AAEpgv8qaIm9Sx96iaJnetdEHr_rsKO7Jjw';
const USER_ID = 7013386742; // sticker pack owner
const PACK_NAME = `CryptoKing_by_PlushifierBot`;
const PACK_TITLE = 'Crypto King 👑';
const BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;

const STICKERS = [
  { file: 'gm.png',           emoji: '☕' },
  { file: 'lfg.png',          emoji: '🔥' },
  { file: 'wagmi.png',        emoji: '🙌' },
  { file: 'ngmi.png',         emoji: '😭' },
  { file: 'diamond_hands.png',emoji: '💎' },
  { file: 'ath.png',          emoji: '📈' },
  { file: 'big_buy.png',      emoji: '💰' },
  { file: 'rekt.png',         emoji: '📉' },
  { file: 'wen_moon.png',     emoji: '🌙' },
  { file: 'higher.png',       emoji: '🚀' },
];

const STICKER_DIR = path.join(__dirname, 'stickers');

function apiGet(method, params = {}) {
  const url = `${BASE}/${method}?` + new URLSearchParams(params).toString();
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

function uploadFile(filePath) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append('sticker', fs.createReadStream(filePath), { filename: path.basename(filePath), contentType: 'image/png' });
    form.append('sticker_format', 'static');

    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/uploadStickerFile?user_id=${USER_ID}`,
      method: 'POST',
      headers: form.getHeaders(),
    };

    const req = https.request(options, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    form.pipe(req);
  });
}

function createStickerSet(firstFileId, firstEmoji, allStickers) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      user_id: USER_ID,
      name: PACK_NAME,
      title: PACK_TITLE,
      stickers: allStickers.map(s => ({
        sticker: s.file_id,
        format: 'static',
        emoji_list: [s.emoji],
      })),
      sticker_format: 'static',
    });

    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/createNewStickerSet`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    };

    const req = https.request(options, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  console.log('Uploading stickers...');
  const uploaded = [];

  for (const s of STICKERS) {
    const filePath = path.join(STICKER_DIR, s.file);
    console.log(`  Uploading ${s.file}...`);
    const res = await uploadFile(filePath);
    if (!res.ok) {
      console.error(`  FAILED: ${JSON.stringify(res)}`);
      process.exit(1);
    }
    const file_id = res.result.file_id;
    console.log(`  ✓ ${s.file} → ${file_id}`);
    uploaded.push({ file_id, emoji: s.emoji });
  }

  console.log('\nCreating sticker set...');
  const res = await createStickerSet(uploaded[0].file_id, uploaded[0].emoji, uploaded);
  console.log(JSON.stringify(res, null, 2));

  if (res.ok) {
    console.log(`\n✅ Pack created! https://t.me/addstickers/${PACK_NAME}`);
  } else {
    console.error('❌ Failed to create pack.');
  }
}

main().catch(console.error);
