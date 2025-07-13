#!/usr/bin/env python3
"""
3-concurrent.py
Concurrent asynchronous database queries with aiosqlite.
"""

import asyncio
import aiosqlite
from typing import List, Tuple


DB_PATH = "example.db"


async def async_fetch_users() -> List[Tuple]:
    """Return every row in the users table."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return rows


async def async_fetch_older_users() -> List[Tuple]:
    """Return users whose age is strictly greater than 40."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            rows = await cursor.fetchall()
            return rows


async def fetch_concurrently() -> None:
    """Run both queries concurrently and print the results."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    print("All users:")
    for row in all_users:
        print(row)

    print("\nUsers older than 40:")
    for row in older_users:
        print(row)


# ------------------------------------------------------------------
# --- Bootstrap / Demo ---------------------------------------------
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure the demo table exists with some data
    import sqlite3

    with sqlite3.connect(DB_PATH) as conn:
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
            [
                ("Alice", 30),
                ("Bob", 45),
                ("Charlie", 25),
                ("Diana", 52),
                ("Eve", 38),
                ("Frank", 41)
            ]
        )
        conn.commit()

    # Run the concurrent queries
    asyncio.run(fetch_concurrently())
