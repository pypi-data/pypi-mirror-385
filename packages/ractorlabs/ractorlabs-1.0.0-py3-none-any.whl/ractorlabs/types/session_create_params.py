# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["SessionCreateParams"]


class SessionCreateParams(TypedDict, total=False):
    name: Required[str]

    busy_timeout_seconds: Optional[int]

    description: Optional[str]

    env: Dict[str, str]

    idle_timeout_seconds: Optional[int]

    instructions: Optional[str]

    metadata: object

    prompt: Optional[str]

    setup: Optional[str]

    tags: SequenceNotStr[str]
