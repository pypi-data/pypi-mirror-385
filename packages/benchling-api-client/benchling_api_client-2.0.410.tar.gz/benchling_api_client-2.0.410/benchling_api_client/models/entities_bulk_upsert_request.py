from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequence_bulk_upsert_request import AaSequenceBulkUpsertRequest
from ..models.custom_entity_bulk_upsert_request import CustomEntityBulkUpsertRequest
from ..models.dna_sequence_bulk_upsert_request import DnaSequenceBulkUpsertRequest
from ..models.molecule_bulk_upsert_request import MoleculeBulkUpsertRequest
from ..models.oligo_bulk_upsert_request import OligoBulkUpsertRequest
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitiesBulkUpsertRequest")


@attr.s(auto_attribs=True, repr=False)
class EntitiesBulkUpsertRequest:
    """  """

    _aa_sequences: Union[Unset, List[AaSequenceBulkUpsertRequest]] = UNSET
    _custom_entities: Union[Unset, List[CustomEntityBulkUpsertRequest]] = UNSET
    _dna_oligos: Union[Unset, List[OligoBulkUpsertRequest]] = UNSET
    _dna_sequences: Union[Unset, List[DnaSequenceBulkUpsertRequest]] = UNSET
    _molecules: Union[Unset, List[MoleculeBulkUpsertRequest]] = UNSET
    _rna_oligos: Union[Unset, List[OligoBulkUpsertRequest]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("aa_sequences={}".format(repr(self._aa_sequences)))
        fields.append("custom_entities={}".format(repr(self._custom_entities)))
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        fields.append("dna_sequences={}".format(repr(self._dna_sequences)))
        fields.append("molecules={}".format(repr(self._molecules)))
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        return "EntitiesBulkUpsertRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aa_sequences, Unset):
            aa_sequences = []
            for aa_sequences_item_data in self._aa_sequences:
                aa_sequences_item = aa_sequences_item_data.to_dict()

                aa_sequences.append(aa_sequences_item)

        custom_entities: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._custom_entities, Unset):
            custom_entities = []
            for custom_entities_item_data in self._custom_entities:
                custom_entities_item = custom_entities_item_data.to_dict()

                custom_entities.append(custom_entities_item)

        dna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligos, Unset):
            dna_oligos = []
            for dna_oligos_item_data in self._dna_oligos:
                dna_oligos_item = dna_oligos_item_data.to_dict()

                dna_oligos.append(dna_oligos_item)

        dna_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_sequences, Unset):
            dna_sequences = []
            for dna_sequences_item_data in self._dna_sequences:
                dna_sequences_item = dna_sequences_item_data.to_dict()

                dna_sequences.append(dna_sequences_item)

        molecules: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._molecules, Unset):
            molecules = []
            for molecules_item_data in self._molecules:
                molecules_item = molecules_item_data.to_dict()

                molecules.append(molecules_item)

        rna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_oligos, Unset):
            rna_oligos = []
            for rna_oligos_item_data in self._rna_oligos:
                rna_oligos_item = rna_oligos_item_data.to_dict()

                rna_oligos.append(rna_oligos_item)

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if aa_sequences is not UNSET:
            field_dict["aaSequences"] = aa_sequences
        if custom_entities is not UNSET:
            field_dict["customEntities"] = custom_entities
        if dna_oligos is not UNSET:
            field_dict["dnaOligos"] = dna_oligos
        if dna_sequences is not UNSET:
            field_dict["dnaSequences"] = dna_sequences
        if molecules is not UNSET:
            field_dict["molecules"] = molecules
        if rna_oligos is not UNSET:
            field_dict["rnaOligos"] = rna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_aa_sequences() -> Union[Unset, List[AaSequenceBulkUpsertRequest]]:
            aa_sequences = []
            _aa_sequences = d.pop("aaSequences")
            for aa_sequences_item_data in _aa_sequences or []:
                aa_sequences_item = AaSequenceBulkUpsertRequest.from_dict(
                    aa_sequences_item_data, strict=False
                )

                aa_sequences.append(aa_sequences_item)

            return aa_sequences

        try:
            aa_sequences = get_aa_sequences()
        except KeyError:
            if strict:
                raise
            aa_sequences = cast(Union[Unset, List[AaSequenceBulkUpsertRequest]], UNSET)

        def get_custom_entities() -> Union[Unset, List[CustomEntityBulkUpsertRequest]]:
            custom_entities = []
            _custom_entities = d.pop("customEntities")
            for custom_entities_item_data in _custom_entities or []:
                custom_entities_item = CustomEntityBulkUpsertRequest.from_dict(
                    custom_entities_item_data, strict=False
                )

                custom_entities.append(custom_entities_item)

            return custom_entities

        try:
            custom_entities = get_custom_entities()
        except KeyError:
            if strict:
                raise
            custom_entities = cast(Union[Unset, List[CustomEntityBulkUpsertRequest]], UNSET)

        def get_dna_oligos() -> Union[Unset, List[OligoBulkUpsertRequest]]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos or []:
                dna_oligos_item = OligoBulkUpsertRequest.from_dict(dna_oligos_item_data, strict=False)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        try:
            dna_oligos = get_dna_oligos()
        except KeyError:
            if strict:
                raise
            dna_oligos = cast(Union[Unset, List[OligoBulkUpsertRequest]], UNSET)

        def get_dna_sequences() -> Union[Unset, List[DnaSequenceBulkUpsertRequest]]:
            dna_sequences = []
            _dna_sequences = d.pop("dnaSequences")
            for dna_sequences_item_data in _dna_sequences or []:
                dna_sequences_item = DnaSequenceBulkUpsertRequest.from_dict(
                    dna_sequences_item_data, strict=False
                )

                dna_sequences.append(dna_sequences_item)

            return dna_sequences

        try:
            dna_sequences = get_dna_sequences()
        except KeyError:
            if strict:
                raise
            dna_sequences = cast(Union[Unset, List[DnaSequenceBulkUpsertRequest]], UNSET)

        def get_molecules() -> Union[Unset, List[MoleculeBulkUpsertRequest]]:
            molecules = []
            _molecules = d.pop("molecules")
            for molecules_item_data in _molecules or []:
                molecules_item = MoleculeBulkUpsertRequest.from_dict(molecules_item_data, strict=False)

                molecules.append(molecules_item)

            return molecules

        try:
            molecules = get_molecules()
        except KeyError:
            if strict:
                raise
            molecules = cast(Union[Unset, List[MoleculeBulkUpsertRequest]], UNSET)

        def get_rna_oligos() -> Union[Unset, List[OligoBulkUpsertRequest]]:
            rna_oligos = []
            _rna_oligos = d.pop("rnaOligos")
            for rna_oligos_item_data in _rna_oligos or []:
                rna_oligos_item = OligoBulkUpsertRequest.from_dict(rna_oligos_item_data, strict=False)

                rna_oligos.append(rna_oligos_item)

            return rna_oligos

        try:
            rna_oligos = get_rna_oligos()
        except KeyError:
            if strict:
                raise
            rna_oligos = cast(Union[Unset, List[OligoBulkUpsertRequest]], UNSET)

        entities_bulk_upsert_request = cls(
            aa_sequences=aa_sequences,
            custom_entities=custom_entities,
            dna_oligos=dna_oligos,
            dna_sequences=dna_sequences,
            molecules=molecules,
            rna_oligos=rna_oligos,
        )

        return entities_bulk_upsert_request

    @property
    def aa_sequences(self) -> List[AaSequenceBulkUpsertRequest]:
        if isinstance(self._aa_sequences, Unset):
            raise NotPresentError(self, "aa_sequences")
        return self._aa_sequences

    @aa_sequences.setter
    def aa_sequences(self, value: List[AaSequenceBulkUpsertRequest]) -> None:
        self._aa_sequences = value

    @aa_sequences.deleter
    def aa_sequences(self) -> None:
        self._aa_sequences = UNSET

    @property
    def custom_entities(self) -> List[CustomEntityBulkUpsertRequest]:
        if isinstance(self._custom_entities, Unset):
            raise NotPresentError(self, "custom_entities")
        return self._custom_entities

    @custom_entities.setter
    def custom_entities(self, value: List[CustomEntityBulkUpsertRequest]) -> None:
        self._custom_entities = value

    @custom_entities.deleter
    def custom_entities(self) -> None:
        self._custom_entities = UNSET

    @property
    def dna_oligos(self) -> List[OligoBulkUpsertRequest]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[OligoBulkUpsertRequest]) -> None:
        self._dna_oligos = value

    @dna_oligos.deleter
    def dna_oligos(self) -> None:
        self._dna_oligos = UNSET

    @property
    def dna_sequences(self) -> List[DnaSequenceBulkUpsertRequest]:
        if isinstance(self._dna_sequences, Unset):
            raise NotPresentError(self, "dna_sequences")
        return self._dna_sequences

    @dna_sequences.setter
    def dna_sequences(self, value: List[DnaSequenceBulkUpsertRequest]) -> None:
        self._dna_sequences = value

    @dna_sequences.deleter
    def dna_sequences(self) -> None:
        self._dna_sequences = UNSET

    @property
    def molecules(self) -> List[MoleculeBulkUpsertRequest]:
        if isinstance(self._molecules, Unset):
            raise NotPresentError(self, "molecules")
        return self._molecules

    @molecules.setter
    def molecules(self, value: List[MoleculeBulkUpsertRequest]) -> None:
        self._molecules = value

    @molecules.deleter
    def molecules(self) -> None:
        self._molecules = UNSET

    @property
    def rna_oligos(self) -> List[OligoBulkUpsertRequest]:
        if isinstance(self._rna_oligos, Unset):
            raise NotPresentError(self, "rna_oligos")
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[OligoBulkUpsertRequest]) -> None:
        self._rna_oligos = value

    @rna_oligos.deleter
    def rna_oligos(self) -> None:
        self._rna_oligos = UNSET
