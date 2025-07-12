#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that streams users from database in batches"""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="fffer",  # Change as needed
            database="ALX_prodev"
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Execute query and fetch in batches
        cursor.execute("SELECT * FROM user_data;")
        
        while True:
            # Fetch a batch of rows
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
            
    finally:
        # Clean up resources
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def batch_processing(batch_size):
    """Process batches of users and yield those over 25 years old"""
    # First loop: iterate through batches
    for batch in stream_users_in_batches(batch_size):
        # Second loop: process each user in batch
        for user in batch:
            # Filter users over 25
            if user['age'] > 25:
                yield user
