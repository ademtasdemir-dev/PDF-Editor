import re, pathlib
# Test für „Fehler melden“: Fehler auslösen, Hinweis prüfen, Bericht als ZIP speichern und Inhalt prüfen
# Aufruf: python3 e2e7_fehlerbericht.py [ausgabeordner]
import sys, json, zipfile, pathlib
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
EDITOR = (HERE.parent/'01_Programm'/'LAGZERO-PDF-Editor.html').as_uri()
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else HERE/'ausgabe_e2e7'); OUT.mkdir(exist_ok=True)
ok = True
def check(cond, msg):
    global ok
    print(('  OK   ' if cond else '  FEHL ') + msg); ok = ok and cond

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1300, 'height':1000}, accept_downloads=True)
    pageerr = []; pg.on('pageerror', lambda e: pageerr.append(str(e)))
    pg.goto(EDITOR)
    check(pg.is_visible('#report'), 'Button „Fehler melden“ sichtbar')
    check(not pg.is_visible('#repBadge'), 'kein Fehlerzähler ohne Fehler')
    # Bericht ohne geöffnete Datei geht auch
    pg.click('#report'); check(pg.is_visible('#rmodal'), 'Dialog öffnet ohne PDF'); check(pg.is_disabled('#rPdf'), 'PDF-Haken ohne Datei gesperrt')
    pg.click('#rClose')

    pg.set_input_files('#file', str(HERE/'testpdfs'/'chrome.pdf')); pg.wait_for_selector('.ln'); pg.wait_for_timeout(600)
    pg.locator('.ln:visible', has_text='Rechnung Nr').first.click(); pg.keyboard.press('Control+A'); pg.keyboard.type('Rechnung Nr. 4712'); pg.wait_for_timeout(300)
    pg.click('#mPara'); pg.locator('.ln:visible', has_text='hiermit stellen').first.click(); pg.keyboard.press('Control+A')
    pg.keyboard.type('Neuer Absatz für den Fehlerbericht-Test.'); pg.wait_for_timeout(300)
    pg.click('#mAdd'); pgel = pg.locator('.page').first; pgel.scroll_into_view_if_needed(); bx = pgel.bounding_box()
    pg.mouse.click(bx['x']+bx['width']*0.5, bx['y']+bx['height']*0.55)
    pg.keyboard.type('Hinzugefügt Qjy'); pg.wait_for_timeout(300); pg.mouse.click(5, 5)
    # erst normal speichern (erzeugt Hinweise mit Textausschnitten -> müssen ohne Haken geschwärzt werden)
    with pg.expect_download() as d: pg.click('#save')
    d.value.save_as(OUT/'chrome_bearbeitet.pdf'); pg.wait_for_timeout(300)
    check(pg.is_visible('#modal'), 'PDF speichern + Pop-up ok'); pg.click('#mClose')
    check(not pg.is_visible('#toast'), 'kein Fehlalarm beim normalen Arbeiten')

    # künstlicher, unbehandelter Fehler (wie ein Programmfehler)
    pg.evaluate("setTimeout(() => { throw new Error('Testfehler: Absturz beim Zeichnen') }, 0)"); pg.wait_for_timeout(600)
    check(pg.is_visible('#toast'), 'Hinweis unten rechts erscheint nach Fehler')
    check(pg.inner_text('#repBadge') == '1', 'Fehlerzähler zeigt 1')
    pg.screenshot(path=str(OUT/'fehler-hinweis.png'))
    pg.click('#tRep'); check(pg.is_visible('#rmodal'), 'Hinweis-Button öffnet den Dialog')
    pg.fill('#rText', 'Testlauf: nach dem Absatz kam ein Absturz.')
    pg.check('#rTexts'); pg.check('#rPdf'); pg.wait_for_timeout(200)
    info = pg.inner_text('#rInfo'); check('Original-PDF' in info and 'Seite 1' in info, 'Vorschau zeigt Änderungen und PDF')
    pg.screenshot(path=str(OUT/'fehler-dialog.png'))
    with pg.expect_download() as d: pg.click('#rZip')
    zp = OUT/d.value.suggested_filename; d.value.save_as(zp)
    check(zp.name.startswith('Fehlerbericht_LAGZERO-PDF-Editor_') and zp.suffix == '.zip', 'ZIP-Name: ' + zp.name)
    check('Gespeichert als' in pg.inner_text('#rSteps'), 'Bestätigung im Dialog')
    with zipfile.ZipFile(zp) as z:
        check(z.testzip() is None, 'ZIP ist gültig (CRC geprüft)')
        names = z.namelist(); check(names == ['INHALT.html', 'bericht.txt', 'bericht.json', 'original.pdf'], 'Dateien: ' + ', '.join(names))
        R = json.loads(z.read('bericht.json'))
        check(z.read('original.pdf') == (HERE/'testpdfs'/'chrome.pdf').read_bytes(), 'original.pdf ist byte-gleich')
        check(len(R['aenderungen']) == 3 and [a['art'] for a in R['aenderungen']] == ['line', 'para', 'add'], 'drei Änderungen erfasst')
        check(R['aenderungen'][0]['text']['nachher'] == 'Rechnung Nr. 4712', 'Text mitgeschickt (mit Haken)')
        check(any('Testfehler' in l and 'ERROR' in l for l in R['protokoll']), 'Absturz steht im Protokoll')
        check(R['version'] == re.search(r"VERSION = '([\d.]+)'", (pathlib.Path(__file__).resolve().parent.parent/'02_Quellcode'/'build.py').read_text(encoding='utf-8')).group(1) and R['beschreibung'].startswith('Testlauf'), 'Version + Beschreibung')
        check('href="bericht.txt"' in z.read('INHALT.html').decode(), 'INHALT.html verlinkt die Dateien')
        (OUT/'bericht-beispiel.txt').write_bytes(z.read('bericht.txt'))
    # ohne Haken: keine Texte, kein PDF
    pg.uncheck('#rTexts'); pg.uncheck('#rPdf')
    with pg.expect_download() as d: pg.click('#rZip')
    zp2 = OUT/'ohne_texte.zip'; d.value.save_as(zp2)
    with zipfile.ZipFile(zp2) as z:
        R2 = json.loads(z.read('bericht.json')); txt = z.read('bericht.txt').decode()
        check('original.pdf' not in z.namelist() and all('text' not in a for a in R2['aenderungen']), 'ohne Haken: keine Texte, kein PDF')
        alles = txt + json.dumps(R2, ensure_ascii=False)
        check('4712' not in alles and 'Neuer Absatz' not in alles and 'Hinzugef' not in alles, 'geänderter Text taucht nirgends auf (auch nicht im Protokoll)')
    # GitHub-Link: öffnet in neuem Fenster, der Editor bleibt mit allen Änderungen offen
    with pg.context.expect_page() as np: pg.click('#rGit')
    url = np.value.url; np.value.close()
    check(url.startswith('https://github.com/') and 'issues' in url and len(url) < 8000, 'GitHub-Formular-Link (' + str(len(url)) + ' Zeichen)')
    check(pg.evaluate('__lz.edits.length') == 3, 'Editor bleibt offen, Änderungen noch da')
    pg.keyboard.press('Escape'); check(not pg.is_visible('#rmodal'), 'Escape schließt den Dialog')
    with pg.expect_download() as d: pg.click('#save', timeout=15000)
    d.value.save_as(OUT/'chrome_bearbeitet2.pdf'); pg.wait_for_timeout(300)
    check(pg.is_visible('#modal'), 'Speichern nach dem Bericht weiterhin ok')
    check(pageerr == ['Testfehler: Absturz beim Zeichnen'], 'keine weiteren Seitenfehler: ' + str(pageerr))
    b.close()
print('ERGEBNIS:', 'ALLES OK' if ok else 'FEHLER GEFUNDEN')
sys.exit(0 if ok else 1)
