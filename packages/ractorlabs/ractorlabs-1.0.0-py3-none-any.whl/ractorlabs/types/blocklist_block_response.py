# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BlocklistBlockResponse"]


class BlocklistBlockResponse(BaseModel):
    blocked: Optional[bool] = None

    created: Optional[bool] = None
