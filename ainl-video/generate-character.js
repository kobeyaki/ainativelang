require('dotenv').config({ path: '/data/.openclaw/workspace/ainativelang/apollo-x-bot/.env' });
const https = require('https');
const fs = require('fs');

const prompt = `A cinematic character concept art of a starfish mid-transformation. On the left side it is a wild, chaotic, glowing orange starfish with erratic energy lines and raw neural sparks flying off it — representing unstructured raw intelligence. On the right side it is being consumed and restructured by a dark mechanical lobster claw, and the starfish is transforming into a clean, glowing geometric circuit-graph form — nodes and edges, deterministic, structured, precise. The transformation is dramatic and beautiful. Deep black background with electric blue and orange energy. Institutional, cinematic quality. No text.`;

const body = JSON.stringify({
  model: 'dall-e-3',
  prompt,
  n: 1,
  size: '1024x1024',
  quality: 'hd',
  style: 'vivid'
});

const options = {
  hostname: 'api.openai.com',
  path: '/v1/images/generations',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
    'Content-Length': Buffer.byteLength(body)
  }
};

const req = https.request(options, res => {
  let data = '';
  res.on('data', d => data += d);
  res.on('end', () => {
    const result = JSON.parse(data);
    if (result.error) { console.error('Error:', result.error.message); process.exit(1); }
    const url = result.data[0].url;
    console.log('Image URL:', url);
    
    // Download it
    const file = fs.createWriteStream('/data/.openclaw/workspace/ainl-video/ainl-character-v1.png');
    https.get(url, r => { r.pipe(file); file.on('finish', () => { file.close(); console.log('Saved: ainl-character-v1.png'); }); });
  });
});
req.on('error', e => { console.error(e.message); process.exit(1); });
req.write(body);
req.end();
