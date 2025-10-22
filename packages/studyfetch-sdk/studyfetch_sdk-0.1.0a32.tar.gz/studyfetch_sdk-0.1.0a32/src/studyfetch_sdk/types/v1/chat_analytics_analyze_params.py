# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["ChatAnalyticsAnalyzeParams"]


class ChatAnalyticsAnalyzeParams(TypedDict, total=False):
    component_id: Annotated[str, PropertyInfo(alias="componentId")]
    """Component ID to analyze"""

    end_date: Annotated[Union[str, datetime], PropertyInfo(alias="endDate", format="iso8601")]
    """End date for analysis"""

    group_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="groupIds")]
    """Group IDs to filter by"""

    model_key: Annotated[str, PropertyInfo(alias="modelKey")]
    """AI model to use for analysis"""

    organization_id: Annotated[str, PropertyInfo(alias="organizationId")]
    """Organization ID to filter by"""

    start_date: Annotated[Union[str, datetime], PropertyInfo(alias="startDate", format="iso8601")]
    """Start date for analysis"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID to filter by"""
