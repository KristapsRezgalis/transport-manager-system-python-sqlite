"""
Run this file whenever you want to clear ONLY the "transport" table
(your test order(s)) and restart order numbering at 10001, WITHOUT
touching any other table (companies, contacts, forwarders, etc.).

    python3 reset_transport.py

This will:
  1. Ask you to type YES to confirm
  2. Back up the current transport rows to a timestamped CSV file
  3. Delete all rows from "transport"
  4. Reset the order-number counter so the next order gets id 10001
"""

from create_tables import reset_transport_table

if __name__ == "__main__":
    reset_transport_table()
