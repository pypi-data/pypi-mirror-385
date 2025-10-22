from __future__ import annotations

from typing import Any


class BaseObject:
    @property
    def xattr(self) -> list[str]:
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    @property
    def xmeta(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in self.xattr if not callable(getattr(self, key))}

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        cname = self.__class__.__name__
        parts = []
        for key, value in self.xmeta.items():
            parts.append(f"{key}={value!r}")
        return f"{cname}({', '.join(parts)})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.xmeta == other.xmeta

    def __hash__(self) -> int:
        sorted_meta = sorted(self.xmeta.items())
        return hash(tuple(sorted_meta))
