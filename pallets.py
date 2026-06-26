import sqlite3
import PySimpleGUI as sg
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH = "transport.db"

PALLET_COLUMNS   = ["quantity", "length", "width", "height"]
PALLET_COL_WIDTHS = [10, 10, 10, 10]

# Max pre-allocated row slots (hidden until data fills them)
MAX_PALLET_ROWS = 10

BG_COLOR        = sg.theme_background_color()
TEXT_COLOR      = sg.theme_text_color()
HIGHLIGHT_COLOR = sg.theme_button_color()[1]
SEP_COLOR       = sg.theme_button_color()[1]  # thin line between header and rows

pallet_data   = []
selected_row  = {"index": None}

# ===========================================================================
# DATABASE FUNCTIONS
# ===========================================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_rows_for_order(order_id):
    """
    Return all pallet rows that belong to the given order_id,
    as a list of dicts sorted by id.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id, order_id, quantity, length, width, height "
            "FROM t_pallet_details "
            "WHERE order_id = ? "
            "ORDER BY id",
            (order_id,),
        )
        return [dict(row) for row in cur.fetchall()]

def insert_pallet_row(order_id, row):
    """
    Insert a new pallet row linked to order_id.
    row is a dict with keys: quantity, length, width, height.
    Returns the new row's auto-generated id.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO t_pallet_details (order_id, quantity, length, width, height) "
            "VALUES (?, ?, ?, ?, ?)",
            (order_id, row["quantity"], row["length"], row["width"], row["height"]),
        )
        return cur.lastrowid

def update_pallet_row(row_id, row):
    """Overwrite the four pallet fields for an existing pallet row."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE t_pallet_details "
            "SET quantity=?, length=?, width=?, height=? "
            "WHERE pallet_id=?",
            (row["quantity"], row["length"], row["width"], row["height"], row_id),
        )
        
def delete_pallet_row(row_id):
    """Delete a single pallet row by its id."""
    with get_connection() as conn:
        conn.execute("DELETE FROM t_pallet_details WHERE pallet_id=?", (row_id,))

row = {'quantity': '5', 'length': '100', 'width': '120', 'height': '1'}
#insert_pallet_row(1, row)
#update_pallet_row(2, row)
#delete_pallet_row(2)

# ===========================================================================
# GUI HELPERS -- table builder
# ===========================================================================

def make_header_row():
    return [
        sg.Text(
            col.capitalize(),
            size=(w, 1),
            font=("Any", 10, "bold"),
            background_color=bg_color,
            text_color=text_color,
            justification="left",
            pad=(2, 2),
        )
        for col, w in zip(PALLET_COLUMNS, COL_WIDTHS)
    ]

def make_data_row(row_idx):
    return [
        sg.Text(
            "",
            size=(w, 1),
            key=("-CELL-", row_idx, col_idx),
            background_color=bg_color,
            text_color=text_color,
            justification="left",
            pad=(2, 2),
            enable_events=True,  # click to select
            visible=False,
        )
        for col_idx, w in enumerate(COL_WIDTHS)
    ]