from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container import Container
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkUpdateContainersAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkUpdateContainersAsyncTaskResponse:
    """  """

    _containers: Union[Unset, List[Container]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("containers={}".format(repr(self._containers)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkUpdateContainersAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        containers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._containers, Unset):
            containers = []
            for containers_item_data in self._containers:
                containers_item = containers_item_data.to_dict()

                containers.append(containers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if containers is not UNSET:
            field_dict["containers"] = containers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_containers() -> Union[Unset, List[Container]]:
            containers = []
            _containers = d.pop("containers")
            for containers_item_data in _containers or []:
                containers_item = Container.from_dict(containers_item_data, strict=False)

                containers.append(containers_item)

            return containers

        try:
            containers = get_containers()
        except KeyError:
            if strict:
                raise
            containers = cast(Union[Unset, List[Container]], UNSET)

        bulk_update_containers_async_task_response = cls(
            containers=containers,
        )

        bulk_update_containers_async_task_response.additional_properties = d
        return bulk_update_containers_async_task_response

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
    def containers(self) -> List[Container]:
        if isinstance(self._containers, Unset):
            raise NotPresentError(self, "containers")
        return self._containers

    @containers.setter
    def containers(self, value: List[Container]) -> None:
        self._containers = value

    @containers.deleter
    def containers(self) -> None:
        self._containers = UNSET
