from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MonomersArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    ARCHIVED = "Archived"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MonomersArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of MonomersArchiveReason must be a string (encountered: {val})")
        newcls = Enum("MonomersArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MonomersArchiveReason, getattr(newcls, "_UNKNOWN"))
