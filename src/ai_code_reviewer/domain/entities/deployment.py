from dataclasses import dataclass
from datetime import datetime

@dataclass
class Deployment:
    id: int
    status: str
    created_at: datetime
