const fs = require('fs');
const path = require('path');
const https = require('https');
const FormData = require('form-data');

const BOT_TOKEN = '8081605621:AAEpgv8qaIm9Sx96iaJnetdEHr_rsKO7Jjw';
const USER_ID = 7013386742;
const PACK_NAME = `StarfishKingKling_by_PlushifierBot`;
const DIR = '/data/.openclaw/workspace/starfish-stickers/kling_stickers';

const NEW_STICKERS = [
  { file: 'gm_v2.webm',    emoji: '☕' },
  { file: 'lfg_v2.webm',   emoji: '🔥' },
  { file: 'wagmi_v2.webm', emoji: '🙌' },
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

function addSticker(file_id, emoji) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      user_id: USER_ID,
      name: PACK_NAME,
      sticker: { sticker: file_id, format: 'video', emoji_list: [emoji] }
    });
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/addStickerToSet`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    };
    const req = https.request(options, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function main() {
  for (const s of NEW_STICKERS) {
    process.stdout.write(`Uploading ${s.file}... `);
    const up = await uploadStickerFile(path.join(DIR, s.file));
    if (!up.ok) { console.error('Upload FAILED:', up); continue; }
    console.log('✓ uploaded');

    process.stdout.write(`Adding to pack... `);
    const add = await addSticker(up.result.file_id, s.emoji);
    if (add.ok) console.log('✓ added');
    else console.error('Add FAILED:', JSON.stringify(add));
  }
  console.log(`\n✅ https://t.me/addstickers/${PACK_NAME}`);
}
main().catch(console.error);
