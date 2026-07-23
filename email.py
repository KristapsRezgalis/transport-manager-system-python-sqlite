


def send_email_purchase_manager():
    pass

# description
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