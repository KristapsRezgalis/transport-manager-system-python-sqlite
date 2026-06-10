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

def add_db(sap_po, sender, delivery, loading, unloading, pallets, weight, forwarder, forwarder_contact, cost, customs, ref):
    """Adds new transport order record into database"""
    new_row = pd.DataFrame([{
        "sap_po":	sap_po,
        "sender":	sender,
        "delivery":	delivery,
        "loading":	loading,
        "unloading":unloading,
        "pallets":	pallets,
        "weight":	weight,
        "forwarder":forwarder,
        "forwarder_contact":forwarder_contact,
        "cost":		cost,
        "customs":	customs,
        "ref":		ref,
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