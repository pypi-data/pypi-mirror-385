# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["SessionUpdateParams"]


class SessionUpdateParams(TypedDict, total=False):
    busy_timeout_seconds: Optional[int]

    description: Optional[str]

    idle_timeout_seconds: Optional[int]

    metadata: Optional[object]

    tags: Optional[SequenceNotStr[str]]
