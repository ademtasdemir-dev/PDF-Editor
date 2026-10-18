# Baut den fertigen Editor: python build.py
# Voraussetzung (einmalig, im Ordner 02_Quellcode):
#   npm i pdfjs-dist@3.11.174 pdf-lib@1.17.1 @pdf-lib/fontkit@1.1.1
import os
HERE = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(HERE, 'node_modules')
VERSION = '2.5.0'   # auch in 05_Windows-App/package.json ändern
t = open(os.path.join(HERE, 'editor-quelle.html'), encoding='utf-8').read()
t = t.replace('/*VERSION*/', VERSION)
esc = lambda s: s.replace('</script', '<\\/script')
parts = {'PDFJS': 'pdfjs-dist/build/pdf.min.js', 'PDFLIB': 'pdf-lib/dist/pdf-lib.min.js',
         'FONTKIT': '@pdf-lib/fontkit/dist/fontkit.umd.min.js', 'WORKER': 'pdfjs-dist/build/pdf.worker.min.js'}
for k, p in parts.items():
    t = t.replace('/*%s*/' % k, esc(open(os.path.join(L, p), encoding='utf-8').read()), 1)
# eingebaute freie Schriften (OFL/Bitstream-Vera-Lizenz, siehe schriften/LIZENZ-*.txt)
import base64, json, re
bundle = {}
for fn in sorted(os.listdir(os.path.join(HERE, 'schriften'))):
    m = re.match(r'(Carlito|Caladea|DejaVuSansMono|DejaVuSans|DejaVuSerif)(?:-(Regular|Bold|Italic|BoldItalic))?\.ttf$', fn)
    if not m: continue
    style = m.group(2) or 'Regular'
    key = '%s|%d|%d' % (m.group(1).lower(), 'Bold' in style, 'Italic' in style)
    bundle[key] = base64.b64encode(open(os.path.join(HERE, 'schriften', fn), 'rb').read()).decode()
t = t.replace('/*BUNDLE*/', json.dumps(bundle), 1)
t = t.replace('/*QRSVG*/', open(os.path.join(HERE, 'qr.svg'), encoding='utf-8').read(), 1)
out = os.path.join(HERE, '..', '01_Programm', 'LAGZERO-PDF-Editor.html')
open(out, 'w', encoding='utf-8').write(t)
print('Fertig:', os.path.normpath(out), len(t) // 1024, 'KB')
