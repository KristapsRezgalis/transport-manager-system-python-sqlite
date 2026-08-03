"""
Table creation functions for transport_db.sql schema.

Each function opens (or creates) the SQLite database at DB_PATH and
issues a CREATE TABLE IF NOT EXISTS statement matching the original
schema exactly (including column names, types, and constraints).

Usage:
    import sqlite3
    from create_tables import create_all_tables

    conn = sqlite3.connect("transport_db.sqlite")
    create_all_tables(conn)
    conn.commit()
    conn.close()
"""

import os
import shutil
import sqlite3
from datetime import datetime

DB_PATH = "transport_db.sqlite"

# The transport table's "nr" column doubles as the customer-facing
# order number (e.g. "Transport agreement Nr 10001"). We start it at
# 10001 instead of 1 so order numbers look more established/serious.
TRANSPORT_ORDER_START = 10001


def create_t_company(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_company" (
            "company_id"    INTEGER NOT NULL,
            "c_name"        TEXT,
            "c_reg"         TEXT,
            "c_vat"         TEXT,
            "c_street"      TEXT,
            "c_city"        TEXT,
            "c_post_code"   TEXT,
            "c_country"     TEXT,
            "c_notes"       TEXT,
            "c_prod_type"   TEXT,
            PRIMARY KEY("company_id" AUTOINCREMENT)
        )
    """)


def create_t_company_address(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_company_address" (
            "address_id"     INTEGER NOT NULL,
            "company_id"     TEXT,
            "adr_name"       TEXT,
            "adr_street"     TEXT,
            "adr_city"       TEXT,
            "adr_post_code"  TEXT,
            "adr_country"    TEXT,
            "adr_hours"      TEXT,
            "adr_book_slot"  TEXT,
            "adr_reference"  TEXT,
            "adr_notes"      TEXT,
            PRIMARY KEY("address_id" AUTOINCREMENT)
        )
    """)


def create_t_company_contact(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_company_contact" (
            "c_con_id"        INTEGER NOT NULL,
            "company_id"      INTEGER,
            "c_con_name"      TEXT,
            "c_con_surname"   TEXT,
            "c_con_position"  TEXT,
            "c_con_phone"     TEXT,
            "c_con_email"     TEXT,
            PRIMARY KEY("c_con_id" AUTOINCREMENT)
        )
    """)


def create_t_forwarder(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_forwarder" (
            "forwarder_id"      INTEGER,
            "fw_name"           TEXT,
            "fw_reg_nr"         INTEGER,
            "fw_vat_nr"         TEXT,
            "fw_street"         TEXT,
            "fw_city"           TEXT,
            "fw_post_code"      TEXT,
            "fw_country"        TEXT,
            "fw_payment_terms"  INTEGER,
            PRIMARY KEY("forwarder_id" AUTOINCREMENT)
        )
    """)


def create_t_fw_contact(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_fw_contact" (
            "fw_contact_id"  INTEGER,
            "forwarder_id"   INTEGER,
            "fw_c_name"      TEXT,
            "fw_c_surname"   TEXT,
            "fw_c_position"  TEXT,
            "fw_c_phone"     TEXT,
            "fw_c_email"     TEXT,
            PRIMARY KEY("fw_contact_id" AUTOINCREMENT),
            CONSTRAINT "fk_forwarder_fwContact" FOREIGN KEY("forwarder_id")
                REFERENCES "t_forwarder"("forwarder_id")
        )
    """)


def create_t_pallet_details(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_pallet_details" (
            "pallet_id"  INTEGER NOT NULL,
            "order_id"   INTEGER,
            "length"     INTEGER,
            "width"      INTEGER,
            "height"     INTEGER,
            "quantity"   INTEGER,
            PRIMARY KEY("pallet_id" AUTOINCREMENT)
        )
    """)


def create_t_purchase_manager(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_purchase_manager" (
            "manager_id"       INTEGER NOT NULL,
            "manager_name"     TEXT,
            "manager_surname"  TEXT,
            "manager_phone"    TEXT,
            "manager_email"    TEXT,
            "department"       TEXT,
            PRIMARY KEY("manager_id" AUTOINCREMENT)
        )
    """)


def create_t_tender_contacts(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "t_tender_contacts" (
            "tender_contact_id"  INTEGER NOT NULL,
            "country"            TEXT NOT NULL,
            "email"              TEXT NOT NULL,
            "active"             INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY("tender_contact_id" AUTOINCREMENT)
        )
    """)


def create_transport(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "transport" (
            "nr"                  INTEGER,
            "sap_po"              INTEGER,
            "sender"              TEXT,
            "sender_adr"          TEXT,
            "sender_cont"         TEXT,
            "delivery"            TEXT,
            "delivery_adr"        TEXT,
            "delivery_cont"       TEXT,
            "loading"             TEXT,
            "loading_to"          TEXT,
            "unloading"           TEXT,
            "unloading_to"        TEXT,
            "pallets"             INTEGER,
            "ldm"                 REAL,
            "weight"              REAL,
            "forwarder"           TEXT,
            "forwarder_contact"   TEXT,
            "cost"                REAL,
            "customs"             TEXT,
            "ref"                 TEXT,
            "info"                TEXT,
            "add_info_to_order"   TEXT,
            "purch_manager"       TEXT,
            "cargo_type"          TEXT,
            "transport_invoice"   TEXT,
            PRIMARY KEY("nr" AUTOINCREMENT)
        )
    """)


def create_user(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            "nr"        INTEGER,
            "name"      TEXT,
            "surname"   TEXT,
            "role"      TEXT,
            "email"     TEXT,
            "phone"     TEXT,
            "login"     TEXT,
            "password"  TEXT,
            PRIMARY KEY("nr" AUTOINCREMENT)
        )
    """)


