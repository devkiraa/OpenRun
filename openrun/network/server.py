from fastapi import FastAPI, Request
from openrun.api.routes import router as api_router
from openrun.core.state import global_state
import importlib.metadata
import logging

try:
    __version__ = importlib.metadata.version('openrun-llm')
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

# Set up access logger for warnings/errors
logger = logging.getLogger("openrun.access")
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('\033[93m[%(levelname)s]\033[0m %(message)s'))
logger.addHandler(handler)

def create_app() -> FastAPI:
    app = FastAPI(title="OpenRun API", version=__version__)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import time
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Detailed errors (400+) show up as WARNING
        if response.status_code >= 400:
            logger.warning(f"Request: {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        # Detailed successes show up as INFO
        else:
            # Uvicorn hides INFO when log_level="warning", so we bypass with our logger if we want.
            # But the user asked for "detailed logs too" so let's log the successful ones too.
            print(f"\033[90m[INFO] {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)\033[0m")
            
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
        model_name = "unknown"
        if global_state.adapter and hasattr(global_state.adapter, 'model_name'):
            model_name = global_state.adapter.model_name
        elif global_state.config and global_state.config.model:
            model_name = global_state.config.model
            
        return {
            "status": "ok",
            "service": "OpenRun API",
            "version": __version__,
            "model": model_name
        }

    # Include the OpenAI-compatible routes
    app.include_router(api_router)
    
    return app
