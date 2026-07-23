import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    # Get the absolute path to the PROJECT root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Explicitly set template and static folders
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # Create the Flask app with explicit paths
    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir,
                static_url_path='/static')
    
    app.config.from_object('config.config.Config')
    
    # Mail settings
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Define user_loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Import and register blueprints
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
    
    # Create upload folder
    upload_folder = os.path.join(base_dir, 'static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Setup logging
    if not app.debug:
        log_dir = os.path.join(base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'bucoinmarket.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        # Log important paths
        app.logger.info(f'Base directory: {base_dir}')
        app.logger.info(f'Template folder: {template_dir}')
        app.logger.info(f'Static folder: {static_dir}')
        app.logger.info(f'Templates exist: {os.path.exists(template_dir)}')
        if os.path.exists(template_dir):
            app.logger.info(f'Template files: {os.listdir(template_dir)}')
    
    return app
