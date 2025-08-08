from flask import Flask
from .extensions import db, migrate, jwt
from .config.settings import config
from .utils.logger import setup_logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger()

def create_app(config_name=None):
    app = Flask(__name__)
    env = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config[env])
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

   
    from .routes import init_routes
    init_routes(app)
    
    logger.info("app initialized with env: %s", env)
    return app