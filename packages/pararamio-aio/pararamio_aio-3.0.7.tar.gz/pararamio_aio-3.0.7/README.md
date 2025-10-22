# Pararamio AIO

Async Python API client for [pararam.io](https://pararam.io) platform.

## Features

- ⚡ **Async/Await**: Modern asynchronous interface with aiohttp
- 🚀 **Explicit Loading**: Predictable API calls with explicit `load()` methods
- 🍪 **Cookie Persistence**: Automatic session management
- 🔐 **Two-Factor Authentication**: Built-in 2FA support
- 🐍 **Type Hints**: Full typing support for better IDE experience

## Installation

```bash
pip install pararamio-aio
```

## Quick Start

```python
import asyncio
from pararamio_aio import AsyncPararamio
from pararamio_aio import AsyncFileCookieManager

async def main():
    # Initialize cookie manager for persistent authentication
    cookie_manager = AsyncFileCookieManager("session.cookie")

    # Initialize client
    async with AsyncPararamio(
        login="your_login",
        password="your_password",
        key="your_2fa_key",
        cookie_manager=cookie_manager
    ) as client:
        # Authenticate
        await client.authenticate()

        # Search for users - returns User objects (clean names!)
        users = await client.search_users("John")
        for user in users:
            print(f"{user.name}")

        # Get chat messages - returns Chat and Post objects
        chat = await client.get_chat_by_id(12345)
        posts = await chat.get_posts(limit=10)
        for post in posts:
            await post.load()  # Explicit loading
            print(f"{post.author.name}: {post.text}")

asyncio.run(main())
```

## Manual Session Management

If you prefer not to use context managers, you can use `connect()` and `close()` methods for manual session management:

```python
import asyncio
from pararamio_aio import AsyncPararamio

async def main():
    client = AsyncPararamio(
        login="your_login",
        password="your_password",
        key="your_2fa_key"
    )

    # Connect and initialize session
    await client.connect()

    try:
        # Work with API
        profile = await client.get_profile()
        print(profile)

        users = await client.search_users("friend")
        for user in users:
            print(user.name)
    finally:
        # Always close to save cookies and release resources
        await client.close()

    # Session can be reconnected after close
    await client.connect()
    profile = await client.get_profile()
    await client.close()

asyncio.run(main())
```

> **Note**: The `connect()` method initializes the session, loads cookies, and checks authentication.
> The `close()` method saves cookies and closes the HTTP session.

## Explicit Loading

Unlike the sync version, pararamio-aio uses explicit loading for predictable async behavior:

```python
from pararamio_aio import AsyncPararamio

async def main():
    # Get user object
    client = AsyncPararamio(
        login="user",
        password="pass",
        key="key",
    )
    await client.authenticate()
    user = await client.get_user_by_id(123)
    print(user.name)  # Basic data is already loaded

    # Load full profile data explicitly
    await user.load()
    print(user.bio)  # Now additional data is available

    # Load specific relations
    posts = await user.get_posts()
    for post in posts:
        await post.load()  # Load each post's content

# Run the async function
import asyncio
asyncio.run(main())
```

## Cookie Management

The async client supports multiple cookie storage options:

### Default (In-Memory)
```python
from pararamio_aio import AsyncPararamio


async def main():
    # By default, uses AsyncInMemoryCookieManager (no persistence)
    async with AsyncPararamio(
            login="user",
            password="pass",
            key="key"
    ) as client:
        await client.authenticate()
        # Cookies are stored in memory only during the session


# Run the async function
import asyncio

asyncio.run(main())
```

### File-based Persistence
```python
from pararamio_aio import AsyncFileCookieManager, AsyncPararamio

async def main():
    # Create a cookie manager for persistent storage
    cookie_manager = AsyncFileCookieManager("session.cookie")

    # First run - authenticates with credentials
    async with AsyncPararamio(
        login="user",
        password="pass",
        key="key",
        cookie_manager=cookie_manager
    ) as client:
        await client.authenticate()

    # Later runs - uses saved cookie
    cookie_manager2 = AsyncFileCookieManager("session.cookie")
    async with AsyncPararamio(cookie_manager=cookie_manager2) as client:
        # Already authenticated!
        profile = await client.get_profile()

# Run the async function
import asyncio
asyncio.run(main())
```

## Concurrent Operations

Take advantage of async for concurrent operations:

```python
import asyncio
async def get_multiple_users(client, user_ids):
    # Fetch all users concurrently
    tasks = [client.get_user_by_id(uid) for uid in user_ids]
    users = await asyncio.gather(*tasks)

    # Load all profiles concurrently
    await asyncio.gather(*[user.load() for user in users])

    return users
```

## API Reference

### Client Methods

All methods are async and must be awaited:

- `authenticate()` - Authenticate with the API
- `search_users(query)` - Search for users
- `get_user_by_id(user_id)` - Get user by ID
- `get_users_by_ids(ids)` - Get multiple users
- `get_chat_by_id(chat_id)` - Get a chat by ID
- `search_groups(query)` - Search for groups
- `create_chat(title, description)` - Create new chat

### Model Objects

All models have async methods:

- `User` - User profile
  - `load()` - Load full profile
  - `get_posts()` - Get user's posts
  - `get_groups()` - Get user's groups

- `Chat` - Chat/conversation
  - `load()` - Load chat details
  - `get_posts(limit, offset)` - Get messages
  - `send_message(text)` - Send a message

- `Post` - Message/post
  - `load()` - Load post content
  - `delete()` - Delete post

- `Group` - Community group
  - `load()` - Load group details
  - `members` - Get member list (property)

## Error Handling

```python
from pararamio_aio import AsyncPararamio
from pararamio_aio.exceptions import PararamioAuthenticationError, PararamioHTTPRequestError



async def main():
    async with AsyncPararamio(login="user", password="pass", key="key") as client:
        try:
            await client.authenticate()
        except PararamioAuthenticationError as e:
            print(f"Authentication failed: {e}")
        except PararamioHTTPRequestError as e:
            print(f"HTTP error {e.code}: {e.message}")


# Run the async function
import asyncio

asyncio.run(main())
```

## Advanced Usage

### Custom Session

```python
import httpx
from pararamio_aio import AsyncPararamio


async def main():
    # Create custom httpx client with specific timeout and limits
    timeout = httpx.Timeout(timeout=60.0, connect=10.0)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=100)

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as session:
        async with AsyncPararamio(session=session, login="user", password="pass", key="key") as client:
            # Client will use your custom session
            await client.authenticate()

            # Perform operations
            user = await client.get_user_by_id(123)
            await user.load()


# Run the async function
import asyncio

asyncio.run(main())
```

### Rate Limiting

The client automatically handles rate limiting:

```python
from pararamio_aio import AsyncPararamio

client = AsyncPararamio(
    login="user",
    password="pass",
    key="key",
    wait_auth_limit=True,  # Wait instead of failing on rate limit
)
```

## Migration from Sync Version

If you're migrating from the synchronous `pararamio` package:

1. Add `async`/`await` keywords
2. Use async context manager (`async with`)
3. Call `load()` explicitly when needed
4. Use `asyncio.gather()` for concurrent operations

Example migration:

```python
from pararamio import Pararamio
from pararamio_aio import AsyncPararamio


async def main():
    # Sync version
    client = Pararamio()
    user = client.get_user_by_id(123)
    print(user.bio)  # Lazy loaded

    # Async version
    async with AsyncPararamio(login="user", password="pass", key="key") as client:
        user = await client.get_user_by_id(123)
        await user.load()  # Explicit load
        print(user.bio)


# Run the async function
import asyncio

asyncio.run(main())
```

## License

MIT License—see LICENSE file for details.
