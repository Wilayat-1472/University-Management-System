import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "University Management System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Database - Switch to PostgreSQL by changing this URL
    # PostgreSQL: "postgresql://ums_user:ums_password@localhost:5432/ums_db"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ums.db"
    )

    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ums-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
