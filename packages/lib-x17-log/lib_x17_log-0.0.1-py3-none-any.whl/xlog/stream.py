from __future__ import annotations

import logging
import subprocess
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from xlog.event import LogEvent
from xlog.object import BaseObject

if TYPE_CHECKING:
    from xlog.group import LogGroup


class LogStream(BaseObject):
    LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
    LITERAL_LEVELS = Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]

    def __init__(
        self,
        name: Optional[str] = "",
        level: LogStream.LITERAL_LEVELS = "INFO",
        format: Optional[str] = None,
        verbose: Optional[bool] = False,
        events: Optional[List[LogEvent]] = None,
        groups: Optional[List["LogGroup"]] = None,  # sinks
    ):
        self.id = str(uuid.uuid4())[:5]
        self.name = name or f"{self.id}"
        self.level = level
        self.verbose = verbose
        self.log_format = format or LogStream.LOG_FORMAT
        self.log_node = self._set_node()
        self.groups = groups or []  # sinks
        self.events = []
        for ev in events or []:
            if isinstance(ev, LogEvent):
                self.events.append(ev)
            else:
                self.events.append(LogEvent.from_dict(ev))

    def __str__(self):
        return self.name

    @property
    def xmeta(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "groups": [group.xmeta for group in self.groups],
            "events": len(self.events),
        }

    def _set_node(self):
        lcname = str(self.__class__.__name__).lower()
        logger = logging.getLogger(f"{lcname}:{self.name}")
        logger.setLevel(
            getattr(logging, self.level.upper(), logging.INFO),
        )
        logger.propagate = False
        if self.verbose and not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(self.log_format),
            )
            logger.addHandler(handler)

        return logger

    def add_group(
        self,
        group: "LogGroup",
    ) -> None:
        if group not in self.groups:
            self.groups.append(group)

    def delete_group(
        self,
        group: "LogGroup",
    ) -> None:
        if group in self.groups:
            self.groups.remove(group)

    def log(
        self,
        message: str,
        name: Optional[str] = None,
        level: str = "INFO",
        datestamp: Optional[str] = None,
        context: Optional[str] = None,
        code: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        event = LogEvent(
            message=message,
            level=level,
            datestamp=datestamp,
            name=name,
            context=context,
            code=code,
            tags=tags,
            metrics=metrics,
            extra=extra,
            **kwargs,
        )
        self.events.append(event)
        for group in self.groups:
            try:
                group.receive(self.name, event)
            except Exception as e:
                self.log_node.error(
                    f"Failed to deliver log to group {group}: {e}",
                )

        if self.verbose:
            logger = getattr(
                logging,
                self.level.upper(),
                logging.INFO,
            )
            self.log_node.log(logger, message)

        return event

    def logprocess(
        self,
        result: subprocess.CompletedProcess[str],
        title: str = "process",
    ):
        indent = "\t"
        rcode = getattr(result, "returncode", "unknown")
        stdout = getattr(result, "stdout", "").splitlines()
        stderr = getattr(result, "stderr", "").splitlines()

        self.info(
            message=f"[{title}] exited with code {rcode}",
        )
        if stdout:
            self.info(f"[{title}] output:")
            for line in stdout:
                self.info(
                    message=f"{indent}{line}",
                )
        if stderr:
            self.error(f"[{title}] errors:")
            for line in stderr:
                self.error(
                    message=f"{indent}{line}",
                )

    def info(
        self,
        message: str,
        **kwargs,
    ) -> LogEvent:
        return self.log(
            message=message,
            level="INFO",
            **kwargs,
        )

    def error(
        self,
        message: str,
        **kwargs,
    ) -> LogEvent:
        return self.log(
            message=message,
            level="ERROR",
            **kwargs,
        )

    def warning(
        self,
        message: str,
        **kwargs,
    ) -> LogEvent:
        return self.log(
            message=message,
            level="WARNING",
            **kwargs,
        )

    def debug(
        self,
        message: str,
        **kwargs,
    ) -> LogEvent:
        return self.log(
            message=message,
            level="DEBUG",
            **kwargs,
        )

    def critical(
        self,
        message: str,
        **kwargs,
    ) -> LogEvent:
        return self.log(
            message=message,
            level="CRITICAL",
            **kwargs,
        )

    def export(self) -> Dict[str, Any]:
        events = [event.export() for event in self.events]
        return {
            "name": self.name,
            "level": self.level,
            "log_format": self.log_format,
            "verbose": self.verbose,
            "events": events,
        }
