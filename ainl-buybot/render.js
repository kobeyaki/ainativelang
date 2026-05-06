const puppeteer = require('puppeteer');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function renderBuyAnimation(data = {}) {
  const {
    amount_sol = '1.5',
    amount_usd = '210',
    market_cap = '148K',
    holders = '663',
    wallet = 'ABC...XYZ',
    mascot_url = `file://${path.resolve(__dirname, '../ainl-video/ainl-mascot-official.jpg')}`
  } = data;

  // Load and fill template
  let html = fs.readFileSync(path.join(__dirname, 'template.html'), 'utf8');
  html = html
    .replace('{{MASCOT_URL}}', mascot_url)
    .replace('{{AMOUNT_SOL}}', amount_sol)
    .replace('{{AMOUNT_USD}}', amount_usd)
    .replace('{{MARKET_CAP}}', market_cap)
    .replace('{{HOLDERS}}', holders)
    .replace('{{WALLET}}', wallet);

  const tmpHtml = '/tmp/ainl-buy-frame.html';
  const framesDir = '/tmp/ainl-frames';
  const outputVideo = `/tmp/ainl-buy-${Date.now()}.mp4`;

  fs.writeFileSync(tmpHtml, html);
  fs.mkdirSync(framesDir, { recursive: true });

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: true
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 480, height: 480 });
  await page.goto(`file://${tmpHtml}`, { waitUntil: 'networkidle0' });

  // Capture frames at ~24fps for 3 seconds
  const fps = 24;
  const duration = 3;
  const totalFrames = fps * duration;

  console.log(`Capturing ${totalFrames} frames...`);
  for (let i = 0; i < totalFrames; i++) {
    await page.screenshot({
      path: `${framesDir}/frame${String(i).padStart(4, '0')}.png`
    });
    await new Promise(r => setTimeout(r, 1000 / fps));
  }

  await browser.close();

  // Convert frames to MP4
  console.log('Converting to MP4...');
  execSync(`ffmpeg -y -framerate ${fps} -i ${framesDir}/frame%04d.png -c:v libx264 -pix_fmt yuv420p -vf "scale=480:480" ${outputVideo}`);

  // Cleanup frames
  execSync(`rm -rf ${framesDir}`);

  console.log(`Done: ${outputVideo}`);
  return outputVideo;
}

// Run with test data if called directly
if (require.main === module) {
  renderBuyAnimation({
    amount_sol: '2.4',
    amount_usd: '336',
    market_cap: '156K',
    holders: '671',
    wallet: 'Gy7k...m9Xp'
  }).then(out => console.log('Output:', out)).catch(console.error);
}

module.exports = { renderBuyAnimation };
