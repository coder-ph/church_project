from flask import Blueprint, jsonify, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from app.models.user import User
from app import db
from flask_jwt_extended import create_access_token
from ..config.settings import Config
from dotenv import load_dotenv
load_dotenv()
import os

google_bp = make_google_blueprint(
    client_id = Config.GOOGLE_OAUTH_CLIENT_ID,
    client_secret = Config.GOOGLE_OAUTH_CLIENT_SECRET,
    scope = ['profile', 'email'],
    redirect_to="auth.oauth_callback"
)
oauth_bp = Blueprint("/auth", __name__)
@oauth_bp.route("/auth/callback")
def oauth_callback():
    resp = google.get('/oauth2/v2/userinfo')
    info = resp.json()
    email = info['email']

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email = email,
            full_name = info.get('name',email.split('@')[0]),
            role = "member"
        )
        db.session.add(user)
        db.session.commit()

    token = create_access_token(identity={'id': user.id, 'role':user.role})
    return jsonify(token=token, user={"name": user.full_name, "email": user.email})