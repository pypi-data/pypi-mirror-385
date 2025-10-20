# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["ResponseView"]


class ResponseView(BaseModel):
    id: Optional[str] = None

    created_at: Optional[datetime] = None

    input_content: Optional[List[object]] = None

    output_content: Optional[List[object]] = None

    segments: Optional[List[object]] = None

    session_name: Optional[str] = None

    status: Optional[str] = None

    updated_at: Optional[datetime] = None
