import FreeSimpleGUI as sg

from datetime import datetime
from db import create_table, read_all, add_db, edit_db, search_db, delete_db, filter_db, check_login, add_user, return_forwarders, add_forwarder, return_fw_contacts, add_fw_contact, add_company
from pdf import create_order_pdf
from stats import generate_diagram
from company import company_entry_modal
from forwarder import forwarder_entry_modal

sg.theme("DarkAmber")

# table column names
ORDER_COLUMNS = ["ID", "SAP PO", "Sender", "Delivery", "Loading", "Unloading", "Pallets", "Weight", "Forwarder", "Contact", "Cost","Customs","REF"]
USER_COLUMNS = ["ID", "Name", "Surname", "Role", "E-mail","Phone","Login","Password",]
COMPANY_COLUMNS = ['ID', 'Name', 'Reg Nr', 'VAT Nr', 'Street', 'City', 'Post code', 'Country']
FORWARDER_COLUMNS = ['ID', 'Name', 'Reg Nr', 'VAT Nr', 'Street', 'City', 'Post code', 'Country', 'Payment days']
FORWARDER_CONTACT_COLUMNS = ['ID', 'Name', 'Surname', 'Position', 'Phone', 'Email']
FW_CONTACT_DB_COLUMNS = ["fw_contact_id","fw_c_name","fw_c_surname","fw_c_position","fw_c_phone","fw_c_email"]

# dropdown variables
user_roles = ['admin', 'user', 'spectator']
countries = ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom", "Vatican City"]
temperature_customs_options = ['Yes', '']
statistics_types = ['Cost per pallet', 'Cost per cargo', 'Total cost', 'Total cargos', 'Total pallets', 'Total weight', 'Pallets per cargo', 'Weight per pallet', 'Weight per cargo', 'Cargos per country', 'Cargos per forwarder', 'Cost per forwarder']
statistic_period = ['Per day', 'Per month', 'Per year']
forwarders_list = return_forwarders()

TABLE_KEYS = [
    "-TABLE-",
    "-USER-TABLE-",
    "-STATISTICS-TABLE-",
    "-COMPANY-TABLE-"
]

def df_to_table(df, columns_to_keep=None):
    """Changes DataFrame to list for FreeSimpleGUI table."""
    if df.empty:
        return []

    # 1. Filter columns if a list is provided, otherwise keep all
    if columns_to_keep is not None:
        # Ensure we only select columns that actually exist in the DataFrame
        existing_cols = [col for col in columns_to_keep if col in df.columns]
        df = df[existing_cols].copy()
    else:
        df = df.copy()

    # Format columns to 2 decimal places
    if "weight" in df.columns:
        df["weight"] = df["weight"].astype(float).map("{:.2f}".format)

    if "cost" in df.columns:
        df["cost"] = df["cost"].astype(float).map("{:.2f}".format)

    return df.values.tolist()

