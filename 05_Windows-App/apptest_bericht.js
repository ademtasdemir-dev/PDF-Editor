// Test der Windows-App (Electron) für „Fehler melden“: ZIP-Speichern-Dialog, GitHub-Link im normalen Browser, Zwischenablage
// Aufruf (im Ordner 05_Windows-App, nach dem Kopieren der HTML nach app/editor.html):
//   node apptest_bericht.js ../03_Tests/testpdfs/lo.pdf <ausgabeordner>
const { _electron } = require('playwright-core'); const fs = require('fs'); const path = require('path');
const pdf = path.resolve(process.argv[2]), out = path.resolve(process.argv[3] || 'apptest_out');
fs.mkdirSync(out, { recursive: true });
let ok = true; const check = (c, m) => { console.log((c ? '  OK   ' : '  FEHL ') + m); ok = ok && c; };
(async () => {
  const app = await _electron.launch({ executablePath: require('electron'), args: ['--no-sandbox', __dirname, pdf] });
  const win = await app.firstWindow(); await win.waitForSelector('.ln', { timeout: 30000 }); await win.waitForTimeout(800);
  // Speichern-Dialog abfangen: Titel/Filter merken, Datei in den Ausgabeordner legen
  await app.evaluate(({ session, shell }, dir) => {
    global.__dl = [];
    session.defaultSession.on('will-download', (e, item) => {
      const o = item.getSaveDialogOptions(); global.__dl.push({ name: item.getFilename(), title: o.title, ext: o.filters && o.filters[0].extensions[0] });
      item.setSavePath(dir + '/' + item.getFilename());
    });
    global.__ext = []; shell.openExternal = async u => { global.__ext.push(u); };
  }, out);
  check((await win.innerText('#status')).includes('Seite(n)'), 'PDF per Startparameter geöffnet');
  await win.locator('.ln:visible', { hasText: 'Bescheinigung' }).first().click(); await win.keyboard.press('Control+A'); await win.keyboard.type('App-Test Bescheinigung');
  await win.mouse.click(5, 5);
  await win.click('#report'); check(await win.isVisible('#rmodal'), 'Dialog in der App');
  await win.fill('#rText', 'App-Test'); await win.check('#rPdf');
  await win.click('#rZip'); await win.waitForTimeout(1500);
  const dl = await app.evaluate(() => global.__dl);
  check(dl.length === 1 && dl[0].ext === 'zip' && dl[0].title === 'Fehlerbericht speichern', 'Speichern-Dialog für ZIP: ' + JSON.stringify(dl[0]));
  check(fs.existsSync(path.join(out, dl[0].name)), 'ZIP gespeichert');
  check((await win.innerText('#rSteps')).includes('Gespeichert als') && !(await win.innerText('#rSteps')).includes('Download-Ordner'), 'Bestätigung ohne „Download-Ordner“');
  const n0 = app.windows().length; await win.click('#rGit'); await win.waitForTimeout(800);
  const ext = await app.evaluate(() => global.__ext);
  check(app.windows().length === n0 && win.url().startsWith('file:'), 'GitHub öffnet kein App-Fenster, Editor bleibt');
  check(ext.length === 1 && ext[0].startsWith('https://github.com/ademtasdemir-dev/PDF-Editor/issues/new?'), 'GitHub-Link geht an den normalen Browser');
  await win.click('#rCopy'); await win.waitForTimeout(400);
  const clip = await app.evaluate(({ clipboard }) => clipboard.readText());
  check(clip.startsWith('LAGZERO PDF Editor – Fehlerbericht') && clip.includes('Windows-App (Electron'), 'Text kopiert (Zwischenablage), Programm = Windows-App');
  await win.screenshot({ path: path.join(out, 'app_bericht.png') });
  await win.click('#rClose');
  await win.click('#save'); await win.waitForTimeout(2500);
  const dl2 = await app.evaluate(() => global.__dl);
  check(dl2.length === 2 && dl2[1].ext === 'pdf', 'PDF-Speichern weiterhin mit PDF-Filter');
  check(await win.isVisible('#modal'), 'Pop-up nach dem Speichern');
  await app.close();
  console.log('ERGEBNIS:', ok ? 'ALLES OK' : 'FEHLER GEFUNDEN'); process.exit(ok ? 0 : 1);
})().catch(e => { console.error('FEHLER', e.message); process.exit(1); });
