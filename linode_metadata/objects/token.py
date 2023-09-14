from datetime import datetime
from dataclasses import dataclass


@dataclass
class MetadataToken:
    token: str
    expiry_seconds: int
    created: datetime