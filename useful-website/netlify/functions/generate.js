const https = require('https');
const url = require('url');

const CHARACTER = "a green cartoon coin character named Useful with a cheerful mischievous grin, big expressive eyes, small arms and legs, wearing tiny boxing gloves, glowing green aura, vibrant comic meme art style with bold outlines";

function fetchBuffer(imageUrl) {
  return new Promise((resolve, reject) => {
    const parsed = url.parse(imageUrl);
    const req = https.get({
      hostname: parsed.hostname,
      path: parsed.path,
      headers: { 'User-Agent': 'UsefulMemeGen/1.0' },
      timeout: 25000,
    }, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return fetchBuffer(res.headers.location).then(resolve).catch(reject);
      }
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve({ buf: Buffer.concat(chunks), ct: res.headers['content-type'], status: res.statusCode }));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const params = event.queryStringParameters || {};
  const userPrompt = params.prompt || 'standing on the moon';
  const seed = Math.floor(Math.random() * 999999);
  const fullPrompt = `${CHARACTER}, ${userPrompt}, meme format, funny, vibrant colors, digital art`;
  const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(fullPrompt)}?width=512&height=512&seed=${seed}&nologo=true&model=flux`;

  try {
    const result = await fetchBuffer(imageUrl);
    if (result.status !== 200 || result.buf.length < 5000) {
      throw new Error(`Bad response status=${result.status} size=${result.buf.length}`);
    }
    return {
      statusCode: 200,
      headers: { ...headers, 'Content-Type': result.ct || 'image/jpeg' },
      body: result.buf.toString('base64'),
      isBase64Encoded: true,
    };
  } catch (err) {
    return {
      statusCode: 502,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
