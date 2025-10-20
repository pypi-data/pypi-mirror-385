# 🎯 quotely

[![PyPI Version](https://img.shields.io/pypi/v/quotely?style=for-the-badge&logo=pypi&logoColor=white&color=blue)](https://pypi.org/project/quotely/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=open-source-initiative&logoColor=white)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000?style=for-the-badge&logo=python&logoColor=white)](https://github.com/psf/black)


> **A minimalist Python library delivering 500+ curated motivational quotes from history's most influential minds.**

---

## Overview

**quotely** provides instant access to hundreds of verified, high-quality motivational quotes—perfect for command-line tools, chatbots, dashboards, and educational apps.  
Built with modern Python best practices, it's dependency-free, type-hinted, and lightweight.

---

## Installation

```bash
pip install quotely
```

For local development with linting and testing tools:

```bash
pip install quotely[dev]
```

**Requirements:** Python 3.8 or higher

---

## Quick Start

```python
from quotely import random, quote

# Get a random quote
print(random(quote))

# Get quote with author
print(random.name(quote))
```

**Example Output:**

```
"The only way to do great work is to love what you do." - Steve Jobs
```

---

## API Reference

### `random(quote)`

Returns a random quote (text only).

```python
text = random(quote)
```

---

### `random.name(quote)`

Returns a random quote with author attribution.

```python
full = random.name(quote)
# → "Success is not final, failure is not fatal..." - Winston Churchill
```

---

### `get_random_quote()`

Returns a structured `Quote` object for detailed access.

```python
from quotely import get_random_quote

q = get_random_quote()
print(str(q))   # Quote text
print(q.name)   # Author
print(repr(q))  # "Quote" - Author
```

---

## Example Use Cases

### Command-Line Tools

```python
import argparse
from quotely import random, quote

parser = argparse.ArgumentParser()
parser.add_argument("--inspire", action="store_true")
args = parser.parse_args()

if args.inspire:
    print(f"\n✨ {random.name(quote)}\n")
```

### Daily Motivation

```python
from quotely import random, quote

print("═" * 40)
print("💡 Your Daily Motivation")
print("═" * 40)
print(random.name(quote))
```

### Chatbot Integration

```python
from quotely import get_random_quote

def get_motivation():
    q = get_random_quote()
    return {
        "text": str(q),
        "author": q.name,
        "full": repr(q)
    }
```

---

## Technical Details

| Feature | Description |
|---------|-------------|
| **Dependencies** | None |
| **Memory Optimization** | Uses `__slots__` (~40% less overhead) |
| **Thread Safety** | Random selection is concurrency-safe |
| **Type Hints** | Fully typed for IDE autocomplete |
| **Tests** | 100% coverage via pytest |

---

## Development

```bash
# Run tests
pytest

# Format with Black
black quotely

# Type check
mypy quotely
```

---

## License

Licensed under the **MIT License**.  
See [LICENSE](LICENSE) for full text.

---

## Credits

Quotes are sourced from verified public domain and attributed works for educational and inspirational use.

**Author:** MJ Dev  
**Contact:** [themjdev@gmail.com](mailto:themjdev@gmail.com)  
**Project Page:** [PyPI: quotely](https://pypi.org/project/quotely/)

---

*"The only way to do great work is to love what you do." — Steve Jobs*
