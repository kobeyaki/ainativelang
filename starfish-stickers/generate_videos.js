const https = require('https');
const fs = require('fs');
const path = require('path');

const KEY = 'ak-97c3a2c425cd11f197027a344a4b0607';
const OUT = '/data/.openclaw/workspace/starfish-stickers/kling_videos';
fs.mkdirSync(OUT, { recursive: true });

const CHARACTER = `cute kawaii orange-red starfish character with exactly 5 chubby rounded legs, big round black eyes, warm orange-to-red gradient body with yellow spots, thick dark outline, cartoon sticker style`;

const STICKERS = [
  {
    name: 'gm',
    prompt: `${CHARACTER}. Holding a steaming coffee cup, eyes half-open sleepy, slowly waking up and taking a sip, happy smile spreading across face, morning energy. White background. Loop animation.`
  },
  {
    name: 'lfg',
    prompt: `${CHARACTER}. Screaming with huge open mouth, arms shooting up in the air, then blasting off like a rocket upward out of frame leaving a trail. Pure hype. White background. Loop animation.`
  },
  {
    name: 'wagmi',
    prompt: `${CHARACTER}. Jumping up and down with fists pumping in the air, mouth open screaming with joy, crinkled happy eyes, triumphant victory dance. White background. Loop animation.`
  },
  {
    name: 'send_it',
    prompt: `${CHARACTER}. Leaning back winding up then explosively launching forward pointing ahead, zoom lines, going fast, determined wild eyes, pure send it energy. White background. Loop animation.`
  },
  {
    name: 'diamond_hands',
    prompt: `${CHARACTER}. Holding up both fists proudly, slowly rotating, glowing and sparkling with diamonds, smug confident grin, powerful stance. White background. Loop animation.`
  },
  {
    name: 'ath',
    prompt: `${CHARACTER}. Starting tiny then zooming in huge toward camera with jaw dropped in amazement, stars and dollar signs sparkling around it, pure excitement. White background. Loop animation.`
  },
  {
    name: 'ape_in',
    prompt: `${CHARACTER}. Diving headfirst down into a pile of gold coins from above, legs kicking in the air, coins splashing everywhere, unhinged excitement. White background. Loop animation.`
  },
  {
    name: '1000x',
    prompt: `${CHARACTER}. Flexing arms like a bodybuilder getting bigger and bigger with each pump, smug grin, growing more powerful, champion energy. White background. Loop animation.`
  },
  {
    name: 'wen_moon',
    prompt: `${CHARACTER}. Floating dreamily upward through stars and a crescent moon, arms spread wide, peaceful happy expression, weightless and ethereal. Dark starry background. Loop animation.`
  },
  {
    name: 'higher',
    prompt: `${CHARACTER}. Spinning and zooming directly toward camera accelerating faster and faster, wild eyes getting bigger, filling the whole frame, unstoppable momentum. White background. Loop animation.`
  },
];

function apiPost(path, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const options = {
      hostname: 'api.shortapi.ai',
      path,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };
    const req = https.request(options, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function apiGet(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.shortapi.ai',
      path,
      method: 'GET',
      headers: { 'Authorization': `Bearer ${KEY}` },
    };
    const req = https.request(options, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    });
    req.on('error', reject);
    req.end();
  });
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    const get = (u) => {
      const mod = u.startsWith('https') ? require('https') : require('http');
      mod.get(u, res => {
        if (res.statusCode === 301 || res.statusCode === 302) {
          return get(res.headers.location);
        }
        res.pipe(file);
        file.on('finish', () => file.close(resolve));
      }).on('error', reject);
    };
    get(url);
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function pollJob(jobId, name) {
  console.log(`  Polling ${name} (${jobId})...`);
  for (let i = 0; i < 60; i++) {
    await sleep(10000);
    const res = await apiGet(`/api/v1/job/${jobId}`);
    const status = res.data?.status || res.status;
    process.stdout.write(`    [${i+1}] status: ${status}\r`);
    
    if (status === 'completed' || status === 'succeed' || status === 'success') {
      const url = res.data?.output?.url || res.data?.video_url || res.data?.url ||
                  res.data?.output?.[0]?.url || res.data?.result?.url;
      console.log(`\n  ✓ ${name} done → ${url}`);
      return url;
    }
    if (status === 'failed' || status === 'error') {
      console.log(`\n  ✗ ${name} failed: ${JSON.stringify(res.data)}`);
      return null;
    }
  }
  console.log(`\n  ✗ ${name} timed out`);
  return null;
}

async function main() {
  const jobs = [];
  
  // Submit all jobs
  console.log('Submitting jobs...');
  for (const s of STICKERS) {
    const res = await apiPost('/api/v1/job/create', {
      model: 'kwaivgi/kling-3.0/text-to-video',
      args: {
        prompt: s.prompt,
        mode: 'pro',
        duration: '5',
        multi_shot: false,
      },
    });
    
    if (res.code !== 0) {
      console.error(`  ✗ ${s.name}: ${JSON.stringify(res)}`);
      continue;
    }
    
    console.log(`  ✓ ${s.name} submitted → job_id: ${res.data.job_id} ($${res.data.amount})`);
    jobs.push({ ...s, job_id: res.data.job_id });
    await sleep(1000);
  }
  
  // Save job IDs
  fs.writeFileSync(path.join(OUT, 'jobs.json'), JSON.stringify(jobs, null, 2));
  console.log(`\nAll ${jobs.length} jobs submitted. Polling for results...`);
  
  // Poll all jobs
  for (const job of jobs) {
    const url = await pollJob(job.job_id, job.name);
    if (url) {
      const dest = path.join(OUT, `${job.name}.mp4`);
      await download(url, dest);
      const size = fs.statSync(dest).size;
      console.log(`  💾 ${job.name}.mp4 saved (${Math.round(size/1024)}KB)`);
    }
  }
  
  console.log('\n✅ All done!');
}

main().catch(console.error);
