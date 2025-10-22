from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.box import Box
from ..types import UNSET, Unset

T = TypeVar("T", bound="BoxesBulkGet")


@attr.s(auto_attribs=True, repr=False)
class BoxesBulkGet:
    """  """

    _boxes: Union[Unset, List[Box]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("boxes={}".format(repr(self._boxes)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BoxesBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        boxes: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._boxes, Unset):
            boxes = []
            for boxes_item_data in self._boxes:
                boxes_item = boxes_item_data.to_dict()

                boxes.append(boxes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if boxes is not UNSET:
            field_dict["boxes"] = boxes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_boxes() -> Union[Unset, List[Box]]:
            boxes = []
            _boxes = d.pop("boxes")
            for boxes_item_data in _boxes or []:
                boxes_item = Box.from_dict(boxes_item_data, strict=False)

                boxes.append(boxes_item)

            return boxes

        try:
            boxes = get_boxes()
        except KeyError:
            if strict:
                raise
            boxes = cast(Union[Unset, List[Box]], UNSET)

        boxes_bulk_get = cls(
            boxes=boxes,
        )

        boxes_bulk_get.additional_properties = d
        return boxes_bulk_get

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
    def boxes(self) -> List[Box]:
        if isinstance(self._boxes, Unset):
            raise NotPresentError(self, "boxes")
        return self._boxes

    @boxes.setter
    def boxes(self, value: List[Box]) -> None:
        self._boxes = value

    @boxes.deleter
    def boxes(self) -> None:
        self._boxes = UNSET
