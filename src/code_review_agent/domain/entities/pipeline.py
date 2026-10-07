from dataclasses import dataclass
from datetime import datetime

@dataclass
class Pipeline:
    id: int
    status: str
    source: str
    ref: str
    created_at: datetime
    web_url: str
