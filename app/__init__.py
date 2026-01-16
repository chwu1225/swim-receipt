"""
Swimming Pool Receipt System - Flask Application (Demo Mode - No Login Required)
"""
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()


class DemoUser:
    """Demo user with full permissions (no login required)"""
    id = 1
    username = 'demo'
    full_name = '展示用戶'
    role = 'admin'
    is_active = True
    is_authenticated = True
    is_anonymous = False

    def get_id(self):
        return str(self.id)

    def can_create_receipt(self):
        return True

    def can_approve_void(self):
        return True

    def can_verify_receipt(self):
        return True

    def can_manage_users(self):
        return True

    def can_manage_fee_items(self):
        return True

    def can_export_reports(self):
        return True

    @property
    def role_display(self):
        return '展示模式'


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Demo mode: always return demo user
    @login_manager.user_loader
    def load_user(user_id):
        return DemoUser()

    # Inject demo user into all requests
    @app.before_request
    def before_request():
        g.user = DemoUser()

    # Make demo user available in templates
    @app.context_processor
    def inject_user():
        return dict(current_user=DemoUser())

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.receipt import receipt_bp
    from app.routes.report import report_bp
    from app.routes.verify import verify_bp
    from app.routes.void import void_bp
    from app.routes.admin import admin_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(receipt_bp, url_prefix='/receipt')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(verify_bp, url_prefix='/verify')
    app.register_blueprint(void_bp, url_prefix='/void')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create database tables
    with app.app_context():
        db.create_all()
        # Initialize default data
        from app.services.init_service import init_default_data
        init_default_data()

    return app


# Create app instance for gunicorn (Zeabur default: gunicorn app:app)
# Use FLASK_ENV environment variable, default to 'production' for cloud deployment
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)
