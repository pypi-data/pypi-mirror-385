# Smart Slugify

A lightweight (0 dependency), smart Python library for converting text into URL-friendly slugs with Unicode support, accent normalization, and customizable options.

[![CI](https://github.com/ali-hai-der/smart-slugify/actions/workflows/ci.yml/badge.svg)](https://github.com/ali-hai-der/smart-slugify/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/smart-slugify.svg)](https://badge.fury.io/py/smart-slugify)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Smart Text Normalization**: Automatically handles Unicode characters and removes diacritics  
🌍 **International Support**: Works seamlessly with non-ASCII characters (Chinese, Arabic, Cyrillic, etc.)  
⚙️ **Customizable**: Configure separator, casing, and maximum length  
🚀 **Fast & Lightweight**: No external dependencies, pure Python  
🧪 **Well-Tested**: Comprehensive test suite included  

## Installation

### Using pip

```bash
pip install smart-slugify
```

### From Source

```bash
git clone https://github.com/ali-hai-der/smart-slugify.git
cd smart-slugify
pip install -e .
```

## Quick Start

```python
from smart_slugify import slugify

# Basic usage
slugify("Hello World!")
# Output: 'hello-world'

# Handles Unicode and accents automatically
slugify("C'est déjà l'été!")
# Output: 'c-est-deja-l-ete'
```

## Usage Examples

### Basic Text Conversion

```python
from smart_slugify import slugify

# Simple text
slugify("Hello World!")
# 'hello-world'

# Multiple spaces and special characters
slugify("Hello   World!!! How are you?")
# 'hello-world-how-are-you'

# Numbers are preserved
slugify("Python 3.11 Released!")
# 'python-3-11-released'
```

### Unicode and Accent Handling

Smart Slugify automatically normalizes Unicode characters and removes diacritics:

```python
# French
slugify("C'est déjà l'été!")
# 'c-est-deja-l-ete'

# Spanish
slugify("¿Cómo estás?")
# 'como-estas'

# Portuguese
slugify("São Paulo")
# 'sao-paulo'

# German
slugify("Über uns")
# 'uber-uns'

# Mixed content
slugify("Café au lait & crème brûlée")
# 'cafe-au-lait-creme-brulee'
```

### Custom Separators

Change the default separator from hyphen to any character:

```python
# Underscore separator
slugify("Hello World!", separator="_")
# 'hello_world'

# Dot separator
slugify("My Blog Post", separator=".")
# 'my.blog.post'

# No separator (empty string)
slugify("Hello World", separator="")
# 'helloworld'
```

### Case Sensitivity

Control whether the output should be lowercase:

```python
# Default: lowercase
slugify("Hello World")
# 'hello-world'

# Preserve original case
slugify("Hello World", lowercase=False)
# 'Hello-World'

# Mixed case with underscores
slugify("iPhone 15 Pro", lowercase=False, separator="_")
# 'iPhone_15_Pro'
```

### Maximum Length

Truncate slugs to a specific length:

```python
# Truncate at 10 characters
slugify("hello world example", max_length=10)
# 'hello-wor'

# Smart truncation removes trailing separators
slugify("hello-world-test", max_length=12)
# 'hello-world'  (not 'hello-world-')

# Long URLs
slugify("This is a very long article title that needs to be shortened", max_length=30)
# 'this-is-a-very-long-article-t'
```

### Edge Cases

Smart Slugify handles edge cases gracefully:

```python
# Empty string
slugify("")
# ''

# None input
slugify(None)
# ''

# Only special characters
slugify("!!@@##$$")
# ''

# Leading/trailing spaces and separators
slugify("  Hello World  ")
# 'hello-world'
```

### Real-World Examples

```python
# Blog post URL
title = "10 Tips for Better Python Code in 2024"
slug = slugify(title)
# '10-tips-for-better-python-code-in-2024'
url = f"https://myblog.com/posts/{slug}"

# Product slugs for e-commerce
product = "MacBook Pro 16\" (2024) - Space Gray"
product_slug = slugify(product)
# 'macbook-pro-16-2024-space-gray'

# User-friendly file names
filename = "My Résumé - Software Engineer.pdf"
safe_filename = slugify(filename, separator="_")
# 'my_resume_software_engineer_pdf'

# Category paths
category = "Fashion & Accessories / Women's Clothing"
category_path = slugify(category, separator="/")
# 'fashion-accessories/women-s-clothing'
```

## API Reference

### `slugify(text, lowercase=True, separator='-', max_length=None)`

Converts input text into a URL-friendly slug.

**Parameters:**

- `text` (str): The input text to slugify. Can be `None` (returns empty string).
- `lowercase` (bool, optional): Convert to lowercase. Default: `True`.
- `separator` (str, optional): Character to use as separator. Default: `'-'`.
- `max_length` (int, optional): Maximum length of the slug. Default: `None` (no limit).

**Returns:**

- `str`: The slugified text.

**Processing Steps:**

1. Normalizes Unicode to NFKD form
2. Removes diacritical marks (accents)
3. Converts to lowercase (if enabled)
4. Replaces non-alphanumeric characters with separator
5. Collapses multiple consecutive separators into one
6. Strips leading and trailing separators
7. Truncates to `max_length` (if specified)
8. Removes trailing separators after truncation

## Development

### Running Tests

```bash
# Install pytest if you haven't already
pip install pytest

# Run tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run with coverage
pip install pytest-cov
pytest --cov=smart_slugify tests/
```

### Project Structure

```
smart-slugify/
├── src/
│   └── smart_slugify/
│       ├── __init__.py
│       └── slugify.py
├── tests/
│   └── test_slugify.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please make sure to:
- Add tests for new features
- Update documentation as needed
- Follow PEP 8 style guidelines
- Write clear commit messages

## Use Cases

- **Web Applications**: Generate SEO-friendly URLs for blog posts, articles, and pages
- **E-commerce**: Create readable product URLs
- **CMS Systems**: Auto-generate slugs from user-provided titles
- **File Management**: Convert file names to safe, filesystem-friendly names
- **APIs**: Create consistent, readable endpoint identifiers
- **Database Keys**: Generate human-readable unique identifiers

## Why Smart Slugify?

- **No Dependencies**: Pure Python implementation with no external packages
- **Unicode-First**: Properly handles international characters out of the box
- **Battle-Tested**: Based on best practices from popular slugify implementations
- **Flexible**: Customizable to fit your specific needs
- **Lightweight**: Minimal footprint, fast performance

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Haider Ali**  
Email: malikhaider0567@gmail.com

## Acknowledgments

- Inspired by Django's `slugify` utility
- Unicode normalization based on Python's `unicodedata` module

## Changelog

### Version 0.1.0 (Initial Release)
- Basic slugification with Unicode support
- Configurable separator and casing
- Maximum length truncation
- Comprehensive test suite

---

**Star ⭐ this repository if you find it useful!**

