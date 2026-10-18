# Test „Formular ausfüllen“ (V2.5): echte Klicks/Tastatur im Editor, danach Prüfung der gespeicherten PDF mit pypdf + Bild
# Aufruf: python3 e2e8_formular.py   (vorher: python3 testpdfs_erzeugen.py im Ordner testpdfs, für formular2.pdf)
import pathlib, subprocess, sys
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
HERE = pathlib.Path(__file__).resolve().parent
EDITOR = (HERE.parent/'01_Programm'/'LAGZERO-PDF-Editor.html').as_uri()
T = HERE/'testpdfs'; OUT = HERE/'ergebnis-formular'; OUT.mkdir(exist_ok=True)
ok = fail = 0
def check(name, cond, info=''):
  global ok, fail
  if cond: ok += 1; print('  OK  ', name)
  else: fail += 1; print('  FEHLER', name, info)

def vals(pdf):
  r = PdfReader(str(pdf)); out = {}
  for k, v in (r.get_fields() or {}).items(): out[k] = v.get('/V')
  return r, out

def session(pdf, fn, flat=False, shot=None):
  with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1300, 'height':1100}, accept_downloads=True)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.goto(EDITOR); pg.set_input_files('#file', str(pdf))
    pg.wait_for_function('document.getElementById("status").textContent.includes("Seite(n)")', timeout=60000)
    res = fn(pg)
    if flat: pg.check('#fFlat')
    if shot: pg.screenshot(path=str(OUT/shot), full_page=False)
    out = OUT/(pdf.stem + ('_flach' if flat else '') + '_ausgefuellt.pdf')
    with pg.expect_download(timeout=30000) as d: pg.click('#save')
    d.value.save_as(out); pg.wait_for_timeout(300)
    warn = pg.inner_text('#mWarn').strip(); st = pg.inner_text('#status')
    b.close()
  return out, res, errs, warn, st

def img(pdf, name):
  r = subprocess.run(['pdftoppm', '-png', '-r', '70', '-f', '1', '-l', '1', str(pdf), str(OUT/name)], capture_output=True, text=True)
  check('PDF fehlerfrei lesbar (Poppler): ' + name, r.returncode == 0 and not r.stderr.strip(), r.stderr.strip()[:200])

print('### 1 Alle Feldarten per Klick/Tastatur (formular2.pdf)')
def fill(pg):
  r = {}
  r['status'] = pg.inner_text('#status')
  r['modus'] = pg.evaluate('document.getElementById("mForm").classList.contains("on")')
  r['felder'] = pg.locator('.ff').count()
  r['flatSichtbar'] = pg.is_visible('#flatWrap')
  pg.click('.ff[data-field="vorname"]'); pg.keyboard.type('Adem Çağrı')
  pg.click('.ff[data-field="nachname"]'); pg.keyboard.press('Control+A'); pg.keyboard.type('Taşdemir-Öztürk')
  pg.click('.ff[data-field="plz"]'); pg.keyboard.type('97225999')            # maxLen 5 -> 97225
  pg.locator('.ff[data-field="geschlecht"]').nth(0).check()                  # m
  pg.click('.ff[data-field="zustimmung"]')                                    # an
  pg.click('.ff[data-field="newsletter"]')                                    # aus
  pg.select_option('.ff[data-field="land"]', 'Hessen')
  pg.select_option('.ff[data-field="kurs"]', 'FISI')
  pg.click('.ff[data-field="bemerkung"]'); pg.keyboard.type('Zeile eins ä ö ü ß'); pg.keyboard.press('Enter'); pg.keyboard.type('Zeile zwei €')
  pg.mouse.click(5, 300)  # Fokus weg -> change
  r['az_disabled'] = pg.evaluate('document.querySelector(\'.ff[data-field="az"]\')')
  r['undo_aktiv'] = not pg.is_disabled('#undo')
  r['geaendert'] = pg.evaluate('__lz.form.changed.size')
  # Text hinzufügen im Formular-Modus (freie Stelle unten: Ort, Datum)
  pg.evaluate('window.scrollTo(0, 450)'); pg.wait_for_timeout(200)
  box = pg.locator('.page').first.bounding_box()
  pg.mouse.click(box['x'] + box['width']*0.13, box['y'] + box['height']*0.665); pg.keyboard.type('Würzburg, 18.10.2026')
  pg.mouse.click(5, 300)
  r['edits'] = pg.evaluate('__lz.edits.length')
  return r
