import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQL_ALCHEMY_TRACK_MODOFOCATIONS = False

class DevelopmentConfig:
    DEBUG = True

class ProductionConfig:
    DEBUG = True

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}