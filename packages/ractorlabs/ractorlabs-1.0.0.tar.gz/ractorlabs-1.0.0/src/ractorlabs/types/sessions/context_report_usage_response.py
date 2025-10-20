# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ContextReportUsageResponse"]


class ContextReportUsageResponse(BaseModel):
    last_context_length: Optional[int] = None

    success: Optional[bool] = None
