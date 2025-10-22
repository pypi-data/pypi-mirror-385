# Intuned Browser SDK (Python)

Intuned's Python SDK for browser automation and web data extraction, designed to work seamlessly with the Intuned platform.

## Installation

### Using Poetry (Recommended)

```bash
poetry add intuned-browser
```

### Using pip

```bash
pip install intuned-browser
```

## Features

The Intuned Browser SDK provides a comprehensive set of tools for browser automation and data extraction:

### 🤖 AI-Powered Extraction

- **Structured Data Extraction** - Extract structured data from web pages using AI
- **Schema Validation** - Validate extracted data against JSON schemas
- **Smart Page Loading Detection** - Determine when pages have fully loaded

### 🌐 Web Automation Helpers

- **Navigation** - Advanced URL navigation with `go_to_url()`
- **Content Loading** - Scroll to load dynamic content with `scroll_to_load_content()`
- **Network Monitoring** - Wait for network activity with `wait_for_network_settled()`
- **DOM Monitoring** - Wait for DOM changes with `wait_for_dom_settled()`
- **Click Automation** - Click elements until exhausted with `click_untill_exhausted()`

### 📄 Content Processing

- **HTML Sanitization** - Clean and sanitize HTML with `sanitize_html()`
- **Markdown Extraction** - Convert HTML to markdown with `extract_markdown()`
- **URL Resolution** - Resolve relative URLs with `resolve_url()`
- **Date Processing** - Parse and process dates with `process_date()`

### 📁 File Operations

- **File Downloads** - Download files with `download_file()`
- **S3 Integration** - Upload and save files to S3 with `upload_file_to_s3()` and `save_file_to_s3()`

### ✅ Data Validation

- **Schema Validation** - Validate data structures with `validate_data_using_schema()`
- **Empty Value Filtering** - Filter empty values with `filter_empty_values()`

## Quick Start

```python
from intuned_browser import (
    extract_markdown,
    sanitize_html,
    go_to_url,
    wait_for_network_settled,
    validate_data_using_schema
)

# Example: Extract and process web content
async def extract_content(page):
    # Navigate to URL
    await go_to_url(page, "https://example.com")

    # Wait for network to settle
    await wait_for_network_settled(page)

    # Get and sanitize HTML
    html = await page.content()
    clean_html = sanitize_html(html)

    # Extract markdown
    markdown = extract_markdown(clean_html)

    return markdown
```

## AI-Powered Data Extraction

```python
from intuned_browser.ai import extract_structured_data
from intuned_browser.ai.types import JsonSchema

# Define your data schema
schema: JsonSchema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"},
        "description": {"type": "string"}
    },
    "required": ["title", "price"]
}

# Extract structured data using AI
async def extract_product_data(page):
    result = await extract_structured_data(
        page=page,
        schema=schema,
        prompt="Extract product information from this page"
    )
    return result
```

## Documentation

For detailed documentation on all functions and types, see the [documentation](https://docs.intunedhq.com/docs-old/getting-started/introduction).

## Support

For support, questions, or contributions, please contact the Intuned team at engineering@intunedhq.com.

## About Intuned

Intuned provides powerful tools for browser automation, web scraping, and data extraction. Visit [intunedhq.com](https://intunedhq.com) to learn more.
