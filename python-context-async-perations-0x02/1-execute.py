#!/usr/bin/env python3
"""
1-execute.py
Reusable query context manager that leverages the exact same
__enter__ and __exit__ structure defined in 0-databaseconnection.py
"""

import sqlite3
from typing import Any, List, Tuple


class ExecuteQuery:
    """
    Re-uses the exact same __enter__ / __exit__ pattern
    to run a single parameterized SELECT and return the rows.
    """

    def __init__(self, query: str, params: Tuple[Any, ...] = (), db_path: str = "example.db") -> None:
        self.query = query
        self.params = params
        self.db_path = db_path
        self._conn = None

    def __enter__(self):
        """Same pattern as 0-databaseconnection.py: open, run, return."""
        self._conn = sqlite3.connect(self.db_path)
        cur = self._conn.cursor()
        cur.execute(self.query, self.params)
        return cur.fetchall()          # rows

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Same clean-up as 0-databaseconnection.py."""
        if self._conn:
            self._conn.close()


# ------------------------------------------------------------------
# --- Demo ---------------------------------------------------------
# ------------------------------------------------------------------
if __name__ == "__main__":
    # create/populate demo table (once, idempotent)
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER
            );
        """)
        cur.executemany(
            "INSERT OR IGNORE INTO users (name, age) VALUES (?, ?);",
            [("Alice", 30), ("Bob", 22), ("Charlie", 27), ("Diana", 19), ("Eve", 25)]
        )
        conn.commit()

    # Required usage: SELECT * FROM users WHERE age > 25
    sql = "SELECT * FROM users WHERE age > ?"
    with ExecuteQuery(sql, (25,)) as rows:
        for row in rows:
            print(row)
