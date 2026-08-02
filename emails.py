import win32com.client as win32
import FreeSimpleGUI as sg
from db import return_fw_data, return_fw_contact_df, return_company_data, return_company_address, return_company_contact, get_pallet_details, get_purchase_manager_df, get_tender_emails
from pdf import get_forwarder_sender_delivery_data

def send_transport_offer(country):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    
    subject = f"NEW CARGO | from - to | 1 pallet | from today"
    
    mail.to = get_tender_emails(country)
    mail.Subject = subject
    print(mail.to)
    
    mail.Display()

def send_email(to, data, nr, attachments=None):   #cc=None, attachments=None
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    loading_address = f"{df_sender_company_address['adr_street'].iloc[0]}, {df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}, {df_sender_company_address['adr_country'].iloc[0]}"
    unloading_address = f"{df_delivery_company_address['adr_street'].iloc[0]}, {df_delivery_company_address['adr_city'].iloc[0]}, {df_delivery_company_address['adr_post_code'].iloc[0]}, {df_delivery_company_address['adr_country'].iloc[0]}"
    
    # Temperature control / Customs clearance — show a dash instead of blank
    def display_val(val):
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
            <td style="padding-bottom:15px;">no {data.get('loading')}</td>
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
            <td style="padding-bottom:15px;">līdz {data.get('unloading')}</td>
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
            <td style="padding-bottom:15px;">{data.get('cost')}0 EUR excl. VAT</td>
        </tr>

        <tr>
            <td><b>Temperatūras režīms:</b></td>
            <td>{display_val(data.get('ref'))}</td>
        </tr>
        <tr>
            <td><b>Atmuitošana:</b></td>
            <td>{display_val(data.get('customs'))}</td>
        </tr>
    </table>
    {signature}

    </body>
    </html>
    """

    mail.HTMLBody = html_body

    if attachments:
        for path in attachments:
            mail.Attachments.Add(path)
    
    #mail.Display() # opens e-mail for editing - good for debugging
    mail.Send()  # or mail.Display() to open it for review first
    
def send_email_purchase_manager(to, data, nr, attachments=None):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    
    df_fw, df_fw_contact, df_sender_company, df_sender_company_address, df_sender_company_contact, df_delivery_company, df_delivery_company_address, df_delivery_company_contact = get_forwarder_sender_delivery_data(data)
    
    loading_address = f"{df_sender_company_address['adr_street'].iloc[0]}, {df_sender_company_address['adr_city'].iloc[0]}, {df_sender_company_address['adr_post_code'].iloc[0]}, {df_sender_company_address['adr_country'].iloc[0]}"
    unloading_address = f"{df_delivery_company_address['adr_street'].iloc[0]}, {df_delivery_company_address['adr_city'].iloc[0]}, {df_delivery_company_address['adr_post_code'].iloc[0]}, {df_delivery_company_address['adr_country'].iloc[0]}"
    
    # Temperature control / Customs clearance — show a dash instead of blank
    def display_val(val):
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

    <p>Sveiki,</p>

    <p>Ir noorganizēts transport šādai kravai:</p>

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
            <td style="padding-bottom:15px;">no {data.get('loading')}</td>
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
            <td style="padding-bottom:15px;">līdz {data.get('unloading')}</td>
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
            <td style="padding-bottom:15px;">{data.get('cost')}0 EUR excl. VAT</td>
        </tr>

        <tr>
            <td><b>Temperatūras režīms:</b></td>
            <td>{display_val(data.get('ref'))}</td>
        </tr>
        <tr>
            <td><b>Atmuitošana:</b></td>
            <td>{display_val(data.get('customs'))}</td>
        </tr>
    </table>
    {signature}

    </body>
    </html>
    """

    mail.HTMLBody = html_body

    if attachments:
        for path in attachments:
            mail.Attachments.Add(path)
    
    #mail.Display() # opens e-mail for editing - good for debugging
    mail.Send()  # or mail.Display() to open it for review first

# Send e-mail function - send an e-mmail with a transport order to a forwarder
def send_order_modal(data, nr, purchase_manager_name):
    #e = existing or {}
    df_fw = return_fw_data(data.get('forwarder')) # gets full forwarder company data from DB
    df_fw_contact = return_fw_contact_df(data.get('forwarder_contact'), df_fw['forwarder_id'].iloc[0]) # gets forwarder contacts data from DB
    purchase_manager_df = get_purchase_manager_df(purchase_manager_name)

    layout = [
        [sg.Checkbox('Send transport agreement to forwarder:', default="", key='-CB-SEND-FORWARDER-', size=35), sg.Input(df_fw_contact['fw_c_email'].iloc[0], key="-TXT-FORWARDER-EMAIL-", size=40)],
        [sg.Checkbox('Send internal transport document:', default="", key='-CB-SEND-INNER-', size=35), sg.Input('transports@gemoss.lv', key="-TXT-INTERNAL-EMAIL-", size=40)],
        [sg.Checkbox('Send confirmation e-mail to purchase manager:', default="", key='-CB-SEND-MANAGER-', size=35), sg.Input(purchase_manager_df['manager_email'].iloc[0], key="-TXT-PURCH-MAN-EMAIL-", size=40)],
        [sg.Checkbox('Send confirmation e-mail to other contact:', default="", key='-CB-SEND-OTHER-', size=35), sg.Input("", key="-IN-EXTRA-EMAIL-", size=40)],
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

send_transport_offer('Germany')