import win32com.client as win32
import FreeSimpleGUI as sg
from db import return_fw_data, return_fw_contact_df, return_company_data, return_company_address, return_company_contact, get_pallet_details, get_purchase_manager_df


def send_email(to, data, nr, attachments=None):   #cc=None, attachments=None
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    
    subject = "Noorganizēts transport {nosutītājs} kravai"
    
    body = """Labdien,

Ir noorganizēts transports sekojošajai kravai:

PO: 
Nosutītājs:
Iekraušanas adrese:
Iekraušanas datums: no 

Piegade:
Piegades adrese: 
Piegādes datums: līdz

Kravas informācija:
6 paletes
6000 kg

Pārvadātājs: 
Transport izdevumi bez PVN:

Temperatūras režīms:
Atmuitošana: 

    """
    
    mail.To = to
    mail.Subject = subject
    mail.Body = body  # plain text; use mail.HTMLBody for HTML

    if attachments:
        for path in attachments:
            mail.Attachments.Add(path)
    
    #mail.Display() # opens e-mail for editing - good for debugging
    mail.Send()  # or mail.Display() to open it for review first
    
def send_email_purchase_manager(to, data, nr):
    subject = "Noorganizēts transport {nosutītājs} kravai"
    
    body = """Labdien,

    Ir noorganizēts transports sekojošajai kravai:
    
    PO: 
    Nosutītājs:
    Iekraušanas adrese:
    Iekraušanas datums: no 

    Piegade:
    Piegades adrese: 
    Piegādes datums: līdz

    Kravas informācija:
    6 paletes
    6000 kg

    Pārvadātājs: 
    Transport izdevumi bez PVN:

    Temperatūras režīms:
    Atmuitošana: 

    """
    
    mail.To = to
    if cc:
        mail.CC = cc
    mail.Subject = subject
    mail.Body = body  # plain text; use mail.HTMLBody for HTML

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

#send_order_modal(100001)
#send_email('transports@gemoss.lv', 'NEW TRANSPORT ORDER NR 10001', 'Labdien! Nosūtu transporta pasutījumu!')