# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["BatchSessionCreateResponse", "Data"]


class Data(BaseModel):
    batch_id: Optional[str] = None
    """Unique identifier for the batch"""

    created_at: Optional[datetime] = None
    """Timestamp when the batch was created"""

    status: Optional[Literal["pending", "processing", "completed", "failed"]] = None
    """Current status of the batch"""

    total_requests: Optional[int] = None
    """Total number of sessions requested in the batch"""


class BatchSessionCreateResponse(BaseModel):
    data: Optional[Data] = None
