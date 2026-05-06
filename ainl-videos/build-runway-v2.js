const RunwayML = require('@runwayml/sdk');
const fs = require('fs');
const https = require('https');
const path = require('path');
const { execSync } = require('child_process');
require('dotenv').config({ path: path.join(__dirname, '../ainl-video/.env') });

const client = new RunwayML({ apiKey: process.env.RUNWAY_API_KEY });
const OUT_DIR = path.join(__dirname, 'runway-v2');
fs.mkdirSync(OUT_DIR, { recursive: true });

// Reference image for gen4_image_turbo (required)
const REF_IMAGE = 'https://runway-static-assets.s3.us-east-1.amazonaws.com/devportal/playground-examples/t2i_gen4_image_turbo_input.png';

const SCENES = [
  {
    id: 'act1_chaos',
    imagePrompt: 'Dark futuristic server room, screens flickering with error messages, "$1,183/year" in red glowing text, chaotic streams of tokens and data cascading, cinematic dramatic lighting, ultra-realistic',
    videoPrompt: 'Screens flickering rapidly, data cascading, chaotic energy, cinematic',
    duration: 5,
  },
  {
    id: 'act2_compile',
    imagePrompt: 'Clean dark terminal screen showing "ainl compile agent.lang" with glowing green checkmarks appearing, elegant code structure visible, calm confident energy, cinematic lighting',
    videoPrompt: 'Checkmarks appearing one by one, green glow pulsing, smooth and deliberate motion',
    duration: 5,
  },
  {
    id: 'act3_proof',
    imagePrompt: 'Sleek dark dashboard showing "17 agents running | $29/month | 99.7% uptime" in bright cyan and white text, clean minimal UI, institutional credibility, cinematic',
    videoPrompt: 'Numbers counting up, data flowing smoothly, confident steady motion',
    duration: 5,
  },
  {
    id: 'act4_cta',
    imagePrompt: 'Minimalist dark background with "AINL" in large clean white letters, "ainativelang.com" below in cyan, subtle light rays emanating, powerful and calm, institutional brand identity',
    videoPrompt: 'Light rays expanding outward, logo glowing brighter, triumphant reveal energy',
    duration: 5,
  }
];

async function pollTask(taskId, label) {
  process.stdout.write(`   Polling ${label}`);
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 5000));
    const t = await client.tasks.retrieve(taskId);
    process.stdout.write('.');
    if (t.status === 'SUCCEEDED') { process.stdout.write(' ✅\n'); return t; }
    if (t.status === 'FAILED') { process.stdout.write(' ❌\n'); throw new Error(`Task failed: ${t.failure || 'unknown'}`); }
  }
  throw new Error('Timed out');
}

async function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, res => {
      if (res.statusCode === 302 || res.statusCode === 301) {
        https.get(res.headers.location, res2 => res2.pipe(file).on('finish', resolve).on('error', reject));
      } else {
        res.pipe(file).on('finish', resolve).on('error', reject);
      }
    }).on('error', reject);
  });
}

async function main() {
  console.log('🎬 AINL Commercial — Runway Pipeline v2\n');

  const videoPaths = [];

  for (const scene of SCENES) {
    console.log(`\n🖼️  Generating image: ${scene.id}`);
    const imgTask = await client.textToImage.create({
      promptText: scene.imagePrompt,
      referenceImages: [{ uri: REF_IMAGE }],
      model: 'gen4_image_turbo',
      ratio: '1920:1080',
      seed: Math.floor(Math.random() * 999999999),
    });
    const imgResult = await pollTask(imgTask.id, 'image');
    const imgUrl = imgResult.output[0];
    const imgPath = path.join(OUT_DIR, `${scene.id}.png`);
    await download(imgUrl, imgPath);
    console.log(`   Saved: ${imgPath}`);

    console.log(`🎥  Animating: ${scene.id}`);
    const vidTask = await client.imageToVideo.create({
      promptText: scene.videoPrompt,
      promptImage: imgUrl,
      model: 'gen3a_turbo',
      duration: scene.duration,
      ratio: '1280:768',
    });
    const vidResult = await pollTask(vidTask.id, 'video');
    const vidUrl = vidResult.output[0];
    const vidPath = path.join(OUT_DIR, `${scene.id}.mp4`);
    await download(vidUrl, vidPath);
    console.log(`   Saved: ${vidPath}`);
    videoPaths.push(vidPath);
  }

  // Stitch videos
  console.log('\n🔗 Stitching scenes...');
  const listFile = path.join(OUT_DIR, 'concat.txt');
  fs.writeFileSync(listFile, videoPaths.map(p => `file '${p}'`).join('\n'));
  const stitchedPath = path.join(OUT_DIR, 'commercial-noaudio.mp4');
  execSync(`ffmpeg -y -f concat -safe 0 -i "${listFile}" -c copy "${stitchedPath}"`);
  console.log('   Stitched:', stitchedPath);

  // Generate voiceover
  console.log('\n🎙️  Generating voiceover (OpenAI TTS)...');
  const script = `AI agents are burning your budget. Every decision loop costs tokens. Every orchestration layer adds drift. One production system. Twelve hundred dollars a year. Just to stay running. AINL compiles your agents once. Deterministic execution. Zero orchestration tokens at runtime. Seventeen agents. Twenty-nine dollars a month. Ninety-nine point seven percent uptime. No drift. No surprises. This is the infrastructure serious AI companies run on. AINL. Compile once. Run forever. ainativelang.com`;

  const voicePath = path.join(OUT_DIR, 'voiceover.mp3');
  const { default: OpenAI } = await import('openai');
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const ttsRes = await openai.audio.speech.create({
    model: 'tts-1-hd',
    voice: 'onyx',
    input: script,
    speed: 0.95,
  });
  fs.writeFileSync(voicePath, Buffer.from(await ttsRes.arrayBuffer()));
  console.log('   Voiceover saved:', voicePath);

  // Mix audio + video
  console.log('\n🎬 Final mix...');
  const finalPath = path.join(OUT_DIR, 'AINL-Commercial-Runway.mp4');
  execSync(`ffmpeg -y -i "${stitchedPath}" -i "${voicePath}" -c:v copy -c:a aac -shortest "${finalPath}"`);
  console.log('\n✅ DONE:', finalPath);
  console.log('   Duration: ~20 seconds');
}

main().catch(e => { console.error('\n❌ Fatal:', e.message); process.exit(1); });
