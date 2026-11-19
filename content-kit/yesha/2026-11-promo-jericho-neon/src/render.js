const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const mode = process.argv[2] || 'stills', fps = +(process.argv[3] || 60), out = process.argv[4] || 'v.mp4';
  const b = await chromium.launch({args:['--disable-web-security','--allow-file-access-from-files']});
  const p = await b.newPage({viewport:{width:1080, height:1920}, deviceScaleFactor:1});
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  await p.goto('file://' + __dirname + '/web/index.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  const dur = await p.evaluate(() => window.DUR); console.log('dur', dur);
  if (mode === 'stills') {
    const ts = (process.argv[5] || '0.5,1.6,3.0,4.6,6.2,7.4,8.4,9.6,11.2,12.6,14.6,16.4,18.5').split(',').map(Number);
    for (const t of ts) { await p.evaluate(t => window.seek(t), t); await p.screenshot({path:`stills/s_${t.toFixed(2)}.jpg`, type:'jpeg', quality:80}); }
  } else {
    const ff = spawn('ffmpeg', ['-v','error','-y','-f','image2pipe','-c:v','mjpeg','-r',String(fps),'-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out], {stdio:['pipe','inherit','inherit']});
    const n = Math.round(dur * fps);
    for (let i = 0; i < n; i++) { await p.evaluate(t => window.seek(t), i / fps); const buf = await p.screenshot({type:'jpeg', quality:92}); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); if (i % 120 == 0) console.log(i, '/', n); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
