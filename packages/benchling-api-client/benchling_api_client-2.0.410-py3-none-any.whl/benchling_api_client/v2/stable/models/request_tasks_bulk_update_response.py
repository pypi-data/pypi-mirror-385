from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.request_task import RequestTask
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestTasksBulkUpdateResponse")


@attr.s(auto_attribs=True, repr=False)
class RequestTasksBulkUpdateResponse:
    """  """

    _tasks: Union[Unset, List[RequestTask]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("tasks={}".format(repr(self._tasks)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestTasksBulkUpdateResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._tasks, Unset):
            tasks = []
            for tasks_item_data in self._tasks:
                tasks_item = tasks_item_data.to_dict()

                tasks.append(tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if tasks is not UNSET:
            field_dict["tasks"] = tasks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_tasks() -> Union[Unset, List[RequestTask]]:
            tasks = []
            _tasks = d.pop("tasks")
            for tasks_item_data in _tasks or []:
                tasks_item = RequestTask.from_dict(tasks_item_data, strict=False)

                tasks.append(tasks_item)

            return tasks

        try:
            tasks = get_tasks()
        except KeyError:
            if strict:
                raise
            tasks = cast(Union[Unset, List[RequestTask]], UNSET)

        request_tasks_bulk_update_response = cls(
            tasks=tasks,
        )

        request_tasks_bulk_update_response.additional_properties = d
        return request_tasks_bulk_update_response

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
    def tasks(self) -> List[RequestTask]:
        """ The Legacy Request Tasks to update """
        if isinstance(self._tasks, Unset):
            raise NotPresentError(self, "tasks")
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[RequestTask]) -> None:
        self._tasks = value

    @tasks.deleter
    def tasks(self) -> None:
        self._tasks = UNSET
