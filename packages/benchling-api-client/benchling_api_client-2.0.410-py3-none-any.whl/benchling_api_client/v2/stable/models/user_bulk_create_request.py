from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.user_create import UserCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class UserBulkCreateRequest:
    """  """

    _users: Union[Unset, List[UserCreate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("users={}".format(repr(self._users)))
        return "UserBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        users: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._users, Unset):
            users = []
            for users_item_data in self._users:
                users_item = users_item_data.to_dict()

                users.append(users_item)

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if users is not UNSET:
            field_dict["users"] = users

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_users() -> Union[Unset, List[UserCreate]]:
            users = []
            _users = d.pop("users")
            for users_item_data in _users or []:
                users_item = UserCreate.from_dict(users_item_data, strict=False)

                users.append(users_item)

            return users

        try:
            users = get_users()
        except KeyError:
            if strict:
                raise
            users = cast(Union[Unset, List[UserCreate]], UNSET)

        user_bulk_create_request = cls(
            users=users,
        )

        return user_bulk_create_request

    @property
    def users(self) -> List[UserCreate]:
        if isinstance(self._users, Unset):
            raise NotPresentError(self, "users")
        return self._users

    @users.setter
    def users(self, value: List[UserCreate]) -> None:
        self._users = value

    @users.deleter
    def users(self) -> None:
        self._users = UNSET
