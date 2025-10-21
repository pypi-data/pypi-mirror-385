"""Input validation utilities for security hardening.

This module provides validation functions to prevent:
- DoS attacks via oversized inputs
- Injection attacks via malicious strings
- Invalid data that could cause crashes

All validators raise ValueError with descriptive messages on validation failure.
"""

import re
import uuid as uuid_module
from typing import Any

# Security Constants - Generous limits for developer-friendly UX
# These prevent abuse while allowing legitimate use cases

MAX_CONTENT_LENGTH = 50_000  # 50KB ≈ 12,500 words (very generous for memory snippets)
MAX_TAG_LENGTH = 100  # Allows descriptive tags like "machine-learning-pytorch-optimization"
MAX_TAGS_COUNT = 50  # Real usage typically < 10, but allows power users
MAX_ENTITIES_COUNT = 100  # Most memories have 2-10 entities, generous headroom
MAX_LIST_LENGTH = 100  # Maximum items in any user-provided list (e.g., memory_ids)

# Whitelists for enumerated values
ALLOWED_TARGETS = {
    "obsidian",  # Obsidian vault with markdown + YAML frontmatter + wikilinks
    # Future: "markdown", "notion", "roam", etc.
}

# Note: target is a STORAGE BACKEND, not a file path!
# - "obsidian" = format/integration type, actual path is from LTM_VAULT_PATH config
# - Whitelist prevents code injection, not path traversal (that's handled separately)

ALLOWED_RELATION_TYPES = {
    "related",  # General association
    "causes",  # Causal relationship
    "supports",  # Supporting evidence
    "contradicts",  # Contradictory information
    "has_decision",  # Links project to decision
    "consolidated_from",  # Result of memory consolidation
    # Add more as needed, but keep controlled
}

# Regex patterns
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)
TAG_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]+$")  # Alphanumeric, hyphens, underscores only
ENTITY_PATTERN = re.compile(r"^[a-zA-Z0-9\-_ ]+$")  # Same + spaces for entity names


def validate_uuid(value: str, field_name: str = "value") -> str:
    """
    Validate that a string is a properly formatted UUID.

    Args:
        value: String to validate
        field_name: Name of field for error messages

    Returns:
        Validated UUID string (lowercase)

    Raises:
        ValueError: If value is not a valid UUID format
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")

    if not UUID_PATTERN.match(value):
        raise ValueError(
            f"{field_name} must be a valid UUID, got: {value[:50]}{'...' if len(value) > 50 else ''}"
        )

    # Verify it's parseable as UUID
    try:
        uuid_module.UUID(value)
    except ValueError as e:
        raise ValueError(f"{field_name} is not a valid UUID: {e}") from e

    return value.lower()


def validate_string_length(
    value: str | None,
    max_length: int,
    field_name: str = "value",
    allow_none: bool = False,
    allow_empty: bool = True,
) -> str | None:
    """
    Validate string length is within acceptable limits.

    Args:
        value: String to validate
        max_length: Maximum allowed length
        field_name: Name of field for error messages
        allow_none: Whether None is acceptable
        allow_empty: Whether empty strings are acceptable

    Returns:
        Validated string (or None if allow_none=True)

    Raises:
        ValueError: If string exceeds max_length or is empty when not allowed
    """
    if value is None:
        if allow_none:
            return None
        raise ValueError(f"{field_name} cannot be None")

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")

    if not allow_empty and len(value) == 0:
        raise ValueError(f"{field_name} cannot be empty")

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length of {max_length:,} characters "
            f"(got {len(value):,} characters)"
        )

    return value


def validate_score(value: float, field_name: str = "score") -> float:
    """
    Validate that a score is within valid range [0.0, 1.0].

    Args:
        value: Score to validate
        field_name: Name of field for error messages

    Returns:
        Validated score

    Raises:
        ValueError: If score is out of range
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number, got {type(value).__name__}")

    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {value}")

    return float(value)


def validate_positive_int(
    value: int,
    field_name: str = "value",
    min_value: int = 1,
    max_value: int | None = None,
) -> int:
    """
    Validate that an integer is positive and optionally within a range.

    Args:
        value: Integer to validate
        field_name: Name of field for error messages
        min_value: Minimum allowed value (default: 1)
        max_value: Maximum allowed value (optional)

    Returns:
        Validated integer

    Raises:
        ValueError: If value is out of range
    """
    if not isinstance(value, int) or isinstance(value, bool):  # bool is subclass of int
        raise ValueError(f"{field_name} must be an integer, got {type(value).__name__}")

    if value < min_value:
        raise ValueError(f"{field_name} must be >= {min_value}, got {value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{field_name} must be <= {max_value}, got {value}")

    return value


