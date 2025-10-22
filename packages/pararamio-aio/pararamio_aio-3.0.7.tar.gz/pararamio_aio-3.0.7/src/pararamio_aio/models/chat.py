"""Async Chat model."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from datetime import datetime
from io import BytesIO
from os import PathLike
from typing import TYPE_CHECKING, BinaryIO, Unpack
from urllib.parse import quote

# Imports from core
from pararamio_aio._core import (
    POSTS_LIMIT,
    PararamioLimitExceededError,
    PararamioRequestError,
    PararamioValidationError,
    validate_post_load_range,
)
from pararamio_aio._core.api_schemas import ChatResponseItem, ChatsResponse
from pararamio_aio._core.api_schemas.requests import (
    ChatCreateRequest,
    ChatUpdateSettingsRequest,
    MarkReadRequest,
    PostSendMessageRequest,
)
from pararamio_aio._core.api_schemas.responses import (
    ChatIdResponse,
    ChatSearchResponse,
    ChatSyncResponse,
    EmptyResponse,
    KeywordsResponse,
    OkResponse,
    PostCreateResponse,
    PostResponseItem,
    PostsResponse,
    ReadStatusResponse,
)
from pararamio_aio._core.models import CoreChat, SerializationMixin
from pararamio_aio._core.utils.helpers import encode_chats_ids, format_datetime, join_ids
from pararamio_aio._core.utils.lazy_loading import (
    LazyLoadBatch,
    LazyLoadingConfig,
    generate_cache_key,
    get_retry_delay,
)
from pararamio_aio._core.utils.logging_config import LoggerManager, get_logger

from .attachment import Attachment
from .base import AsyncClientMixin
from .post import Post

if TYPE_CHECKING:
    from pararamio_aio._core._types import QuoteRangeT
    from pararamio_aio._core.models import CoreFile as File

    from pararamio_aio.client import AsyncPararamio

__all__ = ('Chat',)

# Get component-specific loggers
lazy_logger = get_logger(LoggerManager.LAZY_LOADING)
batch_logger = get_logger(LoggerManager.BATCH_LOGIC)
cache_logger = get_logger(LoggerManager.CACHE)


class Chat(
    CoreChat['AsyncPararamio'],
    AsyncClientMixin[ChatResponseItem],
    SerializationMixin['AsyncPararamio', ChatResponseItem],
):
    """Asynchronous Chat model with lazy loading, caching, and async iterator support.

    Represents a chat/conversation in Pararam.io with comprehensive async message handling,
    search capabilities, and member management.

    Features:
        - Lazy loading: Posts load on-demand with a cache-first approach
        - Async iterator support: Iterate over all posts with automatic batching
        - Smart batching: Optimizes API calls by merging nearby uncached ranges
        - Search: Both lazy (async iterator) and batch (list) post-search methods
        - Caching: Optional response caching for better performance

    Examples:
        Create and send messages:
            >>> async def example():
            ...     chat = await client.get_chat_by_id(123)
            ...     await chat.post('Hello everyone!')

        Async iterate over all posts (lazy loading):
            >>> async def example():
            ...     async for post in chat:
            ...         print(f'{post.user.name}: {post.text}')

        Load a specific range:
            >>> async def example():
            ...     posts = await chat.posts(1, 100)  # Posts 1-100
            ...     recent = await chat.posts(-50, -1)  # Last 50 posts

        Search within chat:
            >>> async def example():
            ...     async for post in chat.search_posts_lazy('bug fix'):
            ...         print(post.text)

        Organize chats:
            >>> async def example():
            ...     await chat.add_tag('important')
            ...     await chat.set_keywords('project deadline urgent')
            ...     await chat.set_custom_title('Q1 Project')

        Manage members:
            >>> async def example():
            ...     await chat.add_users([123, 456])
            ...     await chat.add_admins([123])
    """

    def __init__(  # type: ignore[misc]
        self,
        client: AsyncPararamio,
        chat_id: int | None = None,
        **kwargs: Unpack[ChatResponseItem],
    ) -> None:
        """Initialize async chat.

        Args:
            client: AsyncPararamio client
            chat_id: Chat ID (optional positional or keyword argument)
            **kwargs: Additional chat data
        """
        super().__init__(client, chat_id, **kwargs)

    def __aiter__(self) -> AsyncIterator[Post]:
        """Async iterate over all posts in the chat using lazy loading with cache-first approach.

        Returns:
            Async iterator of Post objects
        """
        # Use the full range from 1 to posts_count
        # If posts_count is not available, use a large default range
        end_post = self.posts_count if self.posts_count else 999999
        return self._lazy_posts_loader(1, end_post)

    async def load(self) -> Chat:
        """Load full chat data from API.

        Returns:
            Self with updated data
        """
        # Get chat ID from data without triggering lazy loading
        chat_id = self._data.get('chat_id') or self._data.get('id')
        lazy_logger.debug('Loading chat %s', chat_id)

        # Try cache first if available
        if self.client._cache:
            cache_key = f'chat.{chat_id}'
            cached = await self.client._cache.get(cache_key)
            if cached:
                cache_logger.debug('Chat %s loaded from cache', chat_id)
                self._data.update(cached)
                self._set_loaded()
                return self

        # Load from API if not in cache
        url = f'/core/chat?ids={chat_id}'
        lazy_logger.debug('Loading chat %s from API', chat_id)

        response = await self.client.api_get(url, response_model=ChatsResponse)
        if response and 'chats' in response:
            chats = response.get('chats', [])
            if chats:
                chat_data = chats[0]
                self._data.update(chat_data)
                self._set_loaded()

                # Cache the data if cache is available
                if self.client._cache:
                    cache_key = f'chat.{chat_id}'
                    await self.client._cache.set(cache_key, chat_data)
                    cache_logger.debug('Cached chat %s data', chat_id)

                return self
        raise PararamioRequestError(f'failed to load data for chat id {chat_id}')

    async def _load_posts_from_api(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        limit: int = POSTS_LIMIT,
    ) -> list[Post]:
        """Load posts from API without any caching - for fresh=True case."""
        validate_post_load_range(start_post_no, end_post_no)

        url = f'/msg/post?chat_id={self.id}&range={start_post_no}x{end_post_no}'

        absolute = abs(end_post_no - start_post_no)
        if start_post_no < 0:
            absolute = 1
        if absolute >= limit:
            raise PararamioLimitExceededError(f'max post load limit is {limit - 1}')

        response = await self.client.api_get(url, response_model=PostsResponse)
        return [Post.from_dict(self, post) for post in response['posts']]

    async def _load_posts(  # pylint: disable=too-many-statements
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        limit: int = POSTS_LIMIT,
        fresh: bool = False,
    ) -> tuple[list[Post], bool]:
        """Internal method to load posts with smart caching.

        Optimization logic:
        - If all posts in cache - return from cache
        - If missing_ranges = 1 range - load only that range
        - If missing_ranges > 1 range - load entire range
          (more efficient to make 1 request than 2+)

        Args:
            start_post_no: Start post-number (negative = from the end)
            end_post_no: End post-number (negative = from the end)
            limit: Maximum number of posts to load
            fresh: If True, ignore cache and load from API

        Returns:
            tuple[list[Post], bool]: (posts, from_cache)
            where from_cache=True if all posts were from cache
        """
        batch_logger.debug(
            'Loading posts for chat %s: range %s to %s, fresh=%s',
            self.id,
            start_post_no,
            end_post_no,
            fresh,
        )

        # If fresh or no cache - load all from API
        if fresh or self.client._cache is None:
            lazy_logger.debug(
                'Loading posts directly from API (fresh=%s, cache=%s)',
                fresh,
                self.client._cache is not None,
            )
            posts = await self._load_posts_from_api(start_post_no, end_post_no, limit)
            return posts, False

        # For negative indices, first need to know total post-count
        actual_start = start_post_no
        actual_end = end_post_no

        if start_post_no < 0 or end_post_no < 0:
            # Need to load chat info to get post-count
            # This could be cached separately or fetched from self._data
            total_posts = self.posts_count  # Property of chat

            if start_post_no < 0:
                actual_start = max(1, total_posts + start_post_no + 1)
            if end_post_no < 0:
                actual_end = max(1, total_posts + end_post_no + 1)

        # Check limit
        absolute = abs(actual_end - actual_start)
        if actual_start < 0:
            absolute = 1
        if absolute >= limit:
            raise PararamioLimitExceededError(f'max post load limit is {limit - 1}')

        # Check cache and collect missing_ranges
        cached_posts = {}
        missing_ranges: list[list[int]] = []

        for post_no in range(actual_start, actual_end + 1):
            cache_key = f'chat.{self.id}.post.{post_no}'
            cached_data = await self.client._cache.get(cache_key)

            if cached_data:
                cached_posts[post_no] = Post.from_dict(self, cached_data)
            else:
                # Add to missing ranges
                if not missing_ranges or post_no != missing_ranges[-1][1] + 1:
                    missing_ranges.append([post_no, post_no])
                else:
                    missing_ranges[-1][1] = post_no

        # If all in cache - return from cache
        if not missing_ranges:
            cache_logger.debug('All %d posts found in cache', len(cached_posts))
            posts = [cached_posts[no] for no in sorted(cached_posts.keys())]
            return posts, True

        # If missing_ranges has more than one range,
        # it's simpler to load entire range with one request
        if len(missing_ranges) > 1:
            batch_logger.debug(
                'Multiple missing ranges (%d), loading entire range %s to %s',
                len(missing_ranges),
                actual_start,
                actual_end,
            )
            # Load entire range
            url = f'/msg/post?chat_id={self.id}&range={actual_start}x{actual_end}'
            response = await self.client.api_get(url, response_model=PostsResponse)
            res = response.get('posts', [])

            posts = []
            for post_data in res:
                post = Post.from_dict(self, post_data)
                posts.append(post)

                # Cache each post
                cache_key = f'chat.{self.id}.post.{post.post_no}'
                await self.client._cache.set(cache_key, post_data)

            cache_logger.debug('Cached %d posts from API', len(posts))
            return posts, False

        # If only one missing_range - load just that
        start, end = missing_ranges[0]
        batch_logger.debug('Single missing range: %s to %s', start, end)
        url = f'/msg/post?chat_id={self.id}&range={start}x{end}'
        response = await self.client.api_get(url, response_model=PostsResponse)
        res = response.get('posts', [])

        # Add loaded posts to cached ones
        for post_data in res:
            post = Post.from_dict(self, post_data)
            post_no = post.post_no
            cached_posts[post_no] = post

            # Cache it
            cache_key = f'chat.{self.id}.post.{post_no}'
            await self.client._cache.set(cache_key, post_data)

        # Return sorted list
        posts = [cached_posts[no] for no in sorted(cached_posts.keys())]
        return posts, False

    async def load_posts(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        limit: int = POSTS_LIMIT,
        fresh: bool = False,
    ) -> list[Post]:
        """Load posts from chat.

        Args:
            start_post_no: Start post-number (negative for from the end)
            end_post_no: End post number (negative for from end)
            limit: Maximum posts to load
            fresh: If True, ignore cache and load from API

        Returns:
            List of posts
        """
        posts, _ = await self._load_posts(start_post_no, end_post_no, limit, fresh)
        return posts

    async def get_recent_posts(self, count: int = 50) -> list[Post]:
        """Get recent posts from chat.

        Args:
            count: Number of recent posts to get

        Returns:
            List of recent posts
        """
        return await self.load_posts(start_post_no=-count, end_post_no=-1)

    @staticmethod
    async def _assign_batch_to_uncached_posts_async(
        start: int,
        end: int,
        batch: LazyLoadBatch,
        config: LazyLoadingConfig,
        cache_check: Callable[[str], Awaitable[bool]],
        post_to_batch: dict[int, LazyLoadBatch | None],
    ) -> None:
        """Async version: Assign batch to uncached posts in range."""
        for post_no in range(start, end + 1):
            cache_key = generate_cache_key(config.cache_key_template, config.chat_id, post_no)
            if not await cache_check(cache_key):
                post_to_batch[post_no] = batch

    @staticmethod
    async def _assign_split_batches_async(
        range_start: int,
        range_end: int,
        config: LazyLoadingConfig,
        cache_check: Callable[[str], Awaitable[bool]],
        post_to_batch: dict[int, LazyLoadBatch | None],
    ) -> None:
        """Async version: Split large range into multiple batches and assign to posts."""
        current = range_start
        while current <= range_end:
            batch_start = current
            batch_end = min(current + config.per_request - 1, range_end)
            batch = LazyLoadBatch(batch_start, batch_end)

            await Chat._assign_batch_to_uncached_posts_async(
                batch_start, min(batch_end, range_end), batch, config, cache_check, post_to_batch
            )

            current = batch_end + 1

    @staticmethod
    def _validate_batch_size(batch_size: int, limit: int) -> None:
        """Validate that batch size doesn't exceed the limit.

        Args:
            batch_size: Size of the batch
            limit: Maximum allowed batch size

        Raises:
            ValueError: If batch size exceeds limit
        """
        if batch_size > limit:
            raise ValueError(f'Batch size {batch_size} exceeds POSTS_LIMIT {limit}')

    @staticmethod
    async def _calculate_lazy_batches_async(
        config: LazyLoadingConfig,
        cache_check: Callable[[str], Awaitable[bool]],
    ) -> AsyncIterator[tuple[int, LazyLoadBatch | None]]:
        """Async version of calculate_lazy_batches with smart batch merging.

        This async generator yields tuples of (post_no, batch) where:
        - If post is in cache: yields (post_no, None)
        - If post needs loading: yields (post_no, LazyLoadBatch)

        The algorithm groups consecutive missing posts into batches and merges close batches
        for efficient loading. If the gap between two batches is smaller than per_request/2,
        they will be merged into a single batch to reduce API calls.

        Args:
            config: Lazy loading configuration
            cache_check: Async function to check if a key exists in cache

        Yields:
            Tuples of (post_number, batch_or_none)
        """
        # First, collect all missing ranges
        missing_ranges: list[tuple[int, int]] = []
        current = config.start_post_no

        while current <= config.end_post_no:
            cache_key = generate_cache_key(config.cache_key_template, config.chat_id, current)

            if not await cache_check(cache_key):
                # Start of a missing range
                range_start = current
                range_end = current

                # Find the end of this missing range
                while current + 1 <= config.end_post_no:
                    next_key = generate_cache_key(
                        config.cache_key_template, config.chat_id, current + 1
                    )
                    if await cache_check(next_key):
                        break
                    current += 1
                    range_end = current

                missing_ranges.append((range_start, range_end))

            current += 1

        # Now merge close ranges and split into batches
        if not missing_ranges:
            # All posts are cached
            for post_no in range(config.start_post_no, config.end_post_no + 1):
                yield post_no, None
            return

        # Merge close ranges (gap less than per_request)
        merge_threshold = config.per_request
        merged_ranges: list[tuple[int, int]] = []

        for start, end in missing_ranges:
            if merged_ranges and start - merged_ranges[-1][1] - 1 < merge_threshold:
                # Merge with previous range
                merged_ranges[-1] = (merged_ranges[-1][0], end)
            else:
                # Add as new range
                merged_ranges.append((start, end))

        # Now create batches from merged ranges and yield
        post_to_batch: dict[int, LazyLoadBatch | None] = {}

        # Mark all posts - cached posts get None, others will be set later
        for post_no in range(config.start_post_no, config.end_post_no + 1):
            cache_key = generate_cache_key(config.cache_key_template, config.chat_id, post_no)
            if await cache_check(cache_key):
                post_to_batch[post_no] = None
            else:
                # Will be set to a batch later
                post_to_batch[post_no] = None  # Temporary

        # Create batches for merged ranges
        for range_start, range_end in merged_ranges:
            # Ensure the range doesn't exceed POSTS_LIMIT
            range_size = range_end - range_start + 1
            if range_size > config.per_request:
                # Split into multiple batches
                await Chat._assign_split_batches_async(
                    range_start, range_end, config, cache_check, post_to_batch
                )
            else:
                # Single batch for the entire range
                batch = LazyLoadBatch(range_start, range_end)
                await Chat._assign_batch_to_uncached_posts_async(
                    range_start, range_end, batch, config, cache_check, post_to_batch
                )

        # Yield results in order
        for post_no in range(config.start_post_no, config.end_post_no + 1):
            yield post_no, post_to_batch[post_no]

    async def _lazy_posts_loader(  # pylint: disable=too-many-statements
        self, start_post_no: int = -50, end_post_no: int = -1, per_request: int = POSTS_LIMIT
    ) -> AsyncIterator[Post]:
        """Async lazy iterator for posts with cache-first approach and retry logic.

        Args:
            start_post_no: Starting post number (negative = from the end)
            end_post_no: Ending post number (negative = from the end)
            per_request: Number of posts to load per batch request

        Yields:
            Post objects, either from cache or loaded from API
        """
        lazy_logger.debug(
            'Starting lazy loading for chat %s: range %s to %s', self.id, start_post_no, end_post_no
        )

        # Handle negative indices
        if start_post_no < 0 or end_post_no < 0:
            total_posts = self.posts_count or 0
            if start_post_no < 0:
                start_post_no = max(1, total_posts + start_post_no + 1)
            if end_post_no < 0:
                end_post_no = max(1, total_posts + end_post_no + 1)

        # Validate range after resolving negative indices
        validate_post_load_range(start_post_no, end_post_no)

        # Configure lazy loading
        config = LazyLoadingConfig(
            start_post_no=start_post_no,
            end_post_no=end_post_no,
            per_request=per_request,
            cache_key_template='chat.{chat_id}.post.{post_no}',
            chat_id=self.id,
        )

        # Check if cache is available
        if not self.client._cache:
            lazy_logger.debug('No cache available, loading posts in batches')
            # No cache - just load everything in batches
            current = start_post_no
            while current <= end_post_no:
                batch_end = min(current + per_request - 1, end_post_no)

                # Retry logic for API failures
                posts: list[Post] = []
                for attempt in range(3):
                    try:
                        posts, _ = await self._load_posts(current, batch_end)
                        break
                    except Exception:
                        if attempt == 2:  # Last attempt
                            raise  # Re-raise the exception
                        await asyncio.sleep(get_retry_delay(attempt))

                for post in posts:
                    if start_post_no <= post.post_no <= end_post_no:
                        yield post

                current = batch_end + 1
            return

        # Use cache-first algorithm from core utilities
        async def async_cache_check(key: str) -> bool:
            """Async wrapper for cache check."""
            if self.client._cache:
                result = await self.client._cache.get(key)
                return result is not None
            return False

        current_batch = None
        loaded_posts = {}

        async for post_no, batch_info in self._calculate_lazy_batches_async(
            config, async_cache_check
        ):
            if batch_info is None:
                # Post is in cache
                cache_key = f'chat.{self.id}.post.{post_no}'
                cached = await self.client._cache.get(cache_key)
                if cached:
                    lazy_logger.debug('Yielding cached post %d from chat %s', post_no, self.id)
                    yield Post.from_dict(self, cached)
            else:
                # Need to load a batch
                if batch_info != current_batch:
                    # New batch to load
                    current_batch = batch_info
                    batch_logger.debug(
                        'Loading batch for chat %s: posts %d to %d',
                        self.id,
                        batch_info.start,
                        batch_info.end,
                    )

                    # Retry logic for API failures
                    for attempt in range(3):
                        try:
                            # Ensure we never exceed POSTS_LIMIT
                            batch_size = batch_info.end - batch_info.start + 1
                            self._validate_batch_size(batch_size, POSTS_LIMIT)
                            posts, _ = await self._load_posts(batch_info.start, batch_info.end)
                            loaded_posts = {p.post_no: p for p in posts}
                            batch_logger.debug(
                                'Successfully loaded batch with %d posts', len(posts)
                            )
                            break
                        except Exception as e:
                            if attempt == 2:  # Last attempt
                                lazy_logger.error('Failed to load batch after 3 attempts: %s', e)
                                raise  # Re-raise the exception
                            lazy_logger.warning(
                                'Batch load attempt %d failed: %s. Retrying...', attempt + 1, e
                            )
                            await asyncio.sleep(get_retry_delay(attempt))

                # Yield the post from loaded batch
                if post_no in loaded_posts:
                    yield loaded_posts[post_no]

    async def lazy_posts_load(
        self, start_post_no: int = -50, end_post_no: int = -1, per_request: int = POSTS_LIMIT
    ) -> list[Post]:
        """Load posts lazily using the new async generator.

        Args:
            start_post_no: Start post-number (negative = from the end)
            end_post_no: End post-number (negative = from the end)
            per_request: Posts per request

        Returns:
            List of posts
        """
        # Collect all posts from the async generator
        return [
            post async for post in self._lazy_posts_loader(start_post_no, end_post_no, per_request)
        ]

    async def send_message(
        self,
        text: str,
        reply_to_post_no: int | None = None,
        quote_text: str | None = None,
    ) -> Post:
        """Send a message to this chat.

        Args:
            text: Message text
            reply_to_post_no: Optional post number to reply to
            quote_text: Optional quote text

        Returns:
            Created post
        """
        url = f'/msg/post/{self.id}'
        data: PostSendMessageRequest = {
            'uuid': str(uuid.uuid4().hex),
            'text': text,
        }

        if reply_to_post_no:
            data['reply_no'] = reply_to_post_no
        if quote_text:
            data['quote'] = quote_text

        response = await self.client.api_post(url, dict(data), response_model=PostCreateResponse)
        post_no = response['post_no']

        # Create a post-object directly like sync version does

        post = Post(self, post_no=post_no)
        # Load the post-data
        await post.load()
        return post

    async def upload_file(
        self,
        file: str | BytesIO | BinaryIO | PathLike[str],
        *,
        filename: str | None = None,
        content_type: str | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> File:
        """Upload a file to this chat.

        Args:
            file: File to upload (path, BytesIO, BinaryIO, or PathLike)
            filename: Optional filename override
            content_type: Optional MIME type
            reply_no: Optional post number to reply to
            quote_range: Optional quote range

        Returns:
            Uploaded file object
        """
        if self.id is None:
            raise ValueError('can not upload file to new chat')
        if not isinstance(file, str | PathLike) and not filename:
            raise PararamioValidationError('can not determine filename for BinaryIO')
        attachment = Attachment(file, filename=filename, content_type=content_type)
        return await self.client.upload_file(
            file=attachment.fp,
            chat_id=self.id,
            filename=attachment.guess_filename,
            content_type=attachment.guess_content_type,
            reply_no=reply_no,
            quote_range=quote_range,
        )

    async def mark_read(self, post_no: int | None = None) -> bool:
        """Mark posts as read.

        Args:
            post_no: Optional specific post number, or None for all

        Returns:
            True if successful
        """
        url = f'/msg/lastread/{self.id}'
        data: MarkReadRequest = {'read_all': True} if post_no is None else {'post_no': post_no}

        response = await self.client.api_post(url, dict(data), response_model=ReadStatusResponse)

        # Update local data
        if 'last_read_post_no' in response:
            self._data['last_read_post_no'] = response['last_read_post_no']
        if 'posts_count' in response:
            self._data['posts_count'] = response['posts_count']

        return True

    async def add_users(self, ids: list[int]) -> bool:
        """Add users to chat.

        Args:
            ids: List of user IDs to add

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/user/{join_ids(ids)}'
        response = await self.client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    async def delete_users(self, ids: list[int]) -> bool:
        """Remove users from chat.

        Args:
            ids: List of user IDs to remove

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/user/{join_ids(ids)}'
        response = await self.client.api_delete(url, None, response_model=ChatIdResponse)
        return 'chat_id' in response

    async def add_admins(self, ids: list[int]) -> bool:
        """Add admins to chat.

        Args:
            ids: List of user IDs to make admins

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/admin/{join_ids(ids)}'
        response = await self.client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    async def delete_admins(self, ids: list[int]) -> bool:
        """Remove admins from chat.

        Args:
            ids: List of user IDs to remove admin rights

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/admin/{join_ids(ids)}'
        response = await self.client.api_delete(url, None, response_model=ChatIdResponse)
        return 'chat_id' in response

    async def delete(self) -> bool:
        """Delete this chat.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}'
        response = await self.client.api_delete(url, None, response_model=ChatIdResponse)
        if 'chat_id' in response:
            # Invalidate cache for this chat
            if self.client._cache:
                cache_key = f'chat.{self.id}'
                await self.client._cache.delete(cache_key)
            return True
        return False

    async def favorite(self) -> bool:
        """Add chat to favorites.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/favorite'
        response = await self.client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    async def unfavorite(self) -> bool:
        """Remove chat from favorites.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/unfavorite'
        response = await self.client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def __eq__(self, other: object) -> bool:
        """Check equality with another chat."""
        if not isinstance(other, Chat):
            return False
        return self.id == other.id

    def __str__(self) -> str:
        """String representation."""
        return f'{self.id} - {self.title or "Untitled"}'

    async def enter(self) -> bool:
        """Enter/join the chat.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/enter'
        response = await self.client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def quit(self) -> bool:
        """Quit/leave the chat.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/quit'
        response = await self.client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def add_tag(self, tag_name: str) -> bool:
        """Add a tag to this chat.

        Args:
            tag_name: Name of the tag to add. Must contain only Latin letters (a-z),
                     numbers (0-9), underscores (_) and dashes (-).
                     Must be 2-15 characters long.

        Returns:
            True if the operation was successful, False otherwise.

        Raises:
            PararamioValidationError: If tag name doesn't meet requirements.
        """
        # Validate tag name using the method from CoreChat
        self._validate_tag_name(tag_name)

        url = f'/user/chat/tags?name={quote(tag_name)}&chat_id={self.id}'
        response = await self.client.api_put(url, None, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def remove_tag(self, tag_name: str) -> bool:
        """Remove a tag from this chat.

        Args:
            tag_name: Name of the tag to remove. Must contain only Latin letters (a-z),
                     numbers (0-9), underscores (_) and dashes (-).
                     Must be 2-15 characters long.

        Returns:
            True if the operation was successful, False otherwise.

        Raises:
            PararamioValidationError: If tag name doesn't meet requirements.
        """
        # Validate tag name using the method from CoreChat
        self._validate_tag_name(tag_name)

        url = f'/user/chat/tags?name={quote(tag_name)}&chat_id={self.id}'
        response = await self.client.api_delete(url, None, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def hide(self) -> bool:
        """Hide chat from the list.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/hide'
        response = await self.client.api_post(url, {'chat_id': self.id}, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def show(self) -> bool:
        """Show hidden chat.

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/show'
        response = await self.client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def add_groups(self, ids: list[int]) -> bool:
        """Add groups to chat.

        Args:
            ids: List of group IDs to add

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/group/{join_ids(ids)}'
        response = await self.client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def delete_groups(self, ids: list[int]) -> bool:
        """Remove groups from chat.

        Args:
            ids: List of group IDs to remove

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/group/{join_ids(ids)}'
        response = await self.client.api_delete(url, None, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def transfer(self, org_id: int) -> bool:
        """Transfer chat ownership to organization.

        Args:
            org_id: Organization ID

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/transfer/{org_id}'
        response = await self.client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    async def set_custom_title(self, title: str) -> bool:
        """Set custom chat title.

        Args:
            title: New title

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}/custom_title'
        response = await self.client.api_post(url, {'title': title}, response_model=ChatIdResponse)
        # API returns {'chat_id': id} on success
        return response.get('chat_id') == self.id

    async def set_keywords(self, keywords: str) -> bool:
        """Set keywords for this chat.

        Args:
            keywords: Keywords to set for the chat

        Returns:
            True if the operation was successful, False otherwise.
        """
        url = '/msg/keywords'
        response = await self.client.api_post(
            url, {'chat_id': self.id, 'kw': keywords}, response_model=EmptyResponse
        )
        # Successful response is an empty dict {}
        return response == {}

    async def get_keywords(self) -> str | None:
        """Get keywords for this chat.

        Returns:
            Keywords string if set, None otherwise.
        """
        url = f'/msg/keywords?chat_id={self.id}'
        response = await self.client.api_get(url, response_model=KeywordsResponse)
        return response.get('kw')

    async def update_settings(self, **kwargs: Unpack[ChatUpdateSettingsRequest]) -> bool:
        """Update chat properties.

        Args:
            **kwargs: Chat settings to update (title, description, etc.)

        Returns:
            True if successful
        """
        url = f'/core/chat/{self.id}'
        response = await self.client.api_put(url, dict(kwargs), response_model=OkResponse)
        if response.get('result') == 'OK':
            # Invalidate cache for this chat
            if self.client._cache:
                cache_key = f'chat.{self.id}'
                await self.client._cache.delete(cache_key)
            return True
        return False

    async def read_status(self, post_no: int) -> bool:
        """Mark a post as read.

        Args:
            post_no: Post number to mark as read

        Returns:
            True if successful
        """
        return await self.mark_read(post_no)

    @staticmethod
    async def sync_chats(
        client: AsyncPararamio,
        chats_ids: list[tuple[int, int, int]],
        sync_time: datetime | None = None,
    ) -> ChatSyncResponse:
        """Sync chat data.

        Args:
            client: AsyncPararamio client
            chats_ids: List of chat ID tuples
            sync_time: Optional sync timestamp

        Returns:
            Chat sync response
        """
        url = '/core/chat/sync'
        data = {'ids': encode_chats_ids(chats_ids)}
        if sync_time:
            data['sync_time'] = format_datetime(sync_time)
        return await client.api_post(url, data, response_model=ChatSyncResponse)

    async def posts(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
    ) -> list[Post]:
        """Load posts in range.

        Args:
            start_post_no: Start post-number (negative counts from the end)
            end_post_no: End post number (negative counts from the end)

        Returns:
            List of posts
        """
        if start_post_no == end_post_no:
            start_post_no = end_post_no - 1
        # Use load_posts which already returns a list
        return await self.load_posts(start_post_no=start_post_no, end_post_no=end_post_no)

    @classmethod
    async def create_private_chat(cls, client: AsyncPararamio, user_id: int) -> Chat:
        """Create private chat with user.

        Args:
            client: Pararamio client
            user_id: User ID

        Returns:
            Created chat
        """
        url = f'/core/chat/pm/{user_id}'
        response = await client.api_post(url, response_model=ChatIdResponse)
        chat_id = response['chat_id']

        chat = await client.get_chat_by_id(chat_id)
        if chat is None:
            raise ValueError(f'Failed to create or get chat {chat_id}')
        return chat

    @classmethod
    async def create(
        cls,
        client: AsyncPararamio,
        **kwargs: Unpack[ChatCreateRequest],
    ) -> Chat:
        """Create a new chat.

        Args:
            client: AsyncPararamio client
            **kwargs: ChatCreateRequest parameters including:
                - title: Chat title
                - description: Chat description (optional)
                - users: List of user IDs to add (optional)
                - groups: List of group IDs to add (optional)
                - organization_id: Organization ID (optional)
                - posts_live_time: Posts live time (optional)
                - two_step_required: Whether two-step auth is required (optional)
                - history_mode: History mode setting (optional)
                - org_visible: Organization visibility (optional)
                - allow_api: Whether API access is allowed (optional)
                - read_only: Whether chat is read-only (optional)

        Returns:
            Created chat instance
        """
        data = CoreChat.prepare_create_chat_data(**kwargs)

        res = await client.api_post('/core/chat', data, response_model=ChatIdResponse)
        id_: int = res['chat_id']
        return cls(client, id=id_)

    @classmethod
    async def load_chats(cls, client: AsyncPararamio, ids: Sequence[int]) -> list[Chat]:
        """Load multiple chats by IDs.

        Args:
            client: AsyncPararamio client
            ids: List of chat IDs

        Returns:
            List of Chat objects
        """

        url = f'/core/chat?ids={join_ids(ids)}'
        res = await client.api_get(url, response_model=ChatsResponse)
        if res and 'chats' in res:
            return [cls(client, **data) for data in res.get('chats', [])]
        raise PararamioRequestError(f'failed to load data for chats ids: {",".join(map(str, ids))}')

    @classmethod
    async def search_posts_lazy(
        cls,
        client: AsyncPararamio,
        q: str,
        *,
        order_type: str = 'time',
        chat_ids: list[int] | None = None,
        max_results: int | None = None,
        per_page: int = POSTS_LIMIT,
    ) -> AsyncIterator[Post]:
        """Search for posts with lazy loading pagination (async generator).

        This method returns an async iterator that fetches posts page by page,
        yielding them one at a time. This is useful for processing large
        search results without loading everything into memory.

        Args:
            client: AsyncPararamio client
            q: Search query
            order_type: Order type ('time' or 'relevance')
            chat_ids: Optional list of chat IDs to filter by
            max_results: Maximum total results to fetch (None = unlimited)
            per_page: Number of posts to fetch per page (default: POSTS_LIMIT)

        Yields:
            Post objects one at a time

        Example:
            >>> async def example():
            ...     async for post in Chat.search_posts_lazy(client, 'hello', max_results=100):
            ...         print(post.text)
        """
        page = 1
        total_yielded = 0
        created_chats = {}

        lazy_logger.debug(
            'Starting lazy search (async): query=%r, order=%s, chat_ids=%s, max_results=%s',
            q,
            order_type,
            chat_ids,
            max_results,
        )

        while True:
            # Calculate how many results to fetch in this batch
            batch_limit = per_page
            if max_results:
                remaining = max_results - total_yielded
                if remaining <= 0:
                    lazy_logger.debug('Reached max_results limit: %d', max_results)
                    break
                batch_limit = min(batch_limit, remaining)

            lazy_logger.debug('Fetching page %d with limit %d', page, batch_limit)

            url = cls._build_search_url(
                q=q,
                order_type=order_type,
                page=page,
                chat_ids=chat_ids,
                limit=batch_limit,
            )

            try:
                response = await client.api_get(url, response_model=PostsResponse)
                if 'posts' not in response:
                    lazy_logger.warning('No posts in response for page %d', page)
                    break

                posts = response['posts']
                if not posts:
                    lazy_logger.debug('No more posts found at page %d', page)
                    break

                lazy_logger.debug('Received %d posts from page %d', len(posts), page)

                # Yield posts one by one
                for post_data in posts:
                    # API returns thread_id in search results, not chat_id
                    _chat_id = post_data.get('thread_id') or post_data.get('chat_id')
                    post_no = post_data['post_no']

                    if _chat_id not in created_chats:
                        created_chats[_chat_id] = cls(client, id=_chat_id)

                    yield Post(created_chats[_chat_id], post_no=post_no)
                    total_yielded += 1

                    if max_results and total_yielded >= max_results:
                        lazy_logger.debug('Reached max_results: %d', max_results)
                        return

                # If we got fewer results than requested, we're done
                if len(posts) < batch_limit:
                    lazy_logger.debug(
                        'Received fewer posts than requested (%d < %d), stopping',
                        len(posts),
                        batch_limit,
                    )
                    break

                page += 1

            except PararamioRequestError as e:
                lazy_logger.error('Search failed at page %d: %s', page, e)
                break

    @classmethod
    async def search_posts(
        cls,
        client: AsyncPararamio,
        q: str,
        *,
        order_type: str = 'time',
        page: int = 1,
        chat_ids: list[int] | None = None,
        limit: int | None = POSTS_LIMIT,
    ) -> tuple[int, AsyncIterator[Post]]:
        """Search for posts across chats.

        Uses chat_ids parameter for chat filtering.
        Note: This endpoint is not in the official documentation but works in practice.

        Args:
            client: AsyncPararamio client
            q: Search query
            order_type: Sort order type (default: 'time')
            page: Page number (default: 1)
            chat_ids: Optional list of chat IDs to search within
            limit: Maximum results (API requires minimum 10)

        Returns:
            Tuple of (total_count, async_iterator_of_posts)
        """
        url = cls._build_search_url(q, order_type, page, chat_ids, limit)
        response = await client.api_get(url, response_model=PostsResponse)

        if 'posts' not in response:
            raise PararamioRequestError('failed to perform search')

        posts_data = response['posts']
        # Apply client-side limit if requested limit is less than API minimum (10)
        if limit and limit < 10 and limit < len(posts_data):
            posts_data = posts_data[:limit]

        posts = cls._create_posts_from_data(client, posts_data)
        total_count = response.get('count') or len(posts)

        async def posts_iterator() -> AsyncIterator[Post]:
            """Async generator to yield posts."""
            for post in posts:
                yield post

        return total_count, posts_iterator()

    @classmethod
    def _create_posts_from_data(
        cls,
        client: AsyncPararamio,
        posts_data: list[PostResponseItem],
    ) -> list[Post]:
        """Create post-objects from search results data."""
        created_chats: dict[int, Chat] = {}
        posts: list[Post] = []

        for post_data in posts_data:
            chat_id = post_data.get('chat_id')
            post_no = post_data.get('post_no')

            # Skip posts without required data
            if not isinstance(chat_id, int) or not isinstance(post_no, int):
                continue

            if chat_id not in created_chats:
                created_chats[chat_id] = cls(client, id=chat_id)
            post = Post(created_chats[chat_id], post_no=post_no)
            posts.append(post)

        return posts

    async def create_post(
        self,
        text: str,
        reply_to_post_no: int | None = None,
        quote_text: str | None = None,
    ) -> Post:
        """Create post in chat (alias for send_message).

        Args:
            text: Post text
            reply_to_post_no: Optional post number to reply to
            quote_text: Optional quote text

        Returns:
            Created post
        """
        return await self.send_message(text, reply_to_post_no, quote_text)

    async def post(
        self,
        text: str,
        quote_range: QuoteRangeT | None = None,
        reply_no: int | None = None,
        attachments: list[Attachment] | None = None,
    ) -> Post:
        """Create post in chat with optional attachments.

        Args:
            text: Post text
            quote_range: Optional quote range with text
            reply_no: Optional post number to reply to
            attachments: Optional list of attachments

        Returns:
            Created post
        """
        if self.id is None:
            raise ValueError('can not post file to new chat')

        _attachments = []
        for attachment in attachments or []:
            _attach = await self.upload_file(
                attachment.fp,
                filename=attachment.guess_filename,
                content_type=attachment.guess_content_type,
                reply_no=reply_no,
            )
            _attachments.append(_attach)

        return await Post.create(
            self,
            text=text,
            reply_no=reply_no,
            quote=str(quote_range['text']) if quote_range and quote_range.get('text') else None,
            attachments=[attach.guid for attach in _attachments],
        )

    @classmethod
    async def search(
        cls,
        client: AsyncPararamio,
        query: str,
        *,
        chat_type: str = 'all',
        visibility: str = 'all',
    ) -> list[Chat]:
        """Search for chats.

        Args:
            client: AsyncPararamio client instance
            query: Search string
            chat_type: Filter by type (all, private, group, etc.)
            visibility: Filter by visibility (all, visible, hidden)

        Returns:
            List of Chat objects matching the search criteria
        """
        url = f'/core/chat/search?flt={quote(query)}&type={chat_type}&visibility={visibility}'
        response = await client.api_get(url, response_model=ChatSearchResponse)

        # Create Chat objects from the thread data
        threads = response.get('threads', [])
        return [cls(client, **thread_data) for thread_data in threads]

    async def get_post(self, post_no: int) -> Post:
        """Get post by number."""
        posts = await self.load_posts(start_post_no=post_no, end_post_no=post_no)
        return posts[0]
