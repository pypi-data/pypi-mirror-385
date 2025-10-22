# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ChatRetrieveFeedbackParams"]


class ChatRetrieveFeedbackParams(TypedDict, total=False):
    component_id: Annotated[str, PropertyInfo(alias="componentId")]
    """Filter by component ID"""

    end_date: Annotated[str, PropertyInfo(alias="endDate")]
    """Filter by end date (ISO string)"""

    feedback_type: Annotated[Literal["thumbsUp", "thumbsDown"], PropertyInfo(alias="feedbackType")]
    """Filter by feedback type"""

    limit: str
    """Number of records to return (default: 100)"""

    skip: str
    """Number of records to skip (default: 0)"""

    start_date: Annotated[str, PropertyInfo(alias="startDate")]
    """Filter by start date (ISO string)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """Filter by user ID"""
