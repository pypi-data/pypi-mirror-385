"""MCP naming conventions for mcp-n8n.

This module implements Chora MCP Conventions v1.0 for namespace management,
tool naming, and resource URI generation.

Reference: https://github.com/liminalcommons/chora-base/blob/main/docs/standards/CHORA_MCP_CONVENTIONS_v1.0.md
"""

import re

# === Namespace Configuration ===

NAMESPACE = "mcpn8n"
"""MCP namespace for mcp-n8n."""

ENABLE_NAMESPACING = True
"""Whether to use namespaced tool names (namespace:tool_name)."""

ENABLE_RESOURCE_URIS = True
"""Whether to use resource URI scheme (namespace://type/id)."""

ENABLE_VALIDATION = True
"""Whether to validate naming conventions at runtime."""

# === Validation Patterns ===

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9]{2,19}$")
"""Valid namespace: 3-20 chars, lowercase alphanumeric."""

TOOL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]+:[a-z][a-z0-9_]+$")
"""Valid tool name: namespace:tool_name (snake_case)."""

RESOURCE_URI_PATTERN = re.compile(r"^[a-z][a-z0-9]+://[a-z0-9_/\-\.]+(\?.*)?$")
"""Valid resource URI: namespace://type/id[?query]."""

# === Helper Functions ===


def make_tool_name(tool: str) -> str:
    """Generate namespaced tool name following Chora MCP Conventions v1.0.

    Args:
        tool: Tool name in snake_case (e.g., "create_task")

    Returns:
        Namespaced tool name if ENABLE_NAMESPACING=True (e.g., "mcpn8n:create_task"),
        otherwise returns tool name unchanged.

    Example:
        >>> make_tool_name("create_task")
        "mcpn8n:create_task"
    """
    if ENABLE_NAMESPACING:
        return f"{NAMESPACE}:{tool}"
    return tool


def make_resource_uri(
    resource_type: str, resource_id: str, query: dict[str, str] | None = None
) -> str:
    """Generate resource URI following Chora MCP Conventions v1.0.

    Args:
        resource_type: Resource type (e.g., "templates", "configs")
        resource_id: Resource identifier (e.g., "daily-report.md")
        query: Optional query parameters (e.g., {"format": "json", "limit": "10"})

    Returns:
        Resource URI in format: namespace://type/id[?key=value&...]

    Example:
        >>> make_resource_uri("templates", "daily-report.md")
        "mcpn8n://templates/daily-report.md"

        >>> make_resource_uri("docs", "123", {"format": "json"})
        "mcpn8n://docs/123?format=json"
    """
    uri = f"{NAMESPACE}://{resource_type}/{resource_id}"

    if query:
        params = "&".join(f"{k}={v}" for k, v in query.items())
        uri += f"?{params}"

    return uri


def parse_tool_name(full_name: str) -> tuple[str, str]:
    """Parse namespaced tool name into (namespace, tool) components.

    Args:
        full_name: Full tool name (e.g., "mcpn8n:create_task")

    Returns:
        Tuple of (namespace, tool_name)

    Raises:
        ValueError: If tool name doesn't contain namespace separator

    Example:
        >>> parse_tool_name("mcpn8n:create_task")
        ("mcpn8n", "create_task")
    """
    if ":" not in full_name:
        raise ValueError(
            f"Tool name '{full_name}' missing namespace separator. "
            f"Expected format: namespace:tool_name"
        )

    namespace, tool = full_name.split(":", 1)
    return namespace, tool


def parse_resource_uri(uri: str) -> tuple[str, str, str, dict[str, str] | None]:
    """Parse resource URI into components.

    Args:
        uri: Resource URI (e.g., "mcpn8n://templates/daily-report.md?format=json")

    Returns:
        Tuple of (namespace, resource_type, resource_id, query_params)

    Raises:
        ValueError: If URI doesn't match expected format

    Example:
        >>> parse_resource_uri("mcpn8n://templates/daily-report.md")
        ("mcpn8n", "templates", "daily-report.md", None)

        >>> parse_resource_uri("mcpn8n://docs/123?format=json&limit=10")
        ("mcpn8n", "docs", "123", {"format": "json", "limit": "10"})
    """
    # Split query params if present
    if "?" in uri:
        uri_base, query_str = uri.split("?", 1)
        query = dict(param.split("=", 1) for param in query_str.split("&"))
    else:
        uri_base = uri
        query = None

    # Parse URI components
    if "://" not in uri_base:
        raise ValueError(
            f"Invalid resource URI: {uri}. Missing '://' separator. "
            f"Expected format: namespace://type/id"
        )

    namespace, path = uri_base.split("://", 1)

    # Split path into type and id
    if "/" not in path:
        raise ValueError(
            f"Invalid resource URI: {uri}. Missing path separator. "
            f"Expected format: namespace://type/id"
        )

    parts = path.split("/", 1)
    resource_type = parts[0]
    resource_id = parts[1] if len(parts) > 1 else ""

    return namespace, resource_type, resource_id, query


