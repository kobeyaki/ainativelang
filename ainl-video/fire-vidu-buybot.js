#!/usr/bin/env node
require('dotenv').config({ path: __dirname + '/.env' });

const SHORTAPI_KEY = process.env.SHORTAPI_KEY;

// Latest Arch image with jetpack + purple lasers
// Using the image we just generated — upload to catbox first, or use direct URL
// For now using the canonical Arch image and describing the full scene
const IMAGE_URL = 'https://files.catbox.moe/ggxry4.png';

const PROMPT = `Glossy orange starfish mascot, five arms perfectly symmetrical, smooth rounded shape, dotted pattern glowing softly across the body, confident mischievous expression, narrow eyes glowing purple. Equipped with a high-tech dual jetpack on its back, thrusters firing bright orange flames and smoke trails, hovering in place against a dark cinematic background. Both eyes emit powerful purple laser beams that sweep horizontally left to right across the screen in a smooth motion. As the lasers sweep, they burn and reveal the glowing text "NEW BUY" in bright neon purple energy — text appears progressively as the lasers pass over it, leaving a glowing neon trail. After the sweep completes, the text pulses once with energy, small purple particles scatter outward. Arch hovers confidently with jetpack flames flickering and subtle smoke drifting. Seamless loop. Cinematic lighting, high contrast, ultra smooth motion, centered composition, clean dark background.`;

async function main() {
  if (!SHORTAPI_KEY) {
    console.error('❌ No SHORTAPI_KEY in .env');
    process.exit(1);
  }

  console.log('🚀 Submitting Vidu buybot animation job...');
  console.log('💬 Prompt:', PROMPT.slice(0, 100) + '...');

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
        console.log('🎬 Video URL:', videoUrl);
        // Download
        const { execSync } = require('child_process');
        execSync(`curl -L "${videoUrl}" -o /data/.openclaw/workspace/ainl-mascot-upgrades/arch_buybot_vidu.mp4`);
        console.log('💾 Saved: arch_buybot_vidu.mp4');
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
