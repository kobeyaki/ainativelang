const https = require('https');
const fs = require('fs');
const path = require('path');

const KEY = 'ak-97c3a2c425cd11f197027a344a4b0607';
const OUT = '/data/.openclaw/workspace/starfish-stickers/kling_videos';

const JOBS = [
  { name: 'gm',            job_id: '69bfb2b8ebf774a658fa4399' },
  { name: 'lfg',           job_id: '69bfb2baebf774a658fa439a' },
  { name: 'wagmi',         job_id: '69bfb2bbebf774a658fa439b' },
  { name: 'send_it',       job_id: '69bfb2bcebf774a658fa439c' },
  { name: 'diamond_hands', job_id: '69bfb2beebf774a658fa439d' },
  { name: 'ath',           job_id: '69bfb2bfebf774a658fa439e' },
  { name: 'ape_in',        job_id: '69bfb2c1ebf774a658fa439f' },
  { name: '1000x',         job_id: '69bfb2c2ebf774a658fa43a0' },
  { name: 'wen_moon',      job_id: '69bfb2c3ebf774a658fa43a1' },
  { name: 'higher',        job_id: '69bfb2c5ebf774a658fa43a2' },
];

function apiGet(p) {
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.shortapi.ai', path: p, method: 'GET',
      headers: { 'Authorization': `Bearer ${KEY}` },
    }, res => {
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
      const mod = u.startsWith('https') ? require('https') : require('http');
      mod.get(u, res => {
        if ([301,302,307,308].includes(res.statusCode)) return get(res.headers.location);
        res.pipe(file);
        file.on('finish', () => file.close(resolve));
      }).on('error', reject);
    };
    get(url);
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const pending = [...JOBS];
  const done = [];
  
  while (pending.length > 0) {
    for (let i = pending.length - 1; i >= 0; i--) {
      const job = pending[i];
      const res = await apiGet(`/api/v1/job/${job.job_id}`);
      
      // Print full response first time to understand structure
      if (!job._seen) {
        console.log(`${job.name} response structure:`, JSON.stringify(res).slice(0,300));
        job._seen = true;
      }
      
      const d = res.data || res;
      const status = d.status || d.state || d.job_status;
      
      if (!status) {
        console.log(`${job.name}: unknown status → ${JSON.stringify(d).slice(0,150)}`);
      } else {
        process.stdout.write(`${job.name}: ${status}  \r`);
      }
      
      const isDone = ['completed','succeed','success','finish','done'].includes(String(status).toLowerCase());
      const isFailed = ['failed','error','cancelled'].includes(String(status).toLowerCase());
      
      if (isDone) {
        const url = d.output?.url || d.video_url || d.url || d.output?.[0]?.url 
                 || d.result?.url || d.result?.video_url || d.works?.[0]?.url
                 || d.videos?.[0]?.url;
        console.log(`\n✓ ${job.name} DONE → ${url}`);
        if (url) {
          const dest = path.join(OUT, `${job.name}.mp4`);
          await download(url, dest);
          console.log(`  saved ${Math.round(fs.statSync(dest).size/1024)}KB`);
          done.push(job.name);
        }
        pending.splice(i, 1);
      } else if (isFailed) {
        console.log(`\n✗ ${job.name} FAILED`);
        pending.splice(i, 1);
      }
    }
    
    if (pending.length > 0) {
      console.log(`\nWaiting... ${pending.length} pending: ${pending.map(j=>j.name).join(', ')}`);
      await sleep(15000);
    }
  }
  
  console.log(`\n✅ Done! ${done.length} videos: ${done.join(', ')}`);
}

main().catch(console.error);
