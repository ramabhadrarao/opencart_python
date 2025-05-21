import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "OpenCart API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Secret key for JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    
    # Database settings
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "127.0.0.1")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "opencart_updated")
    DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"

settings = Settings()