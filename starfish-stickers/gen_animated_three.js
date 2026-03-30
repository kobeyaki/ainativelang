const https = require('https');
const fs = require('fs');
const path = require('path');

const KEY = 'ak-97c3a2c425cd11f197027a344a4b0607';
const OUT = '/data/.openclaw/workspace/starfish-stickers/animated_three';
fs.mkdirSync(OUT, { recursive: true });

const CHARACTER = `cute kawaii orange starfish character with 5 chubby arms, big black eyes, rosy cheeks, thick dark outline, cartoon sticker style, white background`;

const STICKERS = [
  {
    name: 'laser_eyes',
    prompt: `${CHARACTER}. Eyes suddenly glow bright red, then shoot intense laser beams out of both eyes left and right, recoils back from the power, looks down at lasers with a menacing grin, repeating loop. Pure crypto laser eyes meme. White background.`,
  },
  {
    name: 'money_rain',
    prompt: `${CHARACTER}. Arms raised up high in celebration, gold coins and dollar bills raining down from above, bouncing off its head and arms, huge grin getting bigger, spinning slightly with joy. Coins clinking and sparkling. White background. Loop animation.`,
  },
  {
    name: 'rocket',
    prompt: `${CHARACTER}. Gripping a rocket tightly as it blasts off from the ground, flames shooting out the bottom, accelerating upward faster and faster with wild eyes and huge grin, zooming toward the top of frame then looping back. TO THE MOON energy. White background.`,
  },
];

function apiPost(p, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const options = {
      hostname: 'api.shortapi.ai', path: p, method: 'POST',
      headers: {
        'Authorization': `Bearer ${KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };
    const req = https.request(options, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch(e) { resolve({raw: d}); } });
    });
    req.on('error', reject);
    req.write(data); req.end();
  });
}

function apiGet(p) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.shortapi.ai', path: p, method: 'GET',
      headers: { 'Authorization': `Bearer ${KEY}` },
    };
    const req = https.request(options, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch(e) { resolve({raw: d}); } });
    });
    req.on('error', reject); req.end();
  });
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    const get = (u) => {
      https.get(u, res => {
        if (res.statusCode === 301 || res.statusCode === 302) return get(res.headers.location);
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
    process.stdout.write(`    [${i+1}] ${status}    \r`);
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
  console.log('Submitting 3 animation jobs to Kling...\n');
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

  fs.writeFileSync(path.join(OUT, 'jobs.json'), JSON.stringify(jobs, null, 2));
  console.log(`\nAll ${jobs.length} jobs queued. Polling results (may take ~5-10 min)...\n`);

  for (const job of jobs) {
    const url = await pollJob(job.job_id, job.name);
    if (url) {
      const dest = path.join(OUT, `${job.name}.mp4`);
      await download(url, dest);
      const size = fs.statSync(dest).size;
      console.log(`  💾 ${job.name}.mp4 saved (${Math.round(size/1024)}KB)`);
    }
  }
  console.log('\n✅ All done! Run convert_and_publish.js next.');
}

main().catch(console.error);
