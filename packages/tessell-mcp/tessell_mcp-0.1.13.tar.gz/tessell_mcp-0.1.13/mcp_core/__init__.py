"""
mcp_core module

Why separate auth_config and app config modules?
- auth_config (mcp_core/auth_config.py) is context-specific: it manages authentication and environment variables that may differ per request or per user (e.g., per-thread or per-session).
- app config (mcp_core/app_config.py) is application-wide: it manages global flags (like readonly) that are constant for the entire app lifetime and do not change per request.
"""
