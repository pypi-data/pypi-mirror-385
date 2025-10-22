from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssemblyFragmentSharedOrientation(Enums.KnownString):
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssemblyFragmentSharedOrientation":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AssemblyFragmentSharedOrientation must be a string (encountered: {val})"
            )
        newcls = Enum("AssemblyFragmentSharedOrientation", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssemblyFragmentSharedOrientation, getattr(newcls, "_UNKNOWN"))
