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

