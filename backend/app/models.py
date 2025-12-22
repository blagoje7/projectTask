import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for user-team many-to-many relationship
user_teams = db.Table('user_teams',
    db.Column('user_id', db.String(36), db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('team_id', db.String(36), db.ForeignKey('team.team_id'), primary_key=True)
)

# Association table for project-team many-to-many relationship
project_teams = db.Table('project_teams',
    db.Column('project_id', db.String(36), db.ForeignKey('project.project_id'), primary_key=True),
    db.Column('team_id', db.String(36), db.ForeignKey('team.team_id'), primary_key=True)
)

# Association table for task-assignee many-to-many relationship
task_assignees = db.Table('task_assignees',
    db.Column('task_id', db.String(36), db.ForeignKey('task.task_id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('user.user_id'), primary_key=True)
)

class Role(db.Model):
    role_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

class Team(db.Model):
    team_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'teamId': self.team_id,
            'name': self.name
        }

class User(db.Model):
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()))
    
    role_id = db.Column(db.String(36), db.ForeignKey('role.role_id'), nullable=False)
    teams = db.relationship('Team', secondary=user_teams, lazy='subquery',
        backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def login(self):
        pass

    def request_password_reset(self):
        pass

    def verify_token(self):
        pass

    def to_dict(self):
        return {
            'userId': self.user_id,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'role': {'name': self.role.name, 'roleId': self.role.role_id} if self.role else None,
            'isActive': self.is_active,
            'createdAt': self.created_at,
            'teams': [team.to_dict() for team in self.teams]
        }

class Project(db.Model):
    project_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    jira_key = db.Column(db.String(20), nullable=True)  # e.g., "PROJ"
    jira_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()))
    created_by = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    
    # Relationships
    teams = db.relationship('Team', secondary=project_teams, lazy='subquery',
        backref=db.backref('projects', lazy=True))
    epics = db.relationship('Epic', backref='project', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'projectId': self.project_id,
            'name': self.name,
            'description': self.description,
            'jiraKey': self.jira_key,
            'jiraUrl': self.jira_url,
            'createdAt': self.created_at,
            'createdBy': self.created_by,
            'teams': [{'teamId': t.team_id, 'name': t.name} for t in self.teams]
        }

class Epic(db.Model):
    epic_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.project_id'), nullable=False)
    jira_key = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()))
    
    # Relationships
    tasks = db.relationship('Task', backref='epic', lazy=True)
    
    def to_dict(self):
        return {
            'epicId': self.epic_id,
            'name': self.name,
            'description': self.description,
            'projectId': self.project_id,
            'jiraKey': self.jira_key,
            'createdAt': self.created_at
        }

class Task(db.Model):
    task_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.String(36), db.ForeignKey('project.project_id'), nullable=False)
    epic_id = db.Column(db.String(36), db.ForeignKey('epic.epic_id'), nullable=True)
    
    # Task properties
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='to_do')  # to_do, in_progress, for_review, done
    deadline = db.Column(db.Integer, nullable=True)  # Unix timestamp
    
    # Jira integration
    jira_key = db.Column(db.String(20), nullable=True)  # e.g., "PROJ-123"
    jira_url = db.Column(db.String(500), nullable=True)
    
    # Metadata
    created_at = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()))
    created_by = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    updated_at = db.Column(db.Integer, onupdate=lambda: int(datetime.utcnow().timestamp()))
    started_at = db.Column(db.Integer, nullable=True)  # Timestamp when task moved to in_progress
    started_by = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=True)  # User who started the task
    reviewed_at = db.Column(db.Integer, nullable=True)  # Timestamp when task moved to for_review
    reviewed_by = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=True)  # User who sent for review
    completed_at = db.Column(db.Integer, nullable=True)  # Timestamp when task was marked as done
    completed_by = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=True)  # User who completed the task
    accumulated_work_time = db.Column(db.Integer, default=0, nullable=False)  # Total seconds spent in in_progress status
    last_progress_start = db.Column(db.Integer, nullable=True)  # Track current in_progress session start
    
    # Relationships
    assignees = db.relationship('User', secondary=task_assignees, lazy='subquery',
        backref=db.backref('assigned_tasks', lazy=True))
    
    def to_dict(self):
        # Calculate time worked: accumulated time in in_progress status
        time_worked = self.accumulated_work_time
        
        # If currently in progress, add the current session time
        if self.status == 'in_progress' and self.last_progress_start:
            from datetime import datetime
            current_session = int(datetime.utcnow().timestamp()) - self.last_progress_start
            time_worked += current_session
        
        # Calculate total time: from creation to completion (done status)
        total_time = None
        if self.status == 'done' and self.completed_at and self.created_at:
            total_time = self.completed_at - self.created_at
        
        # Get user names for activity tracking
        created_by_user = User.query.get(self.created_by) if self.created_by else None
        started_by_user = User.query.get(self.started_by) if self.started_by else None
        reviewed_by_user = User.query.get(self.reviewed_by) if self.reviewed_by else None
        completed_by_user = User.query.get(self.completed_by) if self.completed_by else None
        
        return {
            'taskId': self.task_id,
            'name': self.name,
            'description': self.description,
            'projectId': self.project_id,
            'epicId': self.epic_id,
            'epicName': self.epic.name if self.epic else None,
            'priority': self.priority,
            'status': self.status,
            'deadline': self.deadline,
            'jiraKey': self.jira_key,
            'jiraUrl': self.jira_url,
            'createdAt': self.created_at,
            'createdBy': self.created_by,
            'createdByName': f"{created_by_user.first_name} {created_by_user.last_name}" if created_by_user else None,
            'updatedAt': self.updated_at,
            'startedAt': self.started_at,
            'startedBy': self.started_by,
            'startedByName': f"{started_by_user.first_name} {started_by_user.last_name}" if started_by_user else None,
            'reviewedAt': self.reviewed_at,
            'reviewedBy': self.reviewed_by,
            'reviewedByName': f"{reviewed_by_user.first_name} {reviewed_by_user.last_name}" if reviewed_by_user else None,
            'completedAt': self.completed_at,
            'completedBy': self.completed_by,
            'completedByName': f"{completed_by_user.first_name} {completed_by_user.last_name}" if completed_by_user else None,
            'timeWorked': time_worked,
            'totalTime': total_time,
            'assignees': [{'userId': u.user_id, 'email': u.email, 'firstName': u.first_name, 'lastName': u.last_name} for u in self.assignees]
        }

class TaskActivity(db.Model):
    """
    Model for tracking all task status changes and activities.
    Provides complete audit trail including rejections and backward movements.
    """
    __tablename__ = 'task_activity'
    
    activity_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey('task.task_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # 'created', 'status_change', 'assigned', etc.
    old_status = db.Column(db.String(50))  # Previous status (null for creation)
    new_status = db.Column(db.String(50))  # New status
    timestamp = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    
    # Relationships
    task = db.relationship('Task', backref=db.backref('activities', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('task_activities', lazy='dynamic'))
    
    def to_dict(self):
        user = User.query.get(self.user_id)
        return {
            'activityId': self.activity_id,
            'taskId': self.task_id,
            'userId': self.user_id,
            'userName': f"{user.first_name} {user.last_name}" if user else None,
            'actionType': self.action_type,
            'oldStatus': self.old_status,
            'newStatus': self.new_status,
            'timestamp': self.timestamp
        }
