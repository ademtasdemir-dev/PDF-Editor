# LAGZERO PDF Editor – Projektanweisungen

Diesen Text in die **Anweisungen** des claude.ai-Projekts einfügen. Die Ordner `02_Quellcode`, `03_Tests` und `04_Version-1` als **Projektwissen** hochladen. Die fertige Datei aus `01_Programm` ist rund 2,5 MB groß, weil alle Bibliotheken eingebaut sind; sie muss nicht ins Projektwissen.

**Aktueller Stand: Version 2.5 (18.10.2026)** – neu: **Formular ausfüllen**. Seit 2.4 Knopf „Fehler melden“, seit 2.3 auch als Windows-App (portable .exe).

Download Windows-App: https://github.com/sikkkilaci/PDF-Editor/blob/main/Download/LAGZERO-PDF-Editor-2.5.0-portable.exe

GitHub: https://github.com/sikkkilaci/PDF-Editor

## Ziel
Ein kostenloser, offline laufender PDF-Editor als einzelne HTML-Datei, als Alternative zu Adobe Acrobat. Ursprünglich für einen Bekannten von Adem, der Text in einem PDF ändern will, ohne Online-Dienste zu nutzen. Die Formatierung soll so originalgetreu wie möglich erhalten bleiben.

## Festgelegte Anforderungen (aus dem ersten Chat)
- Läuft komplett lokal im Browser (Chrome/Edge empfohlen), keine Uploads, kein Internet nötig.
- Prinzip: Originaltext wird abgedeckt und an derselben Stelle als bearbeitbares Feld mit dem Originaltext geöffnet.
- **Zeilen-Modus:** einzelne Zeile anklicken und ändern.
- **Absatz-Modus:** ganzen Absatz bearbeiten; beim Speichern wird passend zur Absatzbreite und zum Zeilenabstand neu umbrochen. Kein echtes Nachrutschen wie in Word (bewusst akzeptiert).
- **Text hinzufügen:** an beliebiger Stelle neuen Text setzen.
- Schrift, Größe, Stil (fett/kursiv), Farbe, Position und Hintergrund/Textmarker werden erkannt und übernommen.
- Schriften (Reihenfolge ab V2.2):
  1. Originalschrift aus dem PDF, wenn alle Zeichen drin sind.
  2. Gleich aussehende Schrift für die ganze Zeile: eigene Schriftdatei → installierte PC-Schrift (Freigabe wird automatisch angefragt) → **eingebaute freie Schrift** (Carlito = Calibri, Caladea = Cambria, DejaVu Sans/Serif/Sans Mono = echt).
  3. **Mischen:** vorhandene Zeichen in Originalschrift, nur fehlende Zeichen aus der besten Ersatzschrift (Hinweis im Chip, z. B. „nur Q J y fehlen“).
  4. Erst dann ganze Zeile in Helvetica/Times/Courier mit Warnung.
