from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTasksArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTasksArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type"""

    _workflow_task_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_task_ids={}".format(repr(self._workflow_task_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTasksArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_task_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_task_ids, Unset):
            workflow_task_ids = self._workflow_task_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if workflow_task_ids is not UNSET:
            field_dict["workflowTaskIds"] = workflow_task_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_workflow_task_ids() -> Union[Unset, List[str]]:
            workflow_task_ids = cast(List[str], d.pop("workflowTaskIds"))

            return workflow_task_ids

        try:
            workflow_task_ids = get_workflow_task_ids()
        except KeyError:
            if strict:
                raise
            workflow_task_ids = cast(Union[Unset, List[str]], UNSET)

        workflow_tasks_archival_change = cls(
            workflow_task_ids=workflow_task_ids,
        )

        workflow_tasks_archival_change.additional_properties = d
        return workflow_tasks_archival_change

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
    def workflow_task_ids(self) -> List[str]:
        if isinstance(self._workflow_task_ids, Unset):
            raise NotPresentError(self, "workflow_task_ids")
        return self._workflow_task_ids

    @workflow_task_ids.setter
    def workflow_task_ids(self, value: List[str]) -> None:
        self._workflow_task_ids = value

    @workflow_task_ids.deleter
    def workflow_task_ids(self) -> None:
        self._workflow_task_ids = UNSET