out, r, errs, warn, st = session(T/'formular2.pdf', fill, shot='editor-formular.png')
check('Formular erkannt + Modus Formular an', r['modus'] and 'Formular mit 9 Feldern' in r['status'], r['status'])
check('11 Eingabefelder (3 Optionsknöpfe, schreibgeschütztes bleibt Bild)', r['felder'] == 11, r['felder'])
check('Schreibgeschütztes Feld bleibt im Bild (kein Eingabefeld)', r['az_disabled'] is None)
check('„Fest einbrennen“ sichtbar', r['flatSichtbar'])
check('9 Felder geändert, Rückgängig aktiv', r['geaendert'] == 9 and r['undo_aktiv'], r)
check('Text im Formular-Modus hinzugefügt', r['edits'] == 1)
check('keine JS-Fehler', not errs, errs)
check('keine Warnungen beim Speichern', not warn, warn)
rd, v = vals(out)
exp = {'vorname':'Adem Çağrı', 'nachname':'Taşdemir-Öztürk', 'plz':'97225', 'geschlecht':'/m', 'zustimmung':'/Yes',
       'newsletter':'/Off', 'land':'Hessen', 'kurs':'FISI', 'bemerkung':'Zeile eins ä ö ü ß\nZeile zwei €', 'az':'AZ-2026-001'}
for k, e in exp.items(): check('Wert ' + k, str(v.get(k)) == e, repr(v.get(k)))
text = rd.pages[0].extract_text()
check('Text „Würzburg, 18.10.2026“ auf der Seite', 'Würzburg, 18.10.2026' in text, text[-200:])
check('Formular bleibt ausfüllbar (Felder vorhanden)', len(v) == 10)
img(out, 'formular2-ausgefuellt')

print('### 2 Wieder öffnen: Werte werden angezeigt (auch ğ ş)')
def reopen(pg):
  return pg.evaluate('[...__lz.form.fields.values()].reduce((m,f)=>(m[f.name]=f.value,m),{})')
out2, r2, errs2, _, _ = session(out, reopen)
check('vorname wieder da', r2.get('vorname') == 'Adem Çağrı', r2.get('vorname'))
check('Kästchen/Optionsfeld wieder da', r2.get('zustimmung') == 'Yes' and r2.get('geschlecht') == 'm', r2)
check('Liste wieder da', r2.get('kurs') == ['FISI'], r2.get('kurs'))
check('keine JS-Fehler beim Wiederöffnen', not errs2, errs2)

print('### 3 Rückgängig + fest einbrennen')
def undo_flat(pg):
  pg.click('.ff[data-field="vorname"]'); pg.keyboard.type('Max'); pg.mouse.click(5, 300)
  pg.click('.ff[data-field="zustimmung"]')
  pg.click('#undo')  # Kästchen zurück
  return {'zust': pg.is_checked('.ff[data-field="zustimmung"]'), 'n': pg.evaluate('__lz.form.changed.size')}
out3, r3, errs3, warn3, _ = session(T/'formular2.pdf', undo_flat, flat=True)
check('Rückgängig nimmt Kästchen zurück', r3['zust'] is False and r3['n'] == 1, r3)
rd3, v3 = vals(out3)
check('Eingebrannt: keine Felder mehr', not v3, v3)
t3 = rd3.pages[0].extract_text()
check('Eingebrannt: „Max“ und „Muster“ als Text sichtbar', 'Max' in t3 and 'Muster' in t3, t3[:300])
check('keine Fehler/Warnungen', not errs3 and not warn3, (errs3, warn3))
img(out3, 'formular2-eingebrannt')

print('### 4 Altes Test-Formular (reportlab, ein Feld) + Zeile ändern')
def old(pg):
  pg.click('.ff[data-field="name"]'); pg.keyboard.press('Control+A'); pg.keyboard.type('Erika Musterfrau'); pg.mouse.click(5, 300)
  pg.click('#mLine'); pg.locator('.ln:visible', has_text='Hinweis').first.click(); pg.keyboard.press('Control+A'); pg.keyboard.type('Hinweis: geändert')
  pg.mouse.click(5, 300); return None
out4, _, errs4, warn4, _ = session(T/'formular.pdf', old)
rd4, v4 = vals(out4)
check('Feld name gesetzt', v4.get('name') == 'Erika Musterfrau', v4)
check('Zeile geändert', 'Hinweis: geändert' in rd4.pages[0].extract_text())
check('keine Fehler', not errs4 and not warn4, (errs4, warn4))
img(out4, 'formular1')

print('### 5 PDF ohne Felder: Formular-Modus = an die Stelle klicken und schreiben')
def nofields(pg):
  st = pg.inner_text('#status'); pg.click('#mForm'); st2 = pg.inner_text('#status')
  box = pg.locator('.page').first.bounding_box(); pg.mouse.click(box['x'] + 200, box['y'] + 400); pg.keyboard.type('X')
  pg.mouse.click(5, 300)
  return st, st2, pg.evaluate('__lz.edits.length')
out5, r5, errs5, _, _ = session(T/'lo.pdf', nofields)
check('Kein Formular-Hinweis beim Laden', 'Formular' not in r5[0], r5[0])
check('Hinweis „keine ausfüllbaren Felder“', 'keine ausfüllbaren Felder' in r5[1], r5[1])
check('Klick setzt Text', r5[2] == 1)
check('keine Fehler', not errs5, errs5)

print('\nERGEBNIS: %d OK, %d Fehler' % (ok, fail))
sys.exit(1 if fail else 0)
