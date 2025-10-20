# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["SessionUpdateStateParams"]


class SessionUpdateStateParams(TypedDict, total=False):
    state: Literal["init", "idle", "busy", "slept"]
    """New session state"""
