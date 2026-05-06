#!/usr/bin/env node
require('dotenv').config({ path: __dirname + '/.env' });

const SHORTAPI_KEY = process.env.SHORTAPI_KEY;
const CALLBACK_URL = process.env.WEBHOOK_PUBLIC_URL || '';

// Arch canonical image (transparent background, locked canonical)
const IMAGE_URL = 'https://files.catbox.moe/ggxry4.png';

const PROMPT = "A happy glowing orange star character with expressive eyes and a big smile flies through a dark neon-lit space with a jetpack strapped to its back, rocket exhaust blazing. The star's eyes suddenly lock forward with intense focus, pupils charging up with electric energy. Twin bright purple laser beams fire from its eyes, sweeping dramatically outward in slow cinematic arcs, leaving crackling neon purple light trails that glow and linger. The star grins wider as the lasers fire. Transparent background. Looping hype energy. Epic cinematic sticker vibe.";

async function main() {
  if (!SHORTAPI_KEY) {
    console.error('❌ No SHORTAPI_KEY in .env');
    process.exit(1);
  }

  console.log('🚀 Submitting Vidu laser sticker job...');
  console.log('📸 Image:', IMAGE_URL);
  console.log('💬 Prompt:', PROMPT.slice(0, 80) + '...');

  const body = {
    model: 'vidu/vidu-q2/image-to-video',
    args: {
      mode: 'pro',
      prompt: PROMPT,
      image: IMAGE_URL
    }
  };

  if (CALLBACK_URL) {
    body.callback_url = CALLBACK_URL;
    console.log('📡 Callback:', CALLBACK_URL);
  }

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
    console.error('❌ No job ID returned. Check key/credits.');
    process.exit(1);
  }

  console.log(`✅ Job submitted! ID: ${jobId}`);
  console.log('⏳ Polling every 15s...');

  for (let i = 0; i < 80; i++) {
    await new Promise(r => setTimeout(r, 15000));

    const poll = await fetch(`https://api.shortapi.ai/api/v1/job/query?id=${jobId}`, {
      headers: { 'Authorization': `Bearer ${SHORTAPI_KEY}` }
    });
    const result = await poll.json();

    const status = result?.data?.status ?? result?.status;
    const output = result?.data?.output ?? result?.output;

    console.log(`[${i+1}] status: ${status} | ${JSON.stringify(result).slice(0, 200)}`);

    if (status === 'success' || status === 'completed') {
      console.log('\n🎉 DONE!');
      console.log('Output:', JSON.stringify(output, null, 2));
      
      // Save result
      const fs = require('fs');
      const resultPath = __dirname + `/results/arch-laser-sticker-${jobId}.json`;
      fs.writeFileSync(resultPath, JSON.stringify({ jobId, status, output }, null, 2));
      console.log(`💾 Saved to: ${resultPath}`);
      break;
    }

    if (status === 'failed' || status === 'error') {
      console.error('❌ Job failed:', JSON.stringify(result, null, 2));
      process.exit(1);
    }
  }
}

main().catch(console.error);
