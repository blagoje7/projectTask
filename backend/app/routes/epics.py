from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..models import db, Epic, Project

epics_bp = Blueprint('epics', __name__)

"""Get all epics for a project"""
@epics_bp.route('/projects/<project_id>/epics', methods=['GET'])
@jwt_required()
def get_epics(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    epics = Epic.query.filter_by(project_id=project_id).all()
    return jsonify([e.to_dict() for e in epics]), 200

"""Create a new epic in a project (Admin/Manager only)"""
@epics_bp.route('/projects/<project_id>/epics', methods=['POST'])
@jwt_required()
def create_epic(project_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"msg": "Epic name is required"}), 400
    
    epic = Epic(
        name=name,
        description=description,
        project_id=project_id
    )
    
    db.session.add(epic)
    db.session.commit()
    
    return jsonify(epic.to_dict()), 201

"""Update an epic (Admin/Manager only)"""
@epics_bp.route('/epics/<epic_id>', methods=['PUT'])
@jwt_required()
def update_epic(epic_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    epic = Epic.query.get(epic_id)
    if not epic:
        return jsonify({"msg": "Epic not found"}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        epic.name = data['name']
    if 'description' in data:
        epic.description = data['description']
    
    db.session.commit()
    return jsonify(epic.to_dict()), 200

"""Delete an epic (Admin/Manager only)"""
@epics_bp.route('/epics/<epic_id>', methods=['DELETE'])
@jwt_required()
def delete_epic(epic_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    epic = Epic.query.get(epic_id)
    if not epic:
        return jsonify({"msg": "Epic not found"}), 404
    
    db.session.delete(epic)
    db.session.commit()
    
    return jsonify({"msg": "Epic deleted"}), 200
