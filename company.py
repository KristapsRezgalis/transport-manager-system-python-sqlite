import FreeSimpleGUI as sg
from db import return_company_contacts, edit_db, add_company_contact, delete_db

countries = ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom", "Vatican City"]
COMPANY_CONTACT_COLUMNS = ['ID', 'Name', 'Surname', 'Position', 'Phone', 'Email']
COMP_CONTACT_DB_COLUMNS = ["c_con_id","c_con_name","c_con_surname","c_con_position","c_con_phone","c_con_email"]

# Function that opens a modal where a new company can be created and saved in sql database
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

# Function that opens a modal where all contaccts of selected company can be seen in a table / create / edit / delete buttons
def company_contacts_modal(company_id, c_name):
    from gui import df_to_table
    
    # checks contacts in databse for the selected forwarder
    comp_contact_df = return_company_contacts(company_id)
    
    selected_row = None
    sort_column = None
    sort_ascending = True
    
    comp_contact_columns = [
        sg.Column([[sg.Table(
            values=[],
            headings=COMPANY_CONTACT_COLUMNS,
            key="-COMPANY-CONTACTS-TABLE-",
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
        sg.Button("Create New Contact",  key="-BTN-CREATE-COMPCONTACT-", size=15),
        sg.Button("Edit Contact", key="-BTN-EDIT-COMPCONTACT-", size=15),
        sg.Button("Delete Contact", key="-BTN-DELETE-COMPCONTACT-", size=15),
        sg.Button("Exit", key="-BTN-EXIT-COMPCONTACT-", size=15),
        ],
        [sg.Text("", key="-TXT-COMPCONTACT-STATUS-", size=60, text_color="green")],
        comp_contact_columns
    ]
    
    app_window = sg.Window(
        f"{c_name} contacts",
        layout,
        resizable=True,
        size=(1000, 400),
        finalize=True
    )
    
    app_window["-COMPANY-CONTACTS-TABLE-"].update(values=df_to_table(comp_contact_df, COMP_CONTACT_DB_COLUMNS))
    
    # function to display/change statuss text
    def company_cont_statuss(text, sel_color="green"):
        app_window["-TXT-COMPCONTACT-STATUS-"].update(text, text_color=sel_color)
    
    # function to refresh company contacts table
    def refresh_company_contacts():
        nonlocal comp_contact_df

        comp_contact_df = return_company_contacts(company_id)

        app_window["-COMPANY-CONTACTS-TABLE-"].update(
            values=df_to_table(
                comp_contact_df,
                COMP_CONTACT_DB_COLUMNS
            )
        )
    
    while True:
        action, values = app_window.read()
        
        # Make the columns sortable
        if isinstance(action, tuple) and action[0] == "-COMPANY-CONTACTS-TABLE-":
            row, col = action[2]
            if row == -1:
                column_name = COMP_CONTACT_DB_COLUMNS[col]
                if sort_column == column_name:
                    sort_ascending = not sort_ascending
                    selected_row = None
                else:
                    sort_column = column_name
                    sort_ascending = True
                    selected_row = None
                comp_contact_df = comp_contact_df.sort_values(
                    by=column_name,
                    ascending=sort_ascending,
                    ignore_index=True
                )
                app_window["-COMPANY-CONTACTS-TABLE-"].update(
                    values=df_to_table(
                        comp_contact_df,
                        ["c_con_id", "c_con_name", "c_con_surname",
                         "c_con_position", "c_con_phone", "c_con_email"]
                    )
                )
            else:
                selected_row = row
        # Closes the forwarder contact modal
        if action in (sg.WIN_CLOSED, "-BTN-EXIT-COMPCONTACT-"):
            app_window.close()
            break
        # opens a modal to create a new forwarder contact
        elif action == "-BTN-CREATE-COMPCONTACT-":
            new_values = create_company_contact_modal(f"Create a new contact for {c_name}")
            if new_values:
                new_record = add_company_contact(
                    company_id, new_values["-TXT-COMPCONTACT-NAME-"], new_values["-TXT-COMPCONTACT-SURNAME-"], new_values["-TXT-COMPCONTACT-POS-"],
                    new_values["-TXT-COMPCONTACT-PHONE-"],new_values["-TXT-COMPCONTACT-EMAIL-"]
                )
                # Reload contacts
                comp_contact_df = return_company_contacts(company_id)
                app_window["-COMPANY-CONTACTS-TABLE-"].update(values=df_to_table(comp_contact_df, COMP_CONTACT_DB_COLUMNS))
                company_cont_statuss(f"✅ {c_name} contact Nr.{new_record} added!")
                selected_row = None
        # opens a modal to edit a new forwarder contact
        elif action == "-BTN-EDIT-COMPCONTACT-":
            if selected_row is None:
                company_cont_statuss("Select a contact!", "red")
            else:
                row = comp_contact_df.iloc[selected_row]
                contact_id = int(row["c_con_id"])
                
                existing = {
                    "c_con_name": str(row["c_con_name"]),
                    "c_con_surname": str(row["c_con_surname"]),
                    "c_con_position": str(row["c_con_position"]),
                    "c_con_phone": str(row["c_con_phone"]),
                    "c_con_email": str(row["c_con_email"]),
                }
                new_values = create_company_contact_modal(f"Editing contact Nr.{contact_id}", existing)
                if new_values:
                    updated_values = {
                        "c_con_name": new_values["-TXT-COMPCONTACT-NAME-"],
                        "c_con_surname": new_values["-TXT-COMPCONTACT-SURNAME-"],
                        "c_con_position": new_values["-TXT-COMPCONTACT-POS-"],
                        "c_con_phone": new_values["-TXT-COMPCONTACT-PHONE-"],
                        "c_con_email": new_values["-TXT-COMPCONTACT-EMAIL-"],
                    }
                    edit_db(contact_id, updated_values, 't_company_contact', 'c_con_id')
                    
                    refresh_company_contacts()
                    company_cont_statuss(f"✅ Contact Nr.{contact_id} updated!")
                    selected_row = None
        elif action == "-BTN-DELETE-COMPCONTACT-":
            if selected_row is None:
                company_cont_statuss("Select a contact!", "red")
            else:
                row = comp_contact_df.iloc[selected_row]
                contact_id = int(row["c_con_id"])
                contact_name_surname = f'{str(row["c_con_name"])} {str(row["c_con_surname"])}'
                
                confirm = sg.popup_yes_no(
                    f"Delete ID Nr.{contact_id}?\n"
                    f"{contact_name_surname}\n"
                    f"from {c_name}",
                    title="Confirm deleting a record"
                )
                if confirm == "Yes":
                    delete_db(contact_id, 't_company_contact', 'c_con_id')
                    refresh_company_contacts()
                    selected_row = None
                    company_cont_statuss(f"🗑   ID Nr.{contact_id} deleted!")

# Function that opens a modal to create a new company contact
def create_company_contact_modal(title, existing=None):
    e = existing or {}
    layout =[
        [sg.Text("Name:", size=16), sg.Input(e.get("c_con_name", ""), key="-TXT-COMPCONTACT-NAME-", size=35)],
        [sg.Text("Surname:", size=16), sg.Input(e.get("c_con_surname", ""), key="-TXT-COMPCONTACT-SURNAME-", size=35)],
        [sg.Text("Position:", size=16), sg.Input(e.get("c_con_position", ""), key="-TXT-COMPCONTACT-POS-", size=35)],
        [sg.Text("Phone Nr:", size=16), sg.Input(e.get("c_con_phone", ""), key="-TXT-COMPCONTACT-PHONE-", size=35)],
        [sg.Text("E-mail:", size=16), sg.Input(e.get("c_con_email", ""), key="-TXT-COMPCONTACT-EMAIL-", size=35)],
        [sg.Button("Save", key="-BTN-COMPCONTACT-SAVE-"), sg.Button("Cancel")]
    ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-BTN-COMPCONTACT-SAVE-":
            app_window.close()
            return values
        
# Function that opens a modal to create a new company loading/delivery address
def create_company_address_modal(title, existing=None):
    e = existing or {}
    layout =[
        [sg.Text("Address name:", size=16), sg.Input(e.get("adr_name", ""), key="-TXT-ADDRESS-NAME-", size=35)],
        [sg.Text("Street:", size=16), sg.Input(e.get("adr_street", ""), key="-TXT-ADDRESS-STREET-", size=35)],
        [sg.Text("City:", size=16), sg.Input(e.get("adr_city", ""), key="-TXT-ADDRESS-CITY-", size=35)],
        [sg.Text("Post code:", size=16), sg.Input(e.get("adr_post_code", ""), key="-TXT-ADDRESS-POST-", size=35)],
        [sg.Text("Country:", size=16), sg.Input(e.get("adr_country", ""), key="-TXT-ADDRESS-COUNTRY-", size=35)],
        [sg.Text("Working hours:", size=16), sg.Input(e.get("adr_hours", ""), key="-TXT-ADDRESS-HOURS-", size=35)],
        [sg.Text("Slot booking:", size=16), sg.Input(e.get("adr_book_slot", ""), key="-TXT-ADDRESS-SLOT-", size=35)],
        [sg.Text("Loading reference:", size=16), sg.Input(e.get("adr_reference", ""), key="-TXT-ADDRESS-REFERENCE-", size=35)],
        [sg.Text("Notes:", size=16), sg.Input(e.get("adr_notes", ""), key="-TXT-ADDRESS-NOTES-", size=35)],
        [sg.Button("Save", key="-BTN-COMPANY-ADDRESS-SAVE-"), sg.Button("Cancel")]
    ]
        
    app_window = sg.Window(title, layout, modal=True)

    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "Cancel"):
            app_window.close()
            return None
        if action == "-BTN-COMPANY-ADDRESS-SAVE-":
            app_window.close()
            return values
        
'''
        [sg.Text("Address name:", size=16), sg.Input(e.get("adr_name", ""), key="-TXT-ADDRESS-NAME-", size=35)],
        [sg.Text("Street:", size=16), sg.Input(e.get("adr_street", ""), key="-TXT-ADDRESS-STREET-", size=35)],
        [sg.Text("City:", size=16), sg.Input(e.get("adr_city", ""), key="-TXT-ADDRESS-CITY-", size=35)],
        [sg.Text("Post code:", size=16), sg.Input(e.get("adr_post_code", ""), key="-TXT-ADDRESS-POST-", size=35)],
        [sg.Text("Country:", size=16), sg.Input(e.get("adr_country", ""), key="-TXT-ADDRESS-COUNTRY-", size=35)],
        [sg.Text("Working hours:", size=16), sg.Input(e.get("adr_hours", ""), key="-TXT-ADDRESS-HOURS-", size=35)],
        [sg.Text("Slot booking:", size=16), sg.Input(e.get("adr_book_slot", ""), key="-TXT-ADDRESS-SLOT-", size=35)],
        [sg.Text("Loading reference:", size=16), sg.Input(e.get("adr_reference", ""), key="-TXT-ADDRESS-REFERENCE-", size=35)],
        [sg.Text("Notes:", size=16), sg.Input(e.get("adr_notes", ""), key="-TXT-ADDRESS-NOTES-", size=35)],
'''