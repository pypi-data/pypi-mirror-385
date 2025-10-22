"""Tests for MCP namespace utilities.

Tests the Chora MCP Conventions v1.0 implementation including tool naming,
resource URI generation, parsing, and validation functions.
"""

import pytest
from mcp_n8n.mcp import (
    ENABLE_NAMESPACING,
    ENABLE_RESOURCE_URIS,
    ENABLE_VALIDATION,
    NAMESPACE,
    make_resource_uri,
    make_tool_name,
    parse_resource_uri,
    parse_tool_name,
    validate_resource_uri,
    validate_tool_name,
)


class TestToolNaming:
    """Tests for tool name generation and parsing."""

    def test_make_tool_name_with_namespacing(self) -> None:
        """Test creating namespaced tool names."""
        assert ENABLE_NAMESPACING is True
        assert make_tool_name("create_task") == f"{NAMESPACE}:create_task"
        assert make_tool_name("list_items") == f"{NAMESPACE}:list_items"

    def test_parse_tool_name_valid(self) -> None:
        """Test parsing valid namespaced tool names."""
        namespace, tool = parse_tool_name(f"{NAMESPACE}:create_task")
        assert namespace == NAMESPACE
        assert tool == "create_task"

    def test_parse_tool_name_no_namespace(self) -> None:
        """Test parsing tool name without namespace raises error."""
        with pytest.raises(ValueError, match="missing namespace separator"):
            parse_tool_name("standalone_tool")

    def test_validate_tool_name_valid(self) -> None:
        """Test validating correct tool names."""
        if ENABLE_VALIDATION:
            # Should not raise
            validate_tool_name(f"{NAMESPACE}:create_task")
            validate_tool_name(f"{NAMESPACE}:list_items")

    def test_validate_tool_name_wrong_namespace(self) -> None:
        """Test validation fails for wrong namespace."""
        if ENABLE_VALIDATION:
            with pytest.raises(ValueError, match="Wrong namespace"):
                validate_tool_name("other:create_task", expected_namespace=NAMESPACE)

    def test_validate_tool_name_missing_namespace(self) -> None:
        """Test validation fails when namespace required but missing."""
        if ENABLE_VALIDATION and ENABLE_NAMESPACING:
            with pytest.raises(ValueError, match="Must match pattern"):
                validate_tool_name("CreateTask")


class TestResourceURIs:
    """Tests for resource URI generation and parsing."""

    def test_make_resource_uri_basic(self) -> None:
        """Test creating basic resource URIs."""
        assert ENABLE_RESOURCE_URIS is True
        uri = make_resource_uri("templates", "daily-report.md")
        assert uri == f"{NAMESPACE}://templates/daily-report.md"

    def test_make_resource_uri_with_query(self) -> None:
        """Test creating resource URIs with query parameters."""
        uri = make_resource_uri(
            "templates", "report.md", query={"format": "markdown", "version": "1"}
        )
        assert uri.startswith(f"{NAMESPACE}://templates/report.md?")
        assert "format=markdown" in uri
        assert "version=1" in uri

    def test_parse_resource_uri_basic(self) -> None:
        """Test parsing basic resource URIs."""
        uri = f"{NAMESPACE}://templates/daily-report.md"
        namespace, resource_type, resource_id, query = parse_resource_uri(uri)
        assert namespace == NAMESPACE
        assert resource_type == "templates"
        assert resource_id == "daily-report.md"
        assert query is None

    def test_parse_resource_uri_with_query(self) -> None:
        """Test parsing resource URIs with query parameters."""
        uri = f"{NAMESPACE}://templates/report.md?format=json&version=2"
        namespace, resource_type, resource_id, query = parse_resource_uri(uri)
        assert namespace == NAMESPACE
        assert resource_type == "templates"
        assert resource_id == "report.md"
        assert query == {"format": "json", "version": "2"}

    def test_parse_resource_uri_no_namespace(self) -> None:
        """Test parsing URI without namespace scheme raises error."""
        with pytest.raises(ValueError, match="Missing '://' separator"):
            parse_resource_uri("/templates/report.md")

    def test_validate_resource_uri_valid(self) -> None:
        """Test validating correct resource URIs."""
        if ENABLE_VALIDATION:
            # Should not raise
            validate_resource_uri(f"{NAMESPACE}://templates/daily-report.md")
            validate_resource_uri(f"{NAMESPACE}://configs/event-router.yaml")

    def test_validate_resource_uri_wrong_namespace(self) -> None:
        """Test validation fails for wrong namespace."""
        if ENABLE_VALIDATION:
            with pytest.raises(ValueError, match="Wrong namespace"):
                validate_resource_uri(
                    "other://templates/report.md", expected_namespace=NAMESPACE
                )

    def test_validate_resource_uri_missing_namespace(self) -> None:
        """Test validation fails when namespace required but missing."""
        if ENABLE_VALIDATION and ENABLE_RESOURCE_URIS:
            with pytest.raises(ValueError, match="Must match pattern"):
                validate_resource_uri("/templates/report.md")


class TestNamespaceConstants:
    """Tests for namespace configuration constants."""

    def test_namespace_format(self) -> None:
        """Test namespace follows conventions (3-20 chars, lowercase alphanumeric)."""
        assert len(NAMESPACE) >= 3
        assert len(NAMESPACE) <= 20
        assert NAMESPACE.islower()
        assert NAMESPACE.isalnum()

    def test_namespace_value(self) -> None:
        """Test namespace matches expected value for mcp-n8n."""
        assert NAMESPACE == "mcpn8n"

    def test_configuration_flags(self) -> None:
        """Test configuration flags are set correctly."""
        assert ENABLE_NAMESPACING is True
        assert ENABLE_RESOURCE_URIS is True
        assert ENABLE_VALIDATION is True
