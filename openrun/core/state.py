from typing import Any, Optional
from openrun.core.config import Config

class AppState:
    def __init__(self):
        self.config: Optional[Config] = None
        self.model: Optional[Any] = None
        self.adapter: Optional[Any] = None

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
