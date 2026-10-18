#!/bin/bash
# Holt echte Formular-PDFs (Testsammlungen von pdf.js und pdf-lib, u. a. US-Steuerformular 1040, CCC-Mitgliedsantrag,
# Formulare mit 700+ Feldern, kaputt gebaute Formulare) nach ./echte-formulare und startet den Massentest e2e9.
# Aufruf: bash echte_formulare_holen.sh   (braucht git, python3, playwright, pypdf, poppler-utils)
set -e
cd "$(dirname "$0")"; mkdir -p echte-formulare; cd echte-formulare
[ -d pdflib ] || { git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Hopding/pdf-lib pdflib; git -C pdflib sparse-checkout set assets/pdfs; }
if [ ! -d pdfjs ]; then
  git clone -q --depth 1 --filter=blob:none --no-checkout https://github.com/mozilla/pdf.js pdfjs
  (cd pdfjs && git ls-tree -r -l HEAD test/pdfs | awk '$4 < 3000000 && $5 ~ /\.pdf$/ {print "/"$5}' > /tmp/lz_sparse.txt \
    && git sparse-checkout init --no-cone && cp /tmp/lz_sparse.txt .git/info/sparse-checkout && git checkout -q HEAD)
fi
# nur PDFs mit Formularfeldern
python3 -W ignore - > liste.txt <<'PY'
import glob
from pypdf import PdfReader
for f in sorted(glob.glob('pdfjs/test/pdfs/*.pdf')) + sorted(glob.glob('pdflib/assets/pdfs/*.pdf')):
  try:
    r = PdfReader(f, strict=False)
    if not r.is_encrypted and r.get_fields(): print(f)
  except Exception: pass
PY
echo "$(wc -l < liste.txt) Formulare gefunden"
cd ..
python3 e2e9_echte_formulare.py echte-formulare/ergebnis $(sed 's|^|echte-formulare/|' echte-formulare/liste.txt)
