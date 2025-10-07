import os
class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")