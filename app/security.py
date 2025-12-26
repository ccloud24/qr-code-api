from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Optional: RapidAPI-only lock
        if settings.require_rapidapi_proxy_secret:
            incoming = request.headers.get("X-RapidAPI-Proxy-Secret")
            if not incoming or not settings.rapidapi_proxy_secret or incoming != settings.rapidapi_proxy_secret:
                return JSONResponse(
                    status_code=401,
                    content={"error": "unauthorized", "message": "Invalid proxy secret."},
                )

        # Optional: your own API keys
        if settings.require_api_key:
            key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            if not key or key not in settings.api_keys:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "unauthorized",
                        "message": "Missing or invalid API key. Provide X-API-Key header (recommended).",
                    },
                )

        return await call_next(request)
