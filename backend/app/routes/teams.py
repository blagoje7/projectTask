from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..models import db, Team, User

teams_bp = Blueprint('teams', __name__)

"""Get all teams (Admin gets all, Manager gets only their teams)"""
@teams_bp.route('/teams', methods=['GET'])
@jwt_required()
def get_teams():
    claims = get_jwt()
    role_claim = claims.get('role')
    user_id = claims.get('userId') or claims.get('sub')  # Backwards compatibility
    
    if not user_id:
        return jsonify({"msg": "Invalid token, please log in again"}), 401
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    if role_claim == 'admin':
        teams = Team.query.all()
    else:  # manager
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        teams = user.teams
        
    return jsonify([t.to_dict() for t in teams]), 200

"""Get team details with members (All authenticated users can view)"""
@teams_bp.route('/teams/<team_id>', methods=['GET'])
@jwt_required()
def get_team_details(team_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    user_id = claims.get('userId') or claims.get('sub')  # Backwards compatibility
    
    if not user_id:
        return jsonify({"msg": "Invalid token, please log in again"}), 401
        
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"msg": "Team not found"}), 404
    
    # Managers and regular users can only view teams they are assigned to
    if role_claim != 'admin':
        user = User.query.get(user_id)
        if not user or team not in user.teams:
            return jsonify({"msg": "You can only view teams you are assigned to"}), 403
        
    team_data = team.to_dict()
    team_data['users'] = [u.to_dict() for u in team.users]
    return jsonify(team_data), 200

"""Create a new team (Admin/Manager only)"""
@teams_bp.route('/teams', methods=['POST'])
@jwt_required()
def create_team():
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
        
    data = request.get_json()
    name = data.get('name')
    
    team = Team(name=name)
    db.session.add(team)
    db.session.commit()
    
    return jsonify(team.to_dict()), 201

"""Delete a team (Admin only)"""
@teams_bp.route('/teams/<team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    
    claims = get_jwt()
    role_claim = claims.get('role')
    
    # Only admins can delete teams
    if role_claim != 'admin':
        return jsonify({"msg": "Admin only"}), 403
        
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"msg": "Team not found"}), 404
        
    db.session.delete(team)
    db.session.commit()
    return jsonify({"msg": "Team deleted"}), 200

"""Add a user to a team (Admin/Manager only - Manager only for their teams)"""
@teams_bp.route('/teams/<team_id>/users', methods=['POST'])
@jwt_required()
def add_user_to_team(team_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    user_id = claims.get('userId') or claims.get('sub')  # Backwards compatibility
    
    if not user_id:
        return jsonify({"msg": "Invalid token, please log in again"}), 401
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"msg": "Team not found"}), 404
    
    # Managers can only add users to teams they are assigned to
    if role_claim == 'manager':
        manager = User.query.get(user_id)
        if not manager or team not in manager.teams:
            return jsonify({"msg": "You can only add users to teams you are assigned to"}), 403
        
    data = request.get_json()
    user_email = data.get('email')
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    if user not in team.users:
        team.users.append(user)
        db.session.commit()
        
    return jsonify({"msg": "User added to team"}), 200

"""Remove a user from a team (Admin/Manager only - Manager only for their teams)"""
@teams_bp.route('/teams/<team_id>/users', methods=['DELETE'])
@jwt_required()
def remove_user_from_team(team_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    user_id = claims.get('userId') or claims.get('sub')  # Backwards compatibility
    
    if not user_id:
        return jsonify({"msg": "Invalid token, please log in again"}), 401
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"msg": "Team not found"}), 404
    
    # Managers can only remove users from teams they are assigned to
    if role_claim == 'manager':
        manager = User.query.get(user_id)
        if not manager or team not in manager.teams:
            return jsonify({"msg": "You can only remove users from teams you are assigned to"}), 403
        
    data = request.get_json()
    user_email = data.get('email')
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    if user in team.users:
        team.users.remove(user)
        db.session.commit()
        
    return jsonify({"msg": "User removed from team"}), 200
