from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])

    data = request.get_json()
    user.full_name = data.get('full_name', user.full_name)
    user.phone = data.get("phone", user.phone)
    

    db.session.commit()
    return jsonify(message='Profile updated successfully'), 200