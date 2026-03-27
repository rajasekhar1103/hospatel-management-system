from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(roles):
    """Custom decorator to check if the current user has one of the required roles."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in roles:
                return jsonify(msg=f"Access forbidden: Requires role(s) {', '.join(roles)}"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper