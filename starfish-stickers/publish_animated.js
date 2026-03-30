const fs = require('fs');
const path = require('path');
const https = require('https');
const FormData = require('form-data');

const BOT_TOKEN = '8081605621:AAEpgv8qaIm9Sx96iaJnetdEHr_rsKO7Jjw';
const USER_ID = 7013386742;
const PACK_NAME = `CryptoKingAnimated_by_PlushifierBot`;
const PACK_TITLE = 'Crypto King Animated 👑🔥';
const BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;
const ANIMATED_DIR = path.join(__dirname, 'animated');

const STICKERS = [
  { file: 'gm.webm',            emoji: '☕' },
  { file: 'lfg.webm',           emoji: '🔥' },
  { file: 'wagmi.webm',         emoji: '🙌' },
  { file: 'ngmi.webm',          emoji: '😭' },
  { file: 'diamond_hands.webm', emoji: '💎' },
  { file: 'ath.webm',           emoji: '📈' },
  { file: 'big_buy.webm',       emoji: '💰' },
  { file: 'rekt.webm',          emoji: '📉' },
  { file: 'wen_moon.webm',      emoji: '🌙' },
  { file: 'higher.webm',        emoji: '🚀' },
];

function uploadStickerFile(filePath) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append('sticker', fs.createReadStream(filePath), {
      filename: path.basename(filePath),
      contentType: 'video/webm',
    });
    form.append('sticker_format', 'video');

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

function createStickerSet(allStickers) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      user_id: USER_ID,
      name: PACK_NAME,
      title: PACK_TITLE,
      stickers: allStickers.map(s => ({
        sticker: s.file_id,
        format: 'video',
        emoji_list: [s.emoji],
      })),
      sticker_format: 'video',
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
  console.log('Uploading animated stickers...');
  const uploaded = [];

  for (const s of STICKERS) {
    const filePath = path.join(ANIMATED_DIR, s.file);
    console.log(`  Uploading ${s.file}...`);
    const res = await uploadStickerFile(filePath);
    if (!res.ok) {
      console.error(`  FAILED: ${JSON.stringify(res)}`);
      process.exit(1);
    }
    const file_id = res.result.file_id;
    console.log(`  ✓ ${s.file} → ${file_id.slice(0, 30)}...`);
    uploaded.push({ file_id, emoji: s.emoji });
  }

  console.log('\nCreating animated sticker set...');
  const res = await createStickerSet(uploaded);
  console.log(JSON.stringify(res, null, 2));

  if (res.ok) {
    console.log(`\n✅ Animated pack live! https://t.me/addstickers/${PACK_NAME}`);
  } else {
    console.error('❌ Failed to create pack.');
  }
}

main().catch(console.error);
