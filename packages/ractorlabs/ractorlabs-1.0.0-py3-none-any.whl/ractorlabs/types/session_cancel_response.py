# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SessionCancelResponse"]


class SessionCancelResponse(BaseModel):
    cancelled: Optional[bool] = None

    session: Optional[str] = None

    status: Optional[str] = None
