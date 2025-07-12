import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connections.
    Opens a connection, passes it to the decorated function, and closes it afterward.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open a new database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection as the first argument if not already provided
            if 'conn' not in kwargs and not (args and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            
            # Execute the function
            result = func(*args, **kwargs)
            return result
        finally:
            # Ensure connection is closed even if an error occurs
            conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Gets a user by their ID from the database
    
    Args:
        conn: Database connection (automatically provided by decorator)
        user_id: ID of the user to fetch
        
    Returns:
        The user record or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Example usage
if __name__ == "__main__":
    # Initialize a test database (for demonstration)
    conn = sqlite3.connect('users.db')
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie')")
    conn.commit()
    conn.close()
    
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print("User:", user)
