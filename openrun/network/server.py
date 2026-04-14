from fastapi import FastAPI, Request
from openrun.api.routes import router as api_router
import logging

# Set up access logger for warnings/errors
logger = logging.getLogger("openrun.access")
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('\033[93m[%(levelname)s]\033[0m %(message)s'))
logger.addHandler(handler)

def create_app() -> FastAPI:
    app = FastAPI(title="OpenRun API", version="0.1.0")

    @app.middleware("http")
    async def log_errors(request: Request, call_next):
        response = await call_next(request)
        if response.status_code >= 400:
            logger.warning(f"Request: {request.method} {request.url.path} - Status: {response.status_code}")
        return response

    @app.get("/")
    async def root():
        return {
            "message": "🚀 OpenRun API is running",
            "status": "online",
            "docs": "/docs",
            "endpoints": {
                "chat": "/v1/chat/completions",
                "health": "/health"
            }
        }

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "OpenRun API",
            "version": "0.1.0"
        }

    # Include the OpenAI-compatible routes
    app.include_router(api_router)
    
    return app
