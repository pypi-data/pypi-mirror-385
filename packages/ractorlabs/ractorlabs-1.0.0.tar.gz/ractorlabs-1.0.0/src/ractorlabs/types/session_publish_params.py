# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SessionPublishParams"]


class SessionPublishParams(TypedDict, total=False):
    code: bool

    content: bool

    env: bool
