"""API response schema for rerere endpoint."""

from __future__ import annotations

from typing import TypedDict


class RerereResponse(TypedDict):
    """Response from /msg/post/{chat_id}/{post_no}/rerere endpoint.

    Returns a chain of post-numbers representing the reply thread,
    where the requested post is the last one in the chain.
    """

    data: list[int]  # List of PostNo (post numbers)


__all__ = ['RerereResponse']
