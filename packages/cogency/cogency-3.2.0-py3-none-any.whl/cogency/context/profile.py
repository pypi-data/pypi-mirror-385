"""User profile management with LLM-based learning.

Profiles are learned through direct LLM analysis of conversation patterns,
stored as human-readable JSON, and assembled contextually.

Why no embeddings for profiles?
1. Transparency - profiles are readable JSON, not opaque vectors
2. Simplicity - no vector database infrastructure required
3. Privacy - user data stays in readable, deletable format
4. Direct learning - LLM analyzes patterns directly from text

Learning triggers:
- Every 5 user messages
- Profile size exceeds threshold (triggers compaction)
"""

import json
from typing import TYPE_CHECKING

from ..lib.logger import logger

if TYPE_CHECKING:
    from ..core.protocols import LLM, Storage

CADENCE = 5
COMPACT_THRESHOLD = 2000

PROFILE_TEMPLATE = """Current: {profile}
Messages: {user_messages}
{instruction}
Example: {{"who":"developer","style":"direct","focus":"AI projects","interests":"tech","misc":"likes cats, morning person"}}"""


def prompt(profile: dict, user_messages: list, compact: bool = False) -> str:
    """Generate profile learning prompt."""
    if compact:
        return PROFILE_TEMPLATE.format(
            profile=json.dumps(profile),
            user_messages="\n".join(user_messages),
            instruction="Profile too large. Compact to essential facts only. JSON only.",
        )
    return PROFILE_TEMPLATE.format(
        profile=json.dumps(profile),
        user_messages="\n".join(user_messages),
        instruction="Update profile keeping it concise. Return SKIP if no changes needed. JSON only.",
    )


async def get(user_id: str | None, storage=None) -> dict | None:
    """Get latest user profile."""
    if not user_id:
        return None
    if storage is None:
        from ..lib.sqlite import SQLite

        storage = SQLite()
    try:
        return await storage.load_profile(user_id)
    except Exception as e:
        if "unable to open database file" in str(e):
            return {}
        raise RuntimeError(f"Profile fetch failed for {user_id}: {e}") from e


async def format(user_id: str | None, storage=None) -> str:
    """Format user profile for context display."""
    try:
        profile_data = await get(user_id, storage)
        if not profile_data:
            return ""

        return f"USER PROFILE:\n{json.dumps(profile_data, indent=2)}"
    except Exception as e:
        raise RuntimeError(f"Profile format failed for {user_id}: {e}") from e


async def should_learn(
    user_id: str,
    *,
    storage: "Storage",
) -> bool:
    """Check if profile learning needed based on message cadence or size threshold."""
    current = await get(user_id, storage)
    if not current:
        unlearned = await storage.count_user_messages(user_id, 0)
        if unlearned >= CADENCE:
            logger.debug(f"📊 INITIAL LEARNING: {unlearned} messages for {user_id}")
            return True
        return False

    # Size-based compaction check
    current_chars = len(json.dumps(current))
    if current_chars > COMPACT_THRESHOLD:
        logger.debug(f"🚨 COMPACT: {current_chars} chars")
        return True

    # Message cadence check
    last_learned = current.get("_meta", {}).get("last_learned_at", 0)
    unlearned = await storage.count_user_messages(user_id, last_learned)

    if unlearned >= CADENCE:
        logger.debug(f"📊 LEARNING: {unlearned} new messages")
        return True

    return False


def learn(
    user_id: str | None,
    *,
    profile_enabled: bool,
    storage: "Storage",
    llm: "LLM",
):
    """Trigger profile learning in background (fire and forget)."""
    if not profile_enabled or not user_id or not llm:
        return

    # Skip in test environments
    import os

    if "pytest" in os.environ.get("_", "") or "PYTEST_CURRENT_TEST" in os.environ:
        return

    import asyncio

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            learn_async(
                user_id,
                storage=storage,
                llm=llm,
            )
        )
    except RuntimeError:
        pass


async def learn_async(
    user_id: str,
    *,
    storage: "Storage",
    llm: "LLM",
) -> bool:
    """Learn user patterns from recent messages using LLM analysis."""

    if not await should_learn(
        user_id,
        storage=storage,
    ):
        return False

    current = await get(user_id, storage) or {
        "who": "",
        "style": "",
        "focus": "",
        "interests": "",
        "misc": "",
        "_meta": {},
    }
    last_learned = current.get("_meta", {}).get("last_learned_at", 0)

    # Get unlearned messages across ALL conversations
    import time

    # Get 2x learning cadence for better pattern detection
    limit = CADENCE * 2

    message_texts = await storage.load_user_messages(user_id, last_learned, limit)

    if not message_texts:
        return False

    logger.debug(f"🧠 LEARNING: {len(message_texts)} new messages for {user_id}")

    # Check size and update
    compact = len(json.dumps(current)) > COMPACT_THRESHOLD
    updated = await update_profile(current, message_texts, llm, compact=compact)

    if updated and updated != current:
        updated["_meta"] = {
            "last_learned_at": time.time(),
            "messages_processed": len(message_texts),
        }
        await storage.save_profile(user_id, updated)
        logger.debug(f"💾 SAVED: {len(json.dumps(updated))} chars")
        return True

    return False


async def update_profile(
    current: dict, user_messages: list, llm, compact: bool = False
) -> dict | None:
    """Update or compact profile."""
    prompt_text = prompt(current, user_messages, compact=compact)
    result = await llm.generate([{"role": "user", "content": prompt_text}])

    if not result:
        return current if compact else None

    # Parse JSON (strip common markdown)
    clean = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```")

    try:
        parsed = json.loads(clean)
        if compact or result.strip().upper() != "SKIP":
            return parsed
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"JSON parse error during profile update: {result[:50]}...", cause=e
        ) from e

    return current if compact else None


__all__ = ["get", "format", "learn"]
