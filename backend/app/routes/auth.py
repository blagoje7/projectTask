"""
Authentication Routes.
Handles user login, registration, and password management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from ..models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    print(f"Login attempt for: {email}")
    
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"User found: {user.email}")
        if user.check_password(password):
            print("Password check passed")
            access_token = create_access_token(identity=user.user_id, additional_claims={'role': user.role.name, 'email': user.email})
            return jsonify(
                access_token=access_token, 
                role=user.role.name,
                userId=user.user_id,
                username=f"{user.first_name} {user.last_name}"
            ), 200
        else:
            print("Password check failed")
    else:
        print("User not found")
    
    return jsonify({"msg": "Bad email or password"}), 401

"""Verify JWT token and return user information for other services"""
@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    return jsonify({
        "userId": user.user_id,
        "email": user.email,
        "role": user.role.name,
        "isActive": user.is_active
    }), 200

"""Send password reset email (mock implementation)"""
@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Mock email sending
        print(f"Sending password reset email to {email}")
        return jsonify({"msg": "Password reset email sent"}), 200
    
    # Return 200 even if user not found to prevent enumeration
    return jsonify({"msg": "Password reset email sent"}), 200

"""Check if email exists for password reset"""
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"msg": "Email not found"}), 404
    
    return jsonify({"msg": "User found"}), 200

"""Update user password"""
@auth_bp.route('/update-password', methods=['POST'])
def update_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('newPassword')
    
    if not new_password or len(new_password) < 6:
        return jsonify({"msg": "Password must be at least 6 characters"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    user.set_password(new_password)
    db.session.commit()
    
    print(f"Password updated for {email}")
    return jsonify({"msg": "Password updated successfully"}), 200