def validate_list_length(
    items: list[Any],
    max_length: int,
    field_name: str = "list",
) -> list[Any]:
    """
    Validate that a list does not exceed maximum length.

    Args:
        items: List to validate
        max_length: Maximum allowed length
        field_name: Name of field for error messages

    Returns:
        Validated list

    Raises:
        ValueError: If list exceeds max_length
    """
    if not isinstance(items, list):
        raise ValueError(f"{field_name} must be a list, got {type(items).__name__}")

    if len(items) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length of {max_length} items (got {len(items)} items)"
        )

    return items


def validate_tag(tag: str, field_name: str = "tag") -> str:
    """
    Validate and sanitize a tag string.

    Tags must be alphanumeric with hyphens and underscores only.
    This prevents injection attacks and ensures consistent formatting.

    Args:
        tag: Tag string to validate
        field_name: Name of field for error messages

    Returns:
        Validated tag (stripped of whitespace)

    Raises:
        ValueError: If tag contains invalid characters or is too long
    """
    if not isinstance(tag, str):
        raise ValueError(f"{field_name} must be a string, got {type(tag).__name__}")

    tag = tag.strip()

    if not tag:
        raise ValueError(f"{field_name} cannot be empty")

    if len(tag) > MAX_TAG_LENGTH:
        raise ValueError(
            f"{field_name} exceeds maximum length of {MAX_TAG_LENGTH} characters "
            f"(got {len(tag)} characters)"
        )

    if not TAG_PATTERN.match(tag):
        raise ValueError(
            f"{field_name} contains invalid characters. "
            f"Only alphanumeric, hyphens, and underscores allowed. Got: {tag[:50]}"
        )

    return tag


def validate_entity(entity: str, field_name: str = "entity") -> str:
    """
    Validate and sanitize an entity string.

    Entities can contain alphanumeric characters, hyphens, underscores, and spaces.
    Examples: "Claude AI", "project-alpha", "user_123"

    Args:
        entity: Entity string to validate
        field_name: Name of field for error messages

    Returns:
        Validated entity (stripped of excess whitespace)

    Raises:
        ValueError: If entity contains invalid characters or is too long
    """
    if not isinstance(entity, str):
        raise ValueError(f"{field_name} must be a string, got {type(entity).__name__}")

    entity = entity.strip()

    if not entity:
        raise ValueError(f"{field_name} cannot be empty")

    if len(entity) > MAX_TAG_LENGTH:  # Reuse TAG length limit
        raise ValueError(
            f"{field_name} exceeds maximum length of {MAX_TAG_LENGTH} characters "
            f"(got {len(entity)} characters)"
        )

    if not ENTITY_PATTERN.match(entity):
        raise ValueError(
            f"{field_name} contains invalid characters. "
            f"Only alphanumeric, hyphens, underscores, and spaces allowed. Got: {entity[:50]}"
        )

    # Normalize multiple spaces to single space
    entity = " ".join(entity.split())

    return entity


def validate_relation_type(rel_type: str, field_name: str = "relation_type") -> str:
    """
    Validate relation type against whitelist.

    Args:
        rel_type: Relation type to validate
        field_name: Name of field for error messages

    Returns:
        Validated relation type

    Raises:
        ValueError: If relation type is not in whitelist
    """
    if not isinstance(rel_type, str):
        raise ValueError(f"{field_name} must be a string, got {type(rel_type).__name__}")

    if rel_type not in ALLOWED_RELATION_TYPES:
        raise ValueError(
            f"{field_name} must be one of {sorted(ALLOWED_RELATION_TYPES)}, got: {rel_type}"
        )

    return rel_type


def validate_target(target: str, field_name: str = "target") -> str:
    """
    Validate storage backend target against whitelist.

    IMPORTANT: 'target' is a STORAGE BACKEND/FORMAT, not a file path!
    - "obsidian" = Use Obsidian-compatible markdown format
    - Actual storage location is configured via LTM_VAULT_PATH in .env

    This prevents code injection by restricting to known backend implementations.
    Path traversal prevention is handled separately in security/paths.py.

    Args:
        target: Storage backend to validate
        field_name: Name of field for error messages

    Returns:
        Validated target

    Raises:
        ValueError: If target is not in whitelist
    """
    if not isinstance(target, str):
        raise ValueError(f"{field_name} must be a string, got {type(target).__name__}")

    if target not in ALLOWED_TARGETS:
        raise ValueError(
            f"{field_name} must be one of {sorted(ALLOWED_TARGETS)}, got: {target}. "
            f"Note: target is a storage backend (e.g., 'obsidian'), not a file path. "
            f"Configure the actual path via LTM_VAULT_PATH in your .env file."
        )

    return target
