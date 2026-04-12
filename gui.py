import FreeSimpleGUI as sg
import keyboard

from datetime import datetime
from db import create_table

COLUMNS = ["Nr.", "Sender", "Delivery", "Loading",
            "Unloading", "Pallets", "Weight", "Forwarder", "Cost","Customs","REF"]

sg.theme("DarkAmber")

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
        table_columns,
        [sg.Text("Search:", pad=(5, 5)),
         sg.Input(key="-SERCH-", size=20),
         sg.Button("Search", key="-BTN-SEARCH-"),
         sg.Button("Filter", key="-BTN-FILTER-"),
         sg.Button("Show All", key="-BTN-ALLDATA-"),
         sg.Button("Edit", key="-BTN-EDIT-"),
         sg.Button("Delete", key="-BTN-DELETE-"),
         sg.VerticalSeparator(),
         sg.Button("Exit", key="-BTN-EXIT-"),
        ],
        [sg.Text("", key="-STATUS-", size=60, text_color="green")],
    ]
    
    app_window = sg.Window(
        "Transport Management System",
        layout,
        resizable=True,
        size=(1000, 500),
        finalize=True
    )
    
    while True:
        action, values = app_window.read()
        
        if action in (sg.WIN_CLOSED, "-BTN-EXIT-"):
            break
    
    
if __name__ == "__main__":
    main_menu()