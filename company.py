import FreeSimpleGUI as sg

countries = ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom", "Vatican City"]

def company_entry_modal(title, existing=None):
    e = existing or {}
    layout =[
        [sg.Text("Company name:", size=16), sg.Input(e.get("c_name", ""), key="-TXT-COMPANY-NAME-", size=35)],
        [sg.Text("Reg. Nr:", size=16), sg.Input(e.get("c_reg", ""), key="-TXT-COMPANY-REG-", size=35)],
        [sg.Text("VAT Nr:", size=16), sg.Input(e.get("c_vat", ""), key="-TXT-COMPANY-VAT-", size=35)],
        [sg.Text("Street:", size=16), sg.Input(e.get("c_street", ""), key="-TXT-COMPANY-STREET-", size=35)],
        [sg.Text("City:", size=16), sg.Input(e.get("c_city", ""), key="-TXT-COMPANY-CITY-", size=35)],
        [sg.Text("Post code:", size=16), sg.Input(e.get("c_post_code", ""), key="-TXT-COMPANY-POST-", size=35)],
        [sg.Text("Country:", size=16), sg.Combo(countries, key="-TXT-COMPANY-COUNTRY-", default_value=e.get("c_country", countries[20]), readonly=True, size=35)],
        [sg.Text("More information:", size=16), sg.Multiline(e.get("c_notes", ""), key="-IN-COMPANY-DETAILS-", size=(40, 6))],
        [sg.Text("Product type:", size=16), sg.Input(e.get("c_prod_type", ""), key="-TXT-COMPANY-PRODUCT-", size=35)],
        [sg.Button("Save", key="-BTN-COMPANY-SAVE-"), sg.Button("Cancel")]
    ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-BTN-COMPANY-SAVE-":
            app_window.close()
            return values