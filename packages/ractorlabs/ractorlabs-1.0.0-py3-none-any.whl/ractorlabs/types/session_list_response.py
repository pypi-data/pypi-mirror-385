# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .published.session import Session

__all__ = ["SessionListResponse"]


class SessionListResponse(BaseModel):
    items: Optional[List[Session]] = None

    limit: Optional[int] = None

    offset: Optional[int] = None

    page: Optional[int] = None

    pages: Optional[int] = None

    total: Optional[int] = None
