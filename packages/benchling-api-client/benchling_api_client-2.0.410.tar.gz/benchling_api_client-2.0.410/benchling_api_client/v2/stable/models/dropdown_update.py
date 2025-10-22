from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.dropdown_option_update import DropdownOptionUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownUpdate")


@attr.s(auto_attribs=True, repr=False)
class DropdownUpdate:
    """  """

    _options: List[DropdownOptionUpdate]

    def __repr__(self):
        fields = []
        fields.append("options={}".format(repr(self._options)))
        return "DropdownUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        options = []
        for options_item_data in self._options:
            options_item = options_item_data.to_dict()

            options.append(options_item)

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_options() -> List[DropdownOptionUpdate]:
            options = []
            _options = d.pop("options")
            for options_item_data in _options:
                options_item = DropdownOptionUpdate.from_dict(options_item_data, strict=False)

                options.append(options_item)

            return options

        try:
            options = get_options()
        except KeyError:
            if strict:
                raise
            options = cast(List[DropdownOptionUpdate], UNSET)

        dropdown_update = cls(
            options=options,
        )

        return dropdown_update

    @property
    def options(self) -> List[DropdownOptionUpdate]:
        """ Options to set for the dropdown """
        if isinstance(self._options, Unset):
            raise NotPresentError(self, "options")
        return self._options

    @options.setter
    def options(self, value: List[DropdownOptionUpdate]) -> None:
        self._options = value
