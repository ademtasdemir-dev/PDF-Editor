# LAG|ZERØ PDF Editor

**TESTED. MEASURED. OPTIMIZED.**

Kostenloser PDF-Editor als **eine einzige HTML-Datei**. Läuft komplett offline im Browser, nichts wird hochgeladen. Eine Alternative zu Adobe Acrobat für das Ändern von Text in PDFs.

## Download & Start

**Windows-App (empfohlen):** [`Download/LAGZERO-PDF-Editor-2.5.0-portable.exe`](Download/LAGZERO-PDF-Editor-2.5.0-portable.exe)
öffnen → rechts „Download raw file“ (⤓) → doppelklicken. Keine Installation nötig.
Beim ersten Start zeigt Windows evtl. „Unbekannter Herausgeber“ → *Weitere Informationen* → *Trotzdem ausführen*.

**Ohne Installation im Browser:** [`01_Programm/LAGZERO-PDF-Editor.html`](01_Programm/LAGZERO-PDF-Editor.html)
herunterladen und doppelklicken (Chrome oder Edge).

PDF öffnen, Text ändern, „PDF speichern“. Das Original bleibt unverändert.

## Funktionen
- **Zeile:** eine Zeile anklicken und ändern
- **Absatz:** ganzen Absatz ändern, wird passend neu umbrochen
- **Text hinzufügen:** an beliebiger Stelle
- **Formular ausfüllen** (neu in 2.5): Textfelder, Kästchen, Optionsfelder und Auswahllisten in ausfüllbaren PDFs direkt ausfüllen. Die Werte landen in den echten PDF-Feldern (Formular bleibt ausfüllbar) oder werden auf Wunsch **fest eingebrannt**. Umlaute und türkische Buchstaben (ğ ş ı İ) gehen. Bei Formularen ohne Felder: an die Stelle klicken und schreiben.
- Schrift, Größe, Fett/Kursiv, Farbe, Hintergrund/Textmarker werden übernommen
- **Originalschrift aus dem PDF**; fehlen Buchstaben (PDFs enthalten meist nur die benutzten), nimmt der Editor
  eine PC-Schrift, eine eingebaute gleich aussehende Schrift (Carlito ≙ Calibri, Caladea ≙ Cambria, DejaVu)
  oder ergänzt nur die fehlenden Buchstaben
- Tabellen, Spalten, Aufzählungen und gedrehte Seiten werden erkannt
- **Fehler melden:** Knopf oben rechts. Erstellt offline einen Fehlerbericht (ZIP) zum Verschicken über [GitHub-Issues](https://github.com/sikkkilaci/PDF-Editor/issues) oder Discord. Texte und PDF nur, wenn man es anhakt.

## Grenzen
- Bearbeitungsgeschützte (verschlüsselte) PDFs werden nicht gespeichert.
- Der alte Text wird abgedeckt, nicht aus der Datei entfernt. Nicht zum Schwärzen geeignet.
- Text rutscht nicht nach wie in Word.
- Dynamische XFA-Formulare (manche Behörden-PDFs aus Adobe LiveCycle) lassen sich nicht ausfüllen; dort hilft „Text hinzufügen“.

## Selbst bauen
```
cd 02_Quellcode
npm i pdfjs-dist@3.11.174 pdf-lib@1.17.1 @pdf-lib/fontkit@1.1.1
python build.py
```
Tests: `03_Tests` (Python + Playwright), Windows-App: `05_Windows-App/BAUEN.md`.
Fehlerbericht nachstellen: `python 03_Tests/bericht_nachstellen.py Fehlerbericht_….zip`

## Lizenzen der Bestandteile
Electron (MIT), pdf.js (Apache-2.0), pdf-lib (MIT), @pdf-lib/fontkit (MIT). Schriften: Carlito und Caladea (SIL OFL 1.1), DejaVu (Bitstream Vera / DejaVu License) – siehe `02_Quellcode/schriften/LIZENZ-*.txt`.

---
Programmiert von **Adem Tasdemir** · Kontakt über [Discord](https://discord.gg/TjRhpfgu2c)
