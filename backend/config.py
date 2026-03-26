"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from `backend/.env` explicitly so that
# the app works regardless of the current working directory.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError(
            "Missing DATABASE_URL. Make sure it is set in `backend/.env`."
        )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
