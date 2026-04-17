from typing import Any, Optional
from openrun.core.config import Config

class AppState:
    def __init__(self):
        self.config: Optional[Config] = None
        self.model: Optional[Any] = None
        self.adapter: Optional[Any] = None
        self.loading_status: str = "idle"
        self.loading_model_key: Optional[str] = None
        self.loading_error: Optional[str] = None
        self.loading_stage: Optional[str] = None
        self.loading_message: Optional[str] = None
        self.loading_progress: int = 0
        self.loading_started_at: Optional[float] = None
        self.loading_updated_at: Optional[float] = None
        self.chats: dict[str, dict[str, Any]] = {}
        self.chat_order: list[str] = []
        self.active_chat_id: Optional[str] = None
        self.latest_metrics: Optional[dict[str, Any]] = None
        self.metrics_history: list[dict[str, Any]] = []
        self.metrics_totals: dict[str, float] = {
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "total_seconds": 0.0,
        }

# Global state instance
global_state = AppState()

def set_global_state(config: Optional[Config] = None, model: Optional[Any] = None, adapter: Optional[Any] = None):
    if config is not None:
        global_state.config = config
    if model is not None:
        global_state.model = model
    if adapter is not None:
        global_state.adapter = adapter

def get_global_state() -> AppState:
    return global_state
