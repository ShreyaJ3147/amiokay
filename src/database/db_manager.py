"""
Database connection and query manager for AmIOkay.

This file is the single point of contact between your Python code
and the SQLite database. Every other file uses these functions
instead of writing raw sqlite3 code.
"""

import sqlite3
import os

# Paths
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'amiokay.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_connection():
    """Open a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # enforce relationships
    conn.row_factory = sqlite3.Row            # access columns by name
    return conn


def initialize_database():
    """Create all tables from schema.sql."""
    # Make sure data/ directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Database initialized!")
    print(f"📁 Location: {os.path.abspath(DB_PATH)}")


def run_query(sql, params=None):
    """
    Run a SELECT query. Returns list of dicts.

    Usage:
        results = run_query("SELECT * FROM symptoms WHERE category_id = ?", (1,))
        for row in results:
            print(row['symptom_name'])
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def run_insert(sql, params):
    """Run an INSERT and return the new row's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def run_execute(sql, params=None):
    """Run any SQL (INSERT/UPDATE/DELETE) without returning data."""
    conn = get_connection()
    conn.execute(sql, params or ())
    conn.commit()
    conn.close()


def run_executemany(sql, data_list):
    """
    Run the same SQL for many rows at once. Much faster than looping.

    Usage:
        run_executemany(
            "INSERT INTO symptoms (symptom_name, category_id) VALUES (?, ?)",
            [("Heavy periods", 1), ("Irregular cycles", 1), ...]
        )
    """
    conn = get_connection()
    conn.executemany(sql, data_list)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()