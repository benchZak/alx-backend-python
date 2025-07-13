#!/usr/bin/env python3
"""
0-databaseconnection.py
Custom class-based context manager for automatic DB connection handling.
"""

import sqlite3


class DatabaseConnection:
    """
    A context manager that opens a SQLite database connection on entry
    and ensures it is properly closed on exit.
    """

    def __init__(self, db_path: str = "example.db") -> None:
        """Store the path to the SQLite database file."""
        self.db_path = db_path
        self.connection = None

    def __enter__(self) -> sqlite3.Connection:
        """Open the database connection and return it."""
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the database connection.
        If an exception occurred in the with-block, it is propagated.
        """
        if self.connection:
            self.connection.close()

# ------------------------------------------------------------------
# --- Usage / Demonstration ----------------------------------------
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure a small demo table exists for the sake of the example
    with DatabaseConnection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """)
        cur.executemany("INSERT OR IGNORE INTO users (name) VALUES (?);",
                        [("Alice",), ("Bob",), ("Charlie",)])
        conn.commit()

    # Now use the context manager to perform the requested query
    with DatabaseConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        rows = cur.fetchall()

    # Print the results
    for row in rows:
        print(row)
