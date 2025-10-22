# Pararamio - Python Client for pararam.io

Python client library for pararam.io platform with lazy loading and automatic API calls.

## Installation

```bash
pip install pararamio
```

## Quick Start

```python
from pararamio import Pararamio

# Initialize client
client = Pararamio(
    login="your_login",
    password="your_password",
    key="your_api_key"
)

# Authenticate
client.authenticate()

# Search users with lazy loading
users = client.search_user("test")
for user in users:
    print(f"User: {user.name}")  # Automatically loads data

# Get chats
chats = list(client.list_chats())
for chat in chats:
    print(f"Chat: {chat.title}")  # Lazy loaded

    # Get recent posts
    posts = chat.posts(start_post_no=-10, end_post_no=-1)
    for post in posts:
        print(f"  {post.text}")
```

## Features

- **Lazy Loading**: Automatic data loading on attribute access
- **Full API Coverage**: Complete pararam.io API support
- **Cookie Management**: Persistent session handling
- **Type Hints**: Full typing support
- **File Handling**: Upload/download support
- **Search**: Users, groups, posts search
- **Real-time**: Activity tracking

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api/)
- [Advanced Usage](docs/advanced-usage.md)
- [Error Handling](docs/error-handling.md)

## Async Version

For async/await support, install the async version:

```bash
pip install pararamio-aio
```

## License

MIT License
