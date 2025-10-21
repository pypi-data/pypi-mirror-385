# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .application import Application

__all__ = ["StyleGuide", "Content", "Definition"]


class Content(BaseModel):
    approved: bool

    content: str

    heading: str


class Definition(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the eval definition was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the eval definition was last modified"""

    name: str

    type: Literal["NATURALNESS", "STYLE", "RECALL", "CUSTOM", "BLACKLIST", "FACT"]
    """Type of evaluation. Valid options: NATURALNESS, STYLE, RECALL, CUSTOM, FACT."""

    application: Optional[Application] = None
    """Application configuration and metadata"""

    global_config: Optional[object] = FieldInfo(alias="globalConfig", default=None)

    style_guide_id: Optional[str] = FieldInfo(alias="styleGuideId", default=None)


class StyleGuide(BaseModel):
    id: str
    """The unique identifier of the style guide"""

    application: Application
    """Application configuration and metadata"""

    application_id: str = FieldInfo(alias="applicationId")
    """The application ID this style guide belongs to"""

    content: List[Content]
    """The content sections of the style guide"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the style guide was created"""

    definitions: List[Definition]

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the style guide was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """The organization ID this style guide belongs to"""

    quickstart_id: Optional[str] = FieldInfo(alias="quickstartId", default=None)
    """The ID of the associated quickstart if any"""
