# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["BlocklistListResponse", "BlocklistListResponseItem"]


class BlocklistListResponseItem(BaseModel):
    created_at: Optional[datetime] = None

    principal: Optional[str] = None

    principal_type: Optional[Literal["User", "Admin"]] = None


BlocklistListResponse: TypeAlias = List[BlocklistListResponseItem]
