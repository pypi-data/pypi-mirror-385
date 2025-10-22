"""Group API request schemas."""

from typing import NotRequired, TypedDict

__all__ = [
    'GroupEditRequest',
]


class GroupEditRequest(TypedDict):
    """Request schema for editing a group (PUT /core/group/{group_id})."""

    name: str  # Required field per API
    description: NotRequired[str]
    unique_name: NotRequired[str | None]
    email_domain: NotRequired[str | None]
    private: NotRequired[bool]
    private_visible: NotRequired[bool]
