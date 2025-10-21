"""Credential validation for backend integrations.

Validates that required credentials are present before executing workflows.
Uses generator dependency metadata from chora-compose v1.3.0+ to detect
required credentials and provide helpful error messages.
"""
# mypy: disable-error-code="attr-defined"

import logging
import os

from mcp_n8n.backends.base import Backend

logger = logging.getLogger(__name__)


class CredentialStatus:
    """Status of a single credential."""

    def __init__(
        self,
        name: str,
        required: bool,
        present: bool,
        description: str | None = None,
        service: str | None = None,
    ):
        self.name = name
        self.required = required
        self.present = present
        self.description = description
        self.service = service

    @property
    def status_emoji(self) -> str:
        """Get emoji for credential status."""
        if self.present:
            return "✅"
        elif self.required:
            return "❌"
        else:
            return "⚠️"

    def __str__(self) -> str:
        """String representation of credential status."""
        status = "present" if self.present else "missing"
        req = "required" if self.required else "optional"
        desc = f" ({self.description})" if self.description else ""
        return f"{self.status_emoji} {self.name}: {status} ({req}){desc}"


class CredentialValidationResult:
    """Result of credential validation for a backend."""

    def __init__(self, backend_name: str):
        self.backend_name = backend_name
        self.credentials: list[CredentialStatus] = []

    def add_credential(self, credential: CredentialStatus) -> None:
        """Add a credential to the validation result."""
        self.credentials.append(credential)

    @property
    def all_required_present(self) -> bool:
        """Check if all required credentials are present."""
        return all(cred.present for cred in self.credentials if cred.required)

    @property
    def missing_required(self) -> list[CredentialStatus]:
        """Get list of missing required credentials."""
        return [cred for cred in self.credentials if cred.required and not cred.present]

    @property
    def missing_optional(self) -> list[CredentialStatus]:
        """Get list of missing optional credentials."""
        return [
            cred for cred in self.credentials if not cred.required and not cred.present
        ]

    def __str__(self) -> str:
        """String representation of validation result."""
        lines = [f"Credential status for backend '{self.backend_name}':"]
        for cred in self.credentials:
            lines.append(f"  {cred}")
        return "\n".join(lines)


