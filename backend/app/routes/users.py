"""
User Routes.
Handles user management, listing, and updates.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import db, User, Role

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (Admin/Manager)"""
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim not in ['admin', 'manager']:
        return jsonify({"msg": "Admins and Managers only!"}), 403
        
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

"""Update user details (Admin only)"""
@users_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    data = request.get_json()
    if 'isActive' in data:
        user.is_active = data['isActive']
    if 'firstName' in data:
        user.first_name = data['firstName']
    if 'lastName' in data:
        user.last_name = data['lastName']
        
    db.session.commit()
    return jsonify(user.to_dict()), 200

"""Create a new user (Admin only)"""
@users_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role_claim = claims.get('role')
    print(f"Create user attempt by: {current_user_id} with role {role_claim}")
    
    if role_claim != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role_name = data.get('role')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400
    
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({"msg": "Invalid role"}), 400
        
    new_user = User(email=email, role=role, first_name=first_name, last_name=last_name)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully"}), 201

"""Get all available roles (Admin only)"""
@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    claims = get_jwt()
    role_claim = claims.get('role')
    
    if role_claim != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
        
    roles = Role.query.all()
    return jsonify([{'roleId': r.role_id, 'name': r.name} for r in roles]), 200
