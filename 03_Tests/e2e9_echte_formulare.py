# Massentest „Formular ausfüllen“ mit echten Formularen (z. B. pdf.js-/pdf-lib-Testsammlung, Behördenformulare)
# Füllt in jedem PDF JEDES Feld wie ein Mensch aus (Klick + Tastatur), ändert zusätzlich eine Textzeile,
# fügt Text hinzu, speichert (ausfüllbar und eingebrannt) und prüft das Ergebnis mit pypdf und Poppler.
# Aufruf: python3 e2e9_echte_formulare.py <ausgabeordner> datei1.pdf datei2.pdf ...
import sys, json, pathlib, subprocess, traceback
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
HERE = pathlib.Path(__file__).resolve().parent
EDITOR = (HERE.parent/'01_Programm'/'LAGZERO-PDF-Editor.html').as_uri()
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
FILES = [pathlib.Path(f) for f in sys.argv[2:]]
TXT = 'Test Ä ö ß 12'

def poppler(pdf):
  r = subprocess.run(['pdftoppm', '-png', '-r', '40', '-f', '1', '-l', '1', str(pdf), str(pdf.with_suffix(''))], capture_output=True, text=True, timeout=60)
  err = [l for l in r.stderr.splitlines() if l.strip()]
  return r.returncode == 0, err

def pyvals(pdf, ohne_sig=False):
  r = PdfReader(str(pdf), strict=False)
  return {k: v.get('/V') for k, v in (r.get_fields() or {}).items() if not (ohne_sig and str(v.get('/FT')) == '/Sig')}

def center(loc):
  # in die Bildmitte scrollen: sonst liegt das Element evtl. unter der festen Kopfleiste und der Klick trifft deren Knöpfe
  loc.evaluate('e => e.scrollIntoView({block:"center", inline:"center"})')

def fill_all(pg):
  """Jedes bedienbare Feld einmal ausfüllen. Gibt die erwarteten Werte zurück."""
  exp = {}
  n = pg.locator('.ff').count()
  done_radio = set()
  for i in range(n):
    el = pg.locator('.ff').nth(i)
    info = el.evaluate('e => ({tag:e.tagName, type:e.type, name:e.dataset.field, dis:e.disabled, max:e.maxLength, on:e.dataset.on, multi:e.multiple, cur:e.tagName==="SELECT"?[...e.selectedOptions].map(o=>o.value):null, opts:e.tagName==="SELECT"?[...e.options].map(o=>o.value):null, vis:e.offsetParent!==null})')
    if info['dis'] or not info['vis']: continue
    name = info['name']
    center(el)
    if info['tag'] in ('INPUT', 'TEXTAREA') and info['type'] in ('text', 'password', 'textarea'):
      if name in exp: continue                       # gleiches Feld auf 2. Widget: wird mitgezogen
      t = TXT if info['max'] is None or info['max'] < 0 or info['max'] >= len(TXT) else TXT.replace(' ', '')[:info['max']]
      el.click(timeout=5000); pg.keyboard.press('Control+A'); pg.keyboard.type(t)
      exp[name] = ('text', t)
    elif info['type'] == 'checkbox':
      if name in exp: continue
      before = el.is_checked(); el.click(timeout=5000)
      exp[name] = ('check', not before, info['on'])
    elif info['type'] == 'radio':
      if name in done_radio: continue
      done_radio.add(name)
      # letzten Knopf der Gruppe wählen
      grp = pg.locator('.ff[type=radio]').filter(has=None)
      last = None
      for j in range(n):
        e2 = pg.locator('.ff').nth(j)
        if e2.get_attribute('data-field') == name and e2.get_attribute('type') == 'radio' and not e2.is_disabled(): last = e2
      if last:
        center(last); last.click(timeout=5000)
        exp[name] = ('radio', last.get_attribute('data-on'))
    elif info['tag'] == 'SELECT':
      if name in exp or not info['opts']: continue
      v = [o for o in info['opts'] if o and o not in info['cur']][-1:] or info['opts'][-1:]
      el.select_option(v); exp[name] = ('choice', v[0])
  pg.mouse.click(3, 3)
  return exp

