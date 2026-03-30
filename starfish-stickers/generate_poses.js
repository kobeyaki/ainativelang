const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.OPENAI_API_KEY;
const OUT_DIR = '/data/.openclaw/workspace/starfish-stickers/poses';
fs.mkdirSync(OUT_DIR, { recursive: true });

const BASE_STYLE = `kawaii cartoon sticker art, cute orange-red starfish character with exactly 5 chubby rounded legs, big round black eyes, warm orange-to-red gradient body with yellow spots, thick dark outline, white background, sticker style, no text, flat illustration, vibrant colors, expressive face`;

const POSES = [
  { name: 'gm',            prompt: `${BASE_STYLE}. The starfish is holding a steaming coffee cup, eyes half-open sleepy but smiling, morning vibes` },
  { name: 'lfg',           prompt: `${BASE_STYLE}. The starfish is screaming with huge open mouth, arms raised in the air celebrating, pure hype energy, teeth showing, wide eyes` },
  { name: 'wagmi',         prompt: `${BASE_STYLE}. The starfish is jumping with fists pumping in the air, huge grin, eyes crinkled happy, victorious pose` },
  { name: 'send_it',       prompt: `${BASE_STYLE}. The starfish is leaning forward aggressively, one arm pointing straight ahead like "go go go", determined wide eyes, action pose` },
  { name: 'diamond_hands', prompt: `${BASE_STYLE}. The starfish is holding up both arms showing fists, looking proud and strong, confident smug smile, diamond energy` },
  { name: 'ath',           prompt: `${BASE_STYLE}. The starfish is looking up at a rocket going up, jaw dropped in amazement, stars in eyes, number going up, pure excitement` },
  { name: 'ape_in',        prompt: `${BASE_STYLE}. The starfish is diving headfirst into a pile of coins, legs in the air, full send, silly excited expression` },
  { name: '1000x',         prompt: `${BASE_STYLE}. The starfish is flexing both arms like a bodybuilder, smug confident face, looking massive and powerful, champion pose` },
  { name: 'wen_moon',      prompt: `${BASE_STYLE}. The starfish is floating in space with a dreamy face, stars and moon around it, eyes half-closed peaceful, floating weightless` },
  { name: 'higher',        prompt: `${BASE_STYLE}. The starfish is zooming upward like a rocket, arms back, eyes huge and wild, moving fast, speed lines around it, pure momentum` },
];

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function generateImage(prompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'dall-e-3',
      prompt,
      n: 1,
      size: '1024x1024',
      quality: 'standard',
      response_format: 'url',
    });

    const options = {
      hostname: 'api.openai.com',
      path: '/v1/images/generations',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    };

    const req = https.request(options, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        const parsed = JSON.parse(data);
        if (parsed.error) return reject(new Error(parsed.error.message));
        resolve(parsed.data[0].url);
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function downloadImage(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, res => {
      res.pipe(file);
      file.on('finish', () => file.close(resolve));
    }).on('error', reject);
  });
}

async function main() {
  for (const pose of POSES) {
    process.stdout.write(`Generating ${pose.name}... `);
    try {
      const url = await generateImage(pose.prompt);
      const dest = path.join(OUT_DIR, `${pose.name}.png`);
      await downloadImage(url, dest);
      console.log(`✓`);
      await sleep(1000); // rate limit buffer
    } catch (e) {
      console.error(`FAILED: ${e.message}`);
    }
  }
  console.log('\nDone! All poses saved to', OUT_DIR);
}

main();
