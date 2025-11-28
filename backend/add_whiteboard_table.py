"""
Database migration to add Whiteboard table
Run this after updating models.py
"""

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    # Create the whiteboard table
    db.create_all()
    print("✅ Whiteboard table created successfully!")
    
    # Verify table creation
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'whiteboard' in tables:
        print("✅ Whiteboard table verified in database")
        
        # Show table columns
        columns = inspector.get_columns('whiteboard')
        print("\nWhiteboard table columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("❌ Whiteboard table not found")
