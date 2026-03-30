const http = require('http');
const https = require('https');
const url = require('url');

const PORT = 3131;

const CHARACTER = "a green cartoon coin character named Useful with a cheerful mischievous grin, big expressive eyes, small arms and legs, wearing tiny boxing gloves, glowing green aura, vibrant comic meme art style with bold outlines";

function fetchImage(imageUrl) {
  return new Promise((resolve, reject) => {
    const parsed = url.parse(imageUrl);
    const options = {
      hostname: parsed.hostname,
      path: parsed.path,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; UsefulMemeGenerator/1.0)',
      },
      timeout: 60000,
    };

    const req = https.request(options, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return fetchImage(res.headers.location).then(resolve).catch(reject);
      }
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve({ 
        data: Buffer.concat(chunks), 
        contentType: res.headers['content-type'] || 'image/jpeg',
        status: res.statusCode 
      }));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    req.end();
  });
}

const server = http.createServer(async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const parsed = url.parse(req.url, true);

  if (parsed.pathname === '/generate') {
    const userPrompt = parsed.query.prompt || 'standing on the moon';
    const seed = Math.floor(Math.random() * 999999);
    const fullPrompt = `${CHARACTER}, ${userPrompt}, meme format, funny, vibrant colors, digital art`;
    const encodedPrompt = encodeURIComponent(fullPrompt);
    const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=512&height=512&seed=${seed}&nologo=true&model=flux`;

    console.log(`[${new Date().toISOString()}] Generating: ${userPrompt}`);

    try {
      const result = await fetchImage(imageUrl);
      if (result.status !== 200 || result.data.length < 5000) {
        throw new Error(`Bad response: status ${result.status}, size ${result.data.length}`);
      }
      res.writeHead(200, {
        'Content-Type': result.contentType,
        'Content-Length': result.data.length,
        'Cache-Control': 'no-cache',
      });
      res.end(result.data);
      console.log(`[OK] ${result.data.length} bytes`);
    } catch (err) {
      console.error(`[ERR] ${err.message}`);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  if (parsed.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true, port: PORT }));
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Useful Meme Server running on http://127.0.0.1:${PORT}`);
});
