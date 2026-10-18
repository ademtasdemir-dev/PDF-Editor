# Windows-App bauen

Die App ist der fertige Editor (`01_Programm/LAGZERO-PDF-Editor.html`) in einem eigenen Fenster (Electron).

```
cd 05_Windows-App
mkdir app
copy ..\01_Programm\LAGZERO-PDF-Editor.html app\editor.html
npm i -D electron@38 electron-builder@26 resedit
npx electron-builder --win portable --x64
```
Ergebnis: `dist/LAGZERO-PDF-Editor-<version>-portable.exe` (startet ohne Installation).

Unter Windows geht zusätzlich `--win nsis` für ein Setup mit Startmenü-Eintrag.

Was die App zusätzlich kann:
- PDF per Doppelklick / „Öffnen mit“ / Ziehen auf die .exe öffnen
- „Speichern unter“-Dialog statt Download-Ordner
- Zugriff auf installierte PC-Schriften ohne Nachfrage
- Links (Discord) öffnen im normalen Browser

Test: `apptest.js` (Node + playwright-core, startet die App, öffnet ein PDF, bearbeitet, speichert).
Test „Formular ausfüllen“: `node apptest_formular.js ../03_Tests/testpdfs/formular2.pdf ausgabe`.
Test „Fehler melden“: `node apptest_bericht.js ../03_Tests/testpdfs/lo.pdf ausgabe` (unter Linux mit `xvfb-run -a`).

Version ändern: `02_Quellcode/build.py` (VERSION) **und** `package.json` (version).
