"""
Run this file whenever you want to wipe the database and start fresh.

    python3 reset_db.py

This will:
  1. Ask you to type YES to confirm
  2. Back up the existing database file (with a timestamp)
  3. Delete the old file
  4. Rebuild an empty schema from create_tables.py

Do NOT run this as part of normal app startup -- only run it
deliberately, when you actually want to clear the data.
"""

from create_tables import reset_database

if __name__ == "__main__":
    reset_database()
