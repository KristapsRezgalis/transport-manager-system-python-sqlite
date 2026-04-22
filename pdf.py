from reportlab.pdfgen import canvas
from reportlab.lib import colors

record_number = 100

fileName = f'Gemoss_Order_Nr_{record_number}.pdf'
documentTitle = 'GEMOSS'

tr_order_text_nummber = f'Transport order Nr: {record_number}'

sender = 'Delinuts BV'
delivery = 'Gemoss SIA'
loading_address = 'SomeTest street 99, Tilsburg, Netherlands'
unloading_address = 'Mûkusalas street 75A, Riga, LV-1004'
loading_date = '2026-04-24'
unloading_date = '2026-04-24'
pallets = 10
weight = 5000
forwarder = 'RAMCO SIA'
cost = 850
customs = 0
ref = 0

textLines = [
    'The forwarder is fully responsable for transportation of the goods at all the times during the shipment.',
    'In case of delays, damages or any other important events that occur during the transportation, the forwarder',
    'is obliged to inform GEMOSS SIA.',
]

gemoss_letterhead = [
    'GEMOSS SIA',
    'Reg. Nr: 40103099092',
    'VAT Nr: LV40103099092',
    'Address: Mûkusalas street 73.Riga, LV-1004',
]

pdf = canvas.Canvas(fileName)
pdf.setTitle(documentTitle)

pdf.drawImage("gemoss_logo.png", x=30, y=800, width=126, height=32) # c.drawImage("image.png", x=100, y=500, width=200, height=150)

pdf.setFont("Times-Bold", 20) # Sets the font style and size.
pdf.drawCentredString(450, 810, tr_order_text_nummber) # Draws text centered at the specified (x, y) position.
pdf.line(30, 790, 550, 790) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

tx_field_1 = pdf.beginText(30, 770)
tx_field_1.setFont("Times-Roman", 10)
for line in gemoss_letterhead:
    tx_field_1.textLine(line)
pdf.drawText(tx_field_1)

pdf.setFont("Times-Roman", 14)
pdf.drawString(30, 700, 'LOADING DETAILS ------------------')
pdf.drawString(30, 680, f'Sender: {sender}')
pdf.drawString(30, 660, f'Reveiver: {delivery}')
'''
pdf.drawCentredString(290, 720, loading_address)
pdf.drawCentredString(290, 720, unloading_address)
pdf.drawCentredString(290, 720, loading_date)
pdf.drawCentredString(290, 720, unloading_date)
pdf.drawCentredString(290, 720, pallets)
pdf.drawCentredString(290, 720, weight)
pdf.drawCentredString(290, 720, forwarder)
pdf.drawCentredString(290, 720, cost)
pdf.drawCentredString(290, 720, customs)
pdf.drawCentredString(290, 720, ref)
'''
pdf.line(30, 640, 550, 640) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
tr_rules = pdf.beginText(40, 100) # Starts a text object at the given position.
tr_rules.setFont("Times-Roman", 10)
tr_rules.setFillColor(colors.red)

for line in textLines:
    tr_rules.textLine(line) # Adds one line of text at a time.

pdf.drawText(tr_rules) # Renders the text object onto the PDF.

pdf.save()
print('PDF file created!')