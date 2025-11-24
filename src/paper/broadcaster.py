# -*- coding: utf-8 -*-
"""
Event Broadcaster

Polls agent_events table and forwards new events to websocket subscribers.
Simple implementation using a background thread and asyncio queues.
"""

import threading
import time
import asyncio
from typing import Dict, List

from ..agent.agent_storage import AgentStorage
from ..core.logger import logger


class Broadcaster:
    def __init__(self, poll_interval: float = 0.5):
        self.storage = AgentStorage()
        self.poll_interval = poll_interval
        self._subs: Dict[str, List[asyncio.Queue]] = {}
        self._last_event_id: Dict[str, int] = {}
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._running = False
        self._loop = None

    def start(self, loop: asyncio.AbstractEventLoop = None):
        if self._running:
            return
        self._running = True
        # store loop to call threadsafe puts
        self._loop = loop or asyncio.get_event_loop()
        self._thread.start()
        logger.info("Event Broadcaster started")

    def stop(self):
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def subscribe(self, agent_id: str) -> asyncio.Queue:
        """Subscribe to events for an agent. Returns an asyncio.Queue."""
        q: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._subs.setdefault(agent_id, []).append(q)
            # initialize last_event_id if not present
            if agent_id not in self._last_event_id:
                events = self.storage.get_agent_events(agent_id, limit=1)
                if events:
                    self._last_event_id[agent_id] = events[0]['id']
                else:
                    self._last_event_id[agent_id] = 0
        # ensure broadcaster running
        if not self._running:
            try:
                self.start()
            except Exception:
                pass
        return q

    def unsubscribe(self, agent_id: str, queue: asyncio.Queue) -> None:
        with self._lock:
            lst = self._subs.get(agent_id)
            if not lst:
                return
            try:
                lst.remove(queue)
            except ValueError:
                pass
            if not lst:
                del self._subs[agent_id]
                if agent_id in self._last_event_id:
                    del self._last_event_id[agent_id]

    def _run(self):
        try:
            while self._running:
                # copy keys to avoid locking long
                with self._lock:
                    agent_ids = list(self._subs.keys())
                for agent_id in agent_ids:
                    try:
                        last_id = self._last_event_id.get(agent_id, 0)
                        events = self.storage.get_agent_events(agent_id, limit=50)
                        # events are newest first; iterate reverse to send oldest-first
                        new_events = [e for e in reversed(events) if e['id'] > last_id]
                        if new_events:
                            # update last id
                            self._last_event_id[agent_id] = new_events[-1]['id']
                            # dispatch to subscribers
                            with self._lock:
                                queues = list(self._subs.get(agent_id, []))
                            for ev in new_events:
                                for q in queues:
                                    # put into asyncio queue thread-safely
                                    if self._loop and not self._loop.is_closed():
                                        try:
                                            self._loop.call_soon_threadsafe(q.put_nowait, ev)
                                        except Exception:
                                            # if queue is closed or other issue, ignore
                                            pass
                    except Exception as e:
                        logger.warning(f"Broadcaster error for {agent_id}: {e}")
                time.sleep(self.poll_interval)
        except Exception as e:
            logger.error(f"Broadcaster main loop failed: {e}", exc_info=True)


# Singleton broadcaster
_broadcaster: Broadcaster = None


def get_broadcaster() -> Broadcaster:
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = Broadcaster()
    return _broadcaster
