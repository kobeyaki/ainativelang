#!/usr/bin/env node
require('dotenv').config({ path: __dirname + '/.env' });

const SHORTAPI_KEY = process.env.SHORTAPI_KEY;

const IMAGE_URL = 'https://files.catbox.moe/ggxry4.png';

const PROMPT = `Cute orange cartoon starfish mascot centered on screen with a happy smiling face. Background is a dark black screen filled with vertical streams of falling green Matrix-style code rain — glowing green digits cascading downward like in The Matrix. The orange starfish has both eyes glowing bright purple. Twin parallel purple laser beams shoot out from both eyes simultaneously, traveling diagonally up-right across the screen. As the laser beams sweep across, they burn glowing letters into the air — the letters "NEW BUY" appear progressively from left to right, written in large bold glowing golden-orange fire text with bright burning edges, like neon fire. The text glows and pulses warmly after being written. The starfish mascot stays centered, smiling confidently, purple eye glow maintained. Cinematic, ultra smooth animation, high contrast, vibrant colors against dark background.`;

async function main() {
  if (!SHORTAPI_KEY) {
    console.error('❌ No SHORTAPI_KEY in .env');
    process.exit(1);
  }

  console.log('🚀 Submitting Vidu buybot V4 animation job...');
  console.log('💬 Prompt:', PROMPT.slice(0, 120) + '...');

  const body = {
    model: 'vidu/vidu-q2/image-to-video',
    args: {
      mode: 'pro',
      prompt: PROMPT,
      image: IMAGE_URL
    }
  };

  const res = await fetch('https://api.shortapi.ai/api/v1/job/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${SHORTAPI_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  const data = await res.json();
  console.log('Response:', JSON.stringify(data, null, 2));

  const jobId = data?.data?.job_id || data?.job_id;
  if (!jobId) {
    console.error('❌ No job ID returned. Check credits.');
    process.exit(1);
  }

  console.log(`✅ Job submitted! ID: ${jobId}`);
  console.log('⏳ Polling every 20s (Vidu takes 2-5 min)...');

  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 20000));

    const poll = await fetch(`https://api.shortapi.ai/api/v1/job/query?id=${jobId}`, {
      headers: { 'Authorization': `Bearer ${SHORTAPI_KEY}` }
    });
    const pdata = await poll.json();
    const status = pdata?.data?.status || pdata?.status;
    const result = pdata?.data?.result || pdata?.result;

    console.log(`[${i+1}] Status: ${status}`);

    if (status === 'success' || status === 'completed') {
      const videoUrl = result?.videos?.[0]?.url || result?.url || result?.video_url;
      console.log('✅ Done!', JSON.stringify(result, null, 2));
      if (videoUrl) {
        const { execSync } = require('child_process');
        execSync(`curl -L "${videoUrl}" -o /data/.openclaw/workspace/ainl-mascot-upgrades/arch_buybot_v4.mp4`);
        console.log('💾 Saved: arch_buybot_v4.mp4');
      }
      process.exit(0);
    }

    if (status === 'failed' || status === 'error') {
      console.error('❌ Job failed:', JSON.stringify(pdata, null, 2));
      process.exit(1);
    }
  }

  console.log('⏰ Timeout — job still processing. Job ID:', jobId);
}

main().catch(console.error);
