"""Promote memory tool - move high-value memories to long-term storage."""

import time
from typing import Any

from ..context import db, mcp
from ..core.scoring import calculate_memory_age, should_promote
from ..integration.basic_memory import BasicMemoryIntegration
from ..security.validators import validate_target, validate_uuid
from ..storage.models import MemoryStatus, PromotionCandidate


@mcp.tool()
def promote_memory(
    memory_id: str | None = None,
    auto_detect: bool = False,
    dry_run: bool = False,
    target: str = "obsidian",
    force: bool = False,
) -> dict[str, Any]:
    """
    Promote high-value memories to long-term storage.

    Memories with high scores or frequent usage are promoted to the Obsidian
    vault (or other long-term storage) where they become permanent.

    Args:
        memory_id: Specific memory ID to promote (valid UUID).
        auto_detect: Automatically detect promotion candidates.
        dry_run: Preview what would be promoted without promoting.
        target: Storage backend for promotion. Default: "obsidian" (Obsidian-compatible markdown).
                Note: This is a storage format, not a file path. Path configured via LTM_VAULT_PATH.
        force: Force promotion even if criteria not met.

    Returns:
        List of promoted memories and promotion statistics.

    Raises:
        ValueError: If memory_id is invalid or target is not supported.
    """
    # Input validation
    if memory_id is not None:
        memory_id = validate_uuid(memory_id, "memory_id")

    target = validate_target(target, "target")

    now = int(time.time())
    promoted_ids = []
    candidates = []

    if memory_id:
        memory = db.get_memory(memory_id)
        if memory is None:
            return {"success": False, "message": f"Memory not found: {memory_id}"}
        if memory.status == MemoryStatus.PROMOTED:
            return {
                "success": False,
                "message": f"Memory already promoted: {memory_id}",
                "promoted_to": memory.promoted_to,
            }

        promote_it, reason, score = should_promote(memory, now)
        if not promote_it and not force:
            return {
                "success": False,
                "message": f"Memory does not meet promotion criteria: {reason}",
                "score": round(score, 4),
            }

        candidates = [
            PromotionCandidate(
                memory=memory,
                reason=reason,
                score=score,
                use_count=memory.use_count,
                age_days=calculate_memory_age(memory, now),
            )
        ]
    elif auto_detect:
        memories = db.list_memories(status=MemoryStatus.ACTIVE)
        for memory in memories:
            promote_it, reason, score = should_promote(memory, now)
            if promote_it:
                candidates.append(
                    PromotionCandidate(
                        memory=memory,
                        reason=reason,
                        score=score,
                        use_count=memory.use_count,
                        age_days=calculate_memory_age(memory, now),
                    )
                )
        candidates.sort(key=lambda c: c.score, reverse=True)
    else:
        return {
            "success": False,
            "message": "Must specify memory_id or set auto_detect=true",
        }

    if not dry_run and candidates:
        integration = BasicMemoryIntegration()
        for candidate in candidates:
            if target == "obsidian":
                result = integration.promote_to_obsidian(candidate.memory)
            else:
                return {"success": False, "message": f"Unknown target: {target}"}

            if result["success"]:
                db.update_memory(
                    memory_id=candidate.memory.id,
                    status=MemoryStatus.PROMOTED,
                    promoted_at=now,
                    promoted_to=result.get("path"),
                )
                promoted_ids.append(candidate.memory.id)

    return {
        "success": True,
        "dry_run": dry_run,
        "candidates_found": len(candidates),
        "promoted_count": len(promoted_ids),
        "promoted_ids": promoted_ids,
        "candidates": [
            {
                "id": c.memory.id,
                "content_preview": c.memory.content[:100],
                "reason": c.reason,
                "score": round(c.score, 4),
                "use_count": c.use_count,
                "age_days": round(c.age_days, 1),
            }
            for c in candidates[:10]
        ],
        "message": (
            f"{'Would promote' if dry_run else 'Promoted'} {len(promoted_ids)} memories to {target}"
        ),
    }
