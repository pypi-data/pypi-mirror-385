# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Operator"]


class Operator(BaseModel):
    active: Optional[bool] = None

    created_at: Optional[datetime] = None

    description: Optional[str] = None

    last_login_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None

    user: Optional[str] = None
