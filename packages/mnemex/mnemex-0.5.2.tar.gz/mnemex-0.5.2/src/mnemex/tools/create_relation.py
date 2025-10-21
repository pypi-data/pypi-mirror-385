"""Create relation tool - link memories explicitly."""

import time
import uuid
from typing import Any

from ..context import db, mcp
from ..security.validators import validate_relation_type, validate_score, validate_uuid
from ..storage.models import Relation


@mcp.tool()
def create_relation(
    from_memory_id: str,
    to_memory_id: str,
    relation_type: str,
    strength: float = 1.0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create an explicit relation between two memories.

    Links two memories with a typed relationship.

    Args:
        from_memory_id: Source memory ID (valid UUID).
        to_memory_id: Target memory ID (valid UUID).
        relation_type: Type of relation (must be one of: related, causes, supports,
                       contradicts, has_decision, consolidated_from).
        strength: Strength of the relation (0.0-1.0).
        metadata: Additional metadata about the relation.

    Returns:
        Created relation ID and confirmation.

    Raises:
        ValueError: If any input fails validation.
    """
    # Input validation
    from_memory_id = validate_uuid(from_memory_id, "from_memory_id")
    to_memory_id = validate_uuid(to_memory_id, "to_memory_id")
    relation_type = validate_relation_type(relation_type, "relation_type")
    strength = validate_score(strength, "strength")

    if not db.get_memory(from_memory_id):
        return {"success": False, "message": f"Source memory not found: {from_memory_id}"}
    if not db.get_memory(to_memory_id):
        return {"success": False, "message": f"Target memory not found: {to_memory_id}"}

    if existing := db.get_relations(
        from_memory_id=from_memory_id,
        to_memory_id=to_memory_id,
        relation_type=relation_type,
    ):
        return {
            "success": False,
            "message": f"Relation already exists: {existing[0].id}",
            "existing_relation_id": existing[0].id,
        }

    relation = Relation(
        id=str(uuid.uuid4()),
        from_memory_id=from_memory_id,
        to_memory_id=to_memory_id,
        relation_type=relation_type,
        strength=strength,
        created_at=int(time.time()),
        metadata=metadata or {},
    )
    db.create_relation(relation)

    return {
        "success": True,
        "relation_id": relation.id,
        "from": from_memory_id,
        "to": to_memory_id,
        "type": relation_type,
        "strength": strength,
        "message": f"Relation created: {from_memory_id} --[{relation_type}]--> {to_memory_id}",
    }
