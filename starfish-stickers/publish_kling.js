const fs = require('fs');
const path = require('path');
const https = require('https');
const FormData = require('form-data');

const BOT_TOKEN = '8081605621:AAEpgv8qaIm9Sx96iaJnetdEHr_rsKO7Jjw';
const USER_ID = 7013386742;
const PACK_NAME = `StarfishKingKling_by_PlushifierBot`;
const PACK_TITLE = 'Starfish King AI 🌟';
const DIR = '/data/.openclaw/workspace/starfish-stickers/kling_stickers';

const STICKERS = [
  { file: 'diamond_hands.webm', emoji: '💎' },
  { file: 'wen_moon.webm',      emoji: '🌙' },
  { file: 'higher.webm',        emoji: '🚀' },
];

function uploadStickerFile(filePath) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append('sticker', fs.createReadStream(filePath), { filename: path.basename(filePath), contentType: 'video/webm' });
    form.append('sticker_format', 'video');
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/uploadStickerFile?user_id=${USER_ID}`,
      method: 'POST', headers: form.getHeaders(),
    };
    const req = https.request(options, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    });
    req.on('error', reject);
    form.pipe(req);
  });
}

function createStickerSet(stickers) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      user_id: USER_ID, name: PACK_NAME, title: PACK_TITLE,
      stickers: stickers.map(s => ({ sticker: s.file_id, format: 'video', emoji_list: [s.emoji] })),
      sticker_format: 'video',
    });
    const options = {
      hostname: 'api.telegram.org', path: `/bot${BOT_TOKEN}/createNewStickerSet`,
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    };
    const req = https.request(options, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function main() {
  const uploaded = [];
  for (const s of STICKERS) {
    process.stdout.write(`Uploading ${s.file}... `);
    const res = await uploadStickerFile(path.join(DIR, s.file));
    if (!res.ok) { console.error('FAILED:', res); process.exit(1); }
    console.log('✓');
    uploaded.push({ file_id: res.result.file_id, emoji: s.emoji });
  }
  const res = await createStickerSet(uploaded);
  if (res.ok) console.log(`\n✅ https://t.me/addstickers/${PACK_NAME}`);
  else console.error('❌', JSON.stringify(res));
}
main().catch(console.error);
