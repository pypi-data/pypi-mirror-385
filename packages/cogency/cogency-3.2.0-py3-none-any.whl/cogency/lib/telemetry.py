import asyncio
import json

from ..lib.logger import logger
from ..lib.sqlite import default_storage


def add_event(events_list: list[dict], event: dict):
    events_list.append(event)


async def persist_events(conversation_id: str, events_list: list[dict]):
    if not events_list:
        return

    try:
        storage = default_storage()
        tasks = []
        for event in events_list:
            content = event.get("content", "")
            if isinstance(content, dict):
                content = json.dumps(content)

            tasks.append(
                storage.save_event(
                    conversation_id=conversation_id,
                    type=event["type"],
                    content=content,
                )
            )
        await asyncio.gather(*tasks)
        logger.debug(f"Persisted telemetry for {conversation_id}: {json.dumps(events_list)}")
        events_list.clear()
    except Exception as exc:
        logger.debug(f"Failed to persist telemetry for {conversation_id}: {exc}")
