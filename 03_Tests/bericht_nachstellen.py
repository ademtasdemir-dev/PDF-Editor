# Stellt einen Fehlerbericht aus „Fehler melden“ automatisch nach, damit der Fehler repariert werden kann.
#
# Aufruf:  python3 bericht_nachstellen.py Fehlerbericht_....zip [ausgabeordner]
#
# Was passiert:
#   1. Bericht lesen und kurz zusammenfassen (Version, Browser, Schriften, Fehler im Protokoll)
#   2. Ist original.pdf dabei: Editor headless öffnen, jede Änderung an derselben Stelle wieder öffnen,
#      Text (oder Platzhalter, wenn keine Texte mitgeschickt wurden), Größe, Farbe, Fett/Kursiv setzen
#   3. Speichern, Fehler/Warnungen ausgeben, betroffene Seiten vorher/nachher als PNG nebeneinander
import sys, json, zipfile, pathlib
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
EDITOR = (HERE.parent/'01_Programm'/'LAGZERO-PDF-Editor.html').as_uri()
PLATZHALTER = 'Testtext ÄÖÜ äöü ß Qjy 0123 €'

zp = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else zp.with_suffix('')); out.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(zp) as z:
    z.extractall(out)
R = json.loads((out/'bericht.json').read_text(encoding='utf-8'))

print('=== Bericht ===')
print('Version:', R['version'], '| Programm:', R['umgebung']['programm'], '|', R['umgebung']['browser'], '|', R['umgebung']['system'])
print('Beschreibung:', R['beschreibung'] or '(keine)')
if R['pdf']: print('PDF:', {k: v for k, v in R['pdf'].items() if k != 'datei'})
for f in R['schriften']: print('  Schrift:', f['name'], 'eingebettet' if f['eingebettet'] else 'nicht eingebettet', 'Type0' if f['zusammengesetzt'] else '')
fehler = [l for l in R['protokoll'] if ' ERROR ' in l or ' WARN ' in l]
print('Fehler/Warnungen im Protokoll:', len(fehler))
for l in fehler: print('  ', l[:400])
for a in R['aenderungen']:
    print('  #%d %s S.%d (%s/%s) %spt -> %s%s' % (a['nr'], a['art'], a['seite'], a['x'], a['y'], a['groesse'],
          a['ergebnis']['hinweis'] or a['ergebnis']['schrift'], '  [WARNUNG]' if a['ergebnis']['warnung'] else ''))

if not (out/'original.pdf').exists():
    print('\nKein original.pdf im Bericht: Nachstellen nur mit einem ähnlichen PDF möglich (Schriften siehe oben).')
    sys.exit(0)

print('\n=== Nachstellen ===')
ergebnis = out/'nachgestellt.pdf'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1300, 'height':1000}, accept_downloads=True)
    errs = []
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
    pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.goto(EDITOR); pg.set_input_files('#file', str(out/'original.pdf'))
    pg.wait_for_function('document.getElementById("status").textContent.includes("Seite(n)") || !__lz.bytes', timeout=120000)
    pg.wait_for_timeout(500)
    for a in R['aenderungen']:
        res = pg.evaluate('a => __lzDebug.open(a)', a)
        if res != 'ok':
            print('  #%d: %s' % (a['nr'], res)); continue
        text = a['text']['nachher'] if 'text' in a else ((PLATZHALTER + ' ') * 4)[:max(a['laengeNachher'], 1)] if a['art'] == 'para' else PLATZHALTER
        pg.keyboard.press('Control+A'); pg.keyboard.type(text.replace('\n', ' ') if a['art'] != 'para' else text)
        pg.evaluate('a => __lzDebug.style(a)', a); pg.wait_for_timeout(250)
        print('  #%d %s -> Chip: %s' % (a['nr'], a['art'], pg.inner_text('#fontChip')))
    F = R.get('formular') or {}
    if F.get('werte'):   # ab V2.5: Formularwerte (nur wenn „Texte mitschicken“ angehakt war)
        for w in F['werte']:
            print('  Formularfeld %s -> %s' % (w['feld'], pg.evaluate('w => __lzDebug.form(w.feld, w.wert)', w)))
    elif F.get('geaendert'):
        print('  Formular: %d Felder geändert, Werte nicht im Bericht' % F['geaendert'])
    if F.get('einbrennen'): pg.check('#fFlat')
    pg.mouse.click(5, 5)
    with pg.expect_download(timeout=60000) as d: pg.click('#save')
    d.value.save_as(ergebnis); pg.wait_for_timeout(400)
    print('Status:', pg.inner_text('#status'))
    w = pg.inner_text('#mWarn').strip()
    if w: print('Warnungen:', w.replace('\n', ' | '))
    print('Fehler beim Nachstellen:', errs or 'keine')
    b.close()

try:
    try: import pymupdf as fitz
    except ImportError: import fitz
    seiten = sorted({a['seite'] for a in R['aenderungen']})[:6]
    a, n = fitz.open(out/'original.pdf'), fitz.open(ergebnis)
    for s in seiten:
        pa, pn = a[s-1].get_pixmap(dpi=90), n[s-1].get_pixmap(dpi=90)
        bild = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, pa.width + pn.width + 20, max(pa.height, pn.height)), False)
        bild.clear_with(255); bild.copy(pa, pa.irect)
        pn.set_origin(pa.width + 20, 0); bild.copy(pn, pn.irect)
        bild.save(out/('vorher-nachher-seite-%d.png' % s))
        print('Bild:', out/('vorher-nachher-seite-%d.png' % s))
except ImportError:
    print('(pip install pymupdf für Vorher/Nachher-Bilder)')
print('Ergebnis-PDF:', ergebnis)
