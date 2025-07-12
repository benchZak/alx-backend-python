import time
import sqlite3
import functools
from functools import wraps

# Global cache dictionary
query_cache = {}

def with_db_connection(func):
    """
    Decorator that handles database connection automatically.
    Provides the connection as the first argument to the wrapped function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            # Pass connection as first argument if not already provided
            if not args or not isinstance(args[0], sqlite3.Connection):
                result = func(conn, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def cache_query(func):
    """
    Decorator that caches database query results based on the query string.
    
    The cache uses the query string as the key and stores the result along with
    a timestamp for potential future cache invalidation.
    """
    @wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Check if query is in cache
        if query in query_cache:
            print("Returning cached result for query:", query)
            return query_cache[query]
        
        # Execute query and cache result if not found
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        print("Caching new result for query:", query)
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database with query result caching.
    
    Args:
        conn: Database connection (provided by decorator)
        query: SQL query string
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    # Initialize test database
    conn = sqlite3.connect('users.db')
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    conn.commit()
    conn.close()
    
    # First call will execute and cache the query
    print("First call (will execute query):")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("Result:", users)
    
    # Second call will use the cached result
    print("\nSecond call (will use cache):")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("Result:", users_again)
    
    # Different query will execute again
    print("\nDifferent query (will execute):")
    specific_user = fetch_users_with_cache(query="SELECT * FROM users WHERE id = 1")
    print("Result:", specific_user)
