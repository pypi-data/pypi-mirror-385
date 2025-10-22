from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_bulk_create import WorkflowTaskBulkCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTasksBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTasksBulkCreateRequest:
    """  """

    _workflow_tasks: Union[Unset, List[WorkflowTaskBulkCreate]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_tasks={}".format(repr(self._workflow_tasks)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTasksBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_tasks, Unset):
            workflow_tasks = []
            for workflow_tasks_item_data in self._workflow_tasks:
                workflow_tasks_item = workflow_tasks_item_data.to_dict()

                workflow_tasks.append(workflow_tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if workflow_tasks is not UNSET:
            field_dict["workflowTasks"] = workflow_tasks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_workflow_tasks() -> Union[Unset, List[WorkflowTaskBulkCreate]]:
            workflow_tasks = []
            _workflow_tasks = d.pop("workflowTasks")
            for workflow_tasks_item_data in _workflow_tasks or []:
                workflow_tasks_item = WorkflowTaskBulkCreate.from_dict(workflow_tasks_item_data, strict=False)

                workflow_tasks.append(workflow_tasks_item)

            return workflow_tasks

        try:
            workflow_tasks = get_workflow_tasks()
        except KeyError:
            if strict:
                raise
            workflow_tasks = cast(Union[Unset, List[WorkflowTaskBulkCreate]], UNSET)

        workflow_tasks_bulk_create_request = cls(
            workflow_tasks=workflow_tasks,
        )

        workflow_tasks_bulk_create_request.additional_properties = d
        return workflow_tasks_bulk_create_request

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
    def workflow_tasks(self) -> List[WorkflowTaskBulkCreate]:
        if isinstance(self._workflow_tasks, Unset):
            raise NotPresentError(self, "workflow_tasks")
        return self._workflow_tasks

    @workflow_tasks.setter
    def workflow_tasks(self, value: List[WorkflowTaskBulkCreate]) -> None:
        self._workflow_tasks = value

    @workflow_tasks.deleter
    def workflow_tasks(self) -> None:
        self._workflow_tasks = UNSET
