# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["FileGetMetadataResponse"]


class FileGetMetadataResponse(BaseModel):
    kind: Optional[Literal["file", "dir", "symlink"]] = None

    link_target: Optional[str] = None

    mode: Optional[str] = None
    """octal permissions, e.g., 0644"""

    mtime: Optional[datetime] = None

    size: Optional[int] = None
