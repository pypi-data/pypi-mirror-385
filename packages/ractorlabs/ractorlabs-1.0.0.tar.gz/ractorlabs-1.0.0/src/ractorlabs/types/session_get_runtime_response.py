# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SessionGetRuntimeResponse"]


class SessionGetRuntimeResponse(BaseModel):
    current_session_seconds: Optional[int] = None

    session_name: Optional[str] = None

    total_runtime_seconds: Optional[int] = None
