"""App configuration from environment."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    # Azure AI Foundry (OpenAI-compatible)
    azure_api_key: str = ""
    azure_base_endpoint: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_url, "http://127.0.0.1:3000"]

    @property
    def azure_ai_configured(self) -> bool:
        return bool(self.azure_api_key and self.azure_base_endpoint)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
