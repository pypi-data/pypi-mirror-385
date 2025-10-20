# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["BlocklistBlockParams"]


class BlocklistBlockParams(TypedDict, total=False):
    principal: Required[str]

    type: Optional[Literal["User", "Admin"]]
