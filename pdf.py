from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from config import convert_date
import os
from datetime import datetime

from db import return_fw_data, return_fw_contact_df, return_company_data, return_company_address, return_company_contact, get_pallet_details

pdfmetrics.registerFont(TTFont('LVSerif', r'fonts\LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LVSerif-Bold', r'fonts\LiberationSerif-Bold.ttf'))
registerFontFamily('LVSerif', normal='LVSerif', bold='LVSerif-Bold')

pdfmetrics.registerFont(TTFont('LVCarlito', r'fonts\Carlito\Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LVCarlito-Bold', r'fonts\Carlito\Carlito-Bold.ttf'))
registerFontFamily('LVCarlito', normal='LVCarlito', bold='LVCarlito-Bold')

record_number = 100

documentTitle = 'GEMOSS'

terms_text = """
By accepting this Transport Order, the Carrier confirms acceptance of these Terms and Conditions and undertakes to perform the transport in accordance with the Convention on the Contract for the International Carriage of Goods by Road (CMR), all applicable national and international legislation, and recognised industry standards.

The Carrier shall provide a roadworthy, clean, dry, odour-free and technically suitable vehicle appropriate for the nature of the cargo. The loading compartment shall be free from contamination, pests, residues of previous cargoes and any other condition that may adversely affect the transported goods.

The Carrier shall ensure the safe transportation of all cargo entrusted by GEMOSS SIA, including, but not limited to, food products, beverages, edible goods, non-food products, consumer goods, kitchen equipment, household appliances, electronic devices, medical products, furniture, oversized or non-standard cargo, palletised freight and temperature-controlled shipments.

Acceptance of this Transport Order constitutes full acceptance of these Terms and Conditions.

Carrier's acceptance of this Transport Order by e-mail, EDI, transport platform or commencement of loading shall constitute full acceptance of these Terms and Conditions.
"""

gemoss_letterhead = [
    'GEMOSS SIA',
    'Reg. Nr: 40103099092',
    'VAT Nr: LV40103099092',
    'Address: Mûkusalas street 73, Riga, LV-1004',
]

def get_forwarder_sender_delivery_data(data):
    if data.get('forwarder'):
        df_fw = return_fw_data(data.get('forwarder')) # gets full forwarder company data from DB
        df_fw_contact = return_fw_contact_df(data.get('forwarder_contact'), df_fw['forwarder_id'].iloc[0]) # gets forwarder contacts data from DB
    else:
        df_fw = ''
        df_fw_contact = ''
    
    df_sender_company = return_company_data(data.get('sender'))
    df_sender_company_address = return_company_address(data.get('sender_adr'), df_sender_company['company_id'].iloc[0])
    df_sender_company_contact = return_company_contact(data.get('sender_cont'), df_sender_company['company_id'].iloc[0])
    
    df_delivery_company = return_company_data(data.get('delivery'))
    df_delivery_company_address = return_company_address(data.get('delivery_adr'), df_delivery_company['company_id'].iloc[0])
    df_delivery_company_contact = return_company_contact(data.get('delivery_cont'), df_delivery_company['company_id'].iloc[0])
    
    return df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact

def draw_header(pdf, data, nr, df_fw):
    pdf.drawImage("gemoss_logo.png", x=30, y=800, width=126, height=32) # c.drawImage("image.png", x=100, y=500, width=200, height=150)
    pdf.setFont("LVSerif-Bold", 15) # Sets the font style and size.
    pdf.drawCentredString(425, 810, f"Transport agreement Nr: {nr}") # Draws text centered at the specified (x, y) position.
    pdf.line(30, 790, 565, 790) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    
    tx_field_1 = pdf.beginText(30, 770)
    tx_field_1.setFont("LVSerif", 10)
    for line in gemoss_letterhead:
        tx_field_1.textLine(line)
    pdf.drawText(tx_field_1)
    
    pdf.setFont("LVSerif", 10)
    pdf.drawString(380, 770, f"{data.get('forwarder')}")
    pdf.drawString(380, 757, f"Reg. Nr: {df_fw['fw_reg_nr'].iloc[0]}")
    pdf.drawString(380, 744, f"VAT Nr: {df_fw['fw_vat_nr'].iloc[0]}")
    pdf.drawString(380, 731, "Address:")
    
    forwarder_address = [f"{df_fw['fw_street'].iloc[0]}", f"{df_fw['fw_city'].iloc[0]}, {df_fw['fw_post_code'].iloc[0]}", f"{df_fw['fw_country'].iloc[0]}"]
    tx_field_2 = pdf.beginText(418, 731)
    tx_field_2.setFont("LVSerif", 10)
    for line in forwarder_address:
        tx_field_2.textLine(line)
    pdf.drawText(tx_field_2)
    
