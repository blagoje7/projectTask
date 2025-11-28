"""
Utility functions for the application
"""
from flask import jsonify
from flask_jwt_extended import get_jwt

def get_current_user_id():
    """
    Extract user ID from JWT token with backwards compatibility
    Returns user_id or None
    """
    claims = get_jwt()
    return claims.get('userId') or claims.get('sub')

def get_current_user_role():
    """
    Extract user role from JWT token
    Returns role name or None
    """
    claims = get_jwt()
    return claims.get('role')

def success_response(data, status_code=200):
    """
    Standard success response
    """
    return jsonify(data), status_code

def error_response(message, status_code=400):
    """
    Standard error response
    """
    return jsonify({"msg": message}), status_code

def validate_user_id(user_id):
    """
    Validate that user_id exists from token
    Returns error response if invalid, None otherwise
    """
    if not user_id:
        return error_response("Invalid token, please log in again", 401)
    return None

def check_role(role, allowed_roles):
    """
    Check if user role is in allowed roles
    Returns error response if unauthorized, None otherwise
    """
    if role not in allowed_roles:
        return error_response("Unauthorized", 403)
    return None
