from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.rna_sequence import RnaSequence
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkUpdateRnaSequencesAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkUpdateRnaSequencesAsyncTaskResponse:
    """  """

    _rna_sequences: Union[Unset, List[RnaSequence]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("rna_sequences={}".format(repr(self._rna_sequences)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkUpdateRnaSequencesAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_sequences, Unset):
            rna_sequences = []
            for rna_sequences_item_data in self._rna_sequences:
                rna_sequences_item = rna_sequences_item_data.to_dict()

                rna_sequences.append(rna_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if rna_sequences is not UNSET:
            field_dict["rnaSequences"] = rna_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_rna_sequences() -> Union[Unset, List[RnaSequence]]:
            rna_sequences = []
            _rna_sequences = d.pop("rnaSequences")
            for rna_sequences_item_data in _rna_sequences or []:
                rna_sequences_item = RnaSequence.from_dict(rna_sequences_item_data, strict=False)

                rna_sequences.append(rna_sequences_item)

            return rna_sequences

        try:
            rna_sequences = get_rna_sequences()
        except KeyError:
            if strict:
                raise
            rna_sequences = cast(Union[Unset, List[RnaSequence]], UNSET)

        bulk_update_rna_sequences_async_task_response = cls(
            rna_sequences=rna_sequences,
        )

        bulk_update_rna_sequences_async_task_response.additional_properties = d
        return bulk_update_rna_sequences_async_task_response

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
    def rna_sequences(self) -> List[RnaSequence]:
        if isinstance(self._rna_sequences, Unset):
            raise NotPresentError(self, "rna_sequences")
        return self._rna_sequences

    @rna_sequences.setter
    def rna_sequences(self, value: List[RnaSequence]) -> None:
        self._rna_sequences = value

    @rna_sequences.deleter
    def rna_sequences(self) -> None:
        self._rna_sequences = UNSET
