import sys, json
from playwright.sync_api import sync_playwright
import pathlib
EDITOR=(pathlib.Path(__file__).resolve().parent.parent/'01_Programm'/'LAGZERO-PDF-Editor.html').as_uri()
def run(pdf, out, acts, shot=None):
  with sync_playwright() as p:
    b=getattr(p, __import__("os").environ.get("BROWSER", "chromium")).launch(); pg=b.new_page(viewport={'width':1300,'height':1000}, accept_downloads=True)
    errs=[]; pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e))); pg.on('console',lambda m: m.type=='error' and errs.append('CONSOLE '+m.text))
    pg.goto(EDITOR); pg.set_input_files('#file',pdf)
    try: pg.wait_for_selector('.ln',timeout=60000)
    except Exception: print('  (keine Textzeilen erkannt)')
    pg.wait_for_timeout(800)
    for a in acts:
      t=a[0]
      if t in('line','para'):
        pg.click('#mLine' if t=='line' else '#mPara'); el=pg.locator('.ln:visible',has_text=a[1]).first; el.scroll_into_view_if_needed(); el.click()
        pg.keyboard.press('Control+A'); pg.keyboard.type(a[2]); pg.wait_for_timeout(250)
        print('  ',t,repr(a[1]),'->',pg.inner_text('#fontChip'))
      elif t=='add':
        pg.click('#mAdd'); pgel=pg.locator('.page').nth(a[1]); pgel.scroll_into_view_if_needed(); bx=pgel.bounding_box()
        pg.mouse.click(bx['x']+a[2]*bx['width'], bx['y']+a[3]*bx['height']); pg.keyboard.type(a[4]); pg.wait_for_timeout(250)
        print('   add ->',pg.inner_text('#fontChip'))
      elif t=='bold': pg.click('#fBold')
      elif t=='ital': pg.click('#fItal')
      elif t=='size': pg.fill('#fSize',str(a[1])); pg.dispatch_event('#fSize','input')
      elif t=='color': pg.evaluate("c=>{const e=document.getElementById('fColor');e.value=c;e.dispatchEvent(new Event('input'))}",a[1])
      elif t=='undo': pg.click('#undo'); print('   undo: edits', pg.evaluate('__lz.edits.length'))
      elif t=='blur': pg.mouse.click(5,5)
    if shot: pg.screenshot(path=shot)
    with pg.expect_download(timeout=30000) as d: pg.click('#save')
    d.value.save_as(out); pg.wait_for_timeout(400)
    print('   STATUS:',pg.inner_text('#status')); w=pg.inner_text('#mWarn').strip()
    if w: print('   WARN:',w.replace('\n',' | '))
    print('   POPUP sichtbar:', pg.is_visible('#modal'), '| Fehler:', errs or 'keine')
    b.close()
if __name__=='__main__':
  run(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), sys.argv[4] if len(sys.argv)>4 else None)
