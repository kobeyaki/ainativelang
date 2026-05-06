#!/usr/bin/env node
require('dotenv').config({ path: __dirname + '/.env' });

const fs = require('fs');
const API_KEY = process.env.KLING_API_KEY;
const IMAGE_URL = 'https://files.catbox.moe/ayqgzl.png';
const PROMPT = "Animate this underwater scene with subtle, looping motion. The starfish character gently bobs up and down with a slow breathing motion, its eyes blinking once every 3 seconds. Bubbles rise continuously from the ocean floor at varying speeds. The seaweed on both sides sways gently in a slow current. Light rays from above shimmer and shift across the scene in a slow, dreamy pulse. The AINL text has a soft golden glow that pulses rhythmically, like it's powered. The rocks on the ocean floor remain still. Everything feels alive but calm — peaceful, not frantic. Loop seamlessly. Cinematic underwater lighting. No camera movement.";

async function main() {
  console.log('Submitting Kling job — AINL banner animation...');

  const res = await fetch('https://api.shortapi.ai/api/v1/job/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'kwaivgi/kling-3.0/image-to-video',
      args: {
        mode: 'pro',
        duration: '5',
        prompt: PROMPT,
        image: IMAGE_URL
      }
    })
  });

  const data = await res.json();
  console.log('Submit response:', JSON.stringify(data, null, 2));

  const jobId = data.data?.job_id || data.job_id;
  if (!jobId) { console.error('No job ID returned'); process.exit(1); }

  console.log(`Job ID: ${jobId}`);
  console.log('Polling every 15s...');

  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 15000));

    const poll = await fetch(`https://api.shortapi.ai/api/v1/job/${jobId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const result = await poll.json();
    const status = result?.data?.status ?? result?.status;
    console.log(`[${i+1}] status:${status} | ${JSON.stringify(result).slice(0, 120)}`);

    if (result.code === 0 && (status === 2 || status === 'completed')) {
      console.log('DONE:', JSON.stringify(result, null, 2));
      const url = result.data?.result?.videos?.[0]?.url ||
                  result.data?.url ||
                  JSON.stringify(result).match(/https?:\/\/[^"]+\.mp4/)?.[0];
      if (url) {
        console.log(`Downloading from: ${url}`);
        const vid = await fetch(url);
        const buf = await vid.arrayBuffer();
        const outPath = `/data/.openclaw/workspace/ainl-video/ainl-banner-animated-${Date.now()}.mp4`;
        fs.writeFileSync(outPath, Buffer.from(buf));
        console.log(`Saved: ${outPath}`);
      }
      process.exit(0);
    }

    if (result.code === 0 && (status === 3 || status === 'failed')) {
      console.error('Failed:', JSON.stringify(result, null, 2));
      process.exit(1);
    }
  }

  console.log('Timed out — check shortapi.ai dashboard for job:', jobId);
}

main().catch(console.error);
