from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListStudiesSort(Enums.KnownString):
    MODIFIEDAT = "modifiedAt"
    MODIFIEDATASC = "modifiedAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAME = "name"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListStudiesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListStudiesSort must be a string (encountered: {val})")
        newcls = Enum("ListStudiesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListStudiesSort, getattr(newcls, "_UNKNOWN"))
