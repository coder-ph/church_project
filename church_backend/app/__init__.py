from flask import Flask
from .extensions import db, migrate
from .routes import init_routes
from .config.settings import config
from flask_jwt_extended import JWTManager
from .utils.logger import setup_logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger()

def create_app():
    app = Flask(__name__)
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config[env])
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)

    init_routes(app)
    
    from .routes.main import main_bp
    from .routes.oauth import google_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(google_bp, url_prefix='/login')
    
    logger.info("app initialized with env: %s", env)
    return app