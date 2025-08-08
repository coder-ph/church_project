from flask import Blueprint
from .auth import auth_bp
from .users import user_bp
from .branch import branch_bp
from .contributions import event_contrib_bp
from .events import event_bp
from .mpesa import mpesa_bp
from .oauth import oauth_bp
from .password_reset import reset_bp
from .social_serv import social_bp

routes_bp = Blueprint('routes', __name__)

def  init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(event_contrib_bp)
    app.register_blueprint(mpesa_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(reset_bp)
    app.register_blueprint(social_bp)
    