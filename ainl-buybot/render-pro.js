const puppeteer = require('puppeteer');
const { execSync } = require('child_process');
const fs = require('fs'), path = require('path');

async function render({ mascotPath, amount, wallet, output, fps = 30, duration = 5 }) {
  let html = fs.readFileSync(path.join(__dirname, 'template-pro.html'), 'utf8');
  html = html
    .replace('{{MASCOT_URL}}', `file://${path.resolve(mascotPath)}`)
    .replace('{{AMOUNT}}', amount || '0.42 SOL')
    .replace('{{WALLET}}', wallet ? wallet.slice(0,4) + '...' + wallet.slice(-4) : 'anon');

  const tmpHtml = `/tmp/ainl-pro-${Date.now()}.html`;
  const framesDir = `/tmp/ainl-pro-frames-${Date.now()}`;
  fs.writeFileSync(tmpHtml, html);
  fs.mkdirSync(framesDir, { recursive: true });

  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-web-security', '--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 480, height: 480, deviceScaleFactor: 1 });
  await page.goto(`file://${tmpHtml}`, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 800)); // let fonts/img settle

  const total = fps * duration;
  for (let i = 0; i < total; i++) {
    const t = i / fps;
    await page.evaluate((tSec) => window.renderFrame(tSec), t);
    await page.screenshot({ path: `${framesDir}/f${String(i).padStart(5,'0')}.png`, type: 'png' });
  }
  await browser.close();

  execSync(`ffmpeg -y -framerate ${fps} -i ${framesDir}/f%05d.png \
    -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
    -vf "scale=480:480" "${output}" 2>/dev/null`);

  fs.rmSync(framesDir, { recursive: true });
  fs.unlinkSync(tmpHtml);
  console.log('Rendered:', output);
}

render({
  mascotPath: path.join(__dirname, 'mascot-clean-v2.png'),
  amount: '1.84 SOL',
  wallet: 'GKx...7Rqp',
  output: path.join(__dirname, 'buybot-pro.mp4'),
  fps: 30,
  duration: 5,
});
