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
import os

from db import return_fw_data, return_fw_contact_df, return_company_data, return_company_address, return_company_contact, get_pallet_details

documentTitle = 'GEMOSS transport order'

pdfmetrics.registerFont(TTFont('LVSerif', r'fonts\LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LVSerif-Bold', r'fonts\LiberationSerif-Bold.ttf'))
registerFontFamily('LVSerif', normal='LVSerif', bold='LVSerif-Bold')

pdfmetrics.registerFont(TTFont('LVCarlito', r'fonts\Carlito\Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LVCarlito-Bold', r'fonts\Carlito\Carlito-Bold.ttf'))
registerFontFamily('LVCarlito', normal='LVCarlito', bold='LVCarlito-Bold')

def draw_heading(pdf, y):
    pdf.setLineWidth(0.6)
    pdf.setStrokeColorRGB(0.0, 0.0, 0.0)
    pdf.setFont("LVCarlito-Bold", 13) # Sets the font style and size.
    # Horizontal lines - HEADER
    pdf.line(80, y, 540, y) # line(x1, y1, x2, y2): Draws a horizontal line on the PDF.
    y -= 15
    pdf.drawString(400, y, "VL-NL-6") # Draws text centered at the specified (x, y) position.
    y -= 16
    pdf.line(300, y, 540, y)
    y -= 6
    pdf.drawImage("gemoss_logo.png", x=80, y=765, width=153, height=39) # c.drawImage("image.png", x=100, y=500, width=200, height=150)
    y -= 6
    pdf.drawString(330, y, "TRANSPORTA PIETEIKUMS (4.16)") # Draws text centered at the specified (x, y) position.
    y -= 5
    pdf.setFont("LVCarlito", 7.7) # Sets the font style and size.
    pdf.drawString(83, y, "SIA GEMOSS, Mūkusalas iela 73, Rīga,  LV-1004, Latvija") # Draws text centered at the specified (x, y) position.
    y -= 10
    pdf.drawString(83, y, "www.gemoss.lv, Tālrunis: +371 67702777, F ax.+371 67860103 ") # Draws text centered at the specified (x, y) position.
    y -= 5
    pdf.line(80, y, 540, y)
    # Vertical lines - HEADER
    pdf.line(80, y, 80, y+63)
    pdf.line(300, y, 300, y+63)
    pdf.line(540, y, 540, y+63)
    y -= 21
    
    return y

