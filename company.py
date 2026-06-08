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
        
def company_contacts_modal(company_id, c_name):
    # checks contacts in databse for the selected forwarder
    comp_contact_df = return_fw_contacts(fw_id)
    
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
        fw_contact_columns
    ]
    
    app_window = sg.Window(
        f"{c_name} contacts",
        layout,
        resizable=True,
        size=(1000, 400),
        finalize=True
    )
    
    app_window["-COMPANY-CONTACTS-TABLE-"].update(values=df_to_table(comp_contact_df, FW_CONTACT_DB_COLUMNS))
    
    # function to display/change statuss text
    def fw_cont_statuss(text, sel_color="green"):
        app_window["-TXT-COMPCONTACT-STATUS-"].update(text, text_color=sel_color)
    
    # function to refresh forwarder contacts table
    def refresh_fw_contacts():
        nonlocal comp_contact_df

        comp_contact_df = return_fw_contacts(fw_id)

        app_window["-COMPANY-CONTACTS-"].update(
            values=df_to_table(
                comp_contact_df,
                COMPANY_CONTACT_COLUMNS
            )
        )
    
    while True:
        action, values = app_window.read()
        
        # Make the columns sortable
        if isinstance(action, tuple) and action[0] == "-FW-CONTACTS-TABLE-":
            row, col = action[2]
            if row == -1:
                column_name = COMPANY_CONTACT_COLUMNS[col]
                if sort_column == column_name:
                    sort_ascending = not sort_ascending
                else:
                    sort_column = column_name
                    sort_ascending = True
                comp_contact_df = comp_contact_df.sort_values(
                    by=column_name,
                    ascending=sort_ascending,
                    ignore_index=True
                )
                app_window["-COMPANY-CONTACTS-TABLE-"].update(
                    values=df_to_table(
                        comp_contact_df,
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
                comp_contact_df = return_fw_contacts(fw_id)
                app_window["-COMPANY-CONTACTS-TABLE-"].update(values=df_to_table(comp_contact_df, FW_CONTACT_DB_COLUMNS))
                fw_cont_statuss(f"✅ {fw_name} contact Nr.{new_record} added!")
                selected_row = None
        # opens a modal to edit a new forwarder contact
        elif action == "-BTN-EDIT-FWCONTACT-":
            if selected_row is None:
                fw_cont_statuss("Select a contact!", "red")
            else:
                row = comp_contact_df.iloc[selected_row]
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
                row = comp_contact_df.iloc[selected_row]
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