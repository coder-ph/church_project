import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQL_ALCHEMY_TRACK_MODOFOCATIONS = False

    JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY")

class DevelopmentConfig:
    DEBUG = True

class ProductionConfig:
    DEBUG = True

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}