def draw_cargo_data(pdf, data, y, df_sender_company_address, df_sender_company_contact, df_delivery_company_address, df_delivery_company_contact):
    y_cargo_start = y
    # Horizontal lines - CARGO DATA
    pdf.line(80, y, 540, y)
    y -= 11
    pdf.setFont("LVCarlito-Bold", 10)
    pdf.drawString(83, y, "Iekraušanas datums un , ja tas")
    pdf.drawString(273, y, f"From {data.get('loading')}")
    y -= 12
    pdf.drawString(83, y, "nepieciešams, uzkraušanas laiks :")
    y -= 13
    pdf.drawString(273, y, f"{df_sender_company_address['adr_hours'].iloc[0]}")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 10
    pdf.setFont("LVCarlito", 10)
    pdf.drawString(83, y, "Iekraušanas adrese:")
    pdf.drawString(273, y, f"GRANORO")
    y -= 12
    pdf.drawString(273, y, f"SP 231 km 35, 100")
    y -= 12
    pdf.drawString(273, y, f"70033, Corato (BA)")
    y -= 12
    pdf.drawString(273, y, f"Italy")
    y -= 28
    pdf.drawString(83, y, "Kontaktpersona:")
    pdf.drawString(273, y, f"Agostino Nanula")
    y -= 12
    pdf.drawString(273, y, f" +390 808 721 821 ext.4211")
    y -= 12
    pdf.drawString(273, y, f"a.nanula@granoro.it")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 15
    pdf.drawString(83, y, "References numurs:")
    pdf.drawString(273, y, f"PO2640000")
    y -= 6
    pdf.line(80, y, 540, y)
    y -= 13
    pdf.drawString(83, y, "Piegādes datums un laiks:")
    pdf.drawString(273, y, f"Līdz 29.07.2026")
    y -= 12
    pdf.drawString(273, y, f"09:00-17:00")
    y -= 15
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(83, y, "Piegādes adrese:")
    pdf.drawString(273, y, f"GEMOSS SIA")
    y -= 12
    pdf.drawString(273, y, f"Mūkusalas iela 75A")
    y -= 12
    pdf.drawString(273, y, f"Rīga, LV-1004, Latvia")
    y -= 24
    
    pdf.drawString(83, y, "Kontaktpersona:")
    pdf.drawString(273, y, f"Kristaps Rezgalis")
    y -= 12
    pdf.drawString(273, y, f"+371 27888014")
    y -= 12
    pdf.drawString(273, y, f"kristaps.rezgalis@gemoss.lv")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(83, y, "Kravas apraksts:")
    pdf.drawString(273, y, f"10 paletes")
    y -= 12
    pdf.drawString(83, y, " (apjoms, svars,")
    pdf.drawString(273, y, f"10 000 kg")
    y -= 12
    pdf.drawString(83, y, "iepakojumu skaits)")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(83, y, "Pārvadājuma temperatūras režīms:")
    pdf.drawString(273, y, f"     NAV NEPIECIEŠAMS")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(83, y, "Transporta")
    y -= 12
    pdf.drawString(83, y, "pakalpojuma cena,")
    pdf.drawString(273, y, f"1000 EUR")
    y -= 12
    pdf.drawString(83, y, "EUR bez PVN")
    y -= 5
    pdf.line(80, y, 540, y)
    
    # Vertical lines - CARGO DATA
    pdf.line(80, y, 80, y_cargo_start)
    pdf.line(270, y, 270, y_cargo_start)
    pdf.line(540, y, 540, y_cargo_start)
    y -= 24
    
    return y

def draw_signature(pdf, y, middle=None):
    if not middle:
        middle = 270
    y_signature_start = y
    # Horizontal lines - SIGNATURE
    pdf.setFillColorRGB(0.9, 0.9, 0.9)
    pdf.rect(80, y, 540-80, -17, fill=1, stroke=1)
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.setFillColor(colors.black) 
    pdf.drawString(158, y, "Pasūtītājs")
    pdf.drawString(390, y, "Izpildītājs")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 90
    pdf.line(80, y, 540, y)
    
    # Vertical lines - SIGNATURE
    pdf.line(80, y, 80, y_signature_start)
    pdf.line(middle, y, middle, y_signature_start)
    pdf.line(540, y, 540, y_signature_start)
    y -= 12
    
    return y

def draw_footer(pdf):
    # Horizontal lines - FOOTER
    y2 = 85
    y2_start = y2
    pdf.setFont("LVCarlito", 7.2)
    pdf.line(80, y2, 540, y2)
    y2 -= 8
    pdf.drawString(84, y2, "Izstrādāja:")
    pdf.drawString(199, y2, "I.Juste-Brīdiņa")
    pdf.drawString(314, y2, "Datums:")
    pdf.drawString(429, y2, "2014.09.08")
    y2 -= 2
    pdf.line(80, y2, 540, y2)
    y2 -= 8
    pdf.drawString(84, y2, "Pārbaudīja:")
    pdf.drawString(199, y2, "-")
    pdf.drawString(314, y2, "Lappuse:")
    pdf.drawString(429, y2, "1")
    y2 -= 2
    pdf.line(80, y2, 540, y2)
    y2 -= 8
    pdf.drawString(84, y2, "Izmaiņas veica:")
    pdf.drawString(199, y2, "I.Juste-Brīdiņa")
    pdf.drawString(314, y2, "Izmaiņu datums:")
    pdf.drawString(429, y2, "2025.02.03")
    y2 -= 2
    pdf.line(80, y2, 540, y2)
    y2 -= 8
    pdf.drawString(84, y2, "Apstiprināja:")
    pdf.drawString(199, y2, "HACCP darba grupa")
    pdf.drawString(314, y2, "Versija:")
    pdf.drawString(429, y2, "6")
    y2 -= 2
    pdf.line(80, y2, 540, y2)
    
    y2_end = (y2_start - y2)
    # Vertical lines - FOOTER
    pdf.line(80, y2_start, 80, y2_start-y2_end)
    pdf.line(195, y2_start, 195, y2_start-y2_end)
    pdf.line(310, y2_start, 310, y2_start-y2_end)
    pdf.line(425, y2_start, 425, y2_start-y2_end)
    pdf.line(540, y2_start, 540, y2_start-y2_end)

