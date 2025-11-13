import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    PORT = int(os.getenv("PORT", 8000))
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


settings = Settings()
