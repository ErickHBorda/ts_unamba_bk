from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str = ""
    DB_NAME: str
    SECRET_KEY: str

    # JWT
    SECRET_KEY:                  str
    ALGORITHM:                   str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Almacenamiento local
    STORAGE_DIR:       Path = BASE_DIR / "storage"
    RESOLUCIONES_DIR:  Path = BASE_DIR / "storage" / "resoluciones"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"

settings = Settings()

# Crear directorios si no existen
settings.STORAGE_DIR.mkdir(exist_ok=True)
settings.RESOLUCIONES_DIR.mkdir(exist_ok=True)