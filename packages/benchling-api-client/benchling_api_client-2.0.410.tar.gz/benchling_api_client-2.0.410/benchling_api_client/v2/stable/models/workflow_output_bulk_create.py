from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutputBulkCreate")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutputBulkCreate:
    """  """

    _workflow_task_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_task_id={}".format(repr(self._workflow_task_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutputBulkCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_task_id = self._workflow_task_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if workflow_task_id is not UNSET:
            field_dict["workflowTaskId"] = workflow_task_id
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_workflow_task_id() -> Union[Unset, str]:
            workflow_task_id = d.pop("workflowTaskId")
            return workflow_task_id

        try:
            workflow_task_id = get_workflow_task_id()
        except KeyError:
            if strict:
                raise
            workflow_task_id = cast(Union[Unset, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Union[Unset, Fields]] = UNSET
            _fields = d.pop("fields")

            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        try:
            fields = get_fields()
        except KeyError:
            if strict:
                raise
            fields = cast(Union[Unset, Fields], UNSET)

        workflow_output_bulk_create = cls(
            workflow_task_id=workflow_task_id,
            fields=fields,
        )

        workflow_output_bulk_create.additional_properties = d
        return workflow_output_bulk_create

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
    def workflow_task_id(self) -> str:
        """ The ID of the workflow task this output belogns to """
        if isinstance(self._workflow_task_id, Unset):
            raise NotPresentError(self, "workflow_task_id")
        return self._workflow_task_id

    @workflow_task_id.setter
    def workflow_task_id(self, value: str) -> None:
        self._workflow_task_id = value

    @workflow_task_id.deleter
    def workflow_task_id(self) -> None:
        self._workflow_task_id = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET
