import FreeSimpleGUI as sg

countries = ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom", "Vatican City"]

def forwarder_entry_modal(title, existing=None):
    e = existing or {}
    layout =[
        [sg.Text("Name:", size=16), sg.Input(e.get("fw_name", ""), key="-FW-NAME-", size=35)],
        [sg.Text("Reg. Nr:", size=16), sg.Input(e.get("fw_reg_nr", ""), key="-FW-REG-", size=35)],
        [sg.Text("VAT Nr:", size=16), sg.Input(e.get("fw_vat_nr", ""), key="-FW-VAT-", size=35)],
        [sg.Text("Street:", size=16), sg.Input(e.get("fw_street", ""), key="-FW-STREET-", size=35)],
        [sg.Text("City:", size=16), sg.Input(e.get("fw_city", ""), key="-FW-CITY-", size=35)],
        [sg.Text("Post code:", size=16), sg.Input(e.get("fw_post_code", ""), key="-FW-POST-", size=35)],
        [sg.Text("Country:", size=16), sg.Combo(countries, key="-FW-COUNTRY-", default_value=e.get("fw_country", countries[20]), readonly=True, size=35)],
        [sg.Text("Payment days:", size=16), sg.Input(e.get("fw_payment_terms", ""), key="-FW-PAYMENT-", size=35)],
        [sg.Button("Save", key="-FORWARDER-SAVE-"), sg.Button("Cancel")]
    ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-FORWARDER-SAVE-":
            app_window.close()
            return values