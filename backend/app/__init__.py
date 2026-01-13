"""
App Factory Module.
Initializes Flask app, extensions (DB, CORS, JWT, SocketIO), and registers blueprints.
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from .models import db, User, Role, TaskActivity, Project, Task, Team

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    db.init_app(app)
    
    from .extensions import socketio, init_arango
    socketio.init_app(app)
    init_arango(app)
    
    # Import socket events
    from . import sockets
    


    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.teams import teams_bp
    from .routes.projects import projects_bp
    from .routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(projects_bp)
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

        # Seed initial data (UserTEST, ManagerTEST, TeamTEST, ProjectTEST)
        manager_role = Role.query.filter_by(name='manager').first()
        user_role = Role.query.filter_by(name='user').first()
        admin_user = User.query.filter_by(email='admin@example.com').first()

        # 1. Create Users
        manager_test = User.query.filter_by(email='manager@manager.com').first()
        if not manager_test:
            manager_test = User(
                email='manager@manager.com',
                first_name='managerTEST',
                last_name='User',
                role=manager_role
            )
            manager_test.set_password('takovo123')
            db.session.add(manager_test)
            print("managerTEST created.")

        user_test = User.query.filter_by(email='user@user.com').first()
        if not user_test:
            user_test = User(
                email='user@user.com',
                first_name='userTEST',
                last_name='User',
                role=user_role
            )
            user_test.set_password('takovo123')
            db.session.add(user_test)
            print("userTEST created.")
        
        db.session.commit()

        # 2. Create Team
        team_test = Team.query.filter_by(name='TeamTEST').first()
        if not team_test:
            team_test = Team(name='TeamTEST')
            team_test.users.append(manager_test)
            team_test.users.append(user_test)
            db.session.add(team_test)
            db.session.commit()
            print("TeamTEST created and users assigned.")

        # 3. Create Project
        project_test = Project.query.filter_by(name='ProjectTEST').first()
        if not project_test:
            project_test = Project(
                name='ProjectTEST',
                description='Initial test project',
                created_by=admin_user.user_id # Admin created it
            )
            project_test.teams.append(team_test)
            db.session.add(project_test)
            db.session.commit()
            print("ProjectTEST created.")

            # 4. Create Tasks
            task1 = Task(
                name='TaskTEST1',
                description='First test task description',
                project_id=project_test.project_id,
                priority='high',
                created_by=manager_test.user_id,
                status='to_do'
            )
            task1.assignees.append(user_test)

            task2 = Task(
                name='TaskTEST2',
                description='Second test task description',
                project_id=project_test.project_id,
                priority='medium',
                created_by=manager_test.user_id,
                status='in_progress'
            )
            task2.assignees.append(manager_test)

            db.session.add(task1)
            db.session.add(task2)
            db.session.commit()
            print("TaskTEST1 and TaskTEST2 created.")

    return app
