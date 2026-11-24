from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    QDRANT_URL: str = "http://localhost:6333"
    OLLAMA_URL: str = "http://localhost:11434"
    COLLECTION: str = "microservices_shop_qwen3_06b_ollama"
    EMBEDDING_MODEL_NAME: str = "qwen3-embedding:0.6b"
    CHAT_MODEL_NAME: str = "qwen3.5:4b"

    TELEGRAM_BOT_TOKEN: SecretStr | None = None
    TELEGRAM_OWNER_ID: int | None = None