from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TZ_", env_file=".env", extra="ignore")

    app_name: str = "kits4kid-triple-zero"
    env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000

    # Zero-Token / MoM
    semantic_cache_threshold: float = 0.86
    default_model_tier: str = "local_small"
    enable_compiled_paths: bool = True

    # vLLM multi-head fabric (OpenAI-compatible)
    vllm_base_url: str = "http://127.0.0.1:8001"
    vllm_frontier_base_url: str | None = None
    vllm_classifier_model: str = "router-bert-tiny"
    vllm_router_model: str = "router-bert-tiny"
    vllm_small_model: str = "meta-llama/Llama-3.2-3B-Instruct"
    vllm_large_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    vllm_creator_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    vllm_critic_model: str = "meta-llama/Llama-3.2-3B-Instruct"
    vllm_compiler_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    vllm_frontier_model: str = "openai/gpt-oss-proxy"

    # Zero-Trust
    deny_by_default: bool = True
    require_parent_approve: bool = True
    max_agent_tool_calls: int = 12

    # Zero-Copy
    object_store_backend: str = "memory"  # memory | ray
    max_object_bytes: int = 64 * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
