from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from .models import db, User, Role

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    db.init_app(app)
    


    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.teams import teams_bp
    from .routes.projects import projects_bp
    from .routes.epics import epics_bp
    from .routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(epics_bp)
    app.register_blueprint(tasks_bp)
    
    # Create tables and seed data
    with app.app_context():
        db.create_all()
        
        # Seed Roles
        roles = ['admin', 'manager', 'user']
        for r_name in roles:
            if not Role.query.filter_by(name=r_name).first():
                db.session.add(Role(name=r_name))
        db.session.commit()

        # Seed Admin
        admin_role = Role.query.filter_by(name='admin').first()
        if not User.query.filter_by(email='admin@example.com').first():
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

    return app