def filter_modal():
    layout = [
        [sg.Text("SAP PO Nr from:", size=16), sg.Input(key="-F-SAP-PO-FROM-",   size=25),
         sg.Text("SAP PO Nr to:", size=16), sg.Input(key="-F-SAP-PO-TO-",   size=25)],
        [sg.Text("Sender:", size=16), sg.Input(key="-F-SENDER-",   size=72)],
        [sg.Text("Delivery:", size=16), sg.Input(key="-F-DELIVERY-",   size=72)],
        [sg.Text("Loading date from:", size=16), sg.Input(key="-F-LOADING-FROM-", size=28, readonly=True, disabled_readonly_background_color="white"), sg.CalendarButton("Pick",target="-F-LOADING-FROM-",format="%Y-%m-%d"),
         sg.Text("Loading date to:", size=16), sg.Input(key="-F-LOADING-TO-", size=28, readonly=True, disabled_readonly_background_color="white"), sg.CalendarButton("Pick",target="-F-LOADING-TO-",format="%Y-%m-%d")],
        [sg.Text("Unloading date from:", size=16), sg.Input(key="-F-UNLOADING-FROM-", size=28, readonly=True, disabled_readonly_background_color="white"), sg.CalendarButton("Pick",target="-F-UNLOADING-FROM-",format="%Y-%m-%d"),
         sg.Text("Unloading date to:", size=16), sg.Input(key="-F-UNLOADING-TO-", size=28, readonly=True, disabled_readonly_background_color="white"), sg.CalendarButton("Pick",target="-F-UNLOADING-TO-",format="%Y-%m-%d")],
        [sg.Text("Pallet count min:", size=16), sg.Input(key="-F-PALLETS-MIN-",   size=25),
         sg.Text("Pallet count max:", size=16), sg.Input(key="-F-PALLETS-MAX-",   size=25)],
        [sg.Text("Gross weight min:", size=16), sg.Input(key="-F-WEIGHT-MIN-",   size=25),
         sg.Text("Gross weight max:", size=16), sg.Input(key="-F-WEIGHT-MAX-",   size=25)],
        [sg.Text("Forwarder:", size=16), sg.Input(key="-F-FORWARDER-",   size=72)],
        [sg.Text("Forwarder contact:", size=16), sg.Input(key="-F-FORWARDER-CONTACT-",   size=72)],
        [sg.Text("Cost min:", size=16), sg.Input(key="-F-COST-MIN-",   size=25),
         sg.Text("Cost max:", size=16), sg.Input(key="-F-COST-MAX-",   size=25)],
        [sg.Text("Customs:", size=16), sg.Combo(temperature_customs_options, key="-F-CUSTOMS-", default_value="", readonly=True, size=33)],
        [sg.Text("Temperature control:", size=16), sg.Combo(temperature_customs_options, key="-F-REF-", default_value="", readonly=True, size=33)],
        [sg.Button("Filter", key="-F-FILTER-"), sg.Button("Cancel")]
    ]
    app_window = sg.Window("Filter", layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-F-FILTER-":
            filtered_values = {
                "sap_po_from":       values["-F-SAP-PO-FROM-"],
                "sap_po_to":     values["-F-SAP-PO-TO-"],
                "sender":  values["-F-SENDER-"],
                "delivery": values["-F-DELIVERY-"],
                "loading_from":   values["-F-LOADING-FROM-"],
                "loading_to": values["-F-LOADING-TO-"],
                "unloading_from":    values["-F-UNLOADING-FROM-"],
                "unloading_to":  values["-F-UNLOADING-TO-"],
                "pallets_min":    values["-F-PALLETS-MIN-"],
                "pallets_max":  values["-F-PALLETS-MAX-"],
                "weight_min":    values["-F-WEIGHT-MIN-"],
                "weight_max":  values["-F-WEIGHT-MAX-"],
                "forwarder":    values["-F-FORWARDER-"],
                "forwarder_contact":    values["-F-FORWARDER-CONTACT-"],
                "cost_min":  values["-F-COST-MIN-"],
                "cost_max":  values["-F-COST-MAX-"],
                "customs":  values["-F-CUSTOMS-"],
                "ref":  values["-F-REF-"],
            }
            app_window.close()
            return filtered_values

def forwarder_contacts_modal(fw_id, fw_name):
    # checks contacts in databse for the selected forwarder
    fw_contact_df = return_fw_contacts(fw_id)
    
    selected_row = None
    sort_column = None
    sort_ascending = True
    
    fw_contact_columns = [
        sg.Column([[sg.Table(
            values=[],
            headings=FORWARDER_CONTACT_COLUMNS,
            key="-FW-CONTACTS-TABLE-",
            auto_size_columns=False,
            col_widths=[3, 15, 15, 15, 15, 20],
            justification="left",
            num_rows=15,
            enable_events=True,
            enable_click_events=True, # for sorting
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            expand_x=True,
            expand_y=True,
            )]], expand_x=True)
    ]
    
    layout = [
        [
        sg.Button("Create New Contact",  key="-BTN-CREATE-FWCONTACT-", size=15),
        sg.Button("Edit Contact", key="-BTN-EDIT-FWCONTACT-", size=15),
        sg.Button("Delete Contact", key="-BTN-DELETE-FWCONTACT-", size=15),
        sg.Button("Exit", key="-BTN-EXIT-FWCONTACT-", size=15),
        ],
        [sg.Text("", key="-FW-C-STATUS-", size=60, text_color="green")],
        fw_contact_columns
    ]
    
    app_window = sg.Window(
        f"{fw_name} contacts",
        layout,
        resizable=True,
        size=(1000, 400),
        finalize=True
    )
    
    app_window["-FW-CONTACTS-TABLE-"].update(values=df_to_table(fw_contact_df, FW_CONTACT_DB_COLUMNS))
    
    # function to display/change statuss text
    def fw_cont_statuss(text, sel_color="green"):
        app_window["-FW-C-STATUS-"].update(text, text_color=sel_color)
    
    # function to refresh forwarder contacts table
    def refresh_fw_contacts():
        nonlocal fw_contact_df

        fw_contact_df = return_fw_contacts(fw_id)

        app_window["-FW-CONTACTS-TABLE-"].update(
            values=df_to_table(
                fw_contact_df,
                FW_CONTACT_DB_COLUMNS
            )
        )
    
    while True:
        action, values = app_window.read()
        
        # Make the columns sortable
        if isinstance(action, tuple) and action[0] == "-FW-CONTACTS-TABLE-":
            row, col = action[2]
            if row == -1:
                column_name = FW_CONTACT_DB_COLUMNS[col]
                if sort_column == column_name:
                    sort_ascending = not sort_ascending
                else:
                    sort_column = column_name
                    sort_ascending = True
                fw_contact_df = fw_contact_df.sort_values(
                    by=column_name,
                    ascending=sort_ascending,
                    ignore_index=True
                )
                app_window["-FW-CONTACTS-TABLE-"].update(
                    values=df_to_table(
                        fw_contact_df,
                        ["fw_contact_id", "fw_c_name", "fw_c_surname",
                         "fw_c_position", "fw_c_phone", "fw_c_email"]
                    )
                )
            else:
                selected_row = row
        # Closes the forwarder contact modal
        if action in (sg.WIN_CLOSED, "-BTN-EXIT-FWCONTACT-"):
            app_window.close()
            break
        # opens a modal to create a new forwarder contact
        elif action == "-BTN-CREATE-FWCONTACT-":
            # fw_id, fw_name
            new_values = create_fw_contact_modal(f"Create a new contact for {fw_name}")
            if new_values:
                new_record = add_fw_contact(
                    fw_id, new_values["-FWCONTACT-NAME-"], new_values["-FWCONTACT-SURNAME-"], new_values["-FWCONTACT-POS-"],
                    new_values["-FWCONTACT-PHONE-"],new_values["-FWCONTACT-EMAIL-"]
                )
                # Reload contacts
                fw_contact_df = return_fw_contacts(fw_id)
                app_window["-FW-CONTACTS-TABLE-"].update(values=df_to_table(fw_contact_df, FW_CONTACT_DB_COLUMNS))
                fw_cont_statuss(f"✅ {fw_name} contact Nr.{new_record} added!")
                selected_row = None
        # opens a modal to edit a new forwarder contact
        elif action == "-BTN-EDIT-FWCONTACT-":
            if selected_row is None:
                fw_cont_statuss("Select a contact!", "red")
            else:
                row = fw_contact_df.iloc[selected_row]
                contact_id = int(row["fw_contact_id"])
                
                existing = {
                    "fw_c_name": str(row["fw_c_name"]),
                    "fw_c_surname": str(row["fw_c_surname"]),
                    "fw_c_position": str(row["fw_c_position"]),
                    "fw_c_phone": str(row["fw_c_phone"]),
                    "fw_c_email": str(row["fw_c_email"]),
                }
                new_values = create_fw_contact_modal(f"Editing contact Nr.{contact_id}", existing)
                if new_values:
                    updated_values = {
                        "fw_c_name": new_values["-FWCONTACT-NAME-"],
                        "fw_c_surname": new_values["-FWCONTACT-SURNAME-"],
                        "fw_c_position": new_values["-FWCONTACT-POS-"],
                        "fw_c_phone": new_values["-FWCONTACT-PHONE-"],
                        "fw_c_email": new_values["-FWCONTACT-EMAIL-"],
                    }
                    edit_db(contact_id, updated_values, 't_fw_contact', 'fw_contact_id')
                    
                    refresh_fw_contacts()
                    fw_cont_statuss(f"✅ Contact Nr.{contact_id} updated!")
                    selected_row = None
        elif action == "-BTN-DELETE-FWCONTACT-":
            if selected_row is None:
                fw_cont_statuss("Select a contact!", "red")
            else:
                row = fw_contact_df.iloc[selected_row]
                contact_id = int(row["fw_contact_id"])
                contact_name_surname = f'{str(row["fw_c_name"])} {str(row["fw_c_surname"])}'
                
                confirm = sg.popup_yes_no(
                    f"Delete ID Nr.{contact_id}?\n"
                    f"{contact_name_surname}\n"
                    f"from {fw_name}",
                    title="Confirm deleting a record"
                )
                if confirm == "Yes":
                    delete_db(contact_id, 't_fw_contact', 'fw_contact_id')
                    refresh_fw_contacts()
                    selected_row = None
                    fw_cont_statuss(f"🗑   ID Nr.{contact_id} deleted!")
                    
            
def create_fw_contact_modal(title, existing=None):
    e = existing or {}
    layout =[
        [sg.Text("Name:", size=16), sg.Input(e.get("fw_c_name", ""), key="-FWCONTACT-NAME-", size=35)],
        [sg.Text("Surname:", size=16), sg.Input(e.get("fw_c_surname", ""), key="-FWCONTACT-SURNAME-", size=35)],
        [sg.Text("Position:", size=16), sg.Input(e.get("fw_c_position", ""), key="-FWCONTACT-POS-", size=35)],
        [sg.Text("Phone Nr:", size=16), sg.Input(e.get("fw_c_phone", ""), key="-FWCONTACT-PHONE-", size=35)],
        [sg.Text("E-mail:", size=16), sg.Input(e.get("fw_c_email", ""), key="-FWCONTACT-EMAIL-", size=35)],
        [sg.Button("Save", key="-FWCONTACT-SAVE-"), sg.Button("Cancel")]
    ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-FWCONTACT-SAVE-":
            app_window.close()
            return values
    

def user_entry_modal(title, existing=None):
    e = existing or {}
    if existing:
        layout =[
            [sg.Text("Name:", size=16), sg.Input(e.get("name", ""), key="-USER-NAME-", size=35)],
            [sg.Text("Surname:", size=16), sg.Input(e.get("surname", ""), key="-USER-SURNAME-", size=35)],
            #[sg.Text("Role:", size=16), sg.Input(e.get("role", ""), key="-USER-ROLE-", size=35)],
            [sg.Text("Role:", size=16), sg.Combo(user_roles, key="-USER-ROLE-", default_value=e.get("role", ""), readonly=True, size=35)],
            [sg.Text("E-mail:", size=16), sg.Input(e.get("email", ""), key="-USER-EMAIL-", size=35)],
            [sg.Text("Phone:", size=16), sg.Input(e.get("phone", ""), key="-USER-PHONE-", size=35)],
            [sg.Text("Login:", size=16), sg.Input(e.get("login", ""), key="-USER-LOGIN-", size=35)],
            [sg.Text("Password:", size=16), sg.Input(e.get("password", ""), key="-USER-PASSWORD-", size=35)],
            [sg.Button("Save", key="-USER-SAVE-"), sg.Button("Cancel")]
        ]
    else:
        layout =[
            [sg.Text("Name:", size=16), sg.Input(e.get("name", ""), key="-USER-NAME-", size=35)],
            [sg.Text("Surname:", size=16), sg.Input(e.get("surname", ""), key="-USER-SURNAME-", size=35)],
            #[sg.Text("Role:", size=16), sg.Input(e.get("role", ""), key="-USER-ROLE-", size=35)],
            [sg.Text("Role:", size=16), sg.Combo(user_roles, key="-USER-ROLE-", default_value=user_roles[0], readonly=True, size=35)],
            [sg.Text("E-mail:", size=16), sg.Input(e.get("email", ""), key="-USER-EMAIL-", size=35)],
            [sg.Text("Phone:", size=16), sg.Input(e.get("phone", ""), key="-USER-PHONE-", size=35)],
            [sg.Text("Login:", size=16), sg.Input(e.get("login", ""), key="-USER-LOGIN-", size=35)],
            [sg.Text("Password:", size=16), sg.Input(e.get("password", ""), key="-USER-PASSWORD-", size=35)],
            [sg.Button("Save", key="-USER-SAVE-"), sg.Button("Cancel")]
        ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-USER-SAVE-":
            app_window.close()
            return values
        
# Entry modal window for creating new records and editing existin ones
def entry_modal(title, existing=None, nr=None):
    e = existing or {}
    forwarder_contact_list = []
    
    if existing:
        layout = [
            [sg.Text("SAP PO Nr:",           size=16), sg.Input(e.get("sap_po", ""),          key="-SAP_PO-",   size=35)],
            [sg.Text("Sender:",           size=16), sg.Input(e.get("sender", ""),          key="-SENDER-",   size=35)],
            [sg.Text("Delivery:",           size=16), sg.Combo(['Gemoss M7', 'Gemoss M75'], key="-DELIVERY-", default_value=e.get("delivery", ""), readonly=True, size=33)],
            [sg.Text("Loading date:", size=16), sg.Input(e.get("loading", ""), key="-LOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-LOADING-",format="%Y-%m-%d")],
            [sg.Text("Unloading date:", size=16), sg.Input(e.get("unloading", ""), key="-UNLOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-UNLOADING-",format="%Y-%m-%d")],
            [sg.Text("Pallet count:",           size=16), sg.Input(e.get("pallets", ""),          key="-PALLETS-",   size=35)],
            [sg.Text("Gross weight:",           size=16), sg.Input(e.get("weight", ""),          key="-WEIGHT-",   size=35)],
            [sg.Text("Forwarder:", size=16), sg.Combo(forwarders_list, key="-FORWARDER-", default_value=e.get("forwarder", ""), readonly=True, size=33, enable_events=True)],
            [sg.Text("Forwarder contact:", size=16), sg.Combo(forwarder_contact_list, key="-FORWARDER-CONTACT-", default_value=e.get("forwarder_contact", ""), readonly=True, size=33)],
            [sg.Text("Cost:",           size=16), sg.Input(e.get("cost", ""),          key="-COST-",   size=35)],
            [sg.Text("Customs:", size=16), sg.Combo(temperature_customs_options, key="-CUSTOMS-", default_value=e.get("customs", ""), readonly=True, size=33)],
            [sg.Text("Temperature control:", size=16), sg.Combo(temperature_customs_options, key="-REF-", default_value=e.get("ref", ""), readonly=True, size=33)],
            [sg.Push(),sg.Button("Create transport order in PDF", key="-CREATE-PDF-"), sg.Push()],
            [sg.Push(),sg.Button("Save", key="-SAVE-", size=15), sg.Button("Cancel", size=15), sg.Push()]
        ]
    else:
        layout = [
            [sg.Text("SAP PO Nr:", size=16), sg.Input(e.get("sap_po", ""),          key="-SAP_PO-",   size=35)],
            [sg.Text("Sender:", size=16), sg.Input(e.get("sender", ""),          key="-SENDER-",   size=35)],
            [sg.Text("Delivery:", size=16), sg.Combo(['Gemoss M7', 'Gemoss M75'], key="-DELIVERY-", default_value=e.get("delivery", ""), readonly=True, size=33)],
            [sg.Text("Loading date:", size=16), sg.Input(e.get("loading", ""), key="-LOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-LOADING-",format="%Y-%m-%d")],
            [sg.Text("Unloading date:", size=16), sg.Input(e.get("unloading", ""), key="-UNLOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-UNLOADING-",format="%Y-%m-%d")],
            [sg.Text("Pallet count:", size=16), sg.Input(e.get("pallets", ""),          key="-PALLETS-",   size=35)],
            [sg.Text("Gross weight:", size=16), sg.Input(e.get("weight", ""),          key="-WEIGHT-",   size=35)],
            [sg.Text("Forwarder:", size=16), sg.Combo(forwarders_list, key="-FORWARDER-", default_value=e.get("forwarder", ""), readonly=True, size=33, enable_events=True)],
            [sg.Text("Forwarder contact:", size=16), sg.Combo(forwarder_contact_list, key="-FORWARDER-CONTACT-", default_value=e.get("forwarder", ""), readonly=True, size=33)],
            [sg.Text("Cost:", size=16), sg.Input(e.get("cost", ""),          key="-COST-",   size=35)],
            [sg.Text("Customs:", size=16), sg.Combo(temperature_customs_options, key="-CUSTOMS-", default_value=e.get("customs", ""), readonly=True, size=33)],
            [sg.Text("Temperature control:", size=16), sg.Combo(temperature_customs_options, key="-REF-", default_value=e.get("ref", ""), readonly=True, size=33)],
            [sg.Button("Save", key="-SAVE-"), sg.Button("Cancel")]
        ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-SAVE-":
            app_window.close()
            return values
        
        # action triggered when "Create transport order in PDF" button is pressed in record Edit modal - it creates a PDF file/transport order
        if action == "-CREATE-PDF-":
            create_order_pdf(existing, nr)
            print('Create transport order in PDF button pressed!')
        elif action == "-FORWARDER-":
            selected_forwarder_name = values['-FORWARDER-']
            print(f'User selected forwarder - {selected_forwarder_name}')
            fw_id = return_forwarders(selected_forwarder_name)
            print(f'Forwarder id = {fw_id}')
            forwarder_contact_list = return_fw_contacts(fw_id, 'list_required')
            print(forwarder_contact_list)
            
            if forwarder_contact_list:
                app_window["-FORWARDER-CONTACT-"].update(values=forwarder_contact_list, value=forwarder_contact_list[0])
            else:
                app_window["-FORWARDER-CONTACT-"].update(values=['No contact'], value='No contact')

def login_modal():  
    #Creates an error popup window. Accepts Enter as keypress to close the window
    def error_popup(message):
        layout = [
            [sg.Text(message, pad=(20, 20))],
            [sg.Push(), sg.Button("OK", key="-OK-", size=10, bind_return_key=True), sg.Push()]
        ]
        # Noņemam return_keyboard_events=True, lai neķertu "Enter" no iepriekšējā loga
        error_window = sg.Window("Kļūda", layout, modal=True, finalize=True, element_justification='c')
        
        # Svarīgi: Iestatām fokusu uz pogu, lai Enter strādātu uzreiz
        error_window["-OK-"].set_focus()
        
        while True:
            event, values = error_window.read()
            if event in (sg.WIN_CLOSED, "-OK-"):
                break
        error_window.close()
    
    
    sg.theme_list()

    received_values = {}

    layout = [
        [sg.Push(),sg.Image(filename="gemoss_logo.png", subsample=2), sg.Push()],
        [sg.Push(),sg.Text('GEMOSS TMS LOGIN', font=("Helvetica", 14, "bold"), pad=(10,10)), sg.Push()],
        [sg.Text("Login:", size=16), sg.Input(received_values.get("login", ""), key="-LOGIN-VALUE-", enable_events=True, size=25)],
        [sg.Text("Password:", size=16), sg.Input(received_values.get("passw", ""), key="-PASSW-VALUE-", enable_events=True, size=25, password_char="*")],
        [sg.Push(),sg.Button("Login", key="-LOGIN-", bind_return_key=True, size=15), sg.Button("Cancel", size=15), sg.Push()]
    ]
    
    app_window = sg.Window('GEMOSS TMS LOGIN', layout, modal=True, finalize=True)
    
    app_window['-LOGIN-VALUE-'].bind("<FocusIn>", "_FOCUS")
    app_window['-PASSW-VALUE-'].bind("<FocusIn>", "_FOCUS")
    has_input_focus = None

    while True:
        action, values = app_window.read()
        
        if "_FOCUS" in action:
            has_input_focus = action.replace("_FOCUS", "")
            continue
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-LOGIN-":
            login_validation = check_login(values["-LOGIN-VALUE-"], values["-PASSW-VALUE-"])
            
            if login_validation:
                print(f'Received login:  {login_validation.get("login")}')
                print(f'Received password:  {login_validation.get("password")}')
                app_window.close()
                main_menu(login_validation, "DarkAmber")
                return login_validation
            else:
                error_popup("Incorrect login or password!")
            print('LOGIN button pressed')


# --- Main menu ---
def main_menu(login_validation, theme_name):
    create_table()
    
    def show_view(view_key):
        views = [
            '-VIEW-TRANSPORT-',
            '-VIEW-STATISTICS-',
            '-VIEW-COMPANIES-',
            '-VIEW-FORWARDERS-',
            '-VIEW-USERS-'
        ]
        for v in views:
            app_window[v].update(visible=(v == view_key))
    
    def create_orders_table(table_key):
        return sg.Column([[sg.Table(
                values=[],
                headings=ORDER_COLUMNS,
                key=table_key,
                auto_size_columns=False,
                col_widths=[4, 8, 18, 18, 10, 10, 5, 8, 18, 15, 10, 6, 5],
                justification="left",
                num_rows=30,
                enable_events=True,
                enable_click_events=True, # for sorting
                select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                expand_x=True,
                expand_y=True,
                )]], expand_x=True)
    
    user_columns = [
        sg.Column([[sg.Table(
            values=[],
            headings=USER_COLUMNS,
            key="-USER-TABLE-",
            auto_size_columns=False,
            col_widths=[14, 16, 16, 16, 16, 16, 16, 16],
            justification="left",
            num_rows=30,
            enable_events=True,
            enable_click_events=True, # for sorting
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            expand_x=True,
            expand_y=True,
            )]], expand_x=True)
    ]
    # ['Nr', 'Name', 'Reg Nr', 'VAT Nr', 'Street', 'City', 'Post code', 'Country', 'Payment days']
    forwarder_columns = [
        sg.Column([[sg.Table(
            values=[],
            headings=FORWARDER_COLUMNS,
            key="-FORWARDER-TABLE-",
            auto_size_columns=False,
            col_widths=[5, 22, 15, 15, 15, 15, 15, 15, 8],
            justification="left",
            num_rows=30,
            enable_events=True,
            enable_click_events=True, # for sorting
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            expand_x=True,
            expand_y=True,
            )]], expand_x=True)
    ]
    
    company_columns = [
        sg.Column([[sg.Table(
            values=[],
            headings=COMPANY_COLUMNS,
            key="-COMPANY-TABLE-",
            auto_size_columns=False,
            col_widths=[5, 20, 13, 13, 13, 13, 13, 13],
            justification="left",
            num_rows=30,
            enable_events=True,
            enable_click_events=True, # for sorting
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            expand_x=True,
            expand_y=True,
            )]], expand_x=True)
    ]

    total_records = [[sg.Text(key="-TOTAL-ACTIVE-RECORDS-")]]
    total_cost = [[sg.Text(key="-TOTAL-COST-")]]
    total_pallets = [[sg.Text(key="-TOTAL-PALLETS-")]]
    cost_per_cargo = [[sg.Text(key="-AVERAGE-CARGO-COST-")]]
    cost_per_pallet = [[sg.Text(key="-AVERAGE-PALLET-COST-")]]
    pallets_per_cargo = [[sg.Text(key="-PALLETS-PER-CARGO-")]]
    
    sidebar_layout = [
        [sg.Button('Transport orders', key='-TRANSPORT-ORDERS-', size=(18, 3))],
        [sg.Button('Statistics', key='-STATISTICS-', size=(18, 3))],
        [sg.Button('Companies', key='-COMPANIES-', size=(18, 3))],
        [sg.Button('Forwarders', key='-MENU-FORWARDERS-', size=(18, 3))],
        [sg.Button('Users', key='-USERS-', size=(18, 3))],
        #[sg.VPush()] # Nobīda pogas uz augšu
    ]
    
    transport_layout = [
        [
        sg.Button("Create",  key="-BTN-CREATE-", size=10),
        sg.Button("Open/Edit", key="-BTN-EDIT-", size=10),
        sg.Button("Delete", key="-BTN-DELETE-", size=10),
        sg.Button("Show All", key="-BTN-ALLDATA-", size=10),
        sg.VerticalSeparator(),
        sg.Button("Filter", key="-BTN-FILTER-", size=10),
        sg.Text("Search:", pad=(5, 5)),
        sg.Input(key="-SEARCH-", size=20),
        sg.Button("Search", key="-BTN-SEARCH-", size=10),
        sg.Button("Exit", key="-BTN-EXIT-", size=10),
        sg.Push(),sg.Combo(['Black', 'BlueMono', 'BluePurple', 'BrightColors', 'BrownBlue', 'Dark', 'Dark2', 'DarkAmber', 'DarkBlack', 'DarkBlack1', 'DarkBlue', 'DarkBlue1', 'DarkBlue10', 'DarkBlue11', 'DarkBlue12', 'DarkBlue13', 'DarkBlue14', 'DarkBlue15', 'DarkBlue16', 'DarkBlue17', 'DarkBlue2', 'DarkBlue3', 'DarkBlue4', 'DarkBlue5', 'DarkBlue6', 'DarkBlue7', 'DarkBlue8', 'DarkBlue9', 'DarkBrown', 'DarkBrown1', 'DarkBrown2', 'DarkBrown3', 'DarkBrown4', 'DarkBrown5', 'DarkBrown6', 'DarkGreen', 'DarkGreen1', 'DarkGreen2', 'DarkGreen3', 'DarkGreen4', 'DarkGreen5', 'DarkGreen6', 'DarkGrey', 'DarkGrey1', 'DarkGrey2', 'DarkGrey3', 'DarkGrey4', 'DarkGrey5', 'DarkGrey6', 'DarkGrey7', 'DarkPurple', 'DarkPurple1', 'DarkPurple2', 'DarkPurple3', 'DarkPurple4', 'DarkPurple5', 'DarkPurple6', 'DarkRed', 'DarkRed1', 'DarkRed2', 'DarkTanBlue', 'DarkTeal', 'DarkTeal1', 'DarkTeal10', 'DarkTeal11', 'DarkTeal12', 'DarkTeal2', 'DarkTeal3', 'DarkTeal4', 'DarkTeal5', 'DarkTeal6', 'DarkTeal7', 'DarkTeal8', 'DarkTeal9', 'Default', 'Default1', 'DefaultNoMoreNagging', 'Green', 'GreenMono', 'GreenTan', 'HotDogStand', 'Kayak', 'LightBlue', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4', 'LightBlue5', 'LightBlue6', 'LightBlue7', 'LightBrown', 'LightBrown1', 'LightBrown10', 'LightBrown11', 'LightBrown12', 'LightBrown13', 'LightBrown2', 'LightBrown3', 'LightBrown4', 'LightBrown5', 'LightBrown6', 'LightBrown7', 'LightBrown8', 'LightBrown9', 'LightGray1', 'LightGreen', 'LightGreen1', 'LightGreen10', 'LightGreen2', 'LightGreen3', 'LightGreen4', 'LightGreen5', 'LightGreen6', 'LightGreen7', 'LightGreen8', 'LightGreen9', 'LightGrey', 'LightGrey1', 'LightGrey2', 'LightGrey3', 'LightGrey4', 'LightGrey5', 'LightGrey6', 'LightPurple', 'LightTeal', 'LightYellow', 'Material1', 'Material2', 'NeutralBlue', 'Purple', 'Reddit', 'Reds', 'SandyBeach', 'SystemDefault', 'SystemDefault1', 'SystemDefaultForReal', 'Tan', 'TanBlue', 'TealMono', 'Topanga'], default_value=theme_name, key='-DEFAULT-COLOR-', enable_events=True, readonly=True)
        ],
        [sg.Text("", key="-STATUS-", size=60, text_color="green")],
        #table_columns,
        [create_orders_table("-TABLE-")],
        [sg.Frame(title="Total cargos", layout=total_records, 
        border_width=2, relief=sg.RELIEF_SOLID, size=(120, 50)), sg.Frame(title="Total cost", layout=total_cost, 
        border_width=2, relief=sg.RELIEF_SOLID, size=(120, 50)), sg.Frame(title="Total pallets", layout=total_pallets, 
        border_width=2, relief=sg.RELIEF_SOLID, size=(120, 50)), sg.Frame(title="Cost per cargo", layout=cost_per_cargo, 
        border_width=2, relief=sg.RELIEF_SOLID, size=(120, 50)), sg.Frame(title="Cost per pallet", layout=cost_per_pallet, 
        border_width=2, relief=sg.RELIEF_SOLID, size=(120, 50)), sg.Frame(title="Pallets per cargo", layout=pallets_per_cargo, 
        border_width=2, relief=sg.RELIEF_SOLID, size=(120, 50))],
        #[sg.Text(key="-TOTAL-ACTIVE-RECORDS-"), sg.Text(key="-AVERAGE-CARGO-COST-"), sg.Text(key="-AVERAGE-PALLET-COST-"), sg.Text(key="-AVERAGE-PALLET-AMOUNT-")]
    ]
    
    statistics_layout = [
            [
                sg.Button("Create diagram", key="-BTN-CREATE-DIAGRAM-", size=12),
                sg.Text("Stat type:", size=7), sg.Combo(statistics_types, key="-STATISTICS-TYPE-", default_value=statistics_types[0], readonly=True, size=20),
                sg.Text("Period:", size=5), sg.Combo(statistic_period, key="-PERIOD-TYPE-", default_value=statistic_period[1], readonly=True, size=10),
                sg.VerticalSeparator(),
                sg.Push(),sg.Button("Filter", key="-BTN-FILTER-STATISTICS-", size=10),
                sg.Button("Show All", key="-BTN-ALLDATA-STATISTICS-", size=10),
                sg.Text("Search:", pad=(5, 5)),
                sg.Input(key="-SEARCH-STATISTICS-", size=20),
                sg.Button("Search", key="-BTN-SEARCH-STATISTICS-", size=10),
                sg.Button("Exit", key="-BTN-EXIT-STATISTICS-", size=10),
            ],
            [create_orders_table("-STATISTICS-TABLE-")],
        ]
    
    companies_layout = [
            [
                sg.Button("Create company",  key="-BTN_CREATE-COMPANY-", size=(8, 2)),
                sg.Button("Edit company", key="-BTN-EDIT-COMPANY-", size=(8, 2)),
                sg.Button("Delete company", key="-BTN-DELETE-COMPANY-", size=(8, 2)),
                sg.VerticalSeparator(),
                sg.Button("Create contact", key="-BTN-CREATE-CONTACT-", size=(8, 2)),
                sg.Button("Show contacts", key="-BTN-SHOW-CONTACT-", size=(8, 2)),
                sg.VerticalSeparator(),
                sg.Button("Create address", key="-BTN-CREATE-ADDRESS-", size=(8, 2)),
                sg.Button("Show addresses", key="-BTN-SHOW-ADDRESS-", size=(8, 2)),
                sg.VerticalSeparator(),
                sg.Button("Show All", key="-BTN-ALLDATA-COMPANY-", size=(8, 2)),
                sg.Text("Search:", pad=(5, 5)),
                sg.Input(key="-IN-SEARCH-COMPANY-", size=20),
                sg.Button("Search", key="-BTN-SEARCH-COMPANY-", size=(8, 2)),
                sg.Button("Exit", key="-BTN-EXIT-COMPANY-", size=(8, 2)),
            ],
            [sg.Text("", key="-TXT-COMPANY-STATUS-", size=60, text_color="green")],
            company_columns
        ]
    
    forwarders_layout = [
            [
                sg.Button("Create",  key="-BTN-CREATE-FORWARDER-", size=10),
                sg.Button("Edit", key="-BTN-EDIT-FORWARDER-", size=10),
                sg.Button("Delete", key="-BTN-DELETE-FORWARDER-", size=10),
                sg.VerticalSeparator(),
                sg.Button("Create contact", key="-CREATE-FW-CONTACT-", size=12),
                sg.Button("Show contacts", key="-SHOW-FW-CONTACT-", size=12),
                sg.VerticalSeparator(),
                sg.Button("Show All", key="-BTN-ALLDATA-FORWARDER-", size=10),
                sg.Text("Search:", pad=(5, 5)),
                sg.Input(key="-SEARCH-FORWARDER-", size=20),
                sg.Button("Search", key="-BTN-SEARCH-FORWARDER-", size=10),
                sg.Button("Exit", key="-BTN-EXIT-FORWARDER-", size=10),
            ],
            [sg.Text("", key="-FWSTATUS-", size=60, text_color="green")],
            forwarder_columns
        ]
    
    users_layout = [
            [
                sg.Button("Create New User",  key="-BTN-CREATE-USER-", size=15),
                sg.Button("Edit User", key="-BTN-EDIT-USER-", size=15),
                sg.Button("Delete User", key="-BTN-DELETE-USER-", size=15),
                sg.Button("Exit", key="-BTN-EXIT-USER-", size=15),
            ],
            [sg.Text("")],
            user_columns
        ]
    
    # Area of each section buttons, tables etc. - 6 possible layout views - only 1 visible at each time
    content_area = [
        [
            sg.Column(transport_layout,   key='-VIEW-TRANSPORT-',  visible=True,  expand_x=True, expand_y=True),
            sg.Column(statistics_layout,  key='-VIEW-STATISTICS-', visible=False, expand_x=True, expand_y=True),
            sg.Column(companies_layout,   key='-VIEW-COMPANIES-',  visible=False, expand_x=True, expand_y=True),
            sg.Column(forwarders_layout,  key='-VIEW-FORWARDERS-', visible=False, expand_x=True, expand_y=True),
            sg.Column(users_layout,       key='-VIEW-USERS-',      visible=False, expand_x=True, expand_y=True),
        ]
    ]
    
    # Detect screen size and scale layout to fit any screen (laptop or desktop)
    import tkinter as _tk
    _root = _tk.Tk()
    _root.withdraw()
    SCREEN_W = _root.winfo_screenwidth()
    SCREEN_H = _root.winfo_screenheight()
    _root.destroy()

    SIDEBAR_W = 180
    CONTENT_W = SCREEN_W - SIDEBAR_W - 20   # 20px breathing room for separator + padding
    CONTENT_H = SCREEN_H - 80               # 80px for title bar + top header row

    # Actual displayed layout - inner fixed layout, wrapped in scrollable column
    inner_layout = [
        [
            sg.Text("Transport Management System", font=("Helvetica", 14, "bold"), pad=(10,10)), 
            sg.Push(),sg.Text(f'{login_validation.get("name")} {login_validation.get("surname")}', font=("Helvetica", 10, "bold"), pad=(10,10))
        ],
        [
            sg.Column(sidebar_layout, key="-SIDEBAR-", size=(SIDEBAR_W, CONTENT_H), expand_x=False, expand_y=False),
            sg.VerticalSeparator(),
            sg.Column(content_area, key="-CONTENT-", size=(CONTENT_W, CONTENT_H), expand_x=False, expand_y=False)
        ]
    ]

    # Wrap everything in a scrollable column so scrollbars appear when the
    # window is resized smaller than the fixed inner layout dimensions.
    layout = [[
        sg.Column(
            inner_layout,
            key="-SCROLL-AREA-",
            scrollable=True,
            vertical_scroll_only=False,
            expand_x=True,
            expand_y=True,
        )
    ]]

    app_window = sg.Window(
        "Transport Management System",
        layout,
        resizable=True,
        size=(1200, 600),
        finalize=True
    )

    # Fixed content dimensions — must match the size= values set on
    # -SIDEBAR- (180) + separator (~2) + -CONTENT- (1700) and height (900).
    CONTENT_W = 1900
    CONTENT_H = 950

    scroll_elem  = app_window["-SCROLL-AREA-"]
    scroll_frame = scroll_elem.TKColFrame
    canvas       = scroll_frame.canvas
    hsb          = scroll_elem.hsb
    vsb          = scroll_elem.vsb

    # Save the original pack settings FreeSimpleGUI used so we can restore them
    hsb_pack = hsb.pack_info()
    vsb_pack = vsb.pack_info()

    # Hide both initially — window starts maximized so no scrollbars needed
    hsb.pack_forget()
    vsb.pack_forget()

    def _update_scrollbars(event=None):
        win_w = app_window.TKroot.winfo_width()
        win_h = app_window.TKroot.winfo_height()

        hsb_visible = hsb.winfo_ismapped()
        vsb_visible = vsb.winfo_ismapped()

        if win_w < CONTENT_W:
            if not hsb_visible:
                hsb.pack(**hsb_pack)
        else:
            if hsb_visible:
                hsb.pack_forget()
                canvas.xview_moveto(0)

        if win_h < CONTENT_H:
            if not vsb_visible:
                vsb.pack(**vsb_pack)
        else:
            if vsb_visible:
                vsb.pack_forget()
                canvas.yview_moveto(0)

        canvas.config(width=win_w, height=win_h)
        canvas.configure(scrollregion=canvas.bbox("all"))

    app_window.TKroot.bind("<Configure>", _update_scrollbars)

    app_window.maximize() 
    
    def refresh_table(df, table_key):
        app_window[table_key].update(values=df_to_table(df))
        
        if table_key == "-TABLE-":
            app_window["-TOTAL-ACTIVE-RECORDS-"].update(f'{len(df)}')
            
            print(f'Length: {len(df)}')

            if len(df) > 0:
                total_cost = 0 
                total_pallets = 0
                total_cost = df['cost'].sum()
                total_pallets = df['pallets'].sum()
                
                app_window["-TOTAL-COST-"].update(f'{int(total_cost):_}'.replace('_', ' ') + ' EUR')
                app_window["-TOTAL-PALLETS-"].update(f'{int(total_pallets)}')
                app_window["-AVERAGE-CARGO-COST-"].update(f"{ int(total_cost / len(df['cost'])):_}".replace('_', ' ')+ ' EUR')
                
                if total_pallets > 0:
                    app_window["-AVERAGE-PALLET-COST-"].update(f'{ int(round(total_cost / total_pallets)) } EUR')
                else:
                    app_window["-AVERAGE-PALLET-COST-"].update('0 EUR')
                
                app_window["-PALLETS-PER-CARGO-"].update(f"{ int(round(total_pallets / len(df['cost']))) } pallets")
            else:
                app_window["-AVERAGE-CARGO-COST-"].update('0 EUR')
                app_window["-AVERAGE-PALLET-COST-"].update('0 EUR')
                app_window["-PALLETS-PER-CARGO-"].update('0 pallets')
        
    def statuss(text, sel_color="green"):
        app_window["-STATUS-"].update(text, text_color=sel_color)
    def fw_statuss(text, sel_color="green"):
        app_window["-FWSTATUS-"].update(text, text_color=sel_color)
    
    
    # --- initial data + sorting state ---
    current_df = read_all('transport', 'nr')
    sort_column = None
    sort_ascending = True
    selected_row = None
    
    def reset_sort_select():
        nonlocal sort_column, sort_ascending, selected_row
        sort_column = None
        sort_ascending = True
        selected_row = None
    
    refresh_table(current_df, "-TABLE-")
    
    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "-BTN-EXIT-", "-BTN-EXIT-STATISTICS-", "-BTN-EXIT-USER-", "-BTN-EXIT-FORWARDER-", "-BTN-EXIT-COMPANY-"):
            app_window.close()
            break
        
        if action == '-TRANSPORT-ORDERS-':
            show_view('-VIEW-TRANSPORT-')
            reset_sort_select()
            current_df = read_all('transport', 'nr')
            refresh_table(current_df, "-TABLE-")
            print('Transport Orders menu selected')
        elif action == '-STATISTICS-':
            print('Statisitcs menu selected')
            reset_sort_select()
            show_view('-VIEW-STATISTICS-')
            current_df = read_all('transport', 'nr')
            refresh_table(current_df, "-STATISTICS-TABLE-")
        elif action == '-COMPANIES-':
            print('Company menu selected')
            show_view('-VIEW-COMPANIES-')
            reset_sort_select()
            current_df = read_all('t_company', 'company_id')
            refresh_table(current_df, "-COMPANY-TABLE-")
        elif action == '-MENU-FORWARDERS-':
            print('Forwarders menu selected')
            show_view('-VIEW-FORWARDERS-')
            reset_sort_select()
            current_df = read_all('t_forwarder', 'forwarder_id')
            refresh_table(current_df, "-FORWARDER-TABLE-")
        elif action == '-USERS-':
            print('Users menu selected')
            show_view('-VIEW-USERS-')
            reset_sort_select()
            current_df = read_all('user', 'nr')
            refresh_table(current_df, "-USER-TABLE-")
        
        # - default theme color changing
        if action == '-DEFAULT-COLOR-':
            print(f"User selected: {values['-DEFAULT-COLOR-']}")
            sg.theme(f"{values['-DEFAULT-COLOR-']}")
            app_window.close()
            main_menu(login_validation, f"{values['-DEFAULT-COLOR-']}")


        # ── Tranport Order Table clicks + selecting + sorting)
        if isinstance(action, tuple) and "TABLE" in action[0]:
            
            table_key = action[0]
            row, col = action[2]

            # Header click → SORT
            if row == -1:
                column_name = current_df.columns[col]

                if sort_column == column_name:
                    sort_ascending = not sort_ascending
                else:
                    sort_column = column_name
                    sort_ascending = True

                current_df = current_df.sort_values(
                    by=column_name,
                    ascending=sort_ascending,
                    ignore_index=True
                )

                refresh_table(current_df, table_key)
                statuss(f"Sorted by '{column_name}' ({'ASC' if sort_ascending else 'DESC'})")

            # Row click → SELECT
            else:
                selected_row = row
        # ── Action triggered when Show All button is pressed - shows all data in database
        elif action == "-BTN-ALLDATA-":
            table_key = action[0]
            current_df = read_all('transport', 'nr')
            refresh_table(current_df, "-TABLE-")
            app_window["-SEARCH-"].update("")
            statuss("Showing all records!")
            
        elif action == "-BTN-ALLDATA-STATISTICS-":
            table_key = action[0]
            current_df = read_all('transport', 'nr')
            refresh_table(current_df, "-STATISTICS-TABLE-")
            app_window["-SEARCH-STATISTICS-"].update("")
            statuss("Showing all records!")
            
        elif action == "-BTN-ALLDATA-FORWARDER-":
            table_key = action[0]
            current_df = read_all('t_forwarder', 'forwarder_id')
            refresh_table(current_df, "-FORWARDER-TABLE-")
            app_window["-SEARCH-FORWARDER-"].update("")
            statuss("Showing all records!")
            
        # ── Action triggered when Search button is pressed - seasrches in Transport orders database for values that match from the searchbox
        elif action == "-BTN-SEARCH-":
            search_value = values["-SEARCH-"].strip()
            if not search_value:
                statuss("Ievadi meklēšanas tekstu!", "red")
            else:
                current_df = search_db(search_value, 'transport')
                refresh_table(current_df, "-TABLE-")
                statuss(f"Found: {len(current_df)} records")
        # ── Action triggered when Search button is pressed - seasrches in Forwarder table database for values that match from the searchbox
        elif action == "-BTN-SEARCH-FORWARDER-":
            search_value = values["-SEARCH-FORWARDER-"].strip()
            if not search_value:
                statuss("Ievadi meklēšanas tekstu!", "red")
            else:
                current_df = search_db(search_value, 't_forwarder')
                refresh_table(current_df, "-FORWARDER-TABLE-")
                fw_statuss(f"Found: {len(current_df)} records")
                
        elif action == "-BTN-SEARCH-STATISTICS-":
            search_value = values["-SEARCH-STATISTICS-"].strip()
            if not search_value:
                ("Ievadi meklēšanas tekstu!", "red")
            else:
                current_df = search_db(search_value, 'transport')
                refresh_table(current_df, "-STATISTICS-TABLE-")
                statuss(f"Found: {len(current_df)} records")
                
        
        # ── Action triggered when Filtrs button is pressed - opens a Filter modal window with filtring options
        elif action == "-BTN-FILTER-":
            filter = filter_modal()
            if filter is not None:
                current_df = filter_db(filter)
                refresh_table(current_df, "-TABLE-")
                selected_row = None
                statuss(f"🔎 Found: {len(current_df)} records")
                
        elif action == "-BTN-FILTER-STATISTICS-":
            filter = filter_modal()
            if filter is not None:
                current_df = filter_db(filter)
                refresh_table(current_df, "-STATISTICS-TABLE-")
                selected_row = None
                statuss(f"🔎 Found: {len(current_df)} records")
        
        # ── Action triggered when CREATE button is pressed - opens Entry modal for creating new record
        elif action == "-BTN-CREATE-":
            new_values = entry_modal("NEW TRANSPORT RECORD")
            if new_values:
                new_record = add_db(
                    new_values["-SAP_PO-"], new_values["-SENDER-"], new_values["-DELIVERY-"], new_values["-LOADING-"],
                    new_values["-UNLOADING-"], new_values["-PALLETS-"], new_values["-WEIGHT-"], new_values["-FORWARDER-"], new_values["-FORWARDER-CONTACT-"],
                    new_values["-COST-"], new_values["-CUSTOMS-"], new_values["-REF-"]
                )
                current_df = read_all('transport', 'nr')
                refresh_table(current_df, "-TABLE-")
                statuss(f"✅ Record Nr.{new_record} added!")
        
        # ── Action triggered when CREATE USER button is pressed - opens Entry modal for creating new record
        elif action == "-BTN-CREATE-USER-":
            print(
                "Sidebar:",
                app_window["-CONTENT-"].Widget.winfo_width()
            )
            new_values = user_entry_modal("NEW USER")
            print(
                "Sidebar:",
                app_window["-CONTENT-"].Widget.winfo_width()
            )
            
            if new_values:
                new_record = add_user(
                    new_values["-USER-NAME-"], new_values["-USER-SURNAME-"], new_values["-USER-ROLE-"], new_values["-USER-EMAIL-"],
                    new_values["-USER-PHONE-"], new_values["-USER-LOGIN-"], new_values["-USER-PASSWORD-"]
                )
                current_df = read_all('user', 'nr')
                refresh_table(current_df, "-USER-TABLE-")
                statuss(f"✅ User Nr.{new_record} added!")

        # ── Action triggered when CREATE FORWARDER button is pressed - opens Entry modal for creating new record
        elif action == "-BTN-CREATE-FORWARDER-":
            new_values = forwarder_entry_modal("NEW FORWARDER")
            if new_values:
                new_record = add_forwarder(
                    new_values["-FW-NAME-"], new_values["-FW-REG-"], new_values["-FW-VAT-"], new_values["-FW-STREET-"],
                    new_values["-FW-CITY-"], new_values["-FW-POST-"], new_values["-FW-COUNTRY-"], new_values["-FW-PAYMENT-"]
                )
                current_df = read_all('t_forwarder', 'forwarder_id')
                refresh_table(current_df, "-FORWARDER-TABLE-")
                fw_statuss(f"✅ Forwarder Nr.{new_record} added!")
        
        # ── Action triggered when CREATE COMPANY button is pressed - opens Entry modal for creating new record
        elif action == "-BTN_CREATE-COMPANY-":
            new_values = company_entry_modal("NEW COMPANY")
            if new_values:
                new_record = add_company(
                    new_values["-TXT-COMPANY-NAME-"], new_values["-TXT-COMPANY-REG-"], new_values["-TXT-COMPANY-VAT-"], new_values["-TXT-COMPANY-STREET-"],
                    new_values["-TXT-COMPANY-CITY-"], new_values["-TXT-COMPANY-POST-"], new_values["-TXT-COMPANY-COUNTRY-"], new_values["-IN-COMPANY-DETAILS-"], new_values["-TXT-COMPANY-PRODUCT-"]
                )
                current_df = read_all('t_company', 'company_id')
                refresh_table(current_df, "-COMPANY-TABLE-")
                fw_statuss(f"✅ Company Nr.{new_record} added!")
            
        # ── Action triggered when Delete button is pressed - deletes the selected record
        elif action == "-BTN-DELETE-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["nr"])
                
                confirm = sg.popup_yes_no(
                    f"Delete rectord Nr.{nr}?\n"
                    f"{row['sender']} | {row['sap_po']}",
                    title="Confirm deleting a record"
                )
                if confirm == "Yes":
                    delete_db(nr, 'transport')
                    current_df = read_all('transport', 'nr')
                    refresh_table(current_df, "-TABLE-")
                    selected_row = None
                    statuss(f"🗑️ Nr.{nr} deleted!")
        # ── Action triggered when Delete User button is pressed - deletes the selected record
        elif action == "-BTN-DELETE-USER-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["nr"])
                
                confirm = sg.popup_yes_no(
                    f"Delete rectord Nr.{nr}?\n"
                    f"{row['name']} {row['surname']}",
                    title="Confirm deleting a record"
                )
                if confirm == "Yes":
                    delete_db(nr, 'user')
                    current_df = read_all('user', 'nr')
                    refresh_table(current_df, "-USER-TABLE-")
                    selected_row = None
                    statuss(f"🗑️ Nr.{nr} deleted!")
        # ── Action triggered when Delete User button is pressed - deletes the selected record
        elif action == "-BTN-DELETE-FORWARDER-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["forwarder_id"])
                
                confirm = sg.popup_yes_no(
                    f"Delete rectord Nr.{nr}?\n"
                    f"{row['fw_name']}",
                    title="Confirm deleting a record"
                )
                if confirm == "Yes":
                    delete_db(nr, 't_forwarder', 'forwarder_id')
                    current_df = read_all('t_forwarder', 'forwarder_id')
                    refresh_table(current_df, "-FORWARDER-TABLE-")
                    selected_row = None
                    fw_statuss(f"🗑️ Nr.{nr} deleted!")
        # ── Action triggered when Delete User button is pressed - deletes the selected record
        elif action == "-BTN-DELETE-COMPANY-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["company_id"])
                
                confirm = sg.popup_yes_no(
                    f"Delete rectord Nr.{nr}?\n"
                    f"{row['c_name']}",
                    title="Confirm deleting a record"
                )
                if confirm == "Yes":
                    delete_db(nr, 't_company', 'company_id')
                    current_df = read_all('t_company', 'company_id')
                    refresh_table(current_df, "-COMPANY-TABLE-")
                    selected_row = None
                    fw_statuss(f"🗑️ Nr.{nr} deleted!")
                    
        # ── Action triggered when Edit button is pressed - opens Entry modal for editing an existing record
        elif action == "-BTN-EDIT-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["nr"])
                
                existing = {
                    "sap_po":          str(row["sap_po"]),
                    "sender":          str(row["sender"]),
                    "delivery":          str(row["delivery"]),
                    "loading":          str(row["loading"]),
                    "unloading":          str(row["unloading"]),
                    "pallets":          str(row["pallets"]),
                    "weight":          str(row["weight"]),
                    "forwarder":          str(row["forwarder"]),
                    "forwarder_contact":          str(row["forwarder_contact"]),
                    "cost":          str(row["cost"]),
                    "customs":          str(row["customs"]),
                    "ref":          str(row["ref"]),
                }
                new_values = entry_modal(f"Editing record Nr.{nr}", existing, nr)
                if new_values:
                    updated_values = {
                        "sap_po":          new_values["-SAP_PO-"],
                        "sender":          new_values["-SENDER-"],
                        "delivery":          new_values["-DELIVERY-"],
                        "loading":          new_values["-LOADING-"],
                        "unloading":          new_values["-UNLOADING-"],
                        "pallets":          int(new_values["-PALLETS-"]),
                        "weight":          float(new_values["-WEIGHT-"]),
                        "forwarder":          new_values["-FORWARDER-"],
                        "forwarder_contact":          new_values["-FORWARDER-CONTACT-"],
                        "cost":          float(new_values["-COST-"]),
                        "customs":          new_values["-CUSTOMS-"],
                        "ref":          new_values["-REF-"],
                    }
                    edit_db(nr, updated_values, 'transport')
                    
                    current_df = read_all('transport', 'nr')
                    refresh_table(current_df, "-TABLE-")
                    statuss(f"✅ Nr.{nr} updated!")
                    app_window["-SEARCH-"].update("")
        # ── Action triggered when Edit User button is pressed - opens Entry modal for editing an existing record
        elif action == "-BTN-EDIT-USER-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["nr"])
                
                existing = {
                    "name": str(row["name"]),
                    "surname": str(row["surname"]),
                    "role": str(row["role"]),
                    "email": str(row["email"]),
                    "phone": str(row["phone"]),
                    "login": str(row["login"]),
                    "password": str(row["password"]),
                }
                new_values = user_entry_modal(f"Editing record Nr.{nr}", existing)
                if new_values:
                    updated_values = {
                        "name": new_values["-USER-NAME-"],
                        "surname": new_values["-USER-SURNAME-"],
                        "role": new_values["-USER-ROLE-"],
                        "email": new_values["-USER-EMAIL-"],
                        "phone": new_values["-USER-PHONE-"],
                        "login": new_values["-USER-LOGIN-"],
                        "password": new_values["-USER-PASSWORD-"],
                    }
                    edit_db(nr, updated_values, 'user')
                    
                    current_df = read_all('user', 'nr')
                    refresh_table(current_df, "-USER-TABLE-")
                    statuss(f"✅ Nr.{nr} updated!")
                    #app_window["-SEARCH-"].update("")
                    
        # ── Action triggered when Edit Forwarder button is pressed - opens Entry modal for editing an existing record
        elif action == "-BTN-EDIT-FORWARDER-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["forwarder_id"])
                
                existing = {
                    "fw_name": str(row["fw_name"]),
                    "fw_reg_nr": str(row["fw_reg_nr"]),
                    "fw_vat_nr": str(row["fw_vat_nr"]),
                    "fw_street": str(row["fw_street"]),
                    "fw_city": str(row["fw_city"]),
                    "fw_post_code": str(row["fw_post_code"]),
                    "fw_country": str(row["fw_country"]),
                    "fw_payment_terms": str(row["fw_payment_terms"]),
                }
                new_values = forwarder_entry_modal(f"Editing record Nr.{nr}", existing)
                if new_values:
                    updated_values = {
                        "fw_name": new_values["-FW-NAME-"],
                        "fw_reg_nr": new_values["-FW-REG-"],
                        "fw_vat_nr": new_values["-FW-VAT-"],
                        "fw_street": new_values["-FW-STREET-"],
                        "fw_city": new_values["-FW-CITY-"],
                        "fw_post_code": new_values["-FW-POST-"],
                        "fw_country": new_values["-FW-COUNTRY-"],
                        "fw_payment_terms": new_values["-FW-PAYMENT-"],
                    }
                    edit_db(nr, updated_values, 't_forwarder', 'forwarder_id')
                    
                    current_df = read_all('t_forwarder', 'forwarder_id')
                    refresh_table(current_df, "-FORWARDER-TABLE-")
                    fw_statuss(f"✅ Nr.{nr} updated!")
                    #app_window["-SEARCH-"].update("")
        elif action == "-SHOW-FW-CONTACT-":
            if selected_row is None:
                fw_statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                fw_id = int(row['forwarder_id'])
                fw_name = str(row['fw_name'])
                forwarder_contacts_modal(fw_id, fw_name)
                
        # Ation to create a new forwarder contact -> opens a model where the contact can be created
        elif action == "-BTN-CREATE-FWCONTACT-" or action == "-CREATE-FW-CONTACT-":
            if selected_row is None:
                fw_statuss("Select a forwarder in the table for which to create a new contact!", "red")
            else:
                row = current_df.iloc[selected_row]
                fw_id = int(row['forwarder_id'])
                fw_name = str(row['fw_name'])
                
                new_values = create_fw_contact_modal(f"Create a new contact for {fw_name}")
                if new_values:
                    new_record = add_fw_contact(
                        fw_id, new_values["-FWCONTACT-NAME-"], new_values["-FWCONTACT-SURNAME-"], new_values["-FWCONTACT-POS-"],
                        new_values["-FWCONTACT-PHONE-"],new_values["-FWCONTACT-EMAIL-"]
                    )
                    current_df = read_all('t_forwarder', 'forwarder_id')
                    #refresh_table(current_df, "-FORWARDER-TABLE-")
                    fw_statuss(f"✅ {fw_name} contact Nr.{new_record} added!")
        
        # ── Action triggered when Edit Forwarder button is pressed - opens Entry modal for editing an existing record
        elif action == "-BTN-EDIT-COMPANY-":
            if selected_row is None:
                statuss("Select a record in the table!", "red")
            else:
                row = current_df.iloc[selected_row]
                nr = int(row["company_id"])
                
                existing = {
                    "c_name": str(row["c_name"]),
                    "c_reg": str(row["c_reg"]),
                    "c_vat": str(row["c_vat"]),
                    "c_street": str(row["c_street"]),
                    "c_city": str(row["c_city"]),
                    "c_post_code": str(row["c_post_code"]),
                    "c_country": str(row["c_country"]),
                    "c_notes": str(row["c_notes"]),
                    "c_prod_type": str(row["c_prod_type"]),
                }
                new_values = company_entry_modal(f"Editing record Nr.{nr}", existing)
                if new_values:
                    updated_values = {
                        "c_name": new_values["-TXT-COMPANY-NAME-"],
                        "c_reg": new_values["-TXT-COMPANY-REG-"],
                        "c_vat": new_values["-TXT-COMPANY-VAT-"],
                        "c_street": new_values["-TXT-COMPANY-STREET-"],
                        "c_city": new_values["-TXT-COMPANY-CITY-"],
                        "c_post_code": new_values["-TXT-COMPANY-POST-"],
                        "c_country": new_values["-TXT-COMPANY-COUNTRY-"],
                        "c_notes": new_values["-IN-COMPANY-DETAILS-"],
                        "c_prod_type": new_values["-TXT-COMPANY-PRODUCT-"],
                    }
                    edit_db(nr, updated_values, 't_company', 'company_id')
                    
                    current_df = read_all('t_company', 'company_id')
                    refresh_table(current_df, "-COMPANY-TABLE-")
                    fw_statuss(f"✅ Nr.{nr} updated!")

        # Action to generate a diagram in Statistic section
        elif action == "-BTN-CREATE-DIAGRAM-":
            print('-BTN-CREATE-DIAGRAM- was pressed!!!')
            generate_diagram(current_df, values['-STATISTICS-TYPE-'], values['-PERIOD-TYPE-'])

if __name__ == "__main__":
    #main_menu()
    login_modal()