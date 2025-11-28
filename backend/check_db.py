from app import create_app
from app.models import db, User, Role
from sqlalchemy import text

app = create_app()

def check_db():
    with app.app_context():
        try:
            # Try to connect
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
            
            # Check if tables exist
            db.create_all()
            print("Tables created/verified.")
            
            # Seed Roles
            roles = ['admin', 'manager', 'user']
            for r_name in roles:
                if not Role.query.filter_by(name=r_name).first():
                    db.session.add(Role(name=r_name))
            db.session.commit()
            print("Roles verified/seeded.")

            # Check for admin user
            admin_role = Role.query.filter_by(name='admin').first()
            admin = User.query.filter_by(email='admin@example.com').first()
            if admin:
                print(f"Admin user found: {admin.email}")
            else:
                print("Admin user NOT found. Attempting to create...")
                admin = User(
                    email='admin@example.com', 
                    first_name='Super', 
                    last_name='Admin',
                    role=admin_role
                )
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created (admin@example.com / admin).")
                
        except Exception as e:
            print(f"Database error: {e}")
            print("Please check your backend/config.py settings.")

if __name__ == "__main__":
    check_db()
