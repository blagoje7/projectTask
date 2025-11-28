from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..models import db, Project, Team, User

projects_bp = Blueprint('projects', __name__)

"""Get all projects (Managers see their team's projects, Admins see all)"""
@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    claims = get_jwt()
    role_claim = claims.get('role')
    user_id = claims.get('userId') or claims.get('sub')  # Backwards compatibility
    
    if not user_id:
        return jsonify({"msg": "Invalid token, please log in again"}), 401
    
    if role_claim == 'admin':
        # Admins see all projects
        projects = Project.query.all()
    elif role_claim == 'manager':
        # Managers see projects where they are in assigned teams
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        # Get all projects that have teams the manager belongs to
        projects = []
        for team in user.teams:
            projects.extend(team.projects)
        # Remove duplicates
        projects = list(set(projects))
    else:
        # Regular users see projects from their teams
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        projects = []
        for team in user.teams:
            projects.extend(team.projects)
        projects = list(set(projects))
    
    return jsonify([p.to_dict() for p in projects]), 200

"""Get project details with teams, epics, and tasks"""
@projects_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project_details(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    project_data = project.to_dict()
    project_data['epics'] = [e.to_dict() for e in project.epics]
    project_data['tasks'] = [t.to_dict() for t in project.tasks]
    
    return jsonify(project_data), 200

"""Create a new project (Admin/Manager only)"""
@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    claims = get_jwt()
    role_claim = claims.get('role')
    user_id = claims.get('userId') or claims.get('sub')  # Backwards compatibility
    
    if not user_id:
        return jsonify({"msg": "Invalid token, please log in again"}), 401
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    team_ids = data.get('teamIds', [])
    
    if not name:
        return jsonify({"msg": "Project name is required"}), 400
    
    # Create project in database
    project = Project(
        name=name,
        description=description,
        created_by=user_id
    )
    
    # Assign teams to project
    for team_id in team_ids:
        team = Team.query.get(team_id)
        if team:
            project.teams.append(team)
    
    db.session.add(project)
    db.session.commit()
    
    # TODO: Create Jira project (will implement in jira_integration)
    
    return jsonify(project.to_dict()), 201

"""Update project details (Admin/Manager only)"""
@projects_bp.route('/projects/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'teamIds' in data:
        # Update team assignments
        project.teams = []
        for team_id in data['teamIds']:
            team = Team.query.get(team_id)
            if team:
                project.teams.append(team)
    
    db.session.commit()
    return jsonify(project.to_dict()), 200

"""Delete a project (Admin only)"""
@projects_bp.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim != 'admin':
        return jsonify({"msg": "Admin only"}), 403
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({"msg": "Project deleted"}), 200
