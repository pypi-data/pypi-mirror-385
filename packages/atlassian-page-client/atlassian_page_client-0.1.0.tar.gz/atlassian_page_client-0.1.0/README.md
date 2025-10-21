# Atlassian Page Client

A Python client library for interacting with Atlassian Confluence pages through the REST API.

## Features

- Simple authentication using email and API token
- Read and modify Confluence page content
- Parse and manipulate HTML content with BeautifulSoup
- Update page versions automatically
- Easy-to-use API for common operations

## Installation

```bash
pip install atlassian-page-client
```

## Quick Start

```python
from atlassian_page_client import AtlassianPageClient

# Initialize the client
client = AtlassianPageClient(
    email="your.email@example.com",
    token="your_api_token", 
    base_url="https://yourcompany.atlassian.net"
)

# Get a page
page = client.get("page_id_here")

# Get the page content for editing
content = page.get_working_page_content()

# Get root element
root = content.get_root()
root.append(content.new_tag('p', string='Hello root'))

# Or find elements by attribute
table = content.find_by_Attribute('ac:local-id', 'table-id')

# Create new elements
new_row = content.new_tag('tr')
cell = content.new_tag('td')
cell.append(content.new_tag('p', string='Hello World'))
new_row.append(cell)

# Add to existing content
table.append(new_row)

# Update the page
updated_page = client.put(page)
```

## API Reference

### AtlassianPageClient

The main client class for interacting with the Atlassian API.

```python
client = AtlassianPageClient(email, token, base_url)
```

#### Methods

- `get(page_id: str) -> AtlassianPage`: Retrieve a page by its ID
- `put(page: AtlassianPage) -> AtlassianPage`: Update a page with modifications

### AtlassianPage

Represents a Confluence page with its content and metadata.

#### Methods

- `get_page_id() -> str`: Get the page ID
- `get_working_page_content() -> AtlassianPageContent`: Get the editable content
- `prettify() -> str`: Get a pretty-printed JSON representation
- `increase_version()`: Increment the page version (called automatically by client.put())

### AtlassianPageContent

Handles the HTML content of a page using BeautifulSoup for parsing and manipulation.

#### Methods

- `find_by_Attribute(attribute_name: str, value: str) -> bs4.element.Tag`: Find element by attribute
- `new_tag(tag_name: str, **kwargs) -> bs4.element.Tag`: Create a new HTML tag
- `get_root() -> bs4.element.Tag`: Get the root BeautifulSoup element
- `prettify() -> str`: Get pretty-printed HTML

## Authentication

You'll need:
1. Your Atlassian email address
2. An API token (create one at https://id.atlassian.com/manage-profile/security/api-tokens)
3. Your Atlassian base URL (e.g., https://yourcompany.atlassian.net)

## Requirements

- Python 3.7+
- requests >= 2.25.0
- beautifulsoup4 >= 4.9.0

## Development

To set up for development:

```bash
git clone https://github.com/yourusername/py-atlassian-page-client.git
cd py-atlassian-page-client
pip install -e .[dev]
```

### Running Tests

The package includes a comprehensive test suite with unit tests, integration tests, and coverage reporting.

**Quick test run:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=atlassian_page_client --cov-report=term-missing
```

**Run specific test files:**
```bash
pytest tests/test_client.py -v
pytest tests/test_integration.py -v
```

**Use the test runner script:**
```bash
python run_tests.py
```

**Test structure:**
- `tests/test_client.py` - Tests for AtlassianPageClient
- `tests/test_page.py` - Tests for AtlassianPage
- `tests/test_content.py` - Tests for AtlassianPageContent  
- `tests/test_integration.py` - Integration tests
- `tests/test_package_imports.py` - Import and basic functionality tests
- `tests/conftest.py` - Shared test fixtures

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
