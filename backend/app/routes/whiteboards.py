from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Whiteboard, Project, User

whiteboards_bp = Blueprint('whiteboards', __name__)

@whiteboards_bp.route('/projects/<project_id>/whiteboard', methods=['GET'])
@jwt_required()
def get_whiteboard(project_id):
    """Get the current whiteboard state for a project - accessible to all team members"""
    try:
        # Verify user has access to this project (is in one of the project's teams)
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user is in any of the project's teams
        user_team_ids = [team.team_id for team in user.teams]
        project_team_ids = [team.team_id for team in project.teams]
        has_access = any(tid in project_team_ids for tid in user_team_ids)
        
        if not has_access and user.role.name != 'admin':
            return jsonify({'error': 'You do not have access to this project'}), 403
        
        # Get the most recent whiteboard for this project
        whiteboard = Whiteboard.query.filter_by(project_id=project_id)\
            .order_by(Whiteboard.created_at.desc())\
            .first()
        
        if not whiteboard:
            return jsonify({'imageData': None, 'history': []}), 200
        
        # Get history (last 20 whiteboards)
        history = Whiteboard.query.filter_by(project_id=project_id)\
            .order_by(Whiteboard.created_at.desc())\
            .limit(20)\
            .all()
        
        return jsonify({
            'imageData': whiteboard.image_data,
            'history': [h.to_dict() for h in history]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whiteboards_bp.route('/projects/<project_id>/whiteboard', methods=['POST'])
@jwt_required()
def save_whiteboard(project_id):
    """Save whiteboard state for a project - accessible to all team members"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()
        
        if not data or 'imageData' not in data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user is in any of the project's teams
        user_team_ids = [team.team_id for team in user.teams]
        project_team_ids = [team.team_id for team in project.teams]
        has_access = any(tid in project_team_ids for tid in user_team_ids)
        
        if not has_access and user.role.name != 'admin':
            return jsonify({'error': 'You do not have access to this project'}), 403
        
        # Create new whiteboard entry
        whiteboard = Whiteboard(
            project_id=project_id,
            image_data=data['imageData'],
            created_by=current_user_id
        )
        
        db.session.add(whiteboard)
        db.session.commit()
        
        return jsonify({
            'message': 'Whiteboard saved successfully',
            'whiteboard': whiteboard.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@whiteboards_bp.route('/projects/<project_id>/whiteboard/history', methods=['GET'])
@jwt_required()
def get_whiteboard_history(project_id):
    """Get whiteboard history for a project - accessible to all team members"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user is in any of the project's teams
        user_team_ids = [team.team_id for team in user.teams]
        project_team_ids = [team.team_id for team in project.teams]
        has_access = any(tid in project_team_ids for tid in user_team_ids)
        
        if not has_access and user.role.name != 'admin':
            return jsonify({'error': 'You do not have access to this project'}), 403
        
        history = Whiteboard.query.filter_by(project_id=project_id)\
            .order_by(Whiteboard.created_at.desc())\
            .limit(20)\
            .all()
        
        return jsonify([h.to_dict() for h in history]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whiteboards_bp.route('/whiteboards/<whiteboard_id>', methods=['DELETE'])
@jwt_required()
def delete_whiteboard(whiteboard_id):
    """Delete a specific whiteboard entry (admin/manager only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role.name not in ['admin', 'manager']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        whiteboard = Whiteboard.query.get(whiteboard_id)
        if not whiteboard:
            return jsonify({'error': 'Whiteboard not found'}), 404
        
        db.session.delete(whiteboard)
        db.session.commit()
        
        return jsonify({'message': 'Whiteboard deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
