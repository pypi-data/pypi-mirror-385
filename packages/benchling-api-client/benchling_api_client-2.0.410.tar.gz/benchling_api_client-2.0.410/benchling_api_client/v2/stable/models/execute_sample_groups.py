from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="ExecuteSampleGroups")


@attr.s(auto_attribs=True, repr=False)
class ExecuteSampleGroups:
    """The response is intentionally empty."""

    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ExecuteSampleGroups({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        execute_sample_groups = cls()

        execute_sample_groups.additional_properties = d
        return execute_sample_groups

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