async def validate_backend_credentials(
    backend: Backend,
) -> CredentialValidationResult:
    """Validate that required credentials are present for a backend.

    Uses the generator dependency metadata from chora-compose v1.3.0+
    to detect required credentials and check if they're present in the
    environment.

    Args:
        backend: Backend instance to validate

    Returns:
        CredentialValidationResult with status of all credentials

    Example:
        >>> from mcp_n8n.backends.chora_composer import ChoraComposerBackend
        >>> backend = ChoraComposerBackend(config)
        >>> await backend.start()
        >>> result = await validate_backend_credentials(backend)
        >>> if not result.all_required_present:
        ...     print("Missing credentials:")
        ...     for cred in result.missing_required:
        ...         print(f"  - {cred.name}: {cred.description}")
    """
    result = CredentialValidationResult(backend.name)

    # For chora-compose v1.3.0+, we would query capabilities://generators
    # but for now with mock backends, we use known dependencies
    # TODO: Implement actual capability querying when JSON-RPC is implemented

    # Determine backend-specific required credentials
    if "chora" in backend.name.lower() or "composer" in backend.name.lower():
        # Chora Composer requires ANTHROPIC_API_KEY for code generation
        generators = [
            {
                "generator_type": "code_generation",
                "upstream_dependencies": {
                    "anthropic_api": {
                        "required": True,
                        "credential": "ANTHROPIC_API_KEY",
                        "description": "Anthropic API for Claude Code Generation",
                    }
                },
            }
        ]
    elif "coda" in backend.name.lower():
        # Coda MCP requires CODA_API_KEY
        generators = [
            {
                "generator_type": "coda_operations",
                "upstream_dependencies": {
                    "coda_api": {
                        "required": True,
                        "credential": "CODA_API_KEY",
                        "description": "Coda API for document operations",
                    }
                },
            }
        ]
    else:
        # Unknown backend type, no known dependencies
        generators = []
        logger.info(f"Backend {backend.name} has no known credential requirements")

    if not generators:
        logger.info(
            f"Backend {backend.name} has no generators - no credentials to validate"
        )
        return result

    # Check each generator's upstream dependencies
    seen_credentials = set()

    for generator in generators:
        gen_type = generator.get("generator_type", "unknown")
        upstream_deps = generator.get("upstream_dependencies", {})

        for service, metadata in upstream_deps.items():
            if not isinstance(metadata, dict):
                logger.warning(
                    f"Generator {gen_type} has invalid upstream_dependencies "
                    f"format for service {service}"
                )
                continue

            credential_name = metadata.get("credential")
            if not credential_name:
                logger.debug(
                    f"Generator {gen_type} service {service} has no credential field"
                )
                continue

            # Skip if we've already checked this credential
            if credential_name in seen_credentials:
                continue
            seen_credentials.add(credential_name)

            # Check if credential is present in environment
            required = metadata.get("required", False)
            present = os.getenv(credential_name) is not None
            description = metadata.get("description", "")

            credential = CredentialStatus(
                name=credential_name,
                required=required,
                present=present,
                description=description,
                service=service,
            )

            result.add_credential(credential)

            # Log credential status
            if required and not present:
                logger.error(
                    f"Missing required credential: {credential_name} "
                    f"({description})"
                )
            elif not present:
                logger.warning(
                    f"Missing optional credential: {credential_name} "
                    f"({description})"
                )
            else:
                logger.debug(f"Credential present: {credential_name}")

    return result


async def validate_all_backends(
    backends: list[Backend],
) -> dict[str, CredentialValidationResult]:
    """Validate credentials for all backends.

    Args:
        backends: List of backend instances to validate

    Returns:
        Dictionary mapping backend name to validation result
    """
    results = {}

    for backend in backends:
        try:
            result = await validate_backend_credentials(backend)
            results[backend.name] = result
        except Exception as e:
            logger.error(
                f"Error validating credentials for backend {backend.name}: {e}"
            )
            # Create empty result for this backend
            results[backend.name] = CredentialValidationResult(backend.name)

    return results


def format_credential_status_summary(
    results: dict[str, CredentialValidationResult],
) -> str:
    """Format credential status summary for all backends.

    Args:
        results: Dictionary of validation results

    Returns:
        Formatted string with credential status for all backends
    """
    lines = ["Credential Status Summary:", ""]

    total_required = 0
    total_missing_required = 0
    total_optional = 0
    total_missing_optional = 0

    for backend_name, result in results.items():
        required_creds = [c for c in result.credentials if c.required]
        optional_creds = [c for c in result.credentials if not c.required]

        total_required += len(required_creds)
        total_optional += len(optional_creds)
        total_missing_required += len(result.missing_required)
        total_missing_optional += len(result.missing_optional)

        # Backend header
        if result.all_required_present:
            status_icon = "✅"
        elif result.missing_required:
            status_icon = "❌"
        else:
            status_icon = "⚠️"

        lines.append(f"{status_icon} {backend_name}:")

        # Show credential status
        for cred in result.credentials:
            lines.append(f"  {cred}")

        lines.append("")  # Blank line between backends

    # Overall summary
    lines.append("Overall:")
    lines.append(
        f"  Required credentials: {total_required - total_missing_required}/"
        f"{total_required} present"
    )
    if total_missing_required > 0:
        lines.append(f"  ❌ {total_missing_required} required credentials missing")
    if total_optional > 0:
        lines.append(
            f"  Optional credentials: {total_optional - total_missing_optional}/"
            f"{total_optional} present"
        )

    return "\n".join(lines)
