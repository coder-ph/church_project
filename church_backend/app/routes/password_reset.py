from flask import Blueprint, request, jsonify
from itsdangerous import URLSafeTimedSerializer
from app.models.user import User
from app import db

reset_bp =Blueprint('reset', __name__)

s = URLSafeTimedSerializer("super_secret")

@reset_bp.route('/reset/request', methods=['POST'])
def request_reset():
    email = request.get_json()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(message="Invalid user"), 404
    
    token = s.dumps(email, salt='password-reset')
    reset_url = f"https://frontend/reset{token}"
    return jsonify(message="Reset link sent to mail", token=token)

@reset_bp.route('/reset/confirm/<token>', methods=['POST'])
def reset_confirm(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except:
        return jsonify(message="Invalid or expired reset token"), 400
    
    user = User.query.filter_by(email=email).first()
    user.set_password(request.json['new_password'])
    db.session.commit()
    return jsonify(message='Password updated')