// Test der Windows-App (Electron) für „Formular ausfüllen“ (V2.5)
// Aufruf (im Ordner 05_Windows-App, nach dem Kopieren der HTML nach app/editor.html):
//   node apptest_formular.js ../03_Tests/testpdfs/formular2.pdf <ausgabeordner>   (unter Linux mit xvfb-run -a)
const { _electron } = require('playwright-core'); const fs = require('fs'); const path = require('path');
const pdf = path.resolve(process.argv[2]), out = path.resolve(process.argv[3] || 'apptest_out');
fs.mkdirSync(out, { recursive: true });
let ok = true; const check = (c, m) => { console.log((c ? '  OK   ' : '  FEHL ') + m); ok = ok && c; };
(async () => {
  const app = await _electron.launch({ executablePath: require('electron'), args: ['--no-sandbox', __dirname, pdf] });
  const win = await app.firstWindow();
  await win.waitForFunction(() => document.getElementById('status').textContent.includes('Seite(n)'), null, { timeout: 30000 });
  await app.evaluate(({ session }, dir) => {
    global.__dl = [];
    session.defaultSession.on('will-download', (e, item) => { global.__dl.push(item.getFilename()); item.setSavePath(dir + '/' + item.getFilename()); });
  }, out);
  check((await win.innerText('#status')).includes('Formular mit 9 Feldern'), 'Formular erkannt');
  check(await win.evaluate(() => document.getElementById('mForm').classList.contains('on')), 'Modus Formular automatisch an');
  await win.click('.ff[data-field="vorname"]'); await win.keyboard.type('Ayşe Yılmaz');
  await win.click('.ff[data-field="zustimmung"]');
  await win.selectOption('.ff[data-field="land"]', 'Berlin');
  await win.screenshot({ path: path.join(out, 'app_formular.png') });
  await win.click('#save'); await win.waitForTimeout(2500);
  const dl = await app.evaluate(() => global.__dl);
  const file = dl[0] && path.join(out, dl[0]);
  check(file && fs.existsSync(file), 'PDF gespeichert: ' + dl[0]);
  check(await win.isVisible('#modal'), 'Pop-up nach dem Speichern');
  const logs = await win.evaluate(() => window.__lzLog.list.map(l => l.m));
  check(logs.some(m => m.includes('Formular gespeichert: 3 von 3')), '3 Formularfelder in die PDF geschrieben');
  await app.close();
  console.log(ok ? 'ERGEBNIS: ALLES OK' : 'ERGEBNIS: FEHLER GEFUNDEN');
  process.exit(ok ? 0 : 1);
})().catch(e => { console.log('FEHLER', e.message); process.exit(1); });
