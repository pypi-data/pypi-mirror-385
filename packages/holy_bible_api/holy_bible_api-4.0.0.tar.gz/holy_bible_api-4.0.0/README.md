# Holy Bible API Python Client

A Python client library for accessing the Holy Bible API with full type support.

## Installation

```bash
pip install holy_bible_api
```

## Usage

### Basic Usage

```python
from holy_bible_api import create_bible_api

# Create an API client
api = create_bible_api()

# Make API calls
bibles = api.get_bibles()
```

### With Type Hints

```python
from holy_bible_api import (
    create_bible_api,
    DefaultApi,
    Bible,
    BibleVerse,
    GetBiblesRes,
    GetBibleVersesRes,
)

# Create a typed API client
api: DefaultApi = create_bible_api()

# Get bibles with type hints
bibles_response: GetBiblesRes = api.get_bibles()
bible: Bible = bibles_response.data[0]

# Get verses with type hints
verses_response: GetBibleVersesRes = api.get_bible_verses(
    bible_id=bible.id,
    book=1,
    chapter=1
)
verse: BibleVerse = verses_response.data[0]
print(f"{verse.book}:{verse.chapter}:{verse.verse} - {verse.text}")
```

### Custom Host

```python
from holy_bible_api import create_bible_api

# Use a custom API host
api = create_bible_api(url="https://custom-host.com")
```

## Available Types

The following types are exported for use:

### API Classes
- `DefaultApi` - Main API client
- `ApiClient` - Low-level HTTP client
- `Configuration` - API configuration
- `ApiResponse` - API response wrapper

### Models
- `Bible` - Bible metadata
- `BibleVerse` - Bible verse data
- `AudioBible` - Audio bible metadata
- `GetBiblesRes` - Response for getting bibles
- `GetBibleVersesRes` - Response for getting verses
- `GetBibleBooksRes` - Response for getting books
- `GetBibleChaptersRes` - Response for getting chapters
- `GetAudioBiblesRes` - Response for getting audio bibles
- `GetAudioBooksRes` - Response for getting audio books
- `GetAudioChaptersRes` - Response for getting audio chapters

### Exceptions
- `OpenApiException` - Base exception
- `ApiTypeError` - Type error
- `ApiValueError` - Value error
- `ApiKeyError` - Key error
- `ApiAttributeError` - Attribute error
- `ApiException` - General API exception

## Type Checking

This package includes `py.typed` marker file for full type checking support with mypy, pyright, and other type checkers.

## License

[Your License Here]

