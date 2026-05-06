#!/usr/bin/env node
require('dotenv').config({ path: __dirname + '/.env' });

const API_KEY = process.env.KLING_API_KEY;
const IMAGE_URL = 'https://files.catbox.moe/ggxry4.png';
const PROMPT = "This exact cartoon starfish character from the reference image. The starfish's eyes suddenly glow bright neon green with intense energy. Twin laser beams shoot from its pupils, sweeping dramatically across the dark screen in slow motion arcs, leaving glowing neon green light trails that burn and crackle. The beams trace the text NEW BUY letter by letter. Starfish holds a deadpan serious expression during the laser sequence, then breaks into a huge triumphant grin as the letters complete. Dark background, cinematic VFX.";

async function main() {
  console.log('🚀 Submitting Kling job (v2 - stable image URL)...');
  
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
  console.log('Response:', JSON.stringify(data, null, 2));

  const jobId = data.data?.job_id || data.job_id;
  if (!jobId) {
    console.error('❌ No job ID');
    process.exit(1);
  }

  console.log(`✅ Job ID: ${jobId}`);
  console.log('⏳ Polling (checking status every 10s)...');
  console.log('NOTE: If polling returns 404, check shortapi.ai dashboard for results');

  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 10000));
    
    const poll = await fetch(`https://api.shortapi.ai/api/v1/job/${jobId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const result = await poll.json();
    
    const status = result?.data?.status ?? result?.status;
    console.log(`[${i+1}] code:${result.code} status:${status} | ${JSON.stringify(result).slice(0, 150)}`);

    if (result.code === 0 && (status === 2 || status === 'completed')) {
      console.log('🎬 DONE! Full result:', JSON.stringify(result, null, 2));
      
      // Extract video URL
      const url = result.data?.result?.videos?.[0]?.url || 
                  result.data?.url ||
                  JSON.stringify(result).match(/https?:\/\/[^"]+\.mp4/)?.[0];
      
      if (url) {
        console.log(`📥 Downloading from: ${url}`);
        const vid = await fetch(url);
        const buf = await vid.arrayBuffer();
        const outPath = `/data/.openclaw/workspace/ainl-video/ainl-lasereyes-${Date.now()}.mp4`;
        require('fs').writeFileSync(outPath, Buffer.from(buf));
        console.log(`💾 Saved: ${outPath}`);
      }
      process.exit(0);
    }

    if (result.code === 0 && (status === 3 || status === 'failed')) {
      console.error('❌ Failed:', JSON.stringify(result, null, 2));
      process.exit(1);
    }
  }

  console.log('⏰ Timed out - check shortapi.ai dashboard for job:', jobId);
}

main().catch(console.error);
