import asyncio
from typing import Any, Awaitable, Callable, Optional

__all__ = ["EventQueue"]


class EventQueue:
    def __init__(self, callback: Callable[[Any, str], Awaitable[None]], delay: float = 1):
        self.callback = callback
        self.delay = delay
        self.pending_events = []
        self.pending_events_task: Optional[asyncio.Task] = None

    def queue(self, event: Any, filename: str):
        self.pending_events.append((event, filename))
        if self.pending_events_task is None or self.pending_events_task.done():
            self.pending_events_task = asyncio.create_task(self.process_pending_events())

    async def process_pending_events(self):
        await asyncio.sleep(self.delay)

        events_by_filename = {}
        for event, filename in self.pending_events:
            events_by_filename[filename] = event
        self.pending_events.clear()

        try:
            for filename, event in events_by_filename.items():
                await self.callback(event, filename)
        finally:
            if self.pending_events:
                self.pending_events_task = asyncio.create_task(self.process_pending_events())
            else:
                self.pending_events_task = None
