from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')
    
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.wallet import wallet_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp
    from app.routes.superadmin import superadmin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(superadmin_bp, url_prefix='/superadmin')
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/bucoinmarket.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('BuCoinMarket startup')
    
    return app
