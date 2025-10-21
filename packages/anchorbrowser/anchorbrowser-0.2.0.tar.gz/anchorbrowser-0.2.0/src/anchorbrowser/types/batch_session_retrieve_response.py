# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["BatchSessionRetrieveResponse", "Data", "DataProgress", "DataSession"]


class DataProgress(BaseModel):
    current_phase: Optional[Literal["queued", "provisioning", "configuring", "ready"]] = None
    """Current processing phase"""

    percentage: Optional[float] = None
    """Completion percentage (0-100)"""


class DataSession(BaseModel):
    cdp_url: Optional[str] = None
    """CDP websocket connection URL (if session is ready)"""

    completed_at: Optional[datetime] = None
    """Timestamp when session creation completed"""

    error: Optional[str] = None
    """Error message if session creation failed"""

    item_index: Optional[int] = None
    """Index of this session within the batch (0-based)"""

    live_view_url: Optional[str] = None
    """Live view URL for the session (if session is ready)"""

    metadata: Optional[Dict[str, object]] = None
    """Session-specific metadata"""

    retry_count: Optional[int] = None
    """Number of times this session creation has been retried"""

    session_id: Optional[str] = None
    """Unique identifier for the browser session (if created successfully)"""

    started_at: Optional[datetime] = None
    """Timestamp when session creation started"""

    status: Optional[Literal["pending", "processing", "completed", "failed"]] = None
    """Current status of this individual session"""


class Data(BaseModel):
    actual_completion_time: Optional[datetime] = None
    """Timestamp when the batch completed (if completed)"""

    batch_id: Optional[str] = None
    """Unique identifier for the batch"""

    completed_requests: Optional[int] = None
    """Number of sessions successfully created"""

    created_at: Optional[datetime] = None
    """Timestamp when the batch was created"""

    error: Optional[str] = None
    """Error message if batch failed"""

    failed_requests: Optional[int] = None
    """Number of sessions that failed to create"""

    pending_requests: Optional[int] = None
    """Number of sessions waiting to be processed"""

    processing_requests: Optional[int] = None
    """Number of sessions currently being processed"""

    progress: Optional[DataProgress] = None

    sessions: Optional[List[DataSession]] = None
    """Array of individual session details"""

    status: Optional[Literal["pending", "processing", "completed", "failed"]] = None
    """Current status of the batch"""

    total_requests: Optional[int] = None
    """Total number of sessions requested"""


class BatchSessionRetrieveResponse(BaseModel):
    data: Optional[Data] = None
