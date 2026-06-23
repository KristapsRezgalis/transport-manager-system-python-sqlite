import sqlite3
import PySimpleGUI as sg
import pandas as pd

DB_PATH = "transport.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
'''
def fetch_rows_for_order(order_id):
    with get_connection() as conn:
        cur = conn.execute(f"SELECT * FROM t_pallet_details WHERE order_id = {order_id} ORDER BY order_id")
        return [dict(row) for row in cur.fetchall()]
'''
def fetch_rows_for_order(order_id):
    query = "SELECT * FROM t_pallet_details WHERE order_id = ? ORDER BY order_id"
    with get_connection() as conn:
        cur = conn.execute(query, (order_id,))
        print([dict(row) for row in cur.fetchall()])
        return [dict(row) for row in cur.fetchall()]

def insert_row(row):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO t_pallet_details (quantity, length, width, height) "
            "VALUES (?, ?, ?, ?)",
            (row["quantity"], row["length"], row["width"], row["height"]),
        )
        return cur.lastrowid