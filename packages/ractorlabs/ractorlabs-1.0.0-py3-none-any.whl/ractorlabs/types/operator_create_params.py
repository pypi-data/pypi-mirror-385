# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["OperatorCreateParams"]


class OperatorCreateParams(TypedDict, total=False):
    pass_: Required[Annotated[str, PropertyInfo(alias="pass")]]

    user: Required[str]

    description: str
