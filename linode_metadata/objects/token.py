from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetadataToken:
    token: str
    expiry_seconds: int
    created: datetime
