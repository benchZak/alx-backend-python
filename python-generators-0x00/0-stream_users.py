#!/usr/bin/python3
import mysql.connector

def stream_users():
    """Generator that streams rows from user_data table one by one"""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="fffer",  # Change as needed
            database="ALX_prodev"
        )
        
        # Create a cursor with dictionary=True to get rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        
        # Execute the query
        cursor.execute("SELECT * FROM user_data;")
        
        # Yield rows one by one
        for row in cursor:
            yield row
            
    finally:
        # Ensure resources are cleaned up
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
