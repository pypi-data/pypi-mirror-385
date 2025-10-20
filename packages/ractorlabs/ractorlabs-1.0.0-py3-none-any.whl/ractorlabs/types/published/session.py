# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Session"]


class Session(BaseModel):
    busy_from: Optional[datetime] = None

    busy_timeout_seconds: Optional[int] = None

    context_cutoff_at: Optional[datetime] = None

    created_at: Optional[datetime] = None

    created_by: Optional[str] = None

    description: Optional[str] = None

    idle_from: Optional[datetime] = None

    idle_timeout_seconds: Optional[int] = None

    is_published: Optional[bool] = None

    last_activity_at: Optional[datetime] = None

    last_context_length: Optional[int] = None

    metadata: Optional[object] = None

    name: Optional[str] = None

    parent_session_name: Optional[str] = None

    publish_permissions: Optional[object] = None

    published_at: Optional[datetime] = None

    published_by: Optional[str] = None

    state: Optional[Literal["init", "idle", "busy", "slept"]] = None
    """Session lifecycle state"""

    tags: Optional[List[str]] = None
