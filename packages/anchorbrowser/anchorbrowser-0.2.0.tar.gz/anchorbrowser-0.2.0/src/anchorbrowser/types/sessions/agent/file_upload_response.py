# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["FileUploadResponse", "Data"]


class Data(BaseModel):
    message: Optional[str] = None

    status: Optional[str] = None


class FileUploadResponse(BaseModel):
    data: Optional[Data] = None
