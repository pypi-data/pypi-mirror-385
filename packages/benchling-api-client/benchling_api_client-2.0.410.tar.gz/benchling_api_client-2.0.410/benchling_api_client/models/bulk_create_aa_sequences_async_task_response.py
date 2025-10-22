from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequence import AaSequence
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCreateAaSequencesAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkCreateAaSequencesAsyncTaskResponse:
    """  """

    _aa_sequences: Union[Unset, List[AaSequence]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("aa_sequences={}".format(repr(self._aa_sequences)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkCreateAaSequencesAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aa_sequences, Unset):
            aa_sequences = []
            for aa_sequences_item_data in self._aa_sequences:
                aa_sequences_item = aa_sequences_item_data.to_dict()

                aa_sequences.append(aa_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if aa_sequences is not UNSET:
            field_dict["aaSequences"] = aa_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_aa_sequences() -> Union[Unset, List[AaSequence]]:
            aa_sequences = []
            _aa_sequences = d.pop("aaSequences")
            for aa_sequences_item_data in _aa_sequences or []:
                aa_sequences_item = AaSequence.from_dict(aa_sequences_item_data, strict=False)

                aa_sequences.append(aa_sequences_item)

            return aa_sequences

        try:
            aa_sequences = get_aa_sequences()
        except KeyError:
            if strict:
                raise
            aa_sequences = cast(Union[Unset, List[AaSequence]], UNSET)

        bulk_create_aa_sequences_async_task_response = cls(
            aa_sequences=aa_sequences,
        )

        bulk_create_aa_sequences_async_task_response.additional_properties = d
        return bulk_create_aa_sequences_async_task_response

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
    def aa_sequences(self) -> List[AaSequence]:
        if isinstance(self._aa_sequences, Unset):
            raise NotPresentError(self, "aa_sequences")
        return self._aa_sequences

    @aa_sequences.setter
    def aa_sequences(self, value: List[AaSequence]) -> None:
        self._aa_sequences = value

    @aa_sequences.deleter
    def aa_sequences(self) -> None:
        self._aa_sequences = UNSET
