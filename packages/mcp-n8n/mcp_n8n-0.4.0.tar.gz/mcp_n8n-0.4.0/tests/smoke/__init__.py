"""Smoke tests for mcp-n8n gateway.

These tests provide quick validation (<30 seconds) of core functionality:
- Gateway startup and initialization
- Namespace routing (chora:*, coda:*)
- Backend communication
- Error handling

Uses mock backends to avoid external dependencies.
"""
