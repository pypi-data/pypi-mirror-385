from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.o_auth_unauthorized_error_error import OAuthUnauthorizedErrorError
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthUnauthorizedError")


@attr.s(auto_attribs=True, repr=False)
class OAuthUnauthorizedError:
    """  """

    _error: Union[Unset, OAuthUnauthorizedErrorError] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("error={}".format(repr(self._error)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "OAuthUnauthorizedError({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        error: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._error, Unset):
            error = self._error.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_error() -> Union[Unset, OAuthUnauthorizedErrorError]:
            error: Union[Unset, Union[Unset, OAuthUnauthorizedErrorError]] = UNSET
            _error = d.pop("error")

            if not isinstance(_error, Unset):
                error = OAuthUnauthorizedErrorError.from_dict(_error)

            return error

        try:
            error = get_error()
        except KeyError:
            if strict:
                raise
            error = cast(Union[Unset, OAuthUnauthorizedErrorError], UNSET)

        o_auth_unauthorized_error = cls(
            error=error,
        )

        o_auth_unauthorized_error.additional_properties = d
        return o_auth_unauthorized_error

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
    def error(self) -> OAuthUnauthorizedErrorError:
        if isinstance(self._error, Unset):
            raise NotPresentError(self, "error")
        return self._error

    @error.setter
    def error(self, value: OAuthUnauthorizedErrorError) -> None:
        self._error = value

    @error.deleter
    def error(self) -> None:
        self._error = UNSET
