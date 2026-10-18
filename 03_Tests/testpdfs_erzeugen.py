from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import pikepdf, subprocess
# 1 Querformat + Farben + kursiv/fett
c=canvas.Canvas('quer.pdf',pagesize=landscape(A4))
c.setFont('Helvetica-Bold',20); c.drawString(60,520,'Quartalsbericht Querformat')
c.setFont('Helvetica-Oblique',12); c.setFillColor(HexColor('#1a4fa0')); c.drawString(60,490,'Blauer kursiver Untertitel')
c.setFillColor(HexColor('#000000')); c.setFont('Times-Roman',12)
for i in range(6): c.drawString(60,450-i*16,f'Zeile {i+1}: Umsatz im Monat {i+1} betrug {1000+i*37},00 Euro.')
c.setFillColor(HexColor('#2e7d32')); c.rect(500,300,250,40,fill=1,stroke=0); c.setFillColor(HexColor('#ffffff')); c.setFont('Helvetica-Bold',14); c.drawString(510,315,'Weisser Text auf Gruen')
c.save()
# 2 zweispaltig
c=canvas.Canvas('spalten.pdf',pagesize=A4); c.setFont('Helvetica',10)
L='Dies ist ein Beispieltext fuer die linke Spalte und er geht ueber mehrere Zeilen weiter.'.split()
for col,x in ((0,50),(1,310)):
    for i in range(12): c.drawString(x,780-i*13,f'{"Links" if col==0 else "Rechts"} Spalte Zeile {i+1} mit etwas Text')
c.save()
# 3 Seite mit /Rotate 90
c=canvas.Canvas('rot_base.pdf',pagesize=A4); c.setFont('Helvetica',14); c.drawString(72,700,'Diese Seite ist im PDF um 90 Grad gedreht.'); c.drawString(72,680,'Zweite Zeile zum Bearbeiten.'); c.save()
p=pikepdf.open('rot_base.pdf'); p.pages[0].Rotate=90; p.save('gedreht.pdf')
# 4 CropBox verschoben
p=pikepdf.open('rot_base.pdf'); p.pages[0].CropBox=[36,300,560,800]; p.pages[0].MediaBox=[0,0,595,842]; p.save('cropbox.pdf')
# 5 Formular
c=canvas.Canvas('formular.pdf',pagesize=A4); c.setFont('Helvetica',12); c.drawString(72,760,'Antrag: Name'); f=c.acroForm; f.textfield(name='name',x=180,y=752,width=200,height=20,value='Max Muster'); c.drawString(72,720,'Hinweis: Bitte vollstaendig ausfuellen.'); c.save()
# 6 Scan (nur Bild)
from PIL import Image, ImageDraw
im=Image.new('RGB',(1240,1754),'white'); d=ImageDraw.Draw(im); d.text((100,100),'Gescanntes Dokument ohne Text',fill='black'); im.save('scan.pdf')
# 7 gross: 40 Seiten
c=canvas.Canvas('gross.pdf',pagesize=A4)
for pg in range(40):
    c.setFont('Helvetica',11)
    for i in range(45): c.drawString(50,800-i*17,f'Seite {pg+1} Zeile {i+1}: Lorem ipsum dolor sit amet consectetur.')
    c.showPage()
c.save()
# 12 Formular mit allen Feldarten (V2.5: Formular ausfüllen)
from reportlab.lib.colors import HexColor, white
c=canvas.Canvas('formular2.pdf',pagesize=A4); f=c.acroForm
c.setFont('Helvetica-Bold',16); c.drawString(72,790,'Antrag auf Testleistung')
c.setFont('Helvetica',11)
c.drawString(72,750,'Vorname:'); f.textfield(name='vorname',x=170,y=744,width=180,height=20,borderColor=HexColor('#888888'),fillColor=HexColor('#eef3ff'),fontSize=11)
c.drawString(72,720,'Nachname:'); f.textfield(name='nachname',x=170,y=714,width=180,height=20,value='Muster',fontSize=11)
c.drawString(72,690,'PLZ:'); f.textfield(name='plz',x=170,y=684,width=70,height=20,maxlen=5,fontSize=11)
c.drawString(72,660,'Geschlecht:')
for i,v in enumerate(['m','w','d']):
  f.radio(name='geschlecht',value=v,x=170+i*60,y=656,size=14,selected=(v=='w')); c.drawString(188+i*60,659,v)
c.drawString(72,630,'Zustimmung:'); f.checkbox(name='zustimmung',x=170,y=626,size=14,checked=False)
c.drawString(72,600,'Newsletter:'); f.checkbox(name='newsletter',x=170,y=596,size=14,checked=True)
c.drawString(72,570,'Bundesland:'); f.choice(name='land',x=170,y=564,width=150,height=20,options=['Bayern','Hessen','Berlin'],value='Bayern',fontSize=11)
c.drawString(72,535,'Kurs:'); f.listbox(name='kurs',x=170,y=480,width=150,height=60,options=['FISI','FIAE','Kaufmann'],value='FIAE',fontSize=10)
c.drawString(72,450,'Bemerkung:'); f.textfield(name='bemerkung',x=170,y=380,width=300,height=80,fieldFlags='multiline',fontSize=10)
c.drawString(72,350,'Aktenzeichen:'); f.textfield(name='az',x=170,y=344,width=180,height=20,value='AZ-2026-001',fieldFlags='readOnly',fontSize=11)
c.drawString(72,300,'Unterschrift / Ort, Datum (kein Feld):'); c.line(72,270,350,270)
c.save()
