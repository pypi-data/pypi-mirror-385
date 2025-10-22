# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ContextPushParams"]


class ContextPushParams(TypedDict, total=False):
    token: Required[str]
    """Embed token"""

    context: Required[str]
    """Context string to add"""
