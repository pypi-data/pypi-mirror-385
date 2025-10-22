from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entity_worklist_items_list_type import EntityWorklistItemsListType
from ..models.generic_entity import GenericEntity
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntityWorklistItemsList")


@attr.s(auto_attribs=True, repr=False)
class EntityWorklistItemsList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _type: Union[Unset, EntityWorklistItemsListType] = UNSET
    _worklist_items: Union[Unset, List[GenericEntity]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("worklist_items={}".format(repr(self._worklist_items)))
        return "EntityWorklistItemsList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        worklist_items: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._worklist_items, Unset):
            worklist_items = []
            for worklist_items_item_data in self._worklist_items:
                worklist_items_item = worklist_items_item_data.to_dict()

                worklist_items.append(worklist_items_item)

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if type is not UNSET:
            field_dict["type"] = type
        if worklist_items is not UNSET:
            field_dict["worklistItems"] = worklist_items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        try:
            next_token = get_next_token()
        except KeyError:
            if strict:
                raise
            next_token = cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, EntityWorklistItemsListType]:
            type = UNSET
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = EntityWorklistItemsListType(_type)
                except ValueError:
                    type = EntityWorklistItemsListType.of_unknown(_type)

            return type

        try:
            type = get_type()
        except KeyError:
            if strict:
                raise
            type = cast(Union[Unset, EntityWorklistItemsListType], UNSET)

        def get_worklist_items() -> Union[Unset, List[GenericEntity]]:
            worklist_items = []
            _worklist_items = d.pop("worklistItems")
            for worklist_items_item_data in _worklist_items or []:
                worklist_items_item = GenericEntity.from_dict(worklist_items_item_data, strict=False)

                worklist_items.append(worklist_items_item)

            return worklist_items

        try:
            worklist_items = get_worklist_items()
        except KeyError:
            if strict:
                raise
            worklist_items = cast(Union[Unset, List[GenericEntity]], UNSET)

        entity_worklist_items_list = cls(
            next_token=next_token,
            type=type,
            worklist_items=worklist_items,
        )

        return entity_worklist_items_list

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET

    @property
    def type(self) -> EntityWorklistItemsListType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: EntityWorklistItemsListType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def worklist_items(self) -> List[GenericEntity]:
        if isinstance(self._worklist_items, Unset):
            raise NotPresentError(self, "worklist_items")
        return self._worklist_items

    @worklist_items.setter
    def worklist_items(self, value: List[GenericEntity]) -> None:
        self._worklist_items = value

    @worklist_items.deleter
    def worklist_items(self) -> None:
        self._worklist_items = UNSET
