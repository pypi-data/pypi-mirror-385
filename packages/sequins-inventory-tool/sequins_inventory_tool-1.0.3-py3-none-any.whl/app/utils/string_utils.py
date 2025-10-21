"""
This module provides utility functions for string manipulation.
"""

import re


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name)
    return re.sub(r'[\s\-]+', '_', name).lower()


def to_screaming_snake_case(name: str) -> str:
    """Convert a string to SCREAMING_SNAKE_CASE."""
    return to_snake_case(name).upper()


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])
