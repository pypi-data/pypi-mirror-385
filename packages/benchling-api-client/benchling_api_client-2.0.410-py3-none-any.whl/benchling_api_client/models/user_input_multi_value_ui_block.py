from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserInputMultiValueUiBlock")


@attr.s(auto_attribs=True, repr=False)
class UserInputMultiValueUiBlock:
    """  """

    _id: str
    _value: Optional[List[str]]
    _label: Union[Unset, None, str] = UNSET
    _required: Union[Unset, None, bool] = UNSET
    _enabled: Union[Unset, None, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("label={}".format(repr(self._label)))
        fields.append("required={}".format(repr(self._required)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("enabled={}".format(repr(self._enabled)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "UserInputMultiValueUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        label = self._label
        required = self._required
        if self._value is None:
            value = None
        else:
            value = self._value

        enabled = self._enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if id is not UNSET:
            field_dict["id"] = id
        if label is not UNSET:
            field_dict["label"] = label
        if required is not UNSET:
            field_dict["required"] = required
        if value is not UNSET:
            field_dict["value"] = value
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_id() -> str:
            id = d.pop("id")
            return id

        try:
            id = get_id()
        except KeyError:
            if strict:
                raise
            id = cast(str, UNSET)

        def get_label() -> Union[Unset, None, str]:
            label = d.pop("label")
            return label

        try:
            label = get_label()
        except KeyError:
            if strict:
                raise
            label = cast(Union[Unset, None, str], UNSET)

        def get_required() -> Union[Unset, None, bool]:
            required = d.pop("required")
            return required

        try:
            required = get_required()
        except KeyError:
            if strict:
                raise
            required = cast(Union[Unset, None, bool], UNSET)

        def get_value() -> Optional[List[str]]:
            value = cast(List[str], d.pop("value"))

            return value

        try:
            value = get_value()
        except KeyError:
            if strict:
                raise
            value = cast(Optional[List[str]], UNSET)

        def get_enabled() -> Union[Unset, None, bool]:
            enabled = d.pop("enabled")
            return enabled

        try:
            enabled = get_enabled()
        except KeyError:
            if strict:
                raise
            enabled = cast(Union[Unset, None, bool], UNSET)

        user_input_multi_value_ui_block = cls(
            id=id,
            label=label,
            required=required,
            value=value,
            enabled=enabled,
        )

        user_input_multi_value_ui_block.additional_properties = d
        return user_input_multi_value_ui_block

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
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def label(self) -> Optional[str]:
        if isinstance(self._label, Unset):
            raise NotPresentError(self, "label")
        return self._label

    @label.setter
    def label(self, value: Optional[str]) -> None:
        self._label = value

    @label.deleter
    def label(self) -> None:
        self._label = UNSET

    @property
    def required(self) -> Optional[bool]:
        """When true, the user must provide a value before the app can proceed. Block must specify a label if required is set to true."""
        if isinstance(self._required, Unset):
            raise NotPresentError(self, "required")
        return self._required

    @required.setter
    def required(self, value: Optional[bool]) -> None:
        self._required = value

    @required.deleter
    def required(self) -> None:
        self._required = UNSET

    @property
    def value(self) -> Optional[List[str]]:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[List[str]]) -> None:
        self._value = value

    @property
    def enabled(self) -> Optional[bool]:
        if isinstance(self._enabled, Unset):
            raise NotPresentError(self, "enabled")
        return self._enabled

    @enabled.setter
    def enabled(self, value: Optional[bool]) -> None:
        self._enabled = value

    @enabled.deleter
    def enabled(self) -> None:
        self._enabled = UNSET