- Design: **LAG|ZERØ** (schwarz/silber/rot, Eyebrow „ʟᴀɢᴢᴇʀᴏ // PDF EDITOR“, Logo „LAG|ZERØ VERIFIED“, Slogan „TESTED. MEASURED. OPTIMIZED.“, Copyright-Zeile wie auf den anderen LAGZERO-Seiten, Vorlage: lagzero-lab/de/nvidia-verstehen.html).
- Nach jedem Speichern Pop-up: „Dieses Programm wurde programmiert von Adem Tasdemir“, Kontakt über Discord, Button + QR-Code zu https://discord.gg/TjRhpfgu2c.
- Downloads zusätzlich immer als ZIP; bei Dateisammlungen ein anklickbares HTML-Inhaltsverzeichnis.

## Formular ausfüllen (neu in 2.5)
- Knopf **„Formular“** in der Modus-Leiste. Hat das PDF ausfüllbare Felder (AcroForm), schaltet der Editor beim Öffnen automatisch in diesen Modus und meldet „Formular mit N Feldern erkannt“.
- Unterstützt: Textfeld (einzeilig, mehrzeilig, Passwort, max. Zeichen, Kammfeld), Kontrollkästchen, Optionsfelder (Radio), Auswahlliste (Dropdown), Liste (auch Mehrfachauswahl). Felder mit demselben Namen (z. B. Name auf Seite 1 und 3) werden gleichzeitig aktualisiert. Tab springt von oben nach unten.
- Technik: pdf.js rendert die Seite mit `AnnotationMode.ENABLE_FORMS`, dadurch fehlen genau die ausfüllbaren Felder im Bild; darüber liegen echte HTML-Eingabefelder (`.ff`, Ebene `.fl`). Schreibgeschützte Textfelder, Unterschriftsfelder und Knöpfe bleiben im Bild (pdf.js `hasOwnCanvas`/Signatur/PushButton).
- Speichern: pdf-lib `getForm()` → `setText`/`check`/`select` nur für geänderte Felder, Aussehen neu erzeugt. Schrift Helvetica; enthält ein Wert Zeichen außerhalb WinAnsi (z. B. ğ ş ı İ), wird die eingebaute DejaVu Sans eingebettet und `NeedAppearances` auf false gesetzt. XFA-Anteile werden entfernt (sonst zeigt Acrobat alte Werte).
- **„Felder fest einbrennen“** (Haken neben „Formular“): `form.flatten()`. pdf-lib lässt dabei bei Optionsknöpfen tote Verweise in `/Annots` stehen (Poppler/Adobe: „Invalid XRef“) → werden danach entfernt.
- Formulare **ohne** Felder: im Formular-Modus an eine freie Stelle klicken = Text hinzufügen (z. B. „X“ ins Kästchen).
- Rückgängig gilt auch für Formularfelder (gemeinsamer Verlauf `S.acts`). Fehlerbericht enthält Anzahl/Arten der Felder, Werte nur mit Haken „Geänderte Texte mitschicken“. `bericht_nachstellen.py` setzt die Werte wieder (`__lzDebug.form(name, wert)`).
- Dynamische XFA-Formulare (ohne AcroForm-Felder) werden nicht unterstützt → Hinweis in der Statuszeile.

## Fehler melden (neu in 2.4)
- Knopf **„Fehler melden“** rechts in der Werkzeugleiste. Im Hintergrund schreibt der Editor ein Protokoll mit (Öffnen, Bearbeiten, Schriftwahl, Speichern, Warnungen, Fehler mit Stacktrace; max. 400 Einträge, nur im Speicher).
- Bei einem echten Fehler (Absturz, Speichern/Öffnen fehlgeschlagen, Seite nicht anzeigbar) erscheint unten rechts ein Hinweis mit Knopf, der Fehler-Knopf zeigt einen roten Zähler. Harmlose Meldungen (z. B. pdf.js-„fake worker“ bei file://) lösen keinen Alarm aus.
- Dialog: Beschreibung, Haken „Geänderte Texte mitschicken“ und „Original-PDF mitschicken“ (beide standardmäßig **aus**; ohne Haken werden auch zitierte Texte im Protokoll geschwärzt), Vorschau des Berichts.
- **Bericht speichern (ZIP):** `INHALT.html` (anklickbar), `bericht.txt`, `bericht.json`, ggf. `original.pdf`. Alles offline, eigener ZIP-Schreiber ohne Bibliothek.
- **Auf GitHub melden:** öffnet https://github.com/sikkkilaci/PDF-Editor/issues/new mit ausgefülltem Titel/Text, ZIP dort hineinziehen (GitHub-Konto nötig). **Text kopieren** + **Discord** für alle ohne GitHub.
- **Reparieren:** `python 03_Tests/bericht_nachstellen.py Fehlerbericht_….zip` liest den Bericht, öffnet das Original-PDF headless, öffnet jede Änderung an derselben Stelle wieder (über `window.__lzDebug`), setzt Text (oder Platzhalter mit Umlauten, wenn keine Texte dabei sind), Größe, Farbe, Fett/Kursiv, speichert und legt Vorher/Nachher-Bilder ab.
- Windows-App: ZIP-Speichern-Dialog mit ZIP-Filter, Zwischenablage erlaubt, GitHub-Link im normalen Browser.

## Windows-App (neu in 2.3)
- Ordner `05_Windows-App`: Electron 38, `main.js`, Bau mit electron-builder (`--win portable`), Symbol/Versionsinfo per `afterPack.js` (resedit, ohne Wine). Anleitung: `05_Windows-App/BAUEN.md`.
- Ergebnis: `LAGZERO-PDF-Editor-<version>-portable.exe` (~85 MB, keine Installation). Liegt im Repo unter `Download/` (Releases kann Claude aus dieser Sitzung nicht anlegen; bei Bedarf selbst als Release hochladen).
- Extras: PDF per Doppelklick/„Öffnen mit“/Ziehen auf die .exe, „Speichern unter“-Dialog, PC-Schriften ohne Nachfrage, Discord-Link im normalen Browser.
- Nicht signiert → Windows SmartScreen zeigt beim ersten Start „Unbekannter Herausgeber“ (Weitere Informationen → Trotzdem ausführen). Ein Setup-Installer (NSIS) lässt sich nur unter Windows bauen.

## Technik
- pdf.js 3.11.174 (Anzeige, Textpositionen, Schriftdaten mit `fontExtraProperties`), pdf-lib 1.17.1 (Speichern), @pdf-lib/fontkit 1.1.1 (eingebettete PC-Schriften).
- **Version:** `VERSION` in `02_Quellcode/build.py` (erscheint im Fuß und im Fehlerbericht) und `05_Windows-App/package.json`.
- **Bauen:** im Ordner `02_Quellcode` einmalig `npm i pdfjs-dist@3.11.174 pdf-lib@1.17.1 @pdf-lib/fontkit@1.1.1`, dann `python build.py` → schreibt `01_Programm/LAGZERO-PDF-Editor.html`.
- **Originalschrift:** Der Editor schreibt neuen Text direkt mit der Schrift-Ressource der Seite (`Tf`/`TJ`). Zeichencodes kommen aus der umgekehrten ToUnicode-Tabelle; ob ein Glyph in der eingebetteten Teilschrift existiert, wird über `toFontChar` + fontkit geprüft. Ressource wird über BaseFont **und** Subtype (Type0 ja/nein) gefunden.
- **Fehlende Breiten (neu in 2.1):** Word schreibt bei einfachen Schriften nur Breiten für benutzte Zeichen (Rest = 0). Der Editor berechnet fehlende Breiten (eingebettet: aus der Schrift per fontkit; nicht eingebettet wie Arial/Times/Courier: aus den metrisch gleichen Standardschriften) und trägt sie beim Speichern ins `Widths`-Array ein.
- **Zeilenerkennung (neu in 2.1):** breite Leer-Stücke von pdf.js trennen Spalten/Tabellenzellen; Aufzählungszeichen sind eigene Zeilen und bleiben stehen; Zeilengröße = Größe mit den meisten Zeichen; Leerzeichen am Zeilenanfang zählen nicht.
- **Eingebaute Schriften:** `02_Quellcode/schriften/` (Latin-Teilmenge, ohne Hinting, ~570 KB). `build.py` bettet sie als JSON/Base64 ein. Lizenzen: OFL 1.1 (Carlito, Caladea), Bitstream Vera/DejaVu (siehe `LIZENZ-*.txt`). Fertige HTML: ~3,2 MB.
- Farben: aus einem zweiten Rendern ohne Anmerkungen per Farbhistogramm; Textfarbe = kräftigster Farbton mit genug Pixeln (nicht die grauen Kantenpixel).
- Abdeckung: Rechteck in Hintergrundfarbe, dann neuer Text.
- **Gedrehte Seiten (/Rotate 90/180/270, neu in 2.3):** Seite wird ungedreht bearbeitet und nur per CSS gedreht angezeigt; Klickfelder und neuer Text liegen dadurch immer richtig.
- Neuer Text („Text hinzufügen“) ist schwarz, außer man hat vorher selbst eine Farbe gewählt (vorher wurde z. B. Weiß der letzten Zeile übernommen → unsichtbar).
- Fett/Kursiv bei Standardschriften (Helvetica/Arial/Times/Courier) gilt nicht mehr als „Ersatzschrift“.
- Verschlüsselte PDFs: Speichern wird mit Hinweis abgebrochen (sonst kaputte Datei). Workaround: in Chrome drucken → „Als PDF speichern“.

## Getestet
**Testdateien (Headless-Chrome + Prüfung der gespeicherten PDFs als Bild):**
- Zeile, Absatz, Text hinzufügen, Rückgängig, Markierung bleibt gelb, rote Schrift bleibt rot.
- Eingebettete Teilschriften (einfach und Type0), fehlendes Zeichen → Warnung + Ersatzschrift, manuelle Schriftdatei.
- Pop-up mit Discord-Button und QR-Code.

**Echte PDFs (10.10.2026):**
- Word-PDF mit nicht eingebettetem Arial (Bewerbung): Zeilen + Absatz in Original-Arial. Fehler „Buchstaben übereinander“ gefunden und behoben.
- Word-PDF mit Calibri-Teilschrift (ComCave-Anleitung): Absatz in Original-Calibri. Fehlen Zeichen in der Teilschrift (z. B. „U“, „c“ in Calibri Bold), wird korrekt gewarnt.
- Telekom-PDF, 58 Seiten, CID-Schriften: lädt in ca. 4 s; Tabellenkopf, Aufzählung, Preistabelle bearbeitet. Fehler „Spalten verschmolzen + Tabellenlinie gelöscht“, „graue statt schwarze Schrift“, „Aufzählungen als ein Absatz“ gefunden und behoben.
- Alle alten Tests danach erneut grün.
- **V2.3 Funktionstest** (`03_Tests/e2e6_suite.sh`, 11 Test-PDFs in `03_Tests/testpdfs`): Querformat mit Farben/kursiv/weiß auf grün, zweispaltig, gedreht 90/180/270, verschobene CropBox, Formular (Feld bleibt), Scan (nur Text hinzufügen), Chrome-PDF (Liberation/DejaVu, Tabelle, Aufzählung, Textmarker), LibreOffice/Word-artig (Carlito/Caladea), 40 Seiten (ca. 8 s). Geprüft: Zeile, Absatz, Hinzufügen, Fett, Kursiv, Größe, Farbe, Rückgängig, Speichern, Pop-up. Gefunden und behoben: unsichtbarer neuer Text, gedrehte Seiten, falsche Ersatzschrift-Warnung. Alle Ergebnisse als Bild geprüft.
- **V2.5 Formular ausfüllen** (`03_Tests/e2e8_formular.py`, 38 Prüfungen, Test-PDF `testpdfs/formular2.pdf` mit allen Feldarten): echte Klicks/Tastatur, Werte per pypdf geprüft (inkl. „Adem Çağrı“, „Taşdemir-Öztürk“, mehrzeilig mit ä ö ü ß €), PLZ auf 5 Zeichen begrenzt, Wiederöffnen zeigt Werte, Rückgängig, Einbrennen (keine Felder mehr, Text sichtbar, Poppler fehlerfrei), altes Formular + Zeile ändern zusammen, PDF ohne Felder → Klick setzt Text. Gefunden und behoben: tote Verweise nach dem Einbrennen. App-Test `05_Windows-App/apptest_formular.js` grün. e2e6-Suite und e2e7 danach erneut grün. Bilder: `03_Tests/screenshot-formular.png`, `03_Tests/ergebnis-formular-ausgefuellt-eingebrannt.png`.
- **V2.4 Fehler melden** (`03_Tests/e2e7_fehlerbericht.py`, 27 Prüfungen): Hinweis + Zähler nach Absturz, kein Fehlalarm bei normaler Arbeit, ZIP gültig (CRC), original.pdf byte-gleich, ohne Haken tauchen keine Texte auf (auch nicht im Protokoll), GitHub-Link öffnet neues Fenster und der Editor bleibt mit allen Änderungen offen, Speichern danach weiter ok. Gefundener und behobener Fehler: GitHub-Knopf hat den Editor verlassen (Änderungen weg). `bericht_nachstellen.py` mit und ohne Texte getestet (gleiche Schrift-Ergebnisse wie im Bericht). App-Test `05_Windows-App/apptest_bericht.js` (10 Prüfungen) grün. e2e6-Suite danach erneut grün.
- **Windows-App** mit derselben Programmlogik unter Electron getestet (`05_Windows-App/apptest.js`): Öffnen per Startparameter, Bearbeiten, Speichern, Pop-up, Discord-Link, PC-Schriften (310 gefunden). Die .exe selbst konnte nicht unter Windows gestartet werden.
- V2.2: Bank-PDF (Volksbank, Schriften GenosGFG + DejaVu Sans Mono, Teilschriften ohne Q/X/j/x/y): vorher ganze Zeile Helvetica (sofort sichtbar), jetzt Brieftext in echter DejaVu Sans Mono und GenosGFG gemischt (nur fehlende Buchstaben in Helvetica). Calibri-Teilschrift → Carlito, optisch gleich. Test nur an einer entschlüsselten Kopie im Testsystem.

## Offen / noch nicht getestet
0. **Formular ausfüllen mit echten Behörden-/Firmen-Formularen** (z. B. Arbeitsagentur, Finanzamt, Krankenkasse) in Chrome/Edge und in Adobe Reader öffnen. Getestet nur mit selbst erzeugten Formularen (reportlab).
1. **„Fehler melden“ auf echtem Windows/Chrome ausprobieren** (Speichern-Dialog, GitHub-Formular mit eingeloggtem Konto, ZIP ins Issue ziehen).
2. **Windows-.exe auf echtem Windows starten** (SmartScreen-Hinweis, Doppelklick auf PDF). Im Browser: PC-Schriftsuche wird automatisch angefragt (in der App ohne Nachfrage).
3. Firmen-Hausschriften (z. B. GenosGFG, TeleGrotesk): fehlende Buchstaben kommen aus Helvetica – fällt kaum auf, ist aber nicht 100 % gleich. Lösung nur mit der echten Schriftdatei.
4. Bearbeitungsgeschützte (verschlüsselte) PDFs, z. B. von Banken: Speichern wird bewusst abgelehnt.
5. Absatz-Vorschau kann minimal anders umbrechen als das gespeicherte PDF.
6. Gemischte Formatierung innerhalb eines Absatzes (einzelne fette Wörter) geht im Absatz-Modus verloren.
7. Text in Form-XObjects und gedrehter Text werden nicht erkannt.
8. Abdecken entfernt den alten Text nicht aus der Datei (für echtes Schwärzen ungeeignet).
9. Wird ein Absatz kürzer, bleibt darunter eine Lücke (kein Nachrutschen, bewusst akzeptiert).
10. pdf.js meldet „fake worker“ bei file:// – funktioniert, ist aber langsamer bei großen PDFs.

## Arbeitsweise für dieses Projekt
- Änderungen immer in `editor-quelle.html`, dann mit `build.py` bauen; für die App die neue HTML nach `05_Windows-App/app/editor.html` kopieren und neu bauen.
- Kommt ein Fehlerbericht: ZIP mit `bericht_nachstellen.py` nachstellen, Fehler beheben, danach erneut nachstellen.
- Vor jeder Ausgabe: Code-Review + Tests aus `03_Tests` (`e2e6_suite.sh` für alle Funktionen, `e2e7_fehlerbericht.py`, `e2e8_formular.py`, `e2e5_echte_pdfs.py` mit echten PDFs) laufen lassen und das gespeicherte PDF als Bild prüfen.
- Ehrlich sagen, was getestet ist und was nicht.
