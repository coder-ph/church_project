from flask import Flask
from .extensions import db, migrate
from .config.settings import config
from app.routes.main import main_bp
import os

def create_app():
    app = Flask(__name__)
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config[env])

    db.init_app(app)
    migrate.init_app(app, db)

    
    app.register_blueprint(main_bp)

    return app