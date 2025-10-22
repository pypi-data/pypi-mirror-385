from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatesArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class PlatesArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of plates along with any IDs of containers that were archived / unarchived."""

    _container_ids: Union[Unset, List[str]] = UNSET
    _plate_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("plate_ids={}".format(repr(self._plate_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PlatesArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._container_ids, Unset):
            container_ids = self._container_ids

        plate_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._plate_ids, Unset):
            plate_ids = self._plate_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if container_ids is not UNSET:
            field_dict["containerIds"] = container_ids
        if plate_ids is not UNSET:
            field_dict["plateIds"] = plate_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_container_ids() -> Union[Unset, List[str]]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        try:
            container_ids = get_container_ids()
        except KeyError:
            if strict:
                raise
            container_ids = cast(Union[Unset, List[str]], UNSET)

        def get_plate_ids() -> Union[Unset, List[str]]:
            plate_ids = cast(List[str], d.pop("plateIds"))

            return plate_ids

        try:
            plate_ids = get_plate_ids()
        except KeyError:
            if strict:
                raise
            plate_ids = cast(Union[Unset, List[str]], UNSET)

        plates_archival_change = cls(
            container_ids=container_ids,
            plate_ids=plate_ids,
        )

        plates_archival_change.additional_properties = d
        return plates_archival_change

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
    def container_ids(self) -> List[str]:
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @container_ids.deleter
    def container_ids(self) -> None:
        self._container_ids = UNSET

    @property
    def plate_ids(self) -> List[str]:
        if isinstance(self._plate_ids, Unset):
            raise NotPresentError(self, "plate_ids")
        return self._plate_ids

    @plate_ids.setter
    def plate_ids(self, value: List[str]) -> None:
        self._plate_ids = value

    @plate_ids.deleter
    def plate_ids(self) -> None:
        self._plate_ids = UNSET
