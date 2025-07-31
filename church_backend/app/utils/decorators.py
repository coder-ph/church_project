from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps
from flask import jsonify

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if identity['role'] not in roles:
                return jsonify(message="User Unauthorized"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper