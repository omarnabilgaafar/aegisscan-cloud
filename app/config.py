import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "scanner.db")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 5))
    MAX_LINKS_TO_SCAN = int(os.getenv("MAX_LINKS_TO_SCAN", 20))
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in {"1", "true", "yes", "on"}

    ALLOWED_HOSTS = [
        host.strip().lower()
        for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
        if host.strip()
    ]