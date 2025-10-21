import re
import datetime
from typing import Any


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case string to camelCase.
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def from_camel_case(camel_str: str, sep: str = '_') -> str:
    """
    Convert camelCase string to snake_case.
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1' + sep + r'\2', camel_str).lower()

def snake_to_pascal_case(snake_str: str) -> str:
    """
    Convert snake_case string to PascalCase.
    """
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def pascal_to_snake_case(pascal_str: str) -> str:
    """
    Convert PascalCase string to snake_case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', pascal_str).lower()

def serialize(data):
    """Serialization logic for dictionaries, lists, and strings."""
    if isinstance(data, dict):
        return {k: serialize(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [serialize(item) for item in data]
    if isinstance(data, datetime.datetime):
        return data.isoformat()
    return data

def deserialize(data: Any):
    """Deserialization logic for dictionaries, lists, and strings."""
    if isinstance(data, list):
        return [deserialize(item) for item in data]
    if isinstance(data, dict):
        return {k: deserialize(v) for k, v in data.items()}
    if isinstance(data, str):
        if data.lower() == 'true':
            return True
        if data.lower() == 'false':
            return False
        try:
            return datetime.datetime.fromisoformat(data)
        except ValueError:
            return data
    return data