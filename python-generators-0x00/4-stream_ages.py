#!/usr/bin/python3
import mysql.connector

def stream_user_ages():
    """Generator that streams user ages one by one from the database"""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="fffer",
            database="ALX_prodev"
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data;")
        
        # Stream ages one by one
        for (age,) in cursor:
            yield age
            
    finally:
        # Clean up resources
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def calculate_average_age():
    """Calculates average age using the stream_user_ages generator"""
    total = 0
    count = 0
    
    # First loop: iterate through ages from generator
    for age in stream_user_ages():
        total += age
        count += 1
    
    # Calculate and print average
    average = total / count if count > 0 else 0
    print(f"Average age of users: {average}")

if __name__ == "__main__":
    calculate_average_age()
