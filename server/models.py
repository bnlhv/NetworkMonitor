""" Models module """
import time
from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class NIC(Document):
    """ The NIC (Network Interface Card) db document model """
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(default="default_nic")

    class Config:
        schema_extra = {
            "example": {
                "id": uuid4(),
                "name": "eth0",
            }
        }


class BandwidthSample(Document):
    """ The Bandwidth test document model """
    id: UUID = Field(default_factory=uuid4)
    nic_name: str
    upload: float = Field(default=0.0)
    download: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "id": uuid4(),
                "nic_name": "eth0",
                "upload": 0.0,
                "download": 0.0,
                "timestamp": time.time(),
            }
        }
