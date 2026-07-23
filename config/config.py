import os
from datetime import timedelta

class Config:
    # Database - use environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # Security - Disable CSRF for now
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this')
    WTF_CSRF_ENABLED = False  # Disable CSRF protection
    WTF_CSRF_CHECK_DEFAULT = False  # Don't check CSRF by default
    
    SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # BuCoin settings
    BUC_EXCHANGE_RATE = float(os.environ.get('BUC_EXCHANGE_RATE', 1.00))
    
    # File uploads
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Logging
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')
    
    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
