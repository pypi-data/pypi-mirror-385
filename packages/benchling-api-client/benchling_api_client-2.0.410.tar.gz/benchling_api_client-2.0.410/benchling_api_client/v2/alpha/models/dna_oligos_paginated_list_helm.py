from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_oligo_helm import DnaOligoHelm
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligosPaginatedListHelm")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosPaginatedListHelm:
    """  """

    _dna_oligos: Union[Unset, List[DnaOligoHelm]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaOligosPaginatedListHelm({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligos, Unset):
            dna_oligos = []
            for dna_oligos_item_data in self._dna_oligos:
                dna_oligos_item = dna_oligos_item_data.to_dict()

                dna_oligos.append(dna_oligos_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if dna_oligos is not UNSET:
            field_dict["dnaOligos"] = dna_oligos
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_dna_oligos() -> Union[Unset, List[DnaOligoHelm]]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos or []:
                dna_oligos_item = DnaOligoHelm.from_dict(dna_oligos_item_data, strict=False)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        try:
            dna_oligos = get_dna_oligos()
        except KeyError:
            if strict:
                raise
            dna_oligos = cast(Union[Unset, List[DnaOligoHelm]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        try:
            next_token = get_next_token()
        except KeyError:
            if strict:
                raise
            next_token = cast(Union[Unset, str], UNSET)

        dna_oligos_paginated_list_helm = cls(
            dna_oligos=dna_oligos,
            next_token=next_token,
        )

        dna_oligos_paginated_list_helm.additional_properties = d
        return dna_oligos_paginated_list_helm

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def dna_oligos(self) -> List[DnaOligoHelm]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[DnaOligoHelm]) -> None:
        self._dna_oligos = value

    @dna_oligos.deleter
    def dna_oligos(self) -> None:
        self._dna_oligos = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
