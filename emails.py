import win32com.client as win32
import FreeSimpleGUI as sg
from db import return_fw_data, return_fw_contact_df, return_company_data, return_company_address, return_company_contact, get_pallet_details, get_purchase_manager_df, get_tender_emails
from pdf import get_forwarder_sender_delivery_data, display_val
from config import convert_date

# Function to generate an e-mail for a new transport offer. It searches for contacts of a company that works in the particular country and enters data from transport order.
def send_transport_offer(nr, data):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    loading_address = f"{df_sender_company_address['adr_street'].iloc[0]}, {df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}, {df_sender_company_address['adr_country'].iloc[0]}"
    unloading_address = f"{df_delivery_company_address['adr_street'].iloc[0]}, {df_delivery_company_address['adr_city'].iloc[0]}, {df_delivery_company_address['adr_post_code'].iloc[0]}, {df_delivery_company_address['adr_country'].iloc[0]}"
    
    subject = f"NEW CARGO | {data.get('sender')}, {df_sender_company_address['adr_post_code'].iloc[0]}, {df_sender_company_address['adr_country'].iloc[0]} -> {data.get('delivery')}, {df_delivery_company_address['adr_country'].iloc[0]} | {data.get('pallets')} {'pallets' if int(data.get('pallets')) > 1 else 'pallet'} | {convert_date(data.get('loading')) if data.get('loading') == data.get('loading_to') else 'from ' + convert_date(data.get('loading'))}"
    
    mail.To = 'kristaps.rezgalis@gemoss.lv'
    if data.get('ref'):
        # calls function in db.py to get e-mails of forwarder which have reefer trucks
        bcc = get_tender_emails('Temperature')
    else:
        # calls function in db.py to get all forwawrder emails in one string for specific loading country
        bcc = get_tender_emails(str(df_sender_company_address['adr_country'].iloc[0]).strip().lower()) 
    mail.Subject = subject
    
    mail.BCC = bcc
    
    mail.Display()
    #signature = mail.HTMLBody
    
    #Gets pallet dimensions data from database and sorts it in a pallet_table variable which is used in html text afterwards.
    pallet_df = get_pallet_details(nr)
    pallet_table = """
    <table style="
        border-collapse:collapse;
        font-family:Calibri, Arial, sans-serif;
        font-size:11px;
        border:1px solid #c0c0c0;
        margin:4px 0;
    ">
    <tr style="background:#f2f2f2;">
        <th style="border:1px solid #c0c0c0;padding:1px 5px;">Qty</th>
        <th style="border:1px solid #c0c0c0;padding:1px 5px;">Length</th>
        <th style="border:1px solid #c0c0c0;padding:1px 5px;">Width</th>
        <th style="border:1px solid #c0c0c0;padding:1px 5px;">Height</th>
    </tr>
    """
    
    for _, row in pallet_df.iterrows():
        pallet_table += f"""
        <tr>
            <td style="border:1px solid #c0c0c0;padding:1px 5px;text-align:center;">
                {int(row['quantity'])}
            </td>
            <td style="border:1px solid #c0c0c0;padding:1px 5px;text-align:center;">
                {int(row['length'])}
            </td>
            <td style="border:1px solid #c0c0c0;padding:1px 5px;text-align:center;">
                {int(row['width'])}
            </td>
            <td style="border:1px solid #c0c0c0;padding:1px 5px;text-align:center;">
                {int(row['height'])}
            </td>
        </tr>
        """

    pallet_table += "</table>"
    
    html_body = f"""
    <html>
        <body style="font-family:Calibri; font-size:10pt;">\
            <p>Sveiki,</p>
            
            <p>Lūdzu paskatīties iespējas paņemt šo:</p>
            
            <p style="margin:0;">Loading date: <b>{'fix day ' + convert_date(data.get('loading')) if data.get('loading') == data.get('loading_to') else 'from ' + convert_date(data.get('loading'))}</b></p>
            <p style="margin:0;">Loading hours: <b>{df_sender_company_address['adr_hours'].iloc[0]}</b></p>
            <p style="margin:0;">Shipper (Consignor): <b>{data.get('sender')}</b></p>
            <p style="margin:0;">Loading address: <b>{loading_address}</b></p>
            <p style="margin:0 0 8px 0;">Slot booking: <b>{df_sender_company_address['adr_book_slot'].iloc[0]}</b></p>
            
            <p style="margin:0;">Consignee: <b>{data.get('delivery')}</b></p>
            <p style="margin:0 0 8px 0;">Delivery address: <b>{unloading_address}</b></p>
            
            <p style="margin:0;">Pallets total: <b>{data.get('pallets')}</b></p>
            {pallet_table}
            <p style="margin:0;">Estimated LDM: <b>{data.get('ldm')}</b></p>
            <p style="margin:0;">Gross weight: <b>{data.get('weight')} kg</b></p>
            <p style="margin:0 0 8px 0;">Temperature control: <b>{display_val(data.get('ref'), data.get('temp_min'), data.get('temp_max'))}</b></p>
            
            <p>Paldies.</p>
            <p style="margin:0;">------- </p>
            <p style="margin:0;"><b>Kristaps Rezgalis</b></p>
            <p style="margin:0;">Transport coordinator</p>
            <p style="margin:0;">Mob. (+371) 27888014</p>
            <p style="margin:0;">kristaps.rezgalis@gemoss.lv</p>
            <p style="margin:0;">GEMOSS SIA, Mūkusalas iela 75A, Rīga, LV-1004</p>
        </body>
    </html>
    """
    
    mail.HTMLBody = html_body

    mail.Display()

