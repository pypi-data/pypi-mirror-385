from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowNodeTaskGroupSummary")


@attr.s(auto_attribs=True, repr=False)
class WorkflowNodeTaskGroupSummary:
    """  """

    _node_config_id: Union[Unset, str] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("node_config_id={}".format(repr(self._node_config_id)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowNodeTaskGroupSummary({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        node_config_id = self._node_config_id
        display_id = self._display_id
        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if node_config_id is not UNSET:
            field_dict["nodeConfigId"] = node_config_id
        if display_id is not UNSET:
            field_dict["displayId"] = display_id
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_node_config_id() -> Union[Unset, str]:
            node_config_id = d.pop("nodeConfigId")
            return node_config_id

        try:
            node_config_id = get_node_config_id()
        except KeyError:
            if strict:
                raise
            node_config_id = cast(Union[Unset, str], UNSET)

        def get_display_id() -> Union[Unset, str]:
            display_id = d.pop("displayId")
            return display_id

        try:
            display_id = get_display_id()
        except KeyError:
            if strict:
                raise
            display_id = cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        try:
            id = get_id()
        except KeyError:
            if strict:
                raise
            id = cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        try:
            name = get_name()
        except KeyError:
            if strict:
                raise
            name = cast(Union[Unset, str], UNSET)

        workflow_node_task_group_summary = cls(
            node_config_id=node_config_id,
            display_id=display_id,
            id=id,
            name=name,
        )

        workflow_node_task_group_summary.additional_properties = d
        return workflow_node_task_group_summary

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
    def node_config_id(self) -> str:
        """ The node in a Flowchart that this task group is associated with. This will be null if the task group is not part of a flowchart. """
        if isinstance(self._node_config_id, Unset):
            raise NotPresentError(self, "node_config_id")
        return self._node_config_id

    @node_config_id.setter
    def node_config_id(self, value: str) -> None:
        self._node_config_id = value

    @node_config_id.deleter
    def node_config_id(self) -> None:
        self._node_config_id = UNSET

    @property
    def display_id(self) -> str:
        """ User-friendly ID of the workflow task group """
        if isinstance(self._display_id, Unset):
            raise NotPresentError(self, "display_id")
        return self._display_id

    @display_id.setter
    def display_id(self, value: str) -> None:
        self._display_id = value

    @display_id.deleter
    def display_id(self) -> None:
        self._display_id = UNSET

    @property
    def id(self) -> str:
        """ The ID of the workflow task group """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def name(self) -> str:
        """ The name of the workflow task group """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
