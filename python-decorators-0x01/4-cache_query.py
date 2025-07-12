4. Using decorators to cache Database Queries
mandatory
Objective: create a decorator that caches the results of a database queries inorder to avoid redundant calls

Instructions:

Complete the code below by implementing a decorator cache_query(func) that caches query results based on the SQL query string
import time
import sqlite3 
import functools


query_cache = {}

"""your code goes here"""

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
Repo:

GitHub repository: alx-backend-python
Directory: python-decorators-0x01
File: 4-cache_query.py
