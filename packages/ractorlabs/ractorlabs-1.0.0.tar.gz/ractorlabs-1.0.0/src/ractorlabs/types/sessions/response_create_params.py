# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ResponseCreateParams"]


class ResponseCreateParams(TypedDict, total=False):
    input: Required[object]
    """Recommended: { content: [{ type: 'text', content: string }] }"""

    background: bool
