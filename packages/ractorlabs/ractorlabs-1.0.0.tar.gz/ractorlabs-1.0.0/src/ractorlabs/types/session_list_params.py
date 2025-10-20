# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["SessionListParams"]


class SessionListParams(TypedDict, total=False):
    limit: int

    offset: int

    page: int

    q: str

    state: str

    tags: SequenceNotStr[str]
    """Repeatable tag filter. Use tags=alpha&tags=beta."""
