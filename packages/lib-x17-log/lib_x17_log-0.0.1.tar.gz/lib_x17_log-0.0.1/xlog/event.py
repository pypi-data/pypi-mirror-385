from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from xlog.object import BaseObject


class LogEvent(BaseObject):
    LITERAL_LEVELS = Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> LogEvent:
        ds = data.get("datestamp")
        if isinstance(ds, str):
            datestamp = datetime.fromisoformat(ds)
        elif isinstance(ds, datetime):
            datestamp = ds
        else:
            datestamp = None

        return LogEvent(
            message=data.get("message"),
            name=data.get("name"),
            datestamp=datestamp,
            level=data.get("level", "INFO"),
            context=data.get("context"),
            code=data.get("code"),
            tags=data.get("tags"),
            metrics=data.get("metrics"),
            extra=data.get("extra"),
        )

    def __init__(
        self,
        message: str,
        name: Optional[str] = "",
        datestamp: Optional[datetime] = None,
        level: LogEvent.LITERAL_LEVELS = "INFO",
        context: Optional[str] = None,
        code: Optional[int] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        self.id = str(uuid.uuid4())[:5]
        self.name = name or f"{self.id}"
        self.datestamp = datestamp or datetime.now()
        self.level = level.upper()
        self.message = message
        self.context = context
        self.code = code
        self.tags = tags or []
        self.metrics = metrics or {}
        self.extra = extra or {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.name

    def export(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "datestamp": self.datestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "context": self.context,
            "code": self.code,
            "tags": self.tags,
            "metrics": self.metrics,
            "extra": self.extra,
        }
