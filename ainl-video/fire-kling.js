#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

require('dotenv').config({ path: path.join(__dirname, '.env') });

const API_KEY = process.env.KLING_API_KEY;
const IMAGE_PATH = '/data/.openclaw/workspace/ainl-buybot/mascot-transparent-clean.png';
const PROMPT = "Cute cartoon starfish mascot stares intensely forward, eyes glow with building energy. Twin laser beams fire from both pupils — bright neon green beams sweep dramatically across the dark screen in synchronized arcs, tracing glowing light trails that form the letters NEW BUY. Each letter burns into existence with crackling energy and lingering afterglow. Matrix green code rain cascades in the background. Mascot holds a stone-cold serious expression during the laser sequence, then shifts to triumphant grin as the text completes. Cinematic slow-motion laser sweep, dark background, epic crypto hype energy.";

async function main() {
  const imageData = 'https://tmpfiles.org/dl/31687072/mascot-transparent-clean.png';

  console.log('🚀 Submitting Kling job...');
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
        image: imageData
      }
    })
  });

  const data = await res.json();
  console.log('Response:', JSON.stringify(data, null, 2));

  const jobId = data.job_id || data.data?.job_id;
  if (!jobId) {
    console.error('❌ No job ID returned');
    process.exit(1);
  }

  console.log(`✅ Job ID: ${jobId}`);
  console.log('⏳ Polling...');

  for (let i = 0; i < 72; i++) {
    await new Promise(r => setTimeout(r, 5000));
    const poll = await fetch(`https://api.shortapi.ai/api/v1/job/${jobId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const result = await poll.json();
    const status = result.status || result.data?.status;
    console.log(`[${i+1}] Status: ${status}`);

    if (status === 'completed') {
      const videoUrl = result.url || result.data?.url || 
                       result.output?.url || result.data?.output?.url ||
                       JSON.stringify(result).match(/https?:\/\/[^"]+\.mp4/)?.[0];
      console.log('🎬 Done! Full result:', JSON.stringify(result, null, 2));
      if (videoUrl) {
        const outPath = `/data/.openclaw/workspace/ainl-video/ainl-lasereyes-${Date.now()}.mp4`;
        const vid = await fetch(videoUrl);
        const buf = await vid.arrayBuffer();
        fs.writeFileSync(outPath, Buffer.from(buf));
        console.log(`💾 Saved to: ${outPath}`);
      }
      process.exit(0);
    }

    if (status === 'failed') {
      console.error('❌ Failed:', JSON.stringify(result, null, 2));
      process.exit(1);
    }
  }

  console.log('⏰ Timed out');
}

main().catch(console.error);
