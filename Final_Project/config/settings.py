from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    upload_dir_str: str = "static/uploads"  # Default upload directory string
    query_image_dir_str: str = "static/query_images" # Default query image dir string
    cors_allow_origins: list[str] = ["http://localhost:5173"] # Default CORS origins
    gemini_api_key: str  # Expecting gemini_api_key
    gemini_model: str = "gemini-2.0-flash"
    @property
    def upload_dir(self) -> Path:
        return Path(self.upload_dir_str)

    @property
    def query_image_dir(self) -> Path:
        return Path(self.query_image_dir_str)


    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file in project root
        env_file_encoding="utf-8"
    )

settings = Settings() # Create a settings instance

if __name__ == "__main__":
    print(f"Upload Directory: {settings.upload_dir}")
    print(f"Query Image Directory: {settings.query_image_dir}")
    print(f"CORS Allow Origins: {settings.cors_allow_origins}")