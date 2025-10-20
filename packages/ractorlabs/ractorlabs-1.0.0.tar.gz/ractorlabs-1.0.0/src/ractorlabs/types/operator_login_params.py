# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["OperatorLoginParams"]


class OperatorLoginParams(TypedDict, total=False):
    pass_: Required[Annotated[str, PropertyInfo(alias="pass")]]

    ttl_hours: Optional[int]
