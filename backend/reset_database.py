"""
Script to delete the SQLite database for a clean start.
"""
import os
from pathlib import Path

# Get the backend directory
BASE_DIR = Path(__file__).resolve().parent
db_file = BASE_DIR / 'db.sqlite3'

try:
    if db_file.exists():
        os.remove(db_file)
        print(f"Database file '{db_file}' deleted.")
    else:
        print(f"Database file '{db_file}' does not exist.")
    
    print("\nDatabase reset complete! Now run: python manage.py migrate")
    
except Exception as e:
    print(f"Error: {e}")