def run_one(br, pdf):
  rep = {'datei': pdf.name}
  pg = br.new_page(viewport={'width': 1300, 'height': 1000}, accept_downloads=True)
  errs = []
  pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:300]))
  pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text[:300]))
  pg.set_default_timeout(20000)
  try:
    global ORIG_ERR
    tmp = OUT/(pdf.stem + '_original.pdf'); tmp.write_bytes(pdf.read_bytes())
    _, oe = poppler(tmp); ORIG_ERR = set(oe) | {l.split(':', 1)[-1].split('(')[0].strip() for l in oe}
    pg.goto(EDITOR); pg.set_input_files('#file', str(pdf))
    pg.wait_for_function('/Seite\\(n\\)|konnte nicht/.test(document.getElementById("status").textContent)', timeout=90000)
    rep['status'] = pg.inner_text('#status')
    rep['felder_editor'] = pg.evaluate('__lz.form.fields.size'); rep['eingaben'] = pg.locator('.ff').count()
    exp = fill_all(pg)
    rep['ausgefuellt'] = len(exp)
    try:
      ff = pg.locator('.ff').first
      if pg.locator('.ff').count(): center(ff)
      pg.screenshot(path=str(OUT/(pdf.stem + '_editor.png')))
    except Exception: pass
    # zusätzlich: eine Textzeile ändern + Text hinzufügen (Zusammenspiel mit Formular)
    if pg.locator('.ln').count():
      pg.click('#mLine'); ln = pg.locator('.ln:visible').first
      try:
        center(ln); ln.click(timeout=5000); pg.keyboard.press('End'); pg.keyboard.type(' X'); pg.mouse.click(3, 3); rep['zeile'] = True
      except Exception as e: rep['zeile'] = 'nicht klickbar: ' + str(e)[:80]
    pg.click('#mForm'); center(pg.locator('.page').first)
    box = pg.locator('.page').first.bounding_box()
    # freie Stelle suchen (kein Feld, keine Zeile) in der sichtbaren Seitenmitte
    pt = pg.evaluate('''([x0,y0,w,h]) => { for (let fy=0.45; fy<0.95; fy+=0.05) for (let fx=0.05; fx<0.95; fx+=0.05){
        const x=x0+w*fx, y=y0+h*fy; if (y < 260 || y > innerHeight-20) continue; const e=document.elementFromPoint(x,y);
        if (e && e.classList.contains('layer')) return [x,y]; } return null; }''', [box['x'], box['y'], box['width'], box['height']])
    if pt: pg.mouse.click(pt[0], pt[1]); pg.keyboard.type('Hinzu'); pg.mouse.click(3, 3)
    rep['edits'] = pg.evaluate('__lz.edits.length')
    for flat in (False, True):
      pg.set_checked('#fFlat', flat) if pg.is_visible('#fFlat') else None
      tag = '_flach' if flat else '_feld'
      with pg.expect_download(timeout=60000) as d: pg.click('#save')
      out = OUT/(pdf.stem + tag + '.pdf'); d.value.save_as(out); pg.wait_for_timeout(300)
      warn = pg.inner_text('#mWarn').strip() if pg.is_visible('#mWarn') else ''
      pg.click('#mClose')
      ok, perr = poppler(out)
      perr = [l for l in perr if l.split(':', 1)[-1].split('(')[0].strip() not in ORIG_ERR and l not in ORIG_ERR]
      r = {'warnung': warn, 'poppler_ok': ok and not perr, 'poppler': perr[:3]}
      if not flat:
        try:
          v = pyvals(out); bad = []
          for k, e in exp.items():
            got = v.get(k)
            if e[0] == 'text' and str(got) != e[1]: bad.append((k, str(got)[:30], e[1]))
            if e[0] == 'check' and (str(got) not in ('/Off', 'None')) != e[1]: bad.append((k, str(got), e[1]))
            if e[0] == 'radio' and str(got).lstrip('/') != e[1]: bad.append((k, str(got), e[1]))
            if e[0] == 'choice' and not (str(got) == e[1] or (isinstance(got, list) and e[1] in [str(x) for x in got])): bad.append((k, str(got)[:30], e[1]))
          if bad:   # zweite Meinung: gespeicherte Datei im Editor wieder öffnen (so sieht es der Nutzer)
            p2 = br.new_page(); p2.goto(EDITOR); p2.set_input_files('#file', str(out))
            p2.wait_for_function('/Seite\\(n\\)/.test(document.getElementById("status").textContent)', timeout=90000)
            ed = p2.evaluate('[...__lz.form.fields.values()].reduce((m,f)=>(m[f.name]=f.value,m),{})'); p2.close()
            def same(k):
              e = exp[k]; v = ed.get(k)
              if e[0] in ('text',): return v == e[1]
              if e[0] == 'check': return (v not in (None, 'Off')) == e[1]
              if e[0] == 'radio': return v == e[1]
              return v == e[1] or (isinstance(v, list) and e[1] in v)
            bad = [b for b in bad if not same(b[0])]
          r['falsche_werte'] = bad[:8]; r['anz_falsch'] = len(bad)
        except Exception as e: r['pypdf_fehler'] = str(e)[:200]
      else:
        try: r['felder_nach_einbrennen'] = len(pyvals(out, True)) if rep['felder_editor'] else 0
        except Exception as e: r['pypdf_fehler'] = str(e)[:200]
      rep[tag[1:]] = r
    rep['alarme'] = pg.evaluate('__lzLog.alarms')
    rep['protokoll_fehler'] = pg.evaluate('__lzLog.list.filter(l=>l.k==="error").map(l=>l.m.slice(0,240)).slice(0,5)')
  except Exception as e:
    rep['ABBRUCH'] = str(e).splitlines()[0][:300]
    try: rep['protokoll_fehler'] = pg.evaluate('__lzLog.list.filter(l=>l.k==="error").map(l=>l.m.slice(0,240)).slice(0,5)')
    except Exception: pass
  rep['js_fehler'] = errs[:5]
  pg.close()
  return rep

with sync_playwright() as p:
  br = getattr(p, __import__("os").environ.get("BROWSER", "chromium")).launch()
  res = []
  for f in FILES:
    r = run_one(br, f); res.append(r)
    prob = (r.get('ABBRUCH') and 'konnte nicht geöffnet' not in r.get('status', '')) or r.get('feld', {}).get('pypdf_fehler') or r.get('js_fehler') or r.get('alarme') or (r.get('feld', {}).get('anz_falsch')) or not r.get('feld', {}).get('poppler_ok', True) or not r.get('flach', {}).get('poppler_ok', True) or r.get('flach', {}).get('felder_nach_einbrennen')
    print(('PROBLEM ' if prob else 'ok      ') + f.name, '| Felder', r.get('felder_editor'), 'ausgefüllt', r.get('ausgefuellt'), '|', json.dumps({k: r[k] for k in r if k not in ('datei', 'status')}, ensure_ascii=False)[:600] if prob else '', flush=True)
  br.close()
json.dump(res, open(OUT/'ergebnis.json', 'w'), ensure_ascii=False, indent=1)
