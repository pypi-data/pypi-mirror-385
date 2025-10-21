# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["EventWaitForResponse"]


class EventWaitForResponse(BaseModel):
    data: Optional[Dict[str, object]] = None
    """The event data that was signaled"""