def draw_loading_unloading(pdf, data, y, df_sender_company_address, df_sender_company_contact, df_delivery_company_address, df_delivery_company_contact):
    pdf.line(30, y, 565, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 10
    pdf.setFont("LVSerif", 11)
    pdf.drawCentredString(300, y, 'SHIPMENT INFORMATION')
    y -= 4
    pdf.line(30, y, 565, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 16
    
    pdf.setFont("LVSerif", 11)
    pdf.drawString(100, y, 'LOADING DETAILS')
    pdf.drawString(370, y, 'UNLOADING DETAILS')
    y -= 20
    pdf.setFont("LVSerif", 10)
    pdf.drawString(30, y, f"Loading date: {'FIX day ' + convert_date(data.get('loading')) if data.get('loading') == data.get('loading_to') else 'from ' + convert_date(data.get('loading'))}")
    pdf.drawString(310, y, f"Unloading date: {'until ' + convert_date(data.get('unloading_to'))}")
    y -= 15
    pdf.drawString(30, y, f"Sender: {data.get('sender')}")
    pdf.drawString(310, y, f"Receiver: {data.get('delivery')}")
    y -= 15
    pdf.drawString(30, y, f"Loading address: {data.get('sender_adr')}")
    pdf.drawString(310, y, f"Unloading address: {data.get('delivery_adr')}")
    y -= 12

    loading_address = [f"{df_sender_company_address['adr_street'].iloc[0]}", f"{df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}", f"{df_sender_company_address['adr_country'].iloc[0]}"]
    unloading_address = [f"{df_delivery_company_address['adr_street'].iloc[0]}", f"{df_delivery_company_address['adr_city'].iloc[0]}, {df_delivery_company_address['adr_post_code'].iloc[0]}", f"{df_delivery_company_address['adr_country'].iloc[0]}"]

    tx_field_address_1 = pdf.beginText(101, 608)
    for line in loading_address:
        tx_field_address_1.textLine(line)
    pdf.drawText(tx_field_address_1)
    
    tx_field_address_2 = pdf.beginText(390, 608)
    for line in unloading_address:
        tx_field_address_2.textLine(line)
    pdf.drawText(tx_field_address_2)
    
    y -= 40
    pdf.drawString(30, y, f"Loading hours: {df_sender_company_address['adr_hours'].iloc[0]}")
    pdf.drawString(310, y, f"Unloading hours: {df_delivery_company_address['adr_hours'].iloc[0]}")
    y -= 15
    pdf.drawString(30, y, f"Slot booking: {df_sender_company_address['adr_book_slot'].iloc[0]}")
    pdf.drawString(310, y, f"Slot booking: {df_delivery_company_address['adr_book_slot'].iloc[0]}")
    y -= 15
    pdf.drawString(30, y, f"Loading reference: {df_sender_company_address['adr_reference'].iloc[0]}")
    pdf.drawString(310, y, f"Loading reference: {df_delivery_company_address['adr_reference'].iloc[0]}")
    y -= 15
    pdf.drawString(30, y, f"Contact: {data.get('sender_cont')}")
    pdf.drawString(310, y, f"Contact: {data.get('delivery_cont')}")
    y -= 15
    pdf.drawString(30, y, f"Phone number: {df_sender_company_contact['c_con_phone'].iloc[0]}")
    pdf.drawString(310, y, f"Phone number: {df_delivery_company_contact['c_con_phone'].iloc[0]}")
    y -= 15
    pdf.drawString(30, y, f"E-mail: {df_sender_company_contact['c_con_email'].iloc[0]}")
    pdf.drawString(310, y, f"E-mail: {df_delivery_company_contact['c_con_email'].iloc[0]}")
    y -= 5
    
    return y

def draw_pallet_data(pdf, data, y, nr):
    # gets order's pallet dataframe -> creates table_data with columns -> coverts dataframe data into ReportLab table data
    pallet_df = get_pallet_details(nr)
    table_data = [["Qty", "Length", "Width", "Height"]]
    for _, row in pallet_df.iterrows():
        table_data.append([ row["quantity"], row["length"], row["width"], row["height"] ])
    
    # creates the actual ReportLab table
    table = Table(table_data, colWidths=[70,70,70,70], rowHeights=14)
    
    # set style for the table
    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,0),"LVSerif-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("BOTTOMPADDING",(0,0),(-1,0),6),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
    ]))
    
    # stores the size of the table to calculate the y later
    table_width, table_height = table.wrap(0,0)
    
    pdf.line(295, 686, 295, y) # line(x1, y1, x2, y2): Draws a vertical line on the PDF.
    
    pdf.line(30, y, 565, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 11
    pdf.setFont("LVSerif", 11)
    pdf.drawCentredString(300, y, 'CARGO DETAILS')
    y -= 3
    pdf.line(30, y, 565, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 15
    
    pdf.setFont("LVSerif", 10)
    pdf.drawString(70, y, f"Total number of pallets: {data.get('pallets')}")
    pdf.drawString(257, y, f"Estimated LDM: {data.get('ldm')}")
    pdf.drawString(400, y, f"Total gross weight: {data.get('weight')} kg")
    y -= 10
    
    table.drawOn(pdf, 170, y-table_height)
    y -= table_height
    y -= 15
    
    return y

def draw_info_and_cost(pdf, data, y, df_fw):
    pdf.line(30, y, 565, y)
    y -= 11
    pdf.setFont("LVSerif", 11)
    pdf.drawCentredString(300, y, 'OTHER INFORMATION')
    y -= 3
    pdf.line(30, y, 565, y)
    y -= 15

    # Temperature control / Customs clearance — show a dash instead of blank
    def display_val(val, temp_min=None, temp_max=None):
        if temp_min is not None and temp_max is not None and str(temp_min).strip() != "" and str(temp_max).strip() != "":
            return f"{temp_min:+d} °C to {temp_max:+d} °C"
    
        val = str(val).strip() if val is not None else ""
        return val if val and val.upper() != "NONE" else "-"

    pdf.setFont("LVSerif", 10)
    pdf.drawString(30, y, f"Product type: {display_val(data.get('cargo_type'))}")
    pdf.drawString(240, y, f"Temperature control: {display_val(data.get('ref'), data.get('temp_min'), data.get('temp_max'))}")
    pdf.drawString(420, y, f"Customs clearance: {display_val(data.get('customs'))}")
    
    y -= 20

    # Instructions — label on its own line, content indented below it
    info_text = data.get('info') if int(data.get('add_info_to_order')) == 1 else ''
    if info_text:
        pdf.setFont("LVSerif-Bold", 10)
        pdf.drawString(30, y, "Instructions:")
        y -= 14

        tx_field_info = pdf.beginText(45, y)
        tx_field_info.setFont("LVSerif", 10)
        tx_field_info.setLeading(13)
        for line in info_text.splitlines():
            tx_field_info.textLine(line)
        pdf.drawText(tx_field_info)

        y -= 13 * len(info_text.splitlines())
        y -= 5
    else:
        y -= 5

    pdf.line(30, y, 565, y)
    y -= 11
    pdf.setFont("LVSerif", 11)
    pdf.drawCentredString(300, y, 'FREIGHT COST')
    y -= 3
    pdf.line(30, y, 565, y)
    y -= 15

    pdf.setFont("LVSerif", 10)
    pdf.drawCentredString(300, y, f"Agreed sum: {data.get('cost')} EUR excl. VAT")
    y -= 15
    pdf.drawCentredString(300, y, f"Payment terms: {df_fw['fw_payment_terms'].iloc[0]} days after receiving invoice and CMR")
    y -= 15
    pdf.drawCentredString(300, y, "Invoice and CMR must be sent only to this e-mail: transports@gemoss.lv")
    y -= 15
    
    return y

def draw_footer_signature(pdf, data, y, login_validation, df_fw_contact):
    pdf.setFont("LVSerif-Bold", 12)
    pdf.drawString(30, 101, 'CLIENT')
    pdf.line(30, 98, 200, 98) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("LVSerif", 12)
    pdf.drawString(30, 80, 'GEMOSS SIA')
    pdf.drawString(30, 65, f"{login_validation.get('name')} {login_validation.get('surname')}")
    pdf.drawString(30, 50, f"{login_validation.get('phone')}")
    pdf.drawString(30, 35, f"{login_validation.get('email')}")

    pdf.setFont("LVSerif-Bold", 12)
    pdf.drawString(380, 100, 'CARRIER')
    pdf.line(380, 98, 550, 98) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    pdf.setFont("LVSerif", 12)
    pdf.drawString(380, 80, f"{data.get('forwarder')}")
    
    if not df_fw_contact.empty:
        pdf.drawString(380, 65, f"{data.get('forwarder_contact')}")  
        pdf.drawString(380, 50, f"{df_fw_contact['fw_c_phone'].iloc[0]}")
        pdf.drawString(380, 35, f"{df_fw_contact['fw_c_email'].iloc[0]}")

# data variable content -> sap_po, sender, delivery, loading,unloading, pallets, weight, forwarder, cost, customs, ref
def create_order_pdf (data, nr, login_validation):
    ##########################
    ### PAGE NR 1 starting ###
    ##########################
    
    y = 700
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    base_dir = r"\\hippo.gemoss.lv\PUBLIC\LOGISTIKA\TMS"
    year = str(datetime.now().year)
    ##folder_name = f"{nr}"
    order_dir = os.path.join(base_dir, year, str(nr))
    
    os.makedirs(order_dir, exist_ok=True)  # create "orders" folder if it doesn't exist yet
    
        ### CREATES THE ACTUAL PDF FILE ###
    filename = f"Gemoss agreement Nr {nr}.pdf"
    pdf_path = os.path.join(order_dir, filename)
    pdf = canvas.Canvas(pdf_path)
    #pdf = canvas.Canvas(filename)
    pdf.setTitle(documentTitle)
    
    ### CALLING ALL PDF CREATION FUNCTION ###
    draw_header(pdf, data, nr, df_fw) # function to draw a header part in PDF - has static place in PDF
    y = draw_loading_unloading(pdf, data, y, df_sender_company_address, df_sender_company_contact, df_delivery_company_address, df_delivery_company_contact)
    y = draw_pallet_data(pdf, data, y, nr)
    y = draw_info_and_cost(pdf, data, y, df_fw)
    draw_footer_signature(pdf, data, y, login_validation, df_fw_contact)
    
    pdf.showPage()
    
    ##############################################
    ### PAGE NR 1 ENDED AND PAGE NR 2 STARTING ###
    ##############################################
    
    y = 700
    
    draw_header(pdf, data, nr, df_fw)
    
    pdf.line(30, y, 565, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 11
    pdf.setFont("LVSerif", 11)
    pdf.drawCentredString(300, y, 'TRANSPORT TERMS AND CONDITIONS')
    y -= 3
    pdf.line(30, y, 565, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 15
    
    terms_style = ParagraphStyle(
        "TermsStyle",
        fontName="LVSerif",
        fontSize=13,
        leading=15,
        alignment=TA_JUSTIFY,
        firstLineIndent=12,
    )
    paragraph_text = terms_text.strip().replace("\n\n", "<br/><br/>")
    paragraph = Paragraph(paragraph_text, terms_style)
    w, h = paragraph.wrap(535, 1000)
    paragraph.drawOn(pdf, 30, y - h)
        
    draw_footer_signature(pdf, data, y, login_validation, df_fw_contact)
    
    pdf.save()
    #os.startfile(filename)
    
    return pdf_path