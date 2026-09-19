import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    FLASK_ENV = os.getenv("FLASK_ENV", "development").strip().lower()
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:3000").strip()

    MAX_MESSAGE_LENGTH = 5000
    MAX_HISTORY_MESSAGES = 20
    GROQ_TIMEOUT = 30.0


settings = Settings()
