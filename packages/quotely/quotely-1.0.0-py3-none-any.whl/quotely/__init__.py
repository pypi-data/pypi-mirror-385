"""quotely - Simple motivational quotes library.

Usage:
    from quotely import random, quote
    
    print(random(quote))        # Get random quote text
    print(random.name(quote))   # Get quote with author
"""

from .core import get_random_quote, quote, random

__version__ = "1.0.0"
__all__ = ["random", "quote", "get_random_quote"]
