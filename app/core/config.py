import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

print("ENV PATH:", ENV_PATH)
print("ENV EXISTS:", ENV_PATH.exists())

print("RAW DATABASE_URL:", os.environ.get("DATABASE_URL"))

class Settings:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 10080)
    )
    PROJECT_NAME = os.environ.get("PROJECT_NAME", "EmpTrackAI")

settings = Settings()

print("FINAL DATABASE_URL:", settings.DATABASE_URL)