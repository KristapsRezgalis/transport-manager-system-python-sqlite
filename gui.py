import FreeSimpleGUI as sg
import keyboard

from datetime import datetime
from db import create_table, read_all, add_db, edit_db, search_db, delete_db, filter_db
from pdf import create_order_pdf

sg.theme("DarkAmber")

COLUMNS = ["Nr.", "SAP PO", "Sender", "Delivery", "Loading",
            "Unloading", "Pallets", "Weight", "Forwarder", "Cost","Customs","REF"]

def df_to_table(df):
    """Changes DataFrame to list for FreeSimpleGUI table."""
    if df.empty:
        return []
    return df.values.tolist()

def filter_modal():
    layout = [
        [sg.Text("SAP PO Nr from:",           size=16), sg.Input(key="-F-SAP-PO-FROM-",   size=25),
         sg.Text("SAP PO Nr to:",           size=16), sg.Input(key="-F-SAP-PO-TO-",   size=25)],
        [sg.Text("Sender:",           size=16), sg.Input(key="-F-SENDER-",   size=72)],
        [sg.Text("Delivery:",           size=16), sg.Input(key="-F-DELIVERY-",   size=72)],
        [sg.Text("Loading date from:",           size=16), sg.Input(key="-F-LOADING-FROM-",   size=25),
         sg.Text("Loading date to:",           size=16), sg.Input(key="-F-LOADING-TO-",   size=25)],
        [sg.Text("Unloading date from:",           size=16), sg.Input(key="-F-UNLOADING-FROM-",   size=25),
         sg.Text("Unloading date to:",           size=16), sg.Input(key="-F-UNLOADING-TO-",   size=25)],
        [sg.Text("Pallet count min:",           size=16), sg.Input(key="-F-PALLETS-MIN-",   size=25),
         sg.Text("Pallet count max:",           size=16), sg.Input(key="-F-PALLETS-MAX-",   size=25)],
        [sg.Text("Gross weight min:",           size=16), sg.Input(key="-F-WEIGHT-MIN-",   size=25),
         sg.Text("Gross weight max:",           size=16), sg.Input(key="-F-WEIGHT-MAX-",   size=25)],
        [sg.Text("Forwarder:",           size=16), sg.Input(key="-F-FORWARDER-",   size=72)],
        [sg.Text("Cost min:",           size=16), sg.Input(key="-F-COST-MIN-",   size=25),
         sg.Text("Cost max:",           size=16), sg.Input(key="-F-COST-MAX-",   size=25)],
        [sg.Text("Customs:",           size=16), sg.Input(key="-F-CUSTOMS-",   size=25)],
        [sg.Text("Temperature control:",        size=16), sg.Input(key="-F-REF-",   size=25)],
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
                "cost_min":  values["-F-COST-MIN-"],
                "cost_max":  values["-F-COST-MAX-"],
                "customs":  values["-F-CUSTOMS-"],
                "ref":  values["-F-REF-"],
            }
            app_window.close()
            return filtered_values

