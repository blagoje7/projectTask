"""
Migration script to create task_activity table for tracking all task status changes.
This enables full audit trail including rejections and backward movements.
Uses SQLAlchemy to work with the configured database (MySQL).
"""
from app import create_app
from app.models import db

def migrate():
    app = create_app()
    
    with app.app_context():
        # Check if table already exists by trying to query the metadata
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        
        if 'task_activity' in inspector.get_table_names():
            print("✓ task_activity table already exists")
            return
        
        # Create table using raw SQL that works with MySQL
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE task_activity (
                    activity_id VARCHAR(36) PRIMARY KEY,
                    task_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    old_status VARCHAR(50),
                    new_status VARCHAR(50),
                    timestamp INT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES task (task_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES user (user_id),
                    INDEX idx_task_activity_task_id (task_id),
                    INDEX idx_task_activity_timestamp (timestamp)
                )
            """))
            conn.commit()
        
        print("✓ Successfully created task_activity table")
        print("✓ Created indexes for task_id and timestamp")

if __name__ == '__main__':
    print("Creating task_activity table...")
    migrate()
    print("\nMigration complete!")