def send_email(to, data, nr, attachments=None):   #cc=None, attachments=None
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    loading_address = f"{df_sender_company_address['adr_street'].iloc[0]}, {df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}, {df_sender_company_address['adr_country'].iloc[0]}"
    unloading_address = f"{df_delivery_company_address['adr_street'].iloc[0]}, {df_delivery_company_address['adr_city'].iloc[0]}, {df_delivery_company_address['adr_post_code'].iloc[0]}, {df_delivery_company_address['adr_country'].iloc[0]}"
    
    # Temperature control / Customs clearance — show a dash instead of blank
    def display_customs_val(val):
        val = str(val).strip() if val is not None else ""
        return val if val and val.upper() != "NONE" else "-"
    
    subject = f"Transporta līgums Nr {nr} | {data.get('sender')} → {data.get('delivery')}"
    
    mail.To = to
    mail.Subject = subject
    
    # Open the email first so Outlook inserts your default signature
    mail.Display()

    # Save the automatically inserted signature
    signature = mail.HTMLBody

    # Create your email body
    html_body = f"""
    <html>
    <body style="font-family:Calibri;font-size:11pt;">

    <p>Labdien,</p>

    <p>Nosūtu transporta pasūtījumu sekojošai kravai:</p>

    <table style="border-collapse:collapse;">
        <tr>
            <td style="padding-right:20px;"><b>Nosūtītājs:</b></td>
            <td>{data.get('sender')}</td>
        </tr>
        <tr>
            <td><b>Iekraušanas adrese:</b></td>
            <td>{loading_address}</td>
        </tr>
        <tr>
            <td style="padding-bottom:15px;"><b>Iekraušanas datums:</b></td>
            <td style="padding-bottom:15px;">{'fix diena ' + convert_date(data.get('loading')) if data.get('loading') == data.get('loading_to') else 'from ' + convert_date(data.get('loading'))}</td>
        </tr>
        
        <tr>
            <td><b>Piegāde:</b></td>
            <td>{data.get('delivery')}</td>
        </tr>
        <tr>
            <td><b>Piegades adrese:</b></td>
            <td>{unloading_address}</td>
        </tr>
        <tr>
            <td style="padding-bottom:15px;"><b>Piegādes datums:</b></td>
            <td style="padding-bottom:15px;">līdz {convert_date(data.get('unloading_to'))}</td>
        </tr>
        
        <tr>
            <td><b>Krava:</b></td>
            <td>{data.get('pallets')} pallets, {data.get('weight')} kg</td>
        </tr>
        <tr>
            <td><b>Pārvadātājs:</b></td>
            <td>{data.get('forwarder')}</td>
        </tr>
        <tr>
            <td style="padding-bottom:15px;"><b>Transporta izmaksas:</b></td>
            <td style="padding-bottom:15px;">{data.get('cost')} EUR excl. VAT</td>
        </tr>

        <tr>
            <td><b>Temperatūras režīms:</b></td>
            <td>{display_val(data.get('ref'), data.get('temp_min'), data.get('temp_max'))}</td>
        </tr>
        <tr>
            <td><b>Atmuitošana:</b></td>
            <td>{display_customs_val(data.get('customs'))}</td>
        </tr>
    </table>
    <p>Lūdzu apstiprināt, ka saņēmāt.</p>
    <p style="margin:0;">------- </p>
    <p style="margin:0;"><b>Kristaps Rezgalis</b></p>
    <p style="margin:0;">Transport coordinator</p>
    <p style="margin:0;">Mob. (+371) 27888014</p>
    <p style="margin:0;">kristaps.rezgalis@gemoss.lv</p>
    <p style="margin:0;">GEMOSS SIA, Mūkusalas iela 75A, Rīga, LV-1004</p>

    </body>
    </html>
    """

    mail.HTMLBody = html_body

    if attachments:
        for path in attachments:
            mail.Attachments.Add(path)
    
    mail.Display() # opens e-mail for editing - good for debugging
    #mail.Send()  # or mail.Display() to open it for review first
    
