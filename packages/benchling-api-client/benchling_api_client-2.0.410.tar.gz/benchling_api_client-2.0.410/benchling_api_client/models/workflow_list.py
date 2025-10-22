from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.legacy_workflow import LegacyWorkflow
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowList:
    """  """

    _workflows: Union[Unset, List[LegacyWorkflow]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflows={}".format(repr(self._workflows)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflows: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflows, Unset):
            workflows = []
            for workflows_item_data in self._workflows:
                workflows_item = workflows_item_data.to_dict()

                workflows.append(workflows_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if workflows is not UNSET:
            field_dict["workflows"] = workflows

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_workflows() -> Union[Unset, List[LegacyWorkflow]]:
            workflows = []
            _workflows = d.pop("workflows")
            for workflows_item_data in _workflows or []:
                workflows_item = LegacyWorkflow.from_dict(workflows_item_data, strict=False)

                workflows.append(workflows_item)

            return workflows

        try:
            workflows = get_workflows()
        except KeyError:
            if strict:
                raise
            workflows = cast(Union[Unset, List[LegacyWorkflow]], UNSET)

        workflow_list = cls(
            workflows=workflows,
        )

        workflow_list.additional_properties = d
        return workflow_list

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
    def workflows(self) -> List[LegacyWorkflow]:
        if isinstance(self._workflows, Unset):
            raise NotPresentError(self, "workflows")
        return self._workflows

    @workflows.setter
    def workflows(self, value: List[LegacyWorkflow]) -> None:
        self._workflows = value

    @workflows.deleter
    def workflows(self) -> None:
        self._workflows = UNSET
