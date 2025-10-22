# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["PdfGeneratorDeleteResponse"]


class PdfGeneratorDeleteResponse(BaseModel):
    message: Optional[str] = None

    success: Optional[bool] = None
