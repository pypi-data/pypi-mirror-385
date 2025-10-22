"""Async Post model."""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Unpack
from uuid import uuid4

from pararamio_aio._core.api_schemas import RerereResponse, WhoReadResponse
from pararamio_aio._core.api_schemas.responses import (
    DataListResponse,
    PostCreateResponse,
    PostDeleteResponse,
    PostEditResponse,
    PostResponseItem,
    PostsResponse,
)
from pararamio_aio._core.models import CoreFile as File
from pararamio_aio._core.models import CorePost
from pararamio_aio._core.utils.helpers import encode_digit

# Imports from core
from pararamio_aio.exceptions import (
    PararamioRequestError,
    PararamioTypeError,
    PararamioValidationError,
    PararamMultipleFoundError,
    PararamNotFoundError,
)
from pararamio_aio.utils import batch_load_with_extractor

from .base import AsyncClientMixin

if TYPE_CHECKING:
    from .chat import Chat

__all__ = ('Post',)


class Post(CorePost['Chat'], AsyncClientMixin[PostResponseItem]):
    """Async Post model with explicit loading."""

    def __init__(  # type: ignore[misc]
        self,
        chat: Chat,
        post_no: int | None = None,
        **kwargs: Unpack[PostResponseItem],
    ) -> None:
        """Initialize async post.

        Args:
            chat: Parent chat object
            post_no: Post number (optional positional or keyword argument)
            **kwargs: Additional post data
        """
        super().__init__(chat, post_no, **kwargs)

    async def load(self) -> Post:
        """Load full post data from API.

        Returns:
            Self with updated data
        """
        # Try cache first if available
        if self._client._cache:
            cache_key = f'chat.{self.chat_id}.post.{self.post_no}'
            cached = await self._client._cache.get(cache_key)
            if cached:
                self._data.update(cached)
                self._set_loaded()
                return self

        # Load from API if not in cache
        url = f'/msg/post?ids={encode_digit(self.chat_id)}-{encode_digit(self.post_no)}'
        response = await self.client.api_get(url, response_model=PostsResponse)
        posts_data = response.get('posts', [])

        if len(posts_data) == 0:
            raise PararamNotFoundError(
                f'Post not found: post_no {self.post_no} in chat {self.chat_id}'
            )
        if len(posts_data) > 1:
            raise PararamMultipleFoundError(
                f'Found {len(posts_data)} posts for post {self.post_no} in chat {self.chat_id}'
            )

        post_data = posts_data[0]

        # Update our data with loaded data
        self._data.update(post_data)
        self._set_loaded()

        # Cache the data if cache is available
        if self._client._cache:
            cache_key = f'chat.{self.chat_id}.post.{self.post_no}'
            await self._client._cache.set(cache_key, post_data)

        return self

    @property
    def in_thread_no(self) -> int:
        """Alias for post_no for backward compatibility."""
        return self.post_no

    async def get_replies(self) -> list[int]:
        """Get list of reply post numbers.

        Returns:
            List of post-numbers that reply to this post
        """
        url = f'/msg/post/{self.chat_id}/{self.post_no}/replies'
        response = await self.client.api_get(url, response_model=DataListResponse[int])
        return response.get('data', [])

    async def load_reply_posts(self) -> list[Post]:
        """Load all posts that reply to this post.

        Returns:
            List of reply posts
        """
        reply_numbers = await self.get_replies()
        if not reply_numbers:
            return []

        # Define loader function for batch loading
        async def load_range(start: int, end: int) -> list[Post]:
            if start == end:
                # Single post
                post = await self.client.get_post(self.chat_id, start)
                return [post] if post else []
            # Batch load posts in range
            return await self._chat.load_posts(start_post_no=start, end_post_no=end + 1)

        # Load all reply posts in parallel batches
        posts_dict = await batch_load_with_extractor(
            reply_numbers, load_range, lambda post: post.post_no, max_gap=50
        )

        # Return posts in the order of reply_numbers
        return [posts_dict[post_no] for post_no in reply_numbers if post_no in posts_dict]

    async def get_reply_to_post(self) -> Post | None:
        """Get the post this post replies to.

        Returns:
            Parent post or None if not a reply
        """
        if not self.is_reply or self.reply_no is None:
            return None

        return await self.client.get_post(self.chat_id, self.reply_no)

    async def replies(self) -> list[int]:
        """Get reply post numbers (alias for backward compatibility).

        Returns:
            List of post numbers that are replies to this post
        """
        return await self.get_replies()

    async def reply(self, text: str, quote: str | None = None) -> Post:
        """Reply to this post.

        Args:
            text: Reply to text
            quote: Optional quote text

        Returns:
            Created reply post
        """
        url = f'/msg/post/{self.chat_id}'
        data = {
            'uuid': str(uuid4().hex),
            'text': text,
            'reply_no': self.post_no,
        }

        if quote:
            data['quote'] = quote

        response = await self.client.api_post(url, data, response_model=PostCreateResponse)
        post_no = response['post_no']

        post = await self.client.get_post(self.chat_id, post_no)
        if post is None:
            raise ValueError(f'Failed to retrieve reply post {post_no} from chat {self.chat_id}')
        return post

    async def edit(self, text: str, quote: str | None = None, reply_no: int | None = None) -> bool:
        """Edit this post.

        Args:
            text: New post text
            quote: Optional new quote
            reply_no: Optional new reply number

        Returns:
            True if successful
        """
        url = f'/msg/post/{self.chat_id}/{self.post_no}'
        data: dict[str, Any] = {
            'uuid': self.uuid or str(uuid4().hex),
            'text': text,
        }

        if quote is not None:
            data['quote'] = quote
        if reply_no is not None:
            data['reply_no'] = reply_no

        response = await self.client.api_put(url, data, response_model=PostEditResponse)

        if response.get('ver'):
            # Invalidate cache for this post
            if self.client._cache:
                cache_key = f'chat.{self.chat_id}.post.{self.post_no}'
                await self.client._cache.delete(cache_key)

            # Reload the post data
            await self.load()
            return True

        return False

    async def delete(self) -> bool:
        """Delete this post.

        Returns:
            True if successful
        """
        url = f'/msg/post/{self.chat_id}/{self.post_no}'
        response = await self.client.api_delete(url, None, response_model=PostDeleteResponse)

        if response.get('ver'):
            # Invalidate cache for this post
            if self.client._cache:
                cache_key = f'chat.{self.chat_id}.post.{self.post_no}'
                await self.client._cache.delete(cache_key)

            # Update local data to reflect deletion
            self._data['is_deleted'] = True
            return True

        return False

    async def who_read(self) -> dict[int, str]:
        """Get who read this post with timestamps.

        Returns:
            Dictionary mapping user IDs to read timestamps (ISO format strings)
        """
        url = f'/activity/who-read?thread_id={self.chat_id}&post_no={self.post_no}'
        response = await self.client.api_get(url, response_model=WhoReadResponse)
        # Convert string user IDs to integers
        return {int(user_id): timestamp for user_id, timestamp in response.items()}

    async def mark_read(self) -> bool:
        """Mark this post as read.

        Returns:
            True if successful
        """
        return await self.chat.mark_read(self.post_no)

    async def get_file(self) -> File | None:
        """Get attached file if any.

        Returns:
            File object or None if no file
        """
        file_data = self.meta.get('file')
        if not file_data:
            return None

        return File(self.client, **file_data)

    async def download_file(self, filename: str | None = None) -> bytes:
        """Download the file attached to this post.

        Args:
            filename: Optional filename to use for download.
                     If not provided, uses the filename from the file metadata.

        Returns:
            File content as bytes

        Raises:
            PararamioTypeError: If the post doesn't have a file attachment
            PararamioValidationError: If filename cannot be determined
        """
        file = await self.get_file()
        if file is None:
            raise PararamioTypeError(f'Post {self.post_no} is not a file post')

        if filename is None:
            filename = getattr(file, 'filename', None) or getattr(file, 'name', None)
            if not filename:
                raise PararamioValidationError('Cannot determine filename')

        bio = await self.client.download_file(file.guid, filename)
        return bio.read()

    async def load_attachments(
        self,
        max_deep: int = 100,  # noqa: ARG002
        raise_if_not_found: bool = True,  # noqa: ARG002
    ) -> list[File]:
        """Load all file attachments for this post.

        Args:
            max_deep: Maximum depth to search for attachments
            raise_if_not_found: Whether to raise error if not all attachments found

        Returns:
            List of attached files
        """
        attachment_uuids = self.meta.get('attachments', [])
        if not attachment_uuids:
            return []

        # This is a simplified implementation
        # In reality, you'd need to search through nearby posts to find the files
        files = []
        main_file = await self.get_file()
        if main_file:
            files.append(main_file)

        return files

    async def get_attachments(self) -> list[File]:
        """Get all file attachments for this post.

        Returns:
            List of attached files
        """
        return await self.load_attachments()

    @property
    def file(self) -> File | None:
        """Get attached file if any (synchronous property for compatibility)."""
        file_data = self.meta.get('file')
        if not file_data:
            return None
        return File(self.client, **file_data)

    async def next(self, skip_event: bool = True) -> Post | None:
        """Get next post in thread.

        Args:
            skip_event: Skip a message if this is an event

        Returns:
            Next post or None if no next post exists
        """
        _next = self.post_no + 1
        if _next > self._chat.posts_count:
            return None
        post = Post(self._chat, post_no=_next)
        if skip_event and post.is_event:
            return await post.next(skip_event)
        return post

    async def prev(self, skip_event: bool = True) -> Post | None:
        """Get previous post in thread.

        Args:
            skip_event: Skip a message if this is an event

        Returns:
            Previous post or None if no previous post exists
        """
        _prev = self.post_no - 1
        if _prev <= 0:
            return None
        post = Post(self._chat, post_no=_prev)
        if skip_event and post.is_event:
            return await post.prev(skip_event)
        return post

    async def rerere(self) -> list[Post]:
        """Get all replies in a thread recursively.

        Returns:
            List of all posts in the reply chain
        """

        url = f'/msg/post/{self.chat_id}/{self.post_no}/rerere'
        response = await self.client.api_get(url, response_model=RerereResponse)

        post_numbers = response.get('data', [])
        if not post_numbers:
            return []

        # Define loader function for batch loading
        async def load_range(start: int, end: int) -> list[Post]:
            if start == end:
                # Single post
                post = Post(self._chat, post_no=start)
                await post.load()
                return [post]
            # Batch load posts in range
            # end_post_no are exclusive in API
            return await self._chat.load_posts(start_post_no=start, end_post_no=end + 1)

        # Load all posts in parallel batches
        posts_dict = await batch_load_with_extractor(
            post_numbers, load_range, lambda post: post.post_no, max_gap=50
        )

        # Return posts in the original order from rerere response
        return [posts_dict[post_no] for post_no in post_numbers if post_no in posts_dict]

    async def get_tree(self, load_limit: int = 1000) -> OrderedDict[int, Post]:
        """Get post-hierarchy as an ordered dictionary.

        Args:
            load_limit: Maximum number of posts to load between first and current

        Returns:
            OrderedDict mapping post-numbers to Post objects
        """
        posts: dict[int, Post] = {self.post_no: self}

        # Get all replies recursively
        for post in await self.rerere():
            posts[post.post_no] = post

        # Find the first post in thread
        first = posts[min(posts.keys())]
        tree = OrderedDict(sorted(posts.items()))

        # Calculate load range
        load_start = first.post_no + 1
        if self.post_no - first.post_no > load_limit:
            load_start = self.post_no - load_limit

        # Load posts in range if needed
        if load_start < self.post_no - 1:
            loaded_posts = await self._chat.load_posts(
                start_post_no=load_start, end_post_no=self.post_no - 1
            )
            for post in loaded_posts:
                posts[post.post_no] = post

        # Build final tree with only connected posts
        for post in sorted(posts.values(), key=lambda p: p.post_no):
            if post.reply_no is None or post.reply_no not in tree:
                continue
            tree[post.post_no] = post

        return OrderedDict(sorted(tree.items()))

    @classmethod
    async def create(
        cls,
        chat: Chat,
        text: str,
        *,
        reply_no: int | None = None,
        quote: str | None = None,
        uuid: str | None = None,
        attachments: list[str] | None = None,
    ) -> Post:
        """Create a new post.

        Args:
            chat: Parent chat
            text: Post text
            reply_no: Optional post number to reply to
            quote: Optional quote text
            uuid: Optional UUID (generated if not provided)
            attachments: Optional list of attachment UUIDs

        Returns:
            Created a Post object
        """
        url = f'/msg/post/{chat.id}'
        data: dict[str, Any] = {
            'uuid': uuid or str(uuid4().hex),
            'text': text,
            'quote': quote,
            'reply_no': reply_no,
        }
        if attachments:
            data['attachments'] = attachments

        response = await chat._client.api_post(url, data, response_model=PostCreateResponse)
        if not response:
            raise PararamioRequestError('Failed to create post')

        post = cls(chat, post_no=response['post_no'])
        await post.load()
        return post

    async def attachment_files(self) -> list[File]:
        """Get attachment files (loads them if needed).

        This is an async method in the async version, unlike the sync version
        where it's a property.

        Returns:
            List of File objects for attachments
        """
        return await self.load_attachments()
