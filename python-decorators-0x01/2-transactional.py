import sqlite3
import functools

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

def transactional(func):
    """
    Decorator that manages database transactions.
    Commits if the function succeeds, rolls back if it raises an exception.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            print("Transaction committed successfully")
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back due to error: {str(e)}")
            raise
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email address in the database.
    
    Args:
        conn: Database connection (provided by decorator)
        user_id: ID of user to update
        new_email: New email address
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Example usage
if __name__ == "__main__":
    # Initialize test database
    conn = sqlite3.connect('users.db')
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    conn.commit()
    conn.close()
    
    # Successful update
    print("Attempting successful update:")
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    
    # Failed update (will rollback)
    print("\nAttempting failed update:")
    try:
        update_user_email(user_id=999, new_email='nonexistent@example.com')
    except Exception as e:
        print(f"Caught exception: {e}")
