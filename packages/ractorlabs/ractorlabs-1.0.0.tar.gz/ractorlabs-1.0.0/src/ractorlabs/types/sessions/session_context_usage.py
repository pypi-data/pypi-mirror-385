# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["SessionContextUsage"]


class SessionContextUsage(BaseModel):
    basis: Optional[str] = None

    cutoff_at: Optional[datetime] = None

    measured_at: Optional[datetime] = None

    session: Optional[str] = None

    soft_limit_tokens: Optional[int] = None

    total_messages_considered: Optional[int] = None

    used_percent: Optional[float] = None

    used_tokens_estimated: Optional[int] = None
