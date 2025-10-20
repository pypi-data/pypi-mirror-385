# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["LoginResponse"]


class LoginResponse(BaseModel):
    token: Optional[str] = None

    expires_at: Optional[datetime] = None

    role: Optional[Literal["user", "admin"]] = None

    token_type: Optional[Literal["Bearer"]] = None

    user: Optional[str] = None
