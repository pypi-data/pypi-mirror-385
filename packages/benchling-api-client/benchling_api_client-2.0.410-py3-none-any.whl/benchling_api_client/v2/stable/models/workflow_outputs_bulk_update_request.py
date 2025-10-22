from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_output_bulk_update import WorkflowOutputBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutputsBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutputsBulkUpdateRequest:
    """  """

    _workflow_outputs: Union[Unset, List[WorkflowOutputBulkUpdate]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_outputs={}".format(repr(self._workflow_outputs)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutputsBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_outputs, Unset):
            workflow_outputs = []
            for workflow_outputs_item_data in self._workflow_outputs:
                workflow_outputs_item = workflow_outputs_item_data.to_dict()

                workflow_outputs.append(workflow_outputs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if workflow_outputs is not UNSET:
            field_dict["workflowOutputs"] = workflow_outputs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_workflow_outputs() -> Union[Unset, List[WorkflowOutputBulkUpdate]]:
            workflow_outputs = []
            _workflow_outputs = d.pop("workflowOutputs")
            for workflow_outputs_item_data in _workflow_outputs or []:
                workflow_outputs_item = WorkflowOutputBulkUpdate.from_dict(
                    workflow_outputs_item_data, strict=False
                )

                workflow_outputs.append(workflow_outputs_item)

            return workflow_outputs

        try:
            workflow_outputs = get_workflow_outputs()
        except KeyError:
            if strict:
                raise
            workflow_outputs = cast(Union[Unset, List[WorkflowOutputBulkUpdate]], UNSET)

        workflow_outputs_bulk_update_request = cls(
            workflow_outputs=workflow_outputs,
        )

        workflow_outputs_bulk_update_request.additional_properties = d
        return workflow_outputs_bulk_update_request

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
    def workflow_outputs(self) -> List[WorkflowOutputBulkUpdate]:
        if isinstance(self._workflow_outputs, Unset):
            raise NotPresentError(self, "workflow_outputs")
        return self._workflow_outputs

    @workflow_outputs.setter
    def workflow_outputs(self, value: List[WorkflowOutputBulkUpdate]) -> None:
        self._workflow_outputs = value

    @workflow_outputs.deleter
    def workflow_outputs(self) -> None:
        self._workflow_outputs = UNSET
