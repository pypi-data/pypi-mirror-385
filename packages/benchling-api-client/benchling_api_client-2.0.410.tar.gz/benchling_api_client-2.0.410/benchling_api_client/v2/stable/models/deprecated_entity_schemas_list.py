from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.deprecated_entity_schema import DeprecatedEntitySchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeprecatedEntitySchemasList")


@attr.s(auto_attribs=True, repr=False)
class DeprecatedEntitySchemasList:
    """  """

    _entity_schemas: Union[Unset, List[DeprecatedEntitySchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_schemas={}".format(repr(self._entity_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DeprecatedEntitySchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entity_schemas, Unset):
            entity_schemas = []
            for entity_schemas_item_data in self._entity_schemas:
                entity_schemas_item = entity_schemas_item_data.to_dict()

                entity_schemas.append(entity_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if entity_schemas is not UNSET:
            field_dict["entitySchemas"] = entity_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_entity_schemas() -> Union[Unset, List[DeprecatedEntitySchema]]:
            entity_schemas = []
            _entity_schemas = d.pop("entitySchemas")
            for entity_schemas_item_data in _entity_schemas or []:
                entity_schemas_item = DeprecatedEntitySchema.from_dict(entity_schemas_item_data, strict=False)

                entity_schemas.append(entity_schemas_item)

            return entity_schemas

        try:
            entity_schemas = get_entity_schemas()
        except KeyError:
            if strict:
                raise
            entity_schemas = cast(Union[Unset, List[DeprecatedEntitySchema]], UNSET)

        deprecated_entity_schemas_list = cls(
            entity_schemas=entity_schemas,
        )

        deprecated_entity_schemas_list.additional_properties = d
        return deprecated_entity_schemas_list

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
    def entity_schemas(self) -> List[DeprecatedEntitySchema]:
        if isinstance(self._entity_schemas, Unset):
            raise NotPresentError(self, "entity_schemas")
        return self._entity_schemas

    @entity_schemas.setter
    def entity_schemas(self, value: List[DeprecatedEntitySchema]) -> None:
        self._entity_schemas = value

    @entity_schemas.deleter
    def entity_schemas(self) -> None:
        self._entity_schemas = UNSET
