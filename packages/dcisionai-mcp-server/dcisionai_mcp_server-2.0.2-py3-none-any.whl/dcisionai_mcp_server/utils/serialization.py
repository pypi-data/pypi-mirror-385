#!/usr/bin/env python3
"""
JSON serialization utilities
"""

from typing import Any, Dict, List, Union


def make_json_serializable(obj: Any) -> Any:
    """Recursively convert non-serializable objects to serializable format"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # Convert non-serializable objects to string
        return str(type(obj).__name__)
