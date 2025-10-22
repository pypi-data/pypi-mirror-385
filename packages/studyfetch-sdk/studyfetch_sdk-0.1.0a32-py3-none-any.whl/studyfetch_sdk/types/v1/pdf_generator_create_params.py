# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PdfGeneratorCreateParams", "CustomImage"]


class PdfGeneratorCreateParams(TypedDict, total=False):
    locale: Required[str]
    """Locale/language for the presentation (e.g., en-US, es-ES, fr-FR)"""

    number_of_slides: Required[Annotated[float, PropertyInfo(alias="numberOfSlides")]]
    """Number of slides to generate"""

    topic: Required[str]
    """The topic for the PDF presentation"""

    custom_images: Annotated[Iterable[CustomImage], PropertyInfo(alias="customImages")]
    """Custom images to use (required when imageMode is "provide-own")"""

    image_mode: Annotated[Literal["search", "provide-own", "none"], PropertyInfo(alias="imageMode")]
    """
    Image handling mode: search (auto-search), provide-own (use custom images), none
    (no images, use icons)
    """

    logo_url: Annotated[str, PropertyInfo(alias="logoUrl")]
    """Custom logo URL to use (optional, falls back to default StudyFetch logo)"""


class CustomImage(TypedDict, total=False):
    description: Required[str]
    """Description of what this image shows"""

    base64: str
    """Base64-encoded image data (provide either url or base64)"""

    url: str
    """Image URL to download and use (provide either url or base64)"""