def draw_conditions(pdf, y):
    # Horizontal lines - CONDITIONS
    pdf.setFont("LVCarlito-Bold", 10)
    pdf.drawString(84, y, "  Aizpilda atbildīgā persona kravas saņemšanas laikā, pie katras ailītes jāievelk  A (Jā, atbilst) un N (Nē, ")
    y -= 12
    pdf.drawString(84, y, "  neatbilst).")
    y -= 3
    y_conditions_start = y # to calculate both side vertical line lengths
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Prasības izpilda pakalpojuma sniedzējs")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.setFont("LVCarlito", 9.65)
    pdf.drawString(84, y, "Ja transporta līdzeklis tiek apstādināts un / vai atstāts bez uzraudzības, pārvadātājs nodrošina produkta drošumu un ")
    y -= 12
    pdf.drawString(84, y, "novērš nepiederošu personu piekļuvi produktiem.")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Ja piegādes laikā notiek incidents -piemēram avārija, laupīšana vai zādzība,  nekavējoties tiek informēts GEMOSS")
    y -= 12
    pdf.drawString(84, y, "SIA. Pārvadājumu organizētājs organizē citu transporta līdzekli, lai nogādātu pasūtījumu, vai piegādes  klientam")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Pieņemot kravu pārvadātājam jāpārbauda CMR ierakstu atbilstība pieņemtajai kravai, kā arī kravas un tās")
    y -= 12
    pdf.drawString(84, y, "iepakojuma ārējais izskats. Ja pārvadātājam ir iebildumi attiecībā uz kravu vai tās iepakojumu, kā arī, ja")
    y -= 12
    pdf.drawString(84, y, "pārvadātājam nav iespējas pārbaudīt pieņemtās kravas atbilstību norādītajam CMR, tad, pārvadātāja pienākums ir")
    y -= 12
    pdf.drawString(84, y, "norādīt to ar attiecīgu ierakstu CMR.")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Prasības aizpilda noliktavas darbinieks")
    y -= 5
    y_conditions_middle = y
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Pārvadātājs pārtikas kravu pārvadāšanai nodrošina higiēnas un pārtikas ")
    y -= 12
    pdf.drawString(84, y, "preču pārvadāšanas prasībām atbilstošus transporta līdzekļus, kuri ir aprīkoti ")
    y -= 12
    pdf.drawString(84, y, "ar kravas nostiprināšanas palīgierīcēm (stieņi, siksnas u.c.) un tā rezultātā ")
    y -= 12
    pdf.drawString(84, y, "prece uz paletēm nav bojāta, nav sagāzusies. Uz pasūtītajām precēm bez ")
    y -= 12
    pdf.drawString(84, y, "saskaņošanas nav izvietotas paletes ar citu preci.")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Ja pārvadāšanas līdzekļus vienlaicīgi izmanto ne tikai pārtikas produktu")
    y -= 12
    pdf.drawString(84, y, "pārvadāšanai, pārtikas produkti ir rūpīgi nodalīti, lai novērstu to")
    y -= 12
    pdf.drawString(84, y, "piesārņošanas iespējas, tai skaitā arī smakas veidā. ")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Ja pārvadājumu  laikā ir nepieciešams ievērot temperatūras režīmu,")
    y -= 12
    pdf.drawString(84, y, "pārvadātājs to nodrošina un vajadzības gadījumā var izsniegt izdruku")
    y -= 12
    pdf.drawString(84, y, "vai citu apliecinājumu par temperatūras režīma ievērošanu.")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.drawString(84, y, "Prece piegādāta atbilstoši prasībām.")
    y -= 12
    pdf.drawString(84, y, "Ja izkraušanas laikā konstatēts transportēšanas laikā radies kravas bojājums, ")
    y -= 12
    pdf.drawString(84, y, "tad GEMOSS SIA apņemas ziņot pārvadātājam par bojājumu apmēru, ")
    y -= 12
    pdf.drawString(84, y, "dokumentēt bojājumus, sastādīt aktu un veikt citas darbības CMR konvencijā ")
    y -= 12
    pdf.drawString(84, y, "noteiktajā kārtībā un termiņos.")
    y -= 5
    pdf.line(80, y, 540, y)
    y -= 12
    pdf.setFont("LVCarlito-Bold", 10)
    pdf.drawString(160, y, "Atbildīgās personas paraksts, datums")
    y -= 14
    pdf.line(80, y, 540, y)
    
    # Vertical lines - SIGNATURE
    pdf.line(80, y, 80, y_conditions_start)
    pdf.line(390, y, 390, y_conditions_middle)
    pdf.line(540, y, 540, y_conditions_start)
    
    y -= 12
    pdf.drawString(92, y, "Pasūtītājs garantē transporta pakalpojuma apmaksu saskaņā ar vienošanos.")
    y -= 12
    pdf.drawString(92, y, "Pārtikas preču pārvadājumi notiek saskaņā ar transpora pakalpojumu specifikāciju Nr.VL-KV-2/4")
    y -= 12
    
    return y


