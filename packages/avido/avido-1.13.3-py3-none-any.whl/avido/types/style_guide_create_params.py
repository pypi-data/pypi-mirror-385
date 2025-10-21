# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["StyleGuideCreateParams", "Content"]


class StyleGuideCreateParams(TypedDict, total=False):
    content: Required[Iterable[Content]]
    """The content sections of the style guide"""


class Content(TypedDict, total=False):
    approved: Required[bool]

    content: Required[str]

    heading: Required[str]
