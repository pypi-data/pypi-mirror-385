from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.not_found_error_error_type import NotFoundErrorErrorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="NotFoundErrorError")


@attr.s(auto_attribs=True, repr=False)
class NotFoundErrorError:
    """  """

    _invalid_id: Union[Unset, str] = UNSET
    _type: Union[Unset, NotFoundErrorErrorType] = UNSET
    _message: Union[Unset, str] = UNSET
    _user_message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("invalid_id={}".format(repr(self._invalid_id)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("user_message={}".format(repr(self._user_message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "NotFoundErrorError({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        invalid_id = self._invalid_id
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        message = self._message
        user_message = self._user_message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if invalid_id is not UNSET:
            field_dict["invalidId"] = invalid_id
        if type is not UNSET:
            field_dict["type"] = type
        if message is not UNSET:
            field_dict["message"] = message
        if user_message is not UNSET:
            field_dict["userMessage"] = user_message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_invalid_id() -> Union[Unset, str]:
            invalid_id = d.pop("invalidId")
            return invalid_id

        try:
            invalid_id = get_invalid_id()
        except KeyError:
            if strict:
                raise
            invalid_id = cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, NotFoundErrorErrorType]:
            type = UNSET
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = NotFoundErrorErrorType(_type)
                except ValueError:
                    type = NotFoundErrorErrorType.of_unknown(_type)

            return type

        try:
            type = get_type()
        except KeyError:
            if strict:
                raise
            type = cast(Union[Unset, NotFoundErrorErrorType], UNSET)

        def get_message() -> Union[Unset, str]:
            message = d.pop("message")
            return message

        try:
            message = get_message()
        except KeyError:
            if strict:
                raise
            message = cast(Union[Unset, str], UNSET)

        def get_user_message() -> Union[Unset, str]:
            user_message = d.pop("userMessage")
            return user_message

        try:
            user_message = get_user_message()
        except KeyError:
            if strict:
                raise
            user_message = cast(Union[Unset, str], UNSET)

        not_found_error_error = cls(
            invalid_id=invalid_id,
            type=type,
            message=message,
            user_message=user_message,
        )

        not_found_error_error.additional_properties = d
        return not_found_error_error

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
    def invalid_id(self) -> str:
        if isinstance(self._invalid_id, Unset):
            raise NotPresentError(self, "invalid_id")
        return self._invalid_id

    @invalid_id.setter
    def invalid_id(self, value: str) -> None:
        self._invalid_id = value

    @invalid_id.deleter
    def invalid_id(self) -> None:
        self._invalid_id = UNSET

    @property
    def type(self) -> NotFoundErrorErrorType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: NotFoundErrorErrorType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def message(self) -> str:
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = UNSET

    @property
    def user_message(self) -> str:
        if isinstance(self._user_message, Unset):
            raise NotPresentError(self, "user_message")
        return self._user_message

    @user_message.setter
    def user_message(self, value: str) -> None:
        self._user_message = value

    @user_message.deleter
    def user_message(self) -> None:
        self._user_message = UNSET
