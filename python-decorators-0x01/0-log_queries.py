import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    """
    Decorator that logs SQL queries with timestamps before executing them.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function that logs queries with timestamps
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from either args or kwargs
        query = kwargs.get('query', args[0] if args else None)
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log the query with timestamp
        print(f"[{timestamp}] Executing query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database
    
    Args:
        query: SQL query to execute
        
    Returns:
        List of users from the database
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    # Initialize a test database (for demonstration)
    conn = sqlite3.connect('users.db')
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie')")
    conn.commit()
    conn.close()
    
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print("Query results:", users)
