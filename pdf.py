from reportlab.pdfgen import canvas
from reportlab.lib import colors

record_number = 100

documentTitle = 'GEMOSS'

sender = 'Delinuts BV'
delivery = 'Gemoss SIA'
loading_address = ['SomeTest street 99,',
                   'Tilsburg, 6985',
                   'Netherlands']
unloading_address = ['Mukusalas street 75A,',
                     'Riga, LV-1004',
                     'Latvia']
loading_date = '2026-04-24'
unloading_date = '2026-04-30'
pallets = 10
weight = 5000
forwarder = 'FORWARDER SIA'
cost = 850
customs = 'NO'
ref = 'NO'

tr_rules = [
    'This transport order is governed by the Convention on the Contract for the International Carriage of Goods by Road (CMR 1956)',
    'and applicable EU and national legislation.',
    'Acceptance of this transport order or commencement of its execution constitutes full acceptance of these terms and conditions.',
    'The Carrier undertakes to perform the transport with due care, using suitable equipment and in compliance with all applicable regulations.',
    'The Carrier’s liability is governed by the CMR Convention and begins at loading and ends upon delivery.',
    'Delivery dates are indicative unless otherwise agreed. The Carrier shall not be liable for delays caused by force majeure events including',
    'but not limited to weather conditions, traffic restrictions, strikes, or border delays.'
]

gemoss_letterhead = [
    'GEMOSS SIA',
    'Reg. Nr: 40103099092',
    'VAT Nr: LV40103099092',
    'Address: Mûkusalas street 73, Riga, LV-1004',
]

forwarder_letterhead = [
    'Reg. Nr: 4000000000',
    'VAT Nr: LV4000000000',
    'Address: Some street 111, Riga, LV-1000',
]

# data variable content -> sap_po, sender, delivery, loading,unloading, pallets, weight, forwarder, cost, customs, ref
def create_order_pdf (data, nr):
    print(data.get('sap_po'))
    pdf = canvas.Canvas(f"Gemoss order Nr {data.get('sap_po')}.pdf")
    pdf.setTitle(documentTitle)

    pdf.drawImage("gemoss_logo.png", x=30, y=800, width=126, height=32) # c.drawImage("image.png", x=100, y=500, width=200, height=150)

    pdf.setFont("Times-Bold", 20) # Sets the font style and size.
    pdf.drawCentredString(450, 810, f"Transport order Nr: {nr}") # Draws text centered at the specified (x, y) position.
    pdf.line(30, 790, 565, 790) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

    tx_field_1 = pdf.beginText(30, 770)
    tx_field_1.setFont("Times-Roman", 10)
    for line in gemoss_letterhead:
        tx_field_1.textLine(line)
    pdf.drawText(tx_field_1)
    
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(400, 770, f"{data.get('forwarder')}")
    tx_field_2 = pdf.beginText(400, 757)
    tx_field_2.setFont("Times-Roman", 10)
    for line in forwarder_letterhead:
        tx_field_2.textLine(line)
    pdf.drawText(tx_field_2)

    pdf.line(30, 720, 565, 720) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(300, 700, 'SHIPMENT INFORMATION')
    pdf.line(30, 690, 565, 690) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

    pdf.setFont("Times-Roman", 12)
    pdf.drawString(100, 670, 'LOADING DETAILS')
    pdf.drawString(30, 640, f"Loading date: {data.get('loading')}")
    pdf.drawString(30, 620, f'Loading address: ')

    tx_field_address_1 = pdf.beginText(115, 620)
    for line in loading_address:
        tx_field_address_1.textLine(line)
    pdf.drawText(tx_field_address_1)

    pdf.drawString(30, 570, f"Sender: {data.get('sender')}")

    pdf.line(295, 690, 295, 550) # line(x1, y1, x2, y2): Draws a vertical line on the PDF.

    pdf.drawString(370, 670, 'UNLOADING DETAILS')
    pdf.drawString(310, 640, f"Unloading date: {data.get('unloading')}")
    pdf.drawString(310, 620, f'Unloading address: ')

    tx_field_address_2 = pdf.beginText(405, 620)
    for line in unloading_address:
        tx_field_address_2.textLine(line)
    pdf.drawText(tx_field_address_2)

    pdf.drawString(310, 570, f"Receiver: {data.get('delivery')}")

    pdf.line(30, 550, 565, 550) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(300, 530, 'CARGO DETAILS')
    pdf.line(30, 520, 565, 520) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(300, 500, f"Number of pallets: {data.get('pallets')}")
    pdf.drawCentredString(300, 480, f'Dimensions of pallets: 80x120x240 cm')
    pdf.drawCentredString(300, 460, f"Gross weight: {data.get('weight')} kg")

    pdf.line(30, 440, 565, 440) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(300, 420, 'OTHER INFORMATION')
    pdf.line(30, 410, 565, 410) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(300, 390, f'Customs clearance: {customs}')
    pdf.drawCentredString(300, 370, f'Temperature control: {ref}')

    pdf.line(30, 350, 565, 350) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(300, 330, 'FREIGHT COST')
    pdf.line(30, 320, 565, 320) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

    pdf.drawCentredString(300, 300, f"Agreed sum: {data.get('cost')} EUR excl. VAT")
    pdf.drawCentredString(300, 280, f'Payment terms: 14 days after receiving invoice and CMR')

    pdf.line(30, 270, 565, 270) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(300, 250, 'TRANSPORT TERMS AND CONDITIONS')
    pdf.line(30, 240, 565, 240) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.

    tr_rules_var = pdf.beginText(30, 220) # Starts a text object at the given position.
    tr_rules_var.setFont("Times-Roman", 10)
    for line in tr_rules:
        tr_rules_var.textLine(line) # Adds one line of text at a time.

    pdf.drawText(tr_rules_var) # Renders the text object onto the PDF.


    pdf.setFont("Times-Bold", 14)
    pdf.drawString(30, 100, 'CLIENT')
    pdf.line(30, 98, 200, 98) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawString(30, 80, 'GEMOSS SIA')
    pdf.drawString(30, 65, 'Kristaps Rezgalis')
    pdf.drawString(30, 50, '+371 22229999')
    pdf.drawString(30, 35, 'kristaps@gemoss.lv')

    pdf.setFont("Times-Bold", 14)
    pdf.drawString(380, 100, 'CARRIER')
    pdf.line(380, 98, 550, 98) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("Times-Roman", 14)
    pdf.drawString(380, 80, f"{data.get('forwarder')}")
    pdf.drawString(380, 65, 'Janis Berzins')
    pdf.drawString(380, 50, '+371 22221111')
    pdf.drawString(380, 35, 'janis.berzins@forwarder.lv')

    pdf.save()
    print('PDF file created!')
