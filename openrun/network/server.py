from fastapi import FastAPI, Request
from starlette.middleware.gzip import GZipMiddleware
from openrun.api.routes import router as api_router
from openrun.core.state import global_state
from openrun import __version__
import logging

# Set up access logger for warnings/errors
logger = logging.getLogger("openrun.access")
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('\033[93m[%(levelname)s]\033[0m %(message)s'))
logger.addHandler(handler)

def create_app() -> FastAPI:
    app = FastAPI(title="OpenRun API", version=__version__)

    # Compress all responses ≥500 bytes (60-80% smaller payloads over tunnels)
    app.add_middleware(GZipMiddleware, minimum_size=500)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import time
        import sys
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Detailed errors (400+) show up as WARNING
        if response.status_code >= 400:
            # Print a newline to clear the in-place log before showing the error
            sys.stdout.write("\n")
            logger.warning(f"Request: {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        # Detailed successes show up as INFO and update in-place with VRAM/RAM stats
        else:
            try:
                from openrun.cli.master import get_hardware_specs
                specs = get_hardware_specs()
                
                ram_used = (specs["total_ram"] - specs["free_ram"]) / (1024**3)
                ram_total = specs["total_ram"] / (1024**3)
                stats_str = f"RAM: {ram_used:.2f}/{ram_total:.2f} GB"
                
                if specs["gpu_available"]:
                    vram_used = (specs["total_vram"] - specs["free_vram"]) / (1024**3)
                    vram_total = specs["total_vram"] / (1024**3)
                    stats_str += f" | VRAM: {vram_used:.2f}/{vram_total:.2f} GB"
            except Exception:
                stats_str = "Stats: N/A"
                
            # Write in-place to avoid filling up the console scrollback on successful hits
            log_msg = f"\r\033[90m[INFO] {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms) | {stats_str}\033[0m\033[K"
            sys.stdout.write(log_msg)
            sys.stdout.flush()
            
        return response

    @app.get("/")
    async def root():
        model_name = None
        if global_state.adapter and hasattr(global_state.adapter, 'model_name'):
            model_name = global_state.adapter.model_name
        elif global_state.config and global_state.config.model:
            model_name = global_state.config.model

        return {
            "message": "🚀 OpenRun API is running",
            "status": "online",
            "model": model_name,
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
    
    # Custom OpenAPI schema to enable bearer padlock authorization in Swagger UI (/docs)
    from fastapi.openapi.utils import get_openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="OpenRun API",
            version=__version__,
            description="OpenRun - Expose any local AI model as an OpenAI-compatible API.",
            routes=app.routes,
        )
        openapi_schema["components"] = openapi_schema.get("components", {})
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "Bearer Token",
                "description": "Enter your OpenRun API Key (Authorization: Bearer <key>) to authorize requests."
            }
        }
        
        # Add security requirement to matching endpoints requiring authorization
        secured_prefixes = [
            "/v1/chat/completions",
            "/v1/chats",
            "/v1/metrics",
            "/v1/models/load",
            "/models/load"
        ]
        for path, path_item in openapi_schema["paths"].items():
            if any(path.startswith(prefix) for prefix in secured_prefixes):
                for method in path_item.values():
                    method["security"] = [{"bearerAuth": []}]
                    
        app.openapi_schema = openapi_schema
        return openapi_schema

    app.openapi = custom_openapi
    
    return app
