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
    sender TEXT NOT NULL,
    delivery TEXT NOT NULL,
    loading TEXT NOT NULL,
    unloading TEXT NOT NULL,
    pallets INTEGER NOT NULL,
    weight REAL NOT NULL,
    forwarder TEXT NOT NULL,
    cost INTEGER NOT NULL,
    customs TEXT NOT NULL,
    ref TEXT NOT NULL,
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

def add_db(nr, sender, delivery, loading,unloading, pallets, weight, forwarder, cost,customs,ref):
 """Adds new record into database"""