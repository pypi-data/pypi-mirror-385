from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListBoxesSort(Enums.KnownString):
    MODIFIEDAT = "modifiedAt"
    MODIFIEDATASC = "modifiedAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAME = "name"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"
    CREATEDAT = "createdAt"
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    BARCODE = "barcode"
    BARCODEASC = "barcode:asc"
    BARCODEDESC = "barcode:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListBoxesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListBoxesSort must be a string (encountered: {val})")
        newcls = Enum("ListBoxesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListBoxesSort, getattr(newcls, "_UNKNOWN"))
