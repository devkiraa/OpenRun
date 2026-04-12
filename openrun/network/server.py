from fastapi import FastAPI
from openrun.api.routes import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(title="OpenRun API", version="0.1.0")

    @app.get("/")
    async def root():
        return {
            "message": "🚀 OpenRun API is running",
            "endpoint": "/v1/chat/completions"
        }

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Include the OpenAI-compatible routes
    app.include_router(api_router)
    
    return app