def create_gemoss_specification_PDF(data, nr, login_validation):
    y = 805
    
    filename = f"Gemoss order Nr {nr}.pdf"
        ### CREATES THE PDF FILE ###
    pdf = canvas.Canvas(filename)
    pdf.setTitle(documentTitle)
    
    df_fw = return_fw_data(data.get('forwarder')) # gets full forwarder company data from DB
    df_fw_contact = return_fw_contact_df(data.get('forwarder_contact'), df_fw['forwarder_id'].iloc[0]) # gets forwarder contacts data from DB
    
    df_sender_company = return_company_data(data.get('sender'))
    df_sender_company_address = return_company_address(data.get('sender_adr'), df_sender_company['company_id'].iloc[0])
    df_sender_company_contact = return_company_contact(data.get('sender_cont'), df_sender_company['company_id'].iloc[0])
    
    df_delivery_company = return_company_data(data.get('delivery'))
    df_delivery_company_address = return_company_address(data.get('delivery_adr'), df_delivery_company['company_id'].iloc[0])
    df_delivery_company_contact = return_company_contact(data.get('delivery_cont'), df_delivery_company['company_id'].iloc[0])
    
    
    ##########################
    ### PAGE NR 1 starting ###
    ##########################
    y = draw_heading(pdf, y)
    y = draw_cargo_data(pdf, data, y, df_sender_company_address, df_sender_company_contact, df_delivery_company_address, df_delivery_company_contact)
    y = draw_signature(pdf, y)
    draw_footer(pdf)

    pdf.showPage()
    
    ##############################################
    ### PAGE NR 1 ENDED AND PAGE NR 2 STARTING ###
    ##############################################
    y = 805
    y = draw_heading(pdf, y)
    y = draw_conditions(pdf, y)
    y = draw_signature(pdf, y, 310)
    draw_footer(pdf)
    
    pdf.save()
    os.startfile(filename)
    
#create_gemoss_specification_PDF(100)