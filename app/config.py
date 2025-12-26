from __future__ import annotations
from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "QR Code API"
    require_api_key: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("1", "true", "yes", "y")
    rapidapi_proxy_secret: str | None = os.getenv("RAPIDAPI_PROXY_SECRET") or None
    require_rapidapi_proxy_secret: bool = os.getenv("REQUIRE_RAPIDAPI_PROXY_SECRET", "false").lower() in ("1","true","yes","y")
    api_keys: list[str] = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
    # If require_api_key is True and api_keys is empty, all requests will be rejected.

    cors_allow_origins: list[str] = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()]

settings = Settings()
