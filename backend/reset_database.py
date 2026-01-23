"""
Script to drop and recreate the database for a clean start.
"""
import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
django.setup()

import pymysql

# Get database config
db_name = config('DB_NAME', default='crm_example')
db_user = config('DB_USER', default='root')
db_password = config('DB_PASSWORD', default='')
db_host = config('DB_HOST', default='localhost')
db_port = config('DB_PORT', default='3306', cast=int)

try:
    # Connect to MySQL (without specifying database)
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )
    
    cursor = conn.cursor()
    
    # Drop database if exists
    cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
    print(f"Database '{db_name}' dropped.")
    
    # Create database
    cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print(f"Database '{db_name}' created.")
    
    cursor.close()
    conn.close()
    
    print("\nDatabase reset complete! Now run: python manage.py migrate")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure MySQL is running and credentials are correct.")