# === Validation Functions ===


def validate_namespace(namespace: str) -> None:
    """Validate namespace follows Chora MCP Conventions v1.0.

    Args:
        namespace: Namespace to validate

    Raises:
        ValueError: If namespace doesn't match pattern

    Example:
        >>> validate_namespace("mcpn8n")  # OK
        >>> validate_namespace("My-Project")  # Raises ValueError
    """
    if not NAMESPACE_PATTERN.match(namespace):
        raise ValueError(
            f"Invalid namespace: {namespace}. "
            f"Must be lowercase, 3-20 chars, alphanumeric only. "
            f"Pattern: [a-z][a-z0-9]{{2,19}}"
        )


def validate_tool_name(name: str, expected_namespace: str | None = None) -> None:
    """Validate tool name follows Chora MCP Conventions v1.0.

    Args:
        name: Full tool name (e.g., "mcpn8n:create_task")
        expected_namespace: Expected namespace (defaults to NAMESPACE)

    Raises:
        ValueError: If tool name doesn't match pattern or wrong namespace

    Example:
        >>> validate_tool_name("mcpn8n:create_task")  # OK
        >>> validate_tool_name("CreateTask")  # ValueError
        >>> validate_tool_name("other:create_task", "mcpn8n")  # ValueError
    """
    if not ENABLE_VALIDATION:
        return

    if not TOOL_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid tool name: {name}. "
            f"Must match pattern: namespace:tool_name (snake_case). "
            f"Example: {expected_namespace or NAMESPACE}:create_task"
        )

    if expected_namespace:
        actual_ns, _ = name.split(":", 1)
        if actual_ns != expected_namespace:
            raise ValueError(
                f"Wrong namespace in tool name. "
                f"Expected: {expected_namespace}:*, got: {name}"
            )


def validate_resource_uri(uri: str, expected_namespace: str | None = None) -> None:
    """Validate resource URI follows Chora MCP Conventions v1.0.

    Args:
        uri: Resource URI (e.g., "mcpn8n://templates/daily-report.md")
        expected_namespace: Expected namespace (defaults to NAMESPACE)

    Raises:
        ValueError: If URI doesn't match pattern or wrong namespace

    Example:
        >>> validate_resource_uri("mcpn8n://templates/daily-report.md")
        >>> validate_resource_uri("/templates/daily-report.md")  # ValueError
        >>> validate_resource_uri("other://templates/report.md", "mcpn8n")
    """
    if not ENABLE_VALIDATION:
        return

    if not RESOURCE_URI_PATTERN.match(uri):
        raise ValueError(
            f"Invalid resource URI: {uri}. "
            f"Must match pattern: namespace://type/id[?query]. "
            f"Example: {expected_namespace or NAMESPACE}://templates/daily-report.md"
        )

    if expected_namespace:
        actual_ns = uri.split("://", 1)[0]
        if actual_ns != expected_namespace:
            raise ValueError(
                f"Wrong namespace in resource URI. "
                f"Expected: {expected_namespace}://*, got: {uri}"
            )


# Validate our own namespace on import
if ENABLE_VALIDATION:
    validate_namespace(NAMESPACE)


__all__ = [
    # Configuration
    "NAMESPACE",
    "ENABLE_NAMESPACING",
    "ENABLE_RESOURCE_URIS",
    "ENABLE_VALIDATION",
    # Patterns
    "NAMESPACE_PATTERN",
    "TOOL_NAME_PATTERN",
    "RESOURCE_URI_PATTERN",
    # Helper functions
    "make_tool_name",
    "make_resource_uri",
    "parse_tool_name",
    "parse_resource_uri",
    # Validation functions
    "validate_namespace",
    "validate_tool_name",
    "validate_resource_uri",
]
