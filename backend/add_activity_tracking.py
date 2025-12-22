"""
Migration script to add user tracking columns to Task table
Run this script to update existing database with new activity tracking fields
"""
import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'projectTask.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Migrating database at {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add new columns if they don't exist
    columns_to_add = [
        ("started_by", "VARCHAR(36)"),
        ("reviewed_by", "VARCHAR(36)"),
        ("completed_by", "VARCHAR(36)")
    ]
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(task)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            print(f"Adding column {column_name}...")
            cursor.execute(f"ALTER TABLE task ADD COLUMN {column_name} {column_type}")
            print(f"✓ Added {column_name}")
        else:
            print(f"Column {column_name} already exists, skipping")
    
    conn.commit()
    print("\n✓ Migration completed successfully!")
    
except Exception as e:
    print(f"\n✗ Migration failed: {str(e)}")
    conn.rollback()
    
finally:
    conn.close()
