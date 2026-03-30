const fs = require('fs');
const path = require('path');
const https = require('https');
const FormData = require('form-data');

const BOT_TOKEN = '8081605621:AAEpgv8qaIm9Sx96iaJnetdEHr_rsKO7Jjw';
const USER_ID = 7013386742;
const PACK_NAME = 'CryptoKing_by_PlushifierBot';
const STICKER_DIR = path.join(__dirname, 'stickers');

const NEW_STICKERS = [
  { file: 'phone_chart.png',    emoji: '📱' },
  { file: 'sunglasses_cool.png', emoji: '😎' },
];

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
      let data = ''; res.on('data', d => data += d);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    form.pipe(req);
  });
}

function addToSet(fileId, emoji) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      user_id: USER_ID,
      name: PACK_NAME,
      sticker: { sticker: fileId, format: 'static', emoji_list: [emoji] },
    });
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/addStickerToSet`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    };
    const req = https.request(options, res => {
      let data = ''; res.on('data', d => data += d);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function main() {
  console.log(`Adding 2 final stickers to pack: ${PACK_NAME}\n`);
  for (const s of NEW_STICKERS) {
    const filePath = path.join(STICKER_DIR, s.file);
    process.stdout.write(`Uploading ${s.file}... `);
    const up = await uploadFile(filePath);
    if (!up.ok) { console.error('UPLOAD FAILED:', JSON.stringify(up)); continue; }
    console.log('✓ uploaded');
    process.stdout.write(`Adding ${s.emoji} to pack... `);
    const add = await addToSet(up.result.file_id, s.emoji);
    if (add.ok) console.log('✓ added');
    else console.error('ADD FAILED:', JSON.stringify(add));
  }
  console.log(`\n✅ Done! https://t.me/addstickers/${PACK_NAME}`);
}

main().catch(console.error);
