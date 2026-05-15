import FreeSimpleGUI as sg

from datetime import datetime
from db import create_table, read_all, add_db, edit_db, search_db, delete_db, filter_db, check_login, add_user
from pdf import create_order_pdf
from stats import generate_diagram

sg.theme("DarkAmber")

ORDER_COLUMNS = ["Nr.", "SAP PO", "Sender", "Delivery", "Loading",
            "Unloading", "Pallets", "Weight", "Forwarder", "Cost","Customs","REF"]

USER_COLUMNS = ["Nr", "Name", "Surname", "Role", "E-mail","Phone","Login","Password",]
user_roles = ['admin', 'user', 'spectator']
temperature_customs_options = ['Yes', '']
statistics_types = ['Cost per pallet', 'Cost per cargo', 'Total cost', 'Total cargos', 'Total pallets', 'Total weight', 'Pallets per cargo', 'Weight per pallet', 'Weight per cargo', 'Cargos per country', 'Cargos per forwarder', 'Cost per forwarder']
statistic_period = ['Per day', 'Per month', 'Per year']

TABLE_KEYS = [
    "-TABLE-",
    "-USER-TABLE-",
    "-STATISTICS-TABLE-",
    "-COMPANY-TABLE-"
]

def df_to_table(df):
    """Changes DataFrame to list for FreeSimpleGUI table."""
    if df.empty:
        return []

    df = df.copy()

    # Format columns to 2 decimal places
    if "weight" in df.columns:
        df["weight"] = df["weight"].astype(float).map("{:.2f}".format)

    if "cost" in df.columns:
        df["cost"] = df["cost"].astype(float).map("{:.2f}".format)

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
    
    if existing:
        layout = [
            [sg.Text("SAP PO Nr:",           size=16), sg.Input(e.get("sap_po", ""),          key="-SAP_PO-",   size=35)],
            [sg.Text("Sender:",           size=16), sg.Input(e.get("sender", ""),          key="-SENDER-",   size=35)],
            [sg.Text("Delivery:",           size=16), sg.Input(e.get("delivery", ""),          key="-DELIVERY-",   size=35)],
            #[sg.Text("Loading date:",           size=16), sg.Input(e.get("loading", ""),          key="-LOADING-",   size=35)],
            [sg.Text("Loading date:", size=16), sg.Input(e.get("loading", ""), key="-LOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-LOADING-",format="%Y-%m-%d")],
            [sg.Text("Unloading date:", size=16), sg.Input(e.get("unloading", ""), key="-UNLOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-UNLOADING-",format="%Y-%m-%d")],
            #[sg.Text("Unloading date:",           size=16), sg.Input(e.get("unloading", ""),          key="-UNLOADING-",   size=35)],
            [sg.Text("Pallet count:",           size=16), sg.Input(e.get("pallets", ""),          key="-PALLETS-",   size=35)],
            [sg.Text("Gross weight:",           size=16), sg.Input(e.get("weight", ""),          key="-WEIGHT-",   size=35)],
            [sg.Text("Forwarder:",           size=16), sg.Input(e.get("forwarder", ""),          key="-FORWARDER-",   size=35)],
            [sg.Text("Cost:",           size=16), sg.Input(e.get("cost", ""),          key="-COST-",   size=35)],
            [sg.Text("Customs:", size=16), sg.Combo(temperature_customs_options, key="-CUSTOMS-", default_value=e.get("customs", ""), readonly=True, size=33)],
            [sg.Text("Temperature control:", size=16), sg.Combo(temperature_customs_options, key="-REF-", default_value=e.get("ref", ""), readonly=True, size=33)],
            #[sg.Text("Customs:",           size=16), sg.Input(e.get("customs", ""),          key="-CUSTOMS-",   size=35)],
            #[sg.Text("Temperature control:",        size=16), sg.Input(e.get("ref", ""),          key="-REF-",   size=35)],
            [sg.Push(),sg.Button("Create transport order in PDF", key="-CREATE-PDF-"), sg.Push()],
            [sg.Push(),sg.Button("Save", key="-SAVE-", size=15), sg.Button("Cancel", size=15), sg.Push()]
        ]
    else:
        layout = [
            [sg.Text("SAP PO Nr:",           size=16), sg.Input(e.get("sap_po", ""),          key="-SAP_PO-",   size=35)],
            [sg.Text("Sender:",           size=16), sg.Input(e.get("sender", ""),          key="-SENDER-",   size=35)],
            [sg.Text("Delivery:",           size=16), sg.Input(e.get("delivery", ""),          key="-DELIVERY-",   size=35)],
            [sg.Text("Loading date:", size=16), sg.Input(e.get("loading", ""), key="-LOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-LOADING-",format="%Y-%m-%d")],
            [sg.Text("Unloading date:", size=16), sg.Input(e.get("unloading", ""), key="-UNLOADING-",size=28,readonly=True,disabled_readonly_background_color="white"),
             sg.CalendarButton("Pick",target="-UNLOADING-",format="%Y-%m-%d")],
            #[sg.Text("Loading date:",           size=16), sg.Input(e.get("loading", ""),          key="-LOADING-",   size=35)],
            #[sg.Text("Unloading date:",           size=16), sg.Input(e.get("unloading", ""),          key="-UNLOADING-",   size=35)],
            [sg.Text("Pallet count:",           size=16), sg.Input(e.get("pallets", ""),          key="-PALLETS-",   size=35)],
            [sg.Text("Gross weight:",           size=16), sg.Input(e.get("weight", ""),          key="-WEIGHT-",   size=35)],
            [sg.Text("Forwarder:",           size=16), sg.Input(e.get("forwarder", ""),          key="-FORWARDER-",   size=35)],
            [sg.Text("Cost:",           size=16), sg.Input(e.get("cost", ""),          key="-COST-",   size=35)],
            [sg.Text("Customs:", size=16), sg.Combo(temperature_customs_options, key="-CUSTOMS-", default_value=e.get("customs", ""), readonly=True, size=33)],
            [sg.Text("Temperature control:", size=16), sg.Combo(temperature_customs_options, key="-REF-", default_value=e.get("ref", ""), readonly=True, size=33)],
            #[sg.Text("Customs:",           size=16), sg.Input(e.get("customs", ""),          key="-CUSTOMS-",   size=35)],
            #[sg.Text("Temperature control:",        size=16), sg.Input(e.get("ref", ""),          key="-REF-",   size=35)],
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
            '-VIEW-ADDRESSES-',
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
                col_widths=[4, 8, 20, 20, 10, 10, 5, 8, 20, 10, 6, 5],
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

    total_records = [[sg.Text(key="-TOTAL-ACTIVE-RECORDS-")]]
    total_cost = [[sg.Text(key="-TOTAL-COST-")]]
    total_pallets = [[sg.Text(key="-TOTAL-PALLETS-")]]
    cost_per_cargo = [[sg.Text(key="-AVERAGE-CARGO-COST-")]]
    cost_per_pallet = [[sg.Text(key="-AVERAGE-PALLET-COST-")]]
    pallets_per_cargo = [[sg.Text(key="-PALLETS-PER-CARGO-")]]
    
    sidebar_layout = [
        [sg.Button('Transport orders', key='-TRANSPORT-ORDERS-', size=(15, 3))],
        [sg.Button('Statistics', key='-STATISTICS-', size=(15, 3))],
        [sg.Button('Companies', key='-COMPANIES-', size=(15, 3))],
        [sg.Button('Addresses', key='-ADDRESSES-', size=(15, 3))],
        [sg.Button('Forwarders', key='-MENU-FORWARDERS-', size=(15, 3))],
        [sg.Button('Users', key='-USERS-', size=(15, 3))],
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
                sg.Button("Create", key="-BTN-CREATE-DIAGRAM-", size=5),
                sg.Text("Stat type:", size=7), sg.Combo(statistics_types, key="-STATISTICS-TYPE-", default_value=statistics_types[0], readonly=True, size=20),
                sg.Text("Period:", size=5), sg.Combo(statistic_period, key="-PERIOD-TYPE-", default_value=statistic_period[1], readonly=True, size=10),
                sg.VerticalSeparator(),
                sg.Push(),sg.Button("Filter", key="-BTN-FILTER-STATISTICS-", size=10),
                sg.Text("Search:", pad=(5, 5)),
                sg.Input(key="-SEARCH-STATISTICS-", size=20),
                sg.Button("Search", key="-BTN-SEARCH-STATISTICS-", size=10),
                sg.Button("Exit", key="-BTN-EXIT-STATISTICS-", size=10),
            ],
            [create_orders_table("-STATISTICS-TABLE-")],
        ]
    
    companies_layout = [
            [
                sg.Button("Create New Company",  key="-BTN-CREATE-COMPANY-", size=10),
            ]
        ]
    
    addresses_layout = [
            [
                sg.Button("Create New Address",  key="-BTN-CREATE-ADDRESS-", size=10),
            ]
        ]
    
    forwarders_layout = [
            [
                sg.Button("Create New Forwarder",  key="-BTN-CREATE-FORWARDER-", size=10),
            ]
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
    
    content_area = [
        [
         sg.Column(transport_layout, key='-VIEW-TRANSPORT-', visible=True, expand_x=True, expand_y=True),
         sg.Column(statistics_layout, key='-VIEW-STATISTICS-', visible=False, expand_x=True, expand_y=True),
         sg.Column(companies_layout, key='-VIEW-COMPANIES-', visible=False, expand_x=True, expand_y=True),
         sg.Column(addresses_layout, key='-VIEW-ADDRESSES-', visible=False, expand_x=True, expand_y=True),
         sg.Column(forwarders_layout, key='-VIEW-FORWARDERS-', visible=False, expand_x=True, expand_y=True),
         sg.Column(users_layout, key='-VIEW-USERS-', visible=False, expand_x=True, expand_y=True),
        ]
    ]
    
    layout = [
        [
            sg.Text("Transport Management System", font=("Helvetica", 14, "bold"), pad=(10,10)), 
            sg.Push(),sg.Text(f'{login_validation.get("name")} {login_validation.get("surname")}', font=("Helvetica", 10, "bold"), pad=(10,10))
        ],
        [
            sg.Column(sidebar_layout, expand_y=True),
            sg.VerticalSeparator(), # Vizuāla līnija starp sānjoslu un saturu
            sg.Column(content_area, expand_x=True, expand_y=True) 
        ]
    ]
    
    app_window = sg.Window(
        "Transport Management System",
        layout,
        resizable=True,
        size=(1200, 600),
        finalize=True
    )
        
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

    
    
    # --- initial data + sorting state ---
    current_df = read_all('transport')
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
        
        if action in (sg.WIN_CLOSED, "-BTN-EXIT-", "-BTN-EXIT-STATISTICS-", "-BTN-EXIT-USER-"):
            app_window.close()
            break
        
        if action == '-TRANSPORT-ORDERS-':
            show_view('-VIEW-TRANSPORT-')
            reset_sort_select()
            current_df = read_all('transport')
            refresh_table(current_df, "-TABLE-")
            print('Transport Orders menu selected')
        elif action == '-STATISTICS-':
            print('Statisitcs menu selected')
            reset_sort_select()
            show_view('-VIEW-STATISTICS-')
            current_df = read_all('transport')
            refresh_table(current_df, "-STATISTICS-TABLE-")
        elif action == '-COMPANIES-':
            print('Company menu selected')
            show_view('-VIEW-COMPANIES-')
            reset_sort_select()
        elif action == '-ADDRESSES-':
            print('Address menu selected')
            show_view('-VIEW-ADDRESSES-')
            reset_sort_select()
        elif action == '-MENU-FORWARDERS-':
            print('Forwarders menu selected')
            show_view('-VIEW-FORWARDERS-')
            reset_sort_select()
        elif action == '-USERS-':
            print('Users menu selected')
            show_view('-VIEW-USERS-')
            reset_sort_select()
            current_df = read_all('user')
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
            current_df = read_all('transport')
            refresh_table(current_df, "-TABLE-")
            app_window["-SEARCH-"].update("")
            statuss("Showing all records!")
            
        # ── Action triggered when Search button is pressed - seasrches in database for values that match from the searchbox
        elif action == "-BTN-SEARCH-":
            search_value = values["-SEARCH-"].strip()
            if not search_value:
                statuss("Ievadi meklēšanas tekstu!", "red")
            else:
                current_df = search_db(search_value)
                refresh_table(current_df, "-TABLE-")
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
                    new_values["-UNLOADING-"], new_values["-PALLETS-"], new_values["-WEIGHT-"], new_values["-FORWARDER-"],
                    new_values["-COST-"], new_values["-CUSTOMS-"], new_values["-REF-"]
                )
                current_df = read_all('transport')
                refresh_table(current_df, "-TABLE-")
                statuss(f"✅ Record Nr.{new_record} added!")
        
        # ── Action triggered when CREATE USER button is pressed - opens Entry modal for creating new record
        elif action == "-BTN-CREATE-USER-":
            new_values = user_entry_modal("NEW USER")
            if new_values:
                new_record = add_user(
                    new_values["-USER-NAME-"], new_values["-USER-SURNAME-"], new_values["-USER-ROLE-"], new_values["-USER-EMAIL-"],
                    new_values["-USER-PHONE-"], new_values["-USER-LOGIN-"], new_values["-USER-PASSWORD-"]
                )
                current_df = read_all('user')
                refresh_table(current_df, "-USER-TABLE-")
                statuss(f"✅ User Nr.{new_record} added!")
                
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
                    current_df = read_all('transport')
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
                    current_df = read_all('user')
                    refresh_table(current_df, "-USER-TABLE-")
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
                        "cost":          float(new_values["-COST-"]),
                        "customs":          new_values["-CUSTOMS-"],
                        "ref":          new_values["-REF-"],
                    }
                    edit_db(nr, updated_values, 'transport')
                    
                    current_df = read_all('transport')
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
                    
                    current_df = read_all('user')
                    refresh_table(current_df, "-USER-TABLE-")
                    statuss(f"✅ Nr.{nr} updated!")
                    #app_window["-SEARCH-"].update("")
        elif action == "-BTN-CREATE-DIAGRAM-":
            print('-BTN-CREATE-DIAGRAM- was pressed!!!')
            generate_diagram(current_df, values['-STATISTICS-TYPE-'], values['-PERIOD-TYPE-'])

if __name__ == "__main__":
    #main_menu()
    login_modal()