def seed_transport_order_start(conn: sqlite3.Connection, start_at: int = TRANSPORT_ORDER_START) -> None:
    """
    Make the next row inserted into "transport" get id = start_at,
    instead of 1, by seeding SQLite's internal autoincrement tracker.

    Safe to call multiple times: if a starting value has already been
    seeded (or real orders already exist with a higher id), this will
    NOT move the counter backwards -- it only raises it, never lowers
    it, so you can't accidentally create duplicate order numbers.
    """
    seed_value = start_at - 1  # AUTOINCREMENT's next id = seq + 1

    row = conn.execute(
        "SELECT seq FROM sqlite_sequence WHERE name = 'transport'"
    ).fetchone()

    if row is None:
        conn.execute(
            "INSERT INTO sqlite_sequence (name, seq) VALUES ('transport', ?)",
            (seed_value,),
        )
    elif row[0] < seed_value:
        conn.execute(
            "UPDATE sqlite_sequence SET seq = ? WHERE name = 'transport'",
            (seed_value,),
        )
    # else: current seq is already >= seed_value, leave it alone


def create_all_tables(conn: sqlite3.Connection) -> None:
    """Create every table in the schema, in dependency order."""
    create_t_company(conn)
    create_t_company_address(conn)
    create_t_company_contact(conn)
    create_t_forwarder(conn)
    create_t_fw_contact(conn)          # depends on t_forwarder
    create_t_pallet_details(conn)
    create_t_purchase_manager(conn)
    create_t_tender_contacts(conn)
    create_transport(conn)
    create_user(conn)
    seed_transport_order_start(conn)   # transport.nr starts at 10001, not 1


def reset_transport_table(
    db_path: str = DB_PATH,
    start_at: int = TRANSPORT_ORDER_START,
    backup: bool = True,
    confirm: bool = True,
) -> None:
    """
    Delete all rows from ONLY the "transport" table and restart its
    order numbering at start_at. All other tables are left untouched.

    Args:
        db_path:  Path to the SQLite database file.
        start_at: The id/order number the next inserted transport
                   row should get (default: TRANSPORT_ORDER_START).
        backup:   If True, saves the current transport rows to a
                   timestamped CSV file before deleting them.
        confirm:  If True, asks for typed confirmation first.
    """
    if confirm:
        answer = input(
            'This will permanently delete ALL rows in the "transport" '
            f'table (other tables are untouched) and restart numbering '
            f"at {start_at}. Type YES to continue: "
        )
        if answer.strip() != "YES":
            print("Reset cancelled. No changes made.")
            return

    conn = sqlite3.connect(db_path)
    try:
        if backup:
            rows = conn.execute("SELECT * FROM transport").fetchall()
            col_names = [d[0] for d in conn.execute("SELECT * FROM transport").description]
            if rows:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"transport_backup_{timestamp}.csv"
                import csv
                with open(backup_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(col_names)
                    writer.writerows(rows)
                print(f"Backed up {len(rows)} row(s) to {backup_path}")
            else:
                print("No existing transport rows to back up.")

        conn.execute("DELETE FROM transport")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'transport'")
        conn.execute(
            "INSERT INTO sqlite_sequence (name, seq) VALUES ('transport', ?)",
            (start_at - 1,),
        )
        conn.commit()
        print(f'"transport" table cleared. Next inserted order will get id {start_at}.')
    finally:
        conn.close()


def reset_database(db_path: str = DB_PATH, backup: bool = True, confirm: bool = True) -> None:
    """
    Wipe the database file and rebuild an empty schema from scratch.

    Args:
        db_path: Path to the SQLite database file to reset.
        backup:  If True, copies the existing file to
                 "<name>_backup_<timestamp>.sqlite" before deleting it.
        confirm: If True, asks for typed confirmation before doing
                 anything destructive. Set to False for non-interactive
                 use (e.g. CI, scripts), but be careful.
    """
    if confirm:
        answer = input(
            f'This will permanently delete all data in "{db_path}" and '
            f"recreate an empty schema. Type YES to continue: "
        )
        if answer.strip() != "YES":
            print("Reset cancelled. No changes made.")
            return

    if os.path.exists(db_path):
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(db_path)
            backup_path = f"{base}_backup_{timestamp}{ext}"
            shutil.copy2(db_path, backup_path)
            print(f"Backup saved to {backup_path}")
        os.remove(db_path)
        print(f"Deleted old database: {db_path}")
    else:
        print(f"No existing database found at {db_path}; creating a new one.")

    connection = sqlite3.connect(db_path)
    try:
        create_all_tables(connection)
        connection.commit()
        print(f"Fresh, empty schema created in {db_path}")
    finally:
        connection.close()


if __name__ == "__main__":
    connection = sqlite3.connect(DB_PATH)
    try:
        create_all_tables(connection)
        connection.commit()
        print(f"All tables created (if not already present) in {DB_PATH}")
    finally:
        connection.close()
