from __future__ import annotations

import queue
import threading
import uuid
from typing import Any, Dict, List, Optional

from xlog.event import LogEvent
from xlog.object import BaseObject
from xlog.stream import LogStream


class LogGroup(BaseObject):
    def __init__(
        self,
        name: Optional[str] = "",
        sync: Optional[bool] = False,
        streams: Optional[List[LogStream]] = None,
        max_queue: int = 0,
    ):
        self.id = str(uuid.uuid4())[:5]
        self.name = name or f"{self.id}"
        self.sync = sync
        self._lock = threading.Lock()
        self._queue = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._consume,
            daemon=True,
        )
        self._buckets: Dict[str, List[LogEvent]] = {}
        self.streams: Dict[str, LogStream] = {}
        for stream in streams or []:
            self.add_stream(stream)

        if not self.sync:
            self._thread.start()

    def __str__(self):
        return self.name

    @property
    def xmeta(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "sync": self.sync,
        }

    def add_stream(
        self,
        stream: LogStream,
    ) -> None:
        self.streams[stream.name] = stream
        stream.add_group(self)
        with self._lock:
            self._buckets.setdefault(stream.name, [])

    def delete_stream(
        self,
        stream: LogStream,
    ) -> None:
        self.streams.pop(stream.name, None)
        stream.delete_group(self)
        with self._lock:
            self._buckets.pop(stream.name, None)

    def receive(
        self,
        stream_name: str,
        event: LogEvent,
    ):
        if self.sync:
            self._add_event(stream_name, event)
        else:
            try:
                self._queue.put_nowait((stream_name, event))
            except queue.Full:
                self._add_event(stream_name, event)

    def _add_event(
        self,
        stream: str,
        event: LogEvent,
    ) -> None:
        with self._lock:
            self._buckets.setdefault(stream, []).append(event)

    def _consume(self) -> None:
        while not self._stop.is_set():
            try:
                stream_name, event = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            self._add_event(stream_name, event)
            self._queue.task_done()

    def stop(
        self,
        drain: bool = True,
        timeout: Optional[float] = 2.0,
    ) -> None:
        if self.sync:
            return False

        if drain:
            try:
                self._queue.join()
            except Exception:
                pass
        self._stop.set()
        self._thread.join(timeout=timeout)
        return self._thread.is_alive()

    def export(
        self,
    ) -> Dict[str, Any]:
        with self._lock:
            result = {}
            result["name"] = self.name
            result["streams"] = {}
            for name, evs in self._buckets.items():
                result["streams"][name] = [ev.export() for ev in evs]
            return result