# Entry modal window for creating new records and editing existin ones
def entry_modal(title, existing=None):
    
    e = existing or {}
    # sap_po, sender, delivery, loading,unloading, pallets, weight, forwarder, cost, customs, ref
    
    if existing:
        layout = [
            [sg.Text("SAP PO Nr:",           size=16), sg.Input(e.get("sap_po", ""),          key="-SAP_PO-",   size=25)],
            [sg.Text("Sender:",           size=16), sg.Input(e.get("sender", ""),          key="-SENDER-",   size=25)],
            [sg.Text("Delivery:",           size=16), sg.Input(e.get("delivery", ""),          key="-DELIVERY-",   size=25)],
            [sg.Text("Loading date:",           size=16), sg.Input(e.get("loading", ""),          key="-LOADING-",   size=25)],
            [sg.Text("Unloading date:",           size=16), sg.Input(e.get("unloading", ""),          key="-UNLOADING-",   size=25)],
            [sg.Text("Pallet count:",           size=16), sg.Input(e.get("pallets", ""),          key="-PALLETS-",   size=25)],
            [sg.Text("Gross weight:",           size=16), sg.Input(e.get("weight", ""),          key="-WEIGHT-",   size=25)],
            [sg.Text("Forwarder:",           size=16), sg.Input(e.get("forwarder", ""),          key="-FORWARDER-",   size=25)],
            [sg.Text("Cost:",           size=16), sg.Input(e.get("cost", ""),          key="-COST-",   size=25)],
            [sg.Text("Customs:",           size=16), sg.Input(e.get("customs", ""),          key="-CUSTOMS-",   size=25)],
            [sg.Text("Temperature control:",        size=16), sg.Input(e.get("ref", ""),          key="-REF-",   size=25)],
            [sg.Button("Create transport order in PDF", key="-CREATE-PDF-")],
            [sg.Button("Save", key="-SAVE-"), sg.Button("Cancel")]
        ]
    else:
        layout = [
            [sg.Text("SAP PO Nr:",           size=16), sg.Input(e.get("sap_po", ""),          key="-SAP_PO-",   size=25)],
            [sg.Text("Sender:",           size=16), sg.Input(e.get("sender", ""),          key="-SENDER-",   size=25)],
            [sg.Text("Delivery:",           size=16), sg.Input(e.get("delivery", ""),          key="-DELIVERY-",   size=25)],
            [sg.Text("Loading date:",           size=16), sg.Input(e.get("loading", ""),          key="-LOADING-",   size=25)],
            [sg.Text("Unloading date:",           size=16), sg.Input(e.get("unloading", ""),          key="-UNLOADING-",   size=25)],
            [sg.Text("Pallet count:",           size=16), sg.Input(e.get("pallets", ""),          key="-PALLETS-",   size=25)],
            [sg.Text("Gross weight:",           size=16), sg.Input(e.get("weight", ""),          key="-WEIGHT-",   size=25)],
            [sg.Text("Forwarder:",           size=16), sg.Input(e.get("forwarder", ""),          key="-FORWARDER-",   size=25)],
            [sg.Text("Cost:",           size=16), sg.Input(e.get("cost", ""),          key="-COST-",   size=25)],
            [sg.Text("Customs:",           size=16), sg.Input(e.get("customs", ""),          key="-CUSTOMS-",   size=25)],
            [sg.Text("Temperature control:",        size=16), sg.Input(e.get("ref", ""),          key="-REF-",   size=25)],
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
            create_order_pdf(existing)
            print('Create transport order in PDF button pressed!')

# --- Main menu ---
def main_menu():
    create_table()
    
    table_columns = [
        sg.Column([[sg.Table(
            values=[],
            headings=COLUMNS,
            key="-TABLE-",
            auto_size_columns=True,
            justification="left",
            num_rows=20,
            enable_events=True,
            enable_click_events=True, # for sorting
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            expand_x=True,
            )]], expand_x=True)
    ]
    
    layout = [
        [sg.Text("Transport Management System", font=("Helvetica", 14, "bold"), pad=(10,10))],
        [
        sg.Button("Create",  key="-BTN-CREATE-"),
        sg.Button("Open/Edit", key="-BTN-EDIT-"),
        sg.Button("Delete", key="-BTN-DELETE-"),
        sg.Button("Show All", key="-BTN-ALLDATA-"),
        sg.VerticalSeparator(),
        sg.Button("Filter", key="-BTN-FILTER-"),
        sg.Text("Search:", pad=(5, 5)),
        sg.Input(key="-SEARCH-", size=20),
        sg.Button("Search", key="-BTN-SEARCH-"),
        sg.Button("Exit", key="-BTN-EXIT-"),
        ],
        [sg.Text("", key="-STATUS-", size=60, text_color="green")],
        table_columns,
    ]
    
    app_window = sg.Window(
        "Transport Management System",
        layout,
        resizable=True,
        size=(1200, 600),
        finalize=True
    )
    
    def refresh_table(df):
        app_window["-TABLE-"].update(values=df_to_table(df))
        
    def statuss(text, sel_color="green"):
        app_window["-STATUS-"].update(text, text_color=sel_color)
    
    # --- initial data + sorting state ---
    current_df = read_all()
    sort_column = None
    sort_ascending = True
    
    refresh_table(current_df)
    
    selected_row = None #atlasita_rinda = None
    
    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "-BTN-EXIT-"):
            app_window.close()
            break
        
        # ── Table clicks (selecting + sorting)
        if isinstance(action, tuple) and action[0] == "-TABLE-":
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

                refresh_table(current_df)
                statuss(f"Sorted by '{column_name}' ({'ASC' if sort_ascending else 'DESC'})")

            # Row click → SELECT
            else:
                selected_row = row
        
        # ── Action triggered when Show All button is pressed - shows all data in database
        elif action == "-BTN-ALLDATA-":
            current_df = read_all()
            refresh_table(current_df)
            app_window["-SEARCH-"].update("")
            statuss("Showing all records!")
            
        # ── Action triggered when Search button is pressed - seasrches in database for values that match from the searchbox
        elif action == "-BTN-SEARCH-":
            search_value = values["-SEARCH-"].strip()
            if not search_value:
                statuss("Ievadi meklēšanas tekstu!", "red")
            else:
                current_df = search_db(search_value)
                refresh_table(current_df)
                statuss(f"Found: {len(current_df)} records")
        
        # ── Action triggered when Filtrs button is pressed - opens a Filter modal window with filtring options
        elif action == "-BTN-FILTER-":
            filter = filter_modal()
            if filter is not None:
                current_df = filter_db(filter)
                refresh_table(current_df)
                atlasita_rinda = None
                statuss(f"🔎 Found: {len(current_df)} records")
        
        # ── Action triggered when CREATE button is pressed - opens Entry modal for creating new record
        elif action == "-BTN-CREATE-":
            new_values = entry_modal("NEW TRANSPORT RECORD")
            if new_values:
                new_record = add_db(
                    new_values["-SAP_PO-"], new_values["-SENDER-"], new_values["-DELIVERY-"], new_values["-LOADING-"],
                    new_values["-UNLOADING-"], new_values["-PALLETS-"], new_values["-WEIGHT-"], new_values["-FORWARDER-"],
                    new_values["-COST-"], new_values["-CUSTOMS-"], new_values["-REF-"]
                )
                current_df = read_all()
                refresh_table(current_df)
                statuss(f"✅ Record Nr.{new_record} added!")
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
                    delete_db(nr)
                    current_df = read_all()
                    refresh_table(current_df)
                    selected_row = None
                    statuss(f"🗑️ Nr.{nr} deleted!")
                
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
                    "cost":          str(row["cost"]),
                    "customs":          str(row["customs"]),
                    "ref":          str(row["ref"]),
                }
                new_values = entry_modal(f"Editing record Nr.{nr}", existing)
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
                        "cost":          int(new_values["-COST-"]),
                        "customs":          new_values["-CUSTOMS-"],
                        "ref":          new_values["-REF-"],
                    }
                    edit_db(nr, updated_values)
                    
                    current_df = read_all()
                    refresh_table(current_df)
                    statuss(f"✅ Nr.{nr} updated!")
                    app_window["-SEARCH-"].update("")


if __name__ == "__main__":
    main_menu()