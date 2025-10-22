from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.multiple_containers_transfer import MultipleContainersTransfer
from ..types import UNSET, Unset

T = TypeVar("T", bound="MultipleContainersTransfersList")


@attr.s(auto_attribs=True, repr=False)
class MultipleContainersTransfersList:
    """  """

    _transfers: List[MultipleContainersTransfer]

    def __repr__(self):
        fields = []
        fields.append("transfers={}".format(repr(self._transfers)))
        return "MultipleContainersTransfersList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        transfers = []
        for transfers_item_data in self._transfers:
            transfers_item = transfers_item_data.to_dict()

            transfers.append(transfers_item)

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if transfers is not UNSET:
            field_dict["transfers"] = transfers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_transfers() -> List[MultipleContainersTransfer]:
            transfers = []
            _transfers = d.pop("transfers")
            for transfers_item_data in _transfers:
                transfers_item = MultipleContainersTransfer.from_dict(transfers_item_data, strict=False)

                transfers.append(transfers_item)

            return transfers

        try:
            transfers = get_transfers()
        except KeyError:
            if strict:
                raise
            transfers = cast(List[MultipleContainersTransfer], UNSET)

        multiple_containers_transfers_list = cls(
            transfers=transfers,
        )

        return multiple_containers_transfers_list

    @property
    def transfers(self) -> List[MultipleContainersTransfer]:
        if isinstance(self._transfers, Unset):
            raise NotPresentError(self, "transfers")
        return self._transfers

    @transfers.setter
    def transfers(self, value: List[MultipleContainersTransfer]) -> None:
        self._transfers = value
