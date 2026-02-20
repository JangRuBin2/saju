from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Anthropic
    anthropic_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM
    llm_model: str = "claude-sonnet-4-5-20250514"
    llm_temperature: float = 0.4
    llm_max_tokens: int = 3000

    # Cache TTL (seconds)
    cache_ttl_calculation: int = 86400  # 24 hours
    cache_ttl_interpretation: int = 3600  # 1 hour
    cache_ttl_fortune: int = 86400  # until end of target date


settings = Settings()
