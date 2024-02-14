"""
Data classes related to Metadata Service token.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetadataToken:
    """
    A token used to access Metadata Service.
    """

    token: str
    expiry_seconds: int
    created: datetime
