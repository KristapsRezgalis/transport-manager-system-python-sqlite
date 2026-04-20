import sqlite3
import pandas as pd
from datetime import datetime    

DB_FILE = "transport.db"
TABLE_NAME = "transport"


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
    cost INTEGER,
    customs TEXT,
    ref TEXT,
    info TEXT
)
""")
    conn.commit()
    conn.close()
    
def read_all():
    """ Reads all data from database """
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM transport ORDER BY nr", conn)
    conn.close()
    return df

def add_db(sap_po, sender, delivery, loading, unloading, pallets, weight, forwarder, cost, customs, ref):
    """Adds new record into database"""
    new_row = pd.DataFrame([{
        "sap_po":	sap_po,
        "sender":	sender,
        "delivery":	delivery,
        "loading":	loading,
        "unloading":unloading,
        "pallets":	pallets,
        "weight":	weight,
        "forwarder":forwarder,
        "cost":		cost,
        "customs":	customs,
        "ref":		ref,
    }])
    conn = sqlite3.connect(DB_FILE)
    new_row.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
    new_record = pd.read_sql("SELECT MAX(nr) as nr FROM transport", conn)["nr"].iloc[0]
    conn.close()

    return new_record
    
def edit_db(nr, updated_values):
    """Updates record in a database"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    set_variables = ", ".join(f"{x} = ?" for x in updated_values)
    values = list(updated_values.values())
    values.append(nr)
    
    cur.execute(f"UPDATE transport SET {set_variables} WHERE nr = ?", values)
    
    conn.commit()
    conn.close()
    
def search_db(search_value):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(""" SELECT * FROM transport
    WHERE sap_po LIKE ? OR sender LIKE ? OR delivery LIKE ? OR loading LIKE ? OR unloading LIKE ? OR pallets LIKE ? OR weight LIKE ? OR forwarder LIKE ? OR cost LIKE ?
    ORDER BY nr
    """, conn, params=(f"%{search_value}%", f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%",f"%{search_value}%"))
    
    conn.close()
    return df
    
def delete_db(nr):
    """Deletes selected record/Nr"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM transport WHERE nr = ?", (nr,))
    conn.commit()
    conn.close()