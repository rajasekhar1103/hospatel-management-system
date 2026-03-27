import os

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-123'
    # SQLite Setup
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings (Example)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-super-secret'

    # Redis and Celery Setup
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL