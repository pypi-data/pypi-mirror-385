# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AuthRetrieveCurrentPrincipalResponse"]


class AuthRetrieveCurrentPrincipalResponse(BaseModel):
    type: Optional[Literal["User", "Admin"]] = None

    user: Optional[str] = None
