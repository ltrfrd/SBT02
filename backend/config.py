# ===========================================================
# backend/config.py — Application Configuration
# -----------------------------------------------------------
# Central place for environment-based settings.
# ===========================================================

import os                                                   # Access environment variables


class Settings:
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"   # Development flag
    ENV: str = os.getenv("ENV", "development")                   # Environment name


settings = Settings()                                       # Singleton settings object