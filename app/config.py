"""
Application Configuration
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'swim-receipt-secret-key-2026'

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Application settings
    RECEIPT_PREFIX = 'SWIM'
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'data', 'swim_dev.db')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # Get DATABASE_URL from environment (Zeabur PostgreSQL)
    # Zeabur uses postgres:// but SQLAlchemy requires postgresql://
    _database_url = os.environ.get('DATABASE_URL')
    if _database_url and _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql://', 1)

    # Use PostgreSQL if DATABASE_URL is set, otherwise fallback to SQLite
    SQLALCHEMY_DATABASE_URI = _database_url or 'sqlite:////tmp/swim.db'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
