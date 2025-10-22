"""
app_config.py

This module manages application-wide (global) configuration flags (like readonly_db) that are constant for the entire app lifetime and do not change per request.
It is application-level, not context-specific.
See mcp_core/__init__.py for architectural rationale.
"""

_readonly_db = False

def set_readonly_db(value: bool):
    global _readonly_db
    _readonly_db = value

def get_readonly_db() -> bool:
    return _readonly_db 