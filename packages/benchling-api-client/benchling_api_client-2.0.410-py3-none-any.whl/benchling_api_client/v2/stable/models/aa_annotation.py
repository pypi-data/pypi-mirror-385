from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaAnnotation")


@attr.s(auto_attribs=True, repr=False)
class AaAnnotation:
    """  """

    _color: Union[Unset, str] = UNSET
    _end: Union[Unset, int] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _notes: Union[Unset, str] = UNSET
    _start: Union[Unset, int] = UNSET
    _type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("color={}".format(repr(self._color)))
        fields.append("end={}".format(repr(self._end)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("start={}".format(repr(self._start)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AaAnnotation({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        color = self._color
        end = self._end
        id = self._id
        name = self._name
        notes = self._notes
        start = self._start
        type = self._type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if color is not UNSET:
            field_dict["color"] = color
        if end is not UNSET:
            field_dict["end"] = end
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if notes is not UNSET:
            field_dict["notes"] = notes
        if start is not UNSET:
            field_dict["start"] = start
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_color() -> Union[Unset, str]:
            color = d.pop("color")
            return color

        try:
            color = get_color()
        except KeyError:
            if strict:
                raise
            color = cast(Union[Unset, str], UNSET)

        def get_end() -> Union[Unset, int]:
            end = d.pop("end")
            return end

        try:
            end = get_end()
        except KeyError:
            if strict:
                raise
            end = cast(Union[Unset, int], UNSET)

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

        def get_notes() -> Union[Unset, str]:
            notes = d.pop("notes")
            return notes

        try:
            notes = get_notes()
        except KeyError:
            if strict:
                raise
            notes = cast(Union[Unset, str], UNSET)

        def get_start() -> Union[Unset, int]:
            start = d.pop("start")
            return start

        try:
            start = get_start()
        except KeyError:
            if strict:
                raise
            start = cast(Union[Unset, int], UNSET)

        def get_type() -> Union[Unset, str]:
            type = d.pop("type")
            return type

        try:
            type = get_type()
        except KeyError:
            if strict:
                raise
            type = cast(Union[Unset, str], UNSET)

        aa_annotation = cls(
            color=color,
            end=end,
            id=id,
            name=name,
            notes=notes,
            start=start,
            type=type,
        )

        aa_annotation.additional_properties = d
        return aa_annotation

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
    def color(self) -> str:
        if isinstance(self._color, Unset):
            raise NotPresentError(self, "color")
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value

    @color.deleter
    def color(self) -> None:
        self._color = UNSET

    @property
    def end(self) -> int:
        """ 0-based exclusive end index. The end of the AA sequence is always represented as 0. """
        if isinstance(self._end, Unset):
            raise NotPresentError(self, "end")
        return self._end

    @end.setter
    def end(self, value: int) -> None:
        self._end = value

    @end.deleter
    def end(self) -> None:
        self._end = UNSET

    @property
    def id(self) -> str:
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
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def notes(self) -> str:
        if isinstance(self._notes, Unset):
            raise NotPresentError(self, "notes")
        return self._notes

    @notes.setter
    def notes(self, value: str) -> None:
        self._notes = value

    @notes.deleter
    def notes(self) -> None:
        self._notes = UNSET

    @property
    def start(self) -> int:
        """ 0-based inclusive start index. """
        if isinstance(self._start, Unset):
            raise NotPresentError(self, "start")
        return self._start

    @start.setter
    def start(self, value: int) -> None:
        self._start = value

    @start.deleter
    def start(self) -> None:
        self._start = UNSET

    @property
    def type(self) -> str:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
