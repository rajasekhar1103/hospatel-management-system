from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
from celery import Celery
from config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
redis_client = FlaskRedis()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
