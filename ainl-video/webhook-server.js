const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3333;
const RESULTS_DIR = path.join(__dirname, 'webhook-results');

// Ensure results directory exists
if (!fs.existsSync(RESULTS_DIR)) {
  fs.mkdirSync(RESULTS_DIR, { recursive: true });
}

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/callback') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const jobId = payload.job_id || payload.data?.job_id || 'unknown';
        const timestamp = new Date().toISOString();

        // Save result to file
        const filename = path.join(RESULTS_DIR, `${jobId}.json`);
        fs.writeFileSync(filename, JSON.stringify({
          jobId,
          timestamp,
          payload
        }, null, 2));

        console.log(`[${timestamp}] Job ${jobId} completed. Saved to ${filename}`);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true, jobId }));
      } catch (err) {
        console.error('Webhook error:', err);
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: err.message }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`Webhook server listening on port ${PORT}`);
  console.log(`Callback URL: http://localhost:${PORT}/callback`);
});