def send_email_purchase_manager(to, data, nr, attachments=None):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    loading_address = f"{df_sender_company_address['adr_street'].iloc[0]}, {df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}, {df_sender_company_address['adr_country'].iloc[0]}"
    unloading_address = f"{df_delivery_company_address['adr_street'].iloc[0]}, {df_delivery_company_address['adr_city'].iloc[0]}, {df_delivery_company_address['adr_post_code'].iloc[0]}, {df_delivery_company_address['adr_country'].iloc[0]}"
    
    # Temperature control / Customs clearance — show a dash instead of blank
    def display_customs_val(val):
        val = str(val).strip() if val is not None else ""
        return val if val and val.upper() != "NONE" else "-"
    
    subject = f"Transporta līgums Nr {nr} | {data.get('sender')} → {data.get('delivery')}"
    
    mail.To = to
    mail.Subject = subject
    
    # Open the email first so Outlook inserts your default signature
    mail.Display()

    # Save the automatically inserted signature
    signature = mail.HTMLBody

    # Create your email body
    html_body = f"""
    <html>
    <body style="font-family:Calibri; font-size:10pt;">

    <p>Sveiki,</p>

    <p>Ir noorganizēts transports šādai kravai:</p>

    <table style="border-collapse:collapse;">
        <tr>
            <td style="padding-bottom:15px;"><b>SAP PO:</b></td>
            <td style="padding-bottom:15px;">{data.get('sap_po')}</td>
        </tr>
    
        <tr>
            <td style="padding-right:20px;"><b>Nosūtītājs:</b></td>
            <td>{data.get('sender')}</td>
        </tr>
        <tr>
            <td><b>Iekraušanas adrese:</b></td>
            <td>{loading_address}</td>
        </tr>
        <tr>
            <td style="padding-bottom:15px;"><b>Iekraušanas datums:</b></td>
            <td style="padding-bottom:15px;">{'fix diena ' + convert_date(data.get('loading')) if data.get('loading') == data.get('loading_to') else 'from ' + convert_date(data.get('loading'))}</td>
        </tr>
        
        <tr>
            <td><b>Piegāde:</b></td>
            <td>{data.get('delivery')}</td>
        </tr>
        <tr>
            <td><b>Piegades adrese:</b></td>
            <td>{unloading_address}</td>
        </tr>
        <tr>
            <td style="padding-bottom:15px;"><b>Piegādes datums:</b></td>
            <td style="padding-bottom:15px;">līdz {convert_date(data.get('unloading_to'))}</td>
        </tr>
        
        <tr>
            <td><b>Krava:</b></td>
            <td>{data.get('pallets')} pallets, {data.get('weight')} kg</td>
        </tr>
        <tr>
            <td><b>Pārvadātājs:</b></td>
            <td>{data.get('forwarder')}</td>
        </tr>
        <tr>
            <td style="padding-bottom:15px;"><b>Transporta izmaksas:</b></td>
            <td style="padding-bottom:15px;">{data.get('cost')} EUR excl. VAT</td>
        </tr>

        <tr>
            <td><b>Temperatūras režīms:</b></td>
            <td>{display_val(data.get('ref'), data.get('temp_min'), data.get('temp_max'))}</td>
        </tr>
        <tr>
            <td><b>Atmuitošana:</b></td>
            <td>{display_customs_val(data.get('customs'))}</td>
        </tr>
    </table>
        <p>Šis ir automātisks paziņojums. Ja pamani kļūdas, lūdzu, informēt mani. Paldies.</p>
        <p style="margin:0;">------- </p>
        <p style="margin:0;"><b>Kristaps Rezgalis</b></p>
        <p style="margin:0;">Transport coordinator</p>
        <p style="margin:0;">Mob. (+371) 27888014</p>
        <p style="margin:0;">kristaps.rezgalis@gemoss.lv</p>
        <p style="margin:0;">GEMOSS SIA, Mūkusalas iela 75A, Rīga, LV-1004</p>

    </body>
    </html>
    """
    #{signature}
    #<img src="gemoss_signature.png" alt="Gemoss" height="80" style="margin:0;">
    #<img src="linkedin_icon.png" alt="Gemoss linkedin" height="15" style="margin:0; padding-left:5px">
    #<img src="facebook_icon.png" alt="Gemoss facebook" height="15" style="margin:0; padding-left:5px">
    #<img src="instagram_icon.png" alt="Gemoss instagram" height="15" style="margin:0; padding-left:5px">

    mail.HTMLBody = html_body

    if attachments:
        for path in attachments:
            mail.Attachments.Add(path)
    
    mail.Display() # opens e-mail for editing - good for debugging
    #mail.Send()  # or mail.Display() to open it for review first

