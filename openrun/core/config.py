from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    model: Optional[str] = None
    file: Optional[str] = None
    port: int = 8000
    public: bool = False
    api_key: Optional[str] = None
