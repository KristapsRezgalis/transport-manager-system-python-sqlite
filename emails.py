import win32com.client as win32

def send_email(to, subject, body, cc=None, attachments=None):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0 = olMailItem

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
    
def send_email_purchase_manager():
    pass

# Send e-mail function - send an e-mmail with a transport order to a forwarder
def send_order_modal(nr):
    e = existing or {}

    layout = [
        
    ]

    window = sg.Window("Send documents", layout, modal=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Cancel"):
            window.close()
            return None

        if event == "Send":
            window.close()
            return values
        
send_email('transports@gemoss.lv', 'NEW TRANSPORT ORDER NR 10001', 'Labdien! Nosūtu transporta pasutījumu!')