const https = require('https');
const fs = require('fs');
const FormData = require('form-data');

const API_KEY = process.env.OPENAI_API_KEY;

const POSES = [
  {
    name: 'laser_eyes',
    prompt: 'This exact orange kawaii starfish character with rosy cheeks, 5 chubby arms, big black eyes - but his eyes are shooting bright red/orange laser beams, looking powerful and intense, pure degen crypto laser eyes meme energy, PURE WHITE BACKGROUND, sticker art style, thick dark outline, white border'
  },
  {
    name: 'rocket',
    prompt: 'This exact orange kawaii starfish character riding a rocket ship blasting upward, holding on tight with arms gripping the rocket, huge excited grin, TO THE MOON energy, PURE WHITE BACKGROUND, sticker art style, thick dark outline'
  },
  {
    name: 'money_rain',
    prompt: 'This exact orange kawaii starfish character standing with arms up celebrating while gold coins and dollar bills rain down all around him, massive grin, rich degen energy, PURE WHITE BACKGROUND, sticker art style, thick dark outline'
  },
  {
    name: 'phone_chart',
    prompt: 'This exact orange kawaii starfish character holding up a phone showing a massive green chart going straight up, eyes wide with excitement, one arm pointing at the chart, number go up energy, PURE WHITE BACKGROUND, sticker art style, thick dark outline'
  },
  {
    name: 'sunglasses_cool',
    prompt: 'This exact orange kawaii starfish character looking extremely cool and unbothered, wearing stylish reflective sunglasses, leaning back with one arm raised in a peace sign, not a care in the world, PURE WHITE BACKGROUND, sticker art style, thick dark outline'
  },
];

function generate(pose) {
  return new Promise((resolve) => {
    const form = new FormData();
    form.append('model', 'gpt-image-1');
    form.append('prompt', pose.prompt);
    form.append('n', '1');
    form.append('size', '1024x1024');
    form.append('image[]', fs.createReadStream('./keeper_diamond.png'), { filename: 'ref.png', contentType: 'image/png' });

    const options = {
      hostname: 'api.openai.com', port: 443,
      path: '/v1/images/edits', method: 'POST',
      headers: { 'Authorization': `Bearer ${API_KEY}`, ...form.getHeaders() }
    };

    const req = https.request(options, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => {
        const r = JSON.parse(d);
        if (r.error) { console.error(`✗ ${pose.name}:`, r.error.message); resolve(null); return; }
        const b64 = r.data[0].b64_json;
        if (b64) {
          fs.writeFileSync(`./transparent_raw/${pose.name}.png`, Buffer.from(b64, 'base64'));
          console.log(`✓ ${pose.name}`);
          resolve(pose.name);
        } else resolve(null);
      });
    });
    req.on('error', e => { console.error(e.message); resolve(null); });
    form.pipe(req);
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

fs.mkdirSync('./transparent_raw', { recursive: true });

(async () => {
  for (const pose of POSES) {
    await generate(pose);
    await sleep(1000);
  }
  console.log('\nAll done!');
})();
