import sqlite3
import pandas as pd
from datetime import datetime    

DB_FILE = "transport.db"
TABLE_NAME = "transport"

# checks if entered login and password matches user table records in DB
def check_login(login_value, passw_value):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(""" SELECT * FROM user
    WHERE login = ? AND password = ?
    """, conn, params=(login_value, passw_value))
    
    conn.close()
    
    if not df.empty:
        return df.iloc[0].to_dict()  # return user data
    return None

def create_table():
    """Create a table if it does not exist"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
CREATE TABLE IF NOT EXISTS transport (
    nr INTEGER PRIMARY KEY AUTOINCREMENT,
    sap_po INTEGER,
    sender TEXT,
    delivery TEXT,
    loading TEXT,
    unloading TEXT,
    pallets INTEGER,
    weight REAL,
    forwarder TEXT,
    forwarder_contact TEXT,
    cost INTEGER,
    customs TEXT,
    ref TEXT,
    info TEXT
)
""")
    conn.commit()
    conn.close()
    
def read_all(table_name, id_header):
    """ Reads all data from database """
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY {id_header}", conn)
    conn.close()
    return df

def add_db(sap_po, sender, sender_adr, sender_cont, delivery, delivery_adr, delivery_cont, loading, loading_to, unloading, unloading_to, pallets, weight, forwarder, forwarder_contact, cost, customs, ref, info, add_info_to_order, purch_manager, cargo_type, transport_invoice):
    """Adds new transport order record into database"""
    new_row = pd.DataFrame([{
        "sap_po":	sap_po,
        "sender":	sender,
        "sender_adr": sender_adr,
        "sender_cont": sender_cont,
        "delivery":	delivery,
        "delivery_adr": delivery_adr,
        "delivery_cont": delivery_cont,
        "loading":	loading,
        "loading_to":	loading_to,
        "unloading":unloading,
        "unloading_to":unloading_to,
        "pallets":	pallets,
        "weight":	weight,
        "forwarder":forwarder,
        "forwarder_contact":forwarder_contact,
        "cost":		cost,
        "customs":	customs,
        "ref":		ref,
        "info": info,
        "add_info_to_order": add_info_to_order,
        "purch_manager": purch_manager,
        "cargo_type": cargo_type,
        "transport_invoice": transport_invoice
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(nr) as nr FROM transport", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def add_user(name, surname, role, email, phone, login, password):
    """Adds new user record into database"""
    new_row=pd.DataFrame([{
        'name': name,
        'surname': surname,
        'role': role,
        'email': email,
        'phone': phone,
        'login': login,
        'password': password
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("user", conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(nr) as nr FROM user", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def add_forwarder(name, reg, vat, street, city, postcode, country, payment):
    """Adds new forwarder record into database"""
    new_row=pd.DataFrame([{
        'fw_name': name,
        'fw_reg_nr': reg,
        'fw_vat_nr': vat,
        'fw_street': street,
        'fw_city': city,
        'fw_post_code': postcode,
        'fw_country': country,
        'fw_payment_terms': payment
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("t_forwarder", conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(forwarder_id) as nr FROM t_forwarder", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def add_company(name, reg, vat, street, city, postcode, country, notes, product):
    """Adds new company record into database"""
    new_row=pd.DataFrame([{
        'c_name': name,
        'c_reg': reg,
        'c_vat': vat,
        'c_street': street,
        'c_city': city,
        'c_post_code': postcode,
        'c_country': country,
        'c_notes': notes,
        'c_prod_type': product
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("t_company", conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(company_id) as nr FROM t_company", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def edit_db(nr, updated_values, table_name, id_name = 'nr'):
    """Updates record in a database"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    set_variables = ", ".join(f"{x} = ?" for x in updated_values)
    values = list(updated_values.values())
    values.append(nr)

    cur.execute(f"UPDATE {table_name} SET {set_variables} WHERE {id_name} = ?", values)
    
    conn.commit()
    conn.close()
    
def search_db(search_value, tableName):
    conn = sqlite3.connect(DB_FILE)
    if tableName == 'transport':
        df = pd.read_sql(f""" SELECT * FROM {tableName}
        WHERE sap_po LIKE ? OR sender LIKE ? OR delivery LIKE ? OR loading LIKE ? OR unloading LIKE ? OR pallets LIKE ? OR weight LIKE ? OR forwarder LIKE ? OR forwarder_contact LIKE ? OR cost LIKE ?
        ORDER BY nr
        """, conn, params=(f"%{search_value}%", f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%"))
    elif tableName == 't_forwarder':
        df = pd.read_sql(f""" SELECT * FROM {tableName}
        WHERE fw_name LIKE ? OR fw_reg_nr LIKE ? OR fw_vat_nr LIKE ? OR fw_street LIKE ? OR fw_city LIKE ? OR fw_post_code LIKE ? OR fw_country LIKE ? OR fw_payment_terms LIKE ? 
        ORDER BY forwarder_id
        """, conn, params=(f"%{search_value}%", f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%"))
    
    conn.close()
    return df

    
def delete_db(nr, table_name, id_name = 'nr'):
    """Deletes selected record/Nr"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(f"DELETE FROM {table_name} WHERE {id_name} = ?", (nr,))
    conn.commit()
    conn.close()
    
def filter_db(filters):

    conditions = []
    parameters = []

    # Text fields
    for field in ("sender","delivery","forwarder","customs","ref"):

        value = filters.get(field,"").strip()

        if value:
            conditions.append(f"{field} LIKE ?")
            parameters.append(f"%{value}%")

    # Date ranges

    date_ranges = {
        "loading": ("loading_from","loading_to"),
        "unloading": ("unloading_from","unloading_to"),
    }

    for column,(key_from,key_to) in date_ranges.items():

        from_value = filters.get(key_from,"").strip()
        to_value = filters.get(key_to,"").strip()

        if from_value:
            conditions.append(f"{column} >= ?")
            parameters.append(from_value)

        if to_value:
            conditions.append(f"{column} <= ?")
            parameters.append(to_value)

    # Numeric ranges

    numeric_ranges = {
        "sap_po": ("sap_po_from","sap_po_to"),
        "pallets": ("pallets_min","pallets_max"),
        "weight": ("weight_min","weight_max"),
        "cost": ("cost_min","cost_max"),
    }

    for column,(key_from,key_to) in numeric_ranges.items():

        from_value = filters.get(key_from,"").strip()
        to_value = filters.get(key_to,"").strip()

        if from_value:
            conditions.append(f"{column} >= ?")
            parameters.append(float(from_value))

        if to_value:
            conditions.append(f"{column} <= ?")
            parameters.append(float(to_value))

    sql = "SELECT * FROM transport"

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY nr"

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql(sql, conn, params=parameters)

    conn.close()

    return df

def return_forwarders(selected_forwarder_name = None):
    """ Get all current forwarder names from DB """
    forw_list = []
    
    conn = sqlite3.connect(DB_FILE)
    
    if selected_forwarder_name:
        fw_id = pd.read_sql(f"SELECT forwarder_id FROM t_forwarder WHERE fw_name = '{selected_forwarder_name}'", conn)
        conn.close()
        print(f'fw_id = {fw_id}')
         # Pārbauda, vai rezultāts nav tukšs
        if not fw_id.empty:
            print(f'int(fw_id.iloc[0, 0]) = {int(fw_id.iloc[0, 0])}')
            return int(fw_id.iloc[0, 0]) 
    
    else:
        df = pd.read_sql(f"SELECT fw_name FROM t_forwarder ORDER BY fw_name", conn)
        conn.close()
        forw_list = df['fw_name'].tolist()
        forw_list.sort()
        return forw_list
    
def return_fw_data(forwarder_name):
    """ Get all data of a specific forwarder (returned in dataframe) - used in pdf.py to display forwarder details """
    if forwarder_name:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("""SELECT * FROM t_forwarder WHERE fw_name = ?""", conn, params=(forwarder_name,))
        conn.close()
        return df

def return_fw_contact_df(contact_name, forwarder_id):
    """ Get all data of a specific forwarder contact (returned in dataframe) - used in pdf.py to display contact details """
    if contact_name:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM t_fw_contact WHERE (fw_c_name || ' ' || fw_c_surname) = ? AND forwarder_id = ?", conn, params=(contact_name, int(forwarder_id)))
        conn.close()
        return df
    return pd.DataFrame() # returns empty df

def return_fw_contacts(forwarder_id, list_required = None):
    conn = sqlite3.connect(DB_FILE)
    
    if list_required:
        df = pd.read_sql(f"SELECT fw_c_name || ' ' || fw_c_surname FROM t_fw_contact  WHERE forwarder_id = {forwarder_id} ORDER BY fw_c_name", conn)
        conn.close()
        forw_cont_list = df.iloc[:, 0].tolist()
        return forw_cont_list
    else:
        df = pd.read_sql(f"SELECT * FROM t_fw_contact WHERE forwarder_id = {forwarder_id} ORDER BY fw_contact_id", conn)
        conn.close()
        return df

def add_fw_contact(fw_id, fwc_name, fwc_surname, fwc_position, fwc_phone, fwc_email):
    """Adds new forwarder contact record into database"""
    new_row=pd.DataFrame([{
        'forwarder_id': fw_id,
        'fw_c_name': fwc_name,
        'fw_c_surname': fwc_surname,
        'fw_c_position': fwc_position,
        'fw_c_phone': fwc_phone,
        'fw_c_email': fwc_email
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("t_fw_contact", conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(fw_contact_id) as nr FROM t_fw_contact", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def return_company_contacts(company_id, list_required = None):
    conn = sqlite3.connect(DB_FILE)
    
    if list_required:
        df = pd.read_sql(f"SELECT c_con_name || ' ' || c_con_surname FROM t_company_contact  WHERE company_id = {company_id} ORDER BY c_con_name", conn)
        conn.close()
        company_cont_list = df.iloc[:, 0].tolist()
        return company_cont_list
    else:
        df = pd.read_sql(f"SELECT * FROM t_company_contact WHERE company_id = {company_id} ORDER BY c_con_id", conn)
        conn.close()
        return df
    
def add_company_contact(company_id, compc_name, compc_surname, compc_position, compc_phone, compc_email):
    """Adds new Company Contact record into database"""
    new_row=pd.DataFrame([{
        'company_id': company_id,
        'c_con_name': compc_name,
        'c_con_surname': compc_surname,
        'c_con_position': compc_position,
        'c_con_phone': compc_phone,
        'c_con_email': compc_email
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("t_company_contact", conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(c_con_id) as nr FROM t_company_contact", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def add_company_address(company_id, c_a_name, c_a_street, c_a_city, c_a_post_code, c_a_country, c_a_hours, c_a_book_slot, c_a_reference, c_a_notes):
    """Adds new Company Contact record into database"""
    new_row=pd.DataFrame([{
        'company_id': company_id,
        'adr_name': c_a_name,
        'adr_street': c_a_street,
        'adr_city': c_a_city,
        'adr_post_code': c_a_post_code,
        'adr_country': c_a_country,
        'adr_hours': c_a_hours,
        'adr_book_slot': c_a_book_slot,
        'adr_reference': c_a_reference,
        'adr_notes': c_a_notes,
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("t_company_address", conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(address_id) as nr FROM t_company_address", conn)["nr"].iloc[0]
    conn.close()

    return new_record

def return_company_addresses(company_id, list_required = None):
    conn = sqlite3.connect(DB_FILE)
    
    if list_required:
        df = pd.read_sql(f"SELECT adr_name FROM t_company_address WHERE company_id = {company_id} ORDER BY adr_name", conn)
        conn.close()
        company_cont_list = df.iloc[:, 0].tolist()
        return company_cont_list
    else:
        df = pd.read_sql(f"SELECT * FROM t_company_address WHERE company_id = {company_id} ORDER BY address_id", conn)
        conn.close()
        return df
    
def return_company(selected_company_name = None):
    """ Get one or all company data from DB """
    company_list = []
    
    conn = sqlite3.connect(DB_FILE)
    
    # used if only one company name needs to be returned
    if selected_company_name:
        comp_id = pd.read_sql(f"SELECT company_id FROM t_company WHERE c_name = '{selected_company_name}'", conn)
        conn.close()
        print(f'comp_id = {comp_id}')
         # Pārbauda, vai rezultāts nav tukšs
        if not comp_id.empty:
            print(f'int(comp_id.iloc[0, 0]) = {int(comp_id.iloc[0, 0])}')
            return int(comp_id.iloc[0, 0]) 
    # used if all company names need to be returned
    else:
        df = pd.read_sql(f"SELECT c_name FROM t_company ORDER BY c_name", conn)
        conn.close()
        company_list = df['c_name'].tolist()
        company_list.sort()
        return company_list
    
def get_purchase_managers():
    conn = sqlite3.connect(DB_FILE)
    
    purchase_manager_df = pd.read_sql(f"SELECT manager_name || ' ' || manager_surname FROM t_purchase_manager ORDER BY manager_name ASC", conn)
    conn.close()
    purchase_manager_df = purchase_manager_df.iloc[:, 0].tolist()
    purchase_manager_df.sort()
    
    return purchase_manager_df

def get_pallet_details(order_id):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("""SELECT * FROM t_pallet_details WHERE order_id = ? ORDER BY pallet_id """, conn, params=(order_id,))
    conn.close()
    return df

def insert_pallet(nr, pll_quantity, pll_length, pll_width, pll_height):
    """Adds new pallet details into database"""
    new_row=pd.DataFrame([{
        'order_id': nr,
        'quantity': pll_quantity,
        'length': pll_length,
        'width': pll_width,
        'height': pll_height
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql("t_pallet_details", conn, if_exists="append", index=False)
    #new_record = pd.read_sql("SELECT MAX(pallet_id) as nr FROM t_pallet_details", conn)["nr"].iloc[0]
    conn.close()
    