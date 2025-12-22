"""
Migration script to add user tracking columns to task table.
Adds: started_by, reviewed_by, completed_by foreign keys.
Uses SQLAlchemy to work with the configured database (MySQL).
"""
from app import create_app
from app.models import db

def migrate():
    app = create_app()
    
    with app.app_context():
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        
        # Get existing columns
        columns = [col['name'] for col in inspector.get_columns('task')]
        
        # Add columns if they don't exist
        if 'started_by' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE task ADD COLUMN started_by VARCHAR(36)"))
                conn.execute(text("ALTER TABLE task ADD FOREIGN KEY (started_by) REFERENCES user(user_id)"))
                conn.commit()
            print("✓ Added started_by column")
        else:
            print("✓ started_by column already exists")
        
        if 'reviewed_by' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE task ADD COLUMN reviewed_by VARCHAR(36)"))
                conn.execute(text("ALTER TABLE task ADD FOREIGN KEY (reviewed_by) REFERENCES user(user_id)"))
                conn.commit()
            print("✓ Added reviewed_by column")
        else:
            print("✓ reviewed_by column already exists")
        
        if 'completed_by' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE task ADD COLUMN completed_by VARCHAR(36)"))
                conn.execute(text("ALTER TABLE task ADD FOREIGN KEY (completed_by) REFERENCES user(user_id)"))
                conn.commit()
            print("✓ Added completed_by column")
        else:
            print("✓ completed_by column already exists")

if __name__ == '__main__':
    print("Adding user tracking columns to task table...")
    migrate()
    print("\nMigration complete!")