# Send e-mail function - send an e-mmail with a transport order to a forwarder
def send_order_modal(data, nr, purchase_manager_name):
    #e = existing or {}
    df_fw = return_fw_data(data.get('forwarder')) # gets full forwarder company data from DB
    df_fw_contact = return_fw_contact_df(data.get('forwarder_contact'), df_fw['forwarder_id'].iloc[0]) # gets forwarder contacts data from DB
    purchase_manager_df = get_purchase_manager_df(purchase_manager_name)

    layout = [
        [sg.Text("File"), sg.VerticalSeparator(), sg.Text("E-mail")],
        [sg.Checkbox('    ', default=True, key='-CB-SEND-ATT-FORWARDER-'), sg.Checkbox('       Send transport agreement to forwarder:', default=True, key='-CB-SEND-FORWARDER-', size=35), sg.Input(df_fw_contact['fw_c_email'].iloc[0], key="-TXT-FORWARDER-EMAIL-", size=50)],
        [sg.Checkbox('    ', default="", key='-CB-SEND-ATT-INNER-'), sg.Checkbox('       Send internal transport document:', default="", key='-CB-SEND-INNER-', size=35), sg.Input('anastasija.sidorenkova@gemoss.lv; arturs.arbidans@gemoss.lv', key="-TXT-INTERNAL-EMAIL-", size=50)],
        [sg.Checkbox('    ', default="", key='-CB-SEND-ATT-MANAGER-'), sg.Checkbox('       Send confirmation e-mail to purchase manager:', default=True, key='-CB-SEND-MANAGER-', size=35), sg.Input(purchase_manager_df['manager_email'].iloc[0], key="-TXT-PURCH-MAN-EMAIL-", size=50)],
        [sg.Checkbox('    ', default="", key='-CB-SEND-ATT-OTHER-'), sg.Checkbox('       Send confirmation e-mail to other contact:', default="", key='-CB-SEND-OTHER-', size=35), sg.Input("", key="-IN-EXTRA-EMAIL-", size=50)],
        [sg.Push(), sg.Button("Send", key="-BTN-SEND-EMAIL-", size=15), sg.Button("Cancel", size=15), sg.Push()]
    ]

    window = sg.Window(f"Send transport order Nr {nr}", layout, modal=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Cancel"):
            window.close()
            return None

        if event == "-BTN-SEND-EMAIL-":
            window.close()
            return values
