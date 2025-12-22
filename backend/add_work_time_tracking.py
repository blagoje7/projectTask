"""
Migration script to add work time tracking columns to Task table.
Adds accumulated_work_time and last_progress_start columns for accurate time tracking
even when tasks are rejected and reworked multiple times.
"""
from app import create_app, db
from sqlalchemy import text

def add_work_time_columns():
    app = create_app()
    
    with app.app_context():
        try:
            # Add accumulated_work_time column (total seconds in in_progress)
            db.session.execute(text("""
                ALTER TABLE task 
                ADD COLUMN accumulated_work_time INT DEFAULT 0 NOT NULL
            """))
            print("✓ Added accumulated_work_time column")
            
            # Add last_progress_start column (track current in_progress session)
            db.session.execute(text("""
                ALTER TABLE task 
                ADD COLUMN last_progress_start INT
            """))
            print("✓ Added last_progress_start column")
            
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            print("\nNew columns added:")
            print("  - accumulated_work_time: Tracks total time spent in 'in_progress' status")
            print("  - last_progress_start: Tracks when current work session started")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {e}")
            print("\nNote: If columns already exist, this is expected.")

if __name__ == '__main__':
    add_work_time_columns()
