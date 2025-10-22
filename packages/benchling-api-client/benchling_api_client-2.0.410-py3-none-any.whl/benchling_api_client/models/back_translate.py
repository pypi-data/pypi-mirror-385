from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.back_translate_gc_content import BackTranslateGcContent
from ..models.back_translate_hairpin_parameters import BackTranslateHairpinParameters
from ..models.reduced_pattern import ReducedPattern
from ..types import UNSET, Unset

T = TypeVar("T", bound="BackTranslate")


@attr.s(auto_attribs=True, repr=False)
class BackTranslate:
    """  """

    _aa_sequence_ids: List[str]
    _folder_id: str
    _avoided_cutsite_enzyme_ids: Union[Unset, List[str]] = UNSET
    _codon_usage_table_id: Union[Unset, str] = UNSET
    _gc_content: Union[Unset, BackTranslateGcContent] = BackTranslateGcContent.ANY
    _hairpin_parameters: Union[Unset, BackTranslateHairpinParameters] = UNSET
    _reduced_patterns: Union[Unset, List[ReducedPattern]] = UNSET
    _schema_id: Union[Unset, str] = UNSET
    _should_deplete_uridine: Union[Unset, bool] = False

    def __repr__(self):
        fields = []
        fields.append("aa_sequence_ids={}".format(repr(self._aa_sequence_ids)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("avoided_cutsite_enzyme_ids={}".format(repr(self._avoided_cutsite_enzyme_ids)))
        fields.append("codon_usage_table_id={}".format(repr(self._codon_usage_table_id)))
        fields.append("gc_content={}".format(repr(self._gc_content)))
        fields.append("hairpin_parameters={}".format(repr(self._hairpin_parameters)))
        fields.append("reduced_patterns={}".format(repr(self._reduced_patterns)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("should_deplete_uridine={}".format(repr(self._should_deplete_uridine)))
        return "BackTranslate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequence_ids = self._aa_sequence_ids

        folder_id = self._folder_id
        avoided_cutsite_enzyme_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._avoided_cutsite_enzyme_ids, Unset):
            avoided_cutsite_enzyme_ids = self._avoided_cutsite_enzyme_ids

        codon_usage_table_id = self._codon_usage_table_id
        gc_content: Union[Unset, int] = UNSET
        if not isinstance(self._gc_content, Unset):
            gc_content = self._gc_content.value

        hairpin_parameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._hairpin_parameters, Unset):
            hairpin_parameters = self._hairpin_parameters.to_dict()

        reduced_patterns: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._reduced_patterns, Unset):
            reduced_patterns = []
            for reduced_patterns_item_data in self._reduced_patterns:
                reduced_patterns_item = reduced_patterns_item_data.to_dict()

                reduced_patterns.append(reduced_patterns_item)

        schema_id = self._schema_id
        should_deplete_uridine = self._should_deplete_uridine

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if aa_sequence_ids is not UNSET:
            field_dict["aaSequenceIds"] = aa_sequence_ids
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if avoided_cutsite_enzyme_ids is not UNSET:
            field_dict["avoidedCutsiteEnzymeIds"] = avoided_cutsite_enzyme_ids
        if codon_usage_table_id is not UNSET:
            field_dict["codonUsageTableId"] = codon_usage_table_id
        if gc_content is not UNSET:
            field_dict["gcContent"] = gc_content
        if hairpin_parameters is not UNSET:
            field_dict["hairpinParameters"] = hairpin_parameters
        if reduced_patterns is not UNSET:
            field_dict["reducedPatterns"] = reduced_patterns
        if schema_id is not UNSET:
            field_dict["schemaId"] = schema_id
        if should_deplete_uridine is not UNSET:
            field_dict["shouldDepleteUridine"] = should_deplete_uridine

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_aa_sequence_ids() -> List[str]:
            aa_sequence_ids = cast(List[str], d.pop("aaSequenceIds"))

            return aa_sequence_ids

        try:
            aa_sequence_ids = get_aa_sequence_ids()
        except KeyError:
            if strict:
                raise
            aa_sequence_ids = cast(List[str], UNSET)

        def get_folder_id() -> str:
            folder_id = d.pop("folderId")
            return folder_id

        try:
            folder_id = get_folder_id()
        except KeyError:
            if strict:
                raise
            folder_id = cast(str, UNSET)

        def get_avoided_cutsite_enzyme_ids() -> Union[Unset, List[str]]:
            avoided_cutsite_enzyme_ids = cast(List[str], d.pop("avoidedCutsiteEnzymeIds"))

            return avoided_cutsite_enzyme_ids

        try:
            avoided_cutsite_enzyme_ids = get_avoided_cutsite_enzyme_ids()
        except KeyError:
            if strict:
                raise
            avoided_cutsite_enzyme_ids = cast(Union[Unset, List[str]], UNSET)

        def get_codon_usage_table_id() -> Union[Unset, str]:
            codon_usage_table_id = d.pop("codonUsageTableId")
            return codon_usage_table_id

        try:
            codon_usage_table_id = get_codon_usage_table_id()
        except KeyError:
            if strict:
                raise
            codon_usage_table_id = cast(Union[Unset, str], UNSET)

        def get_gc_content() -> Union[Unset, BackTranslateGcContent]:
            gc_content = UNSET
            _gc_content = d.pop("gcContent")
            if _gc_content is not None and _gc_content is not UNSET:
                try:
                    gc_content = BackTranslateGcContent(_gc_content)
                except ValueError:
                    gc_content = BackTranslateGcContent.of_unknown(_gc_content)

            return gc_content

        try:
            gc_content = get_gc_content()
        except KeyError:
            if strict:
                raise
            gc_content = cast(Union[Unset, BackTranslateGcContent], UNSET)

        def get_hairpin_parameters() -> Union[Unset, BackTranslateHairpinParameters]:
            hairpin_parameters: Union[Unset, Union[Unset, BackTranslateHairpinParameters]] = UNSET
            _hairpin_parameters = d.pop("hairpinParameters")

            if not isinstance(_hairpin_parameters, Unset):
                hairpin_parameters = BackTranslateHairpinParameters.from_dict(_hairpin_parameters)

            return hairpin_parameters

        try:
            hairpin_parameters = get_hairpin_parameters()
        except KeyError:
            if strict:
                raise
            hairpin_parameters = cast(Union[Unset, BackTranslateHairpinParameters], UNSET)

        def get_reduced_patterns() -> Union[Unset, List[ReducedPattern]]:
            reduced_patterns = []
            _reduced_patterns = d.pop("reducedPatterns")
            for reduced_patterns_item_data in _reduced_patterns or []:
                reduced_patterns_item = ReducedPattern.from_dict(reduced_patterns_item_data, strict=False)

                reduced_patterns.append(reduced_patterns_item)

            return reduced_patterns

        try:
            reduced_patterns = get_reduced_patterns()
        except KeyError:
            if strict:
                raise
            reduced_patterns = cast(Union[Unset, List[ReducedPattern]], UNSET)

        def get_schema_id() -> Union[Unset, str]:
            schema_id = d.pop("schemaId")
            return schema_id

        try:
            schema_id = get_schema_id()
        except KeyError:
            if strict:
                raise
            schema_id = cast(Union[Unset, str], UNSET)

        def get_should_deplete_uridine() -> Union[Unset, bool]:
            should_deplete_uridine = d.pop("shouldDepleteUridine")
            return should_deplete_uridine

        try:
            should_deplete_uridine = get_should_deplete_uridine()
        except KeyError:
            if strict:
                raise
            should_deplete_uridine = cast(Union[Unset, bool], UNSET)

        back_translate = cls(
            aa_sequence_ids=aa_sequence_ids,
            folder_id=folder_id,
            avoided_cutsite_enzyme_ids=avoided_cutsite_enzyme_ids,
            codon_usage_table_id=codon_usage_table_id,
            gc_content=gc_content,
            hairpin_parameters=hairpin_parameters,
            reduced_patterns=reduced_patterns,
            schema_id=schema_id,
            should_deplete_uridine=should_deplete_uridine,
        )

        return back_translate

    @property
    def aa_sequence_ids(self) -> List[str]:
        """ IDs of AA sequences to back-translate. """
        if isinstance(self._aa_sequence_ids, Unset):
            raise NotPresentError(self, "aa_sequence_ids")
        return self._aa_sequence_ids

    @aa_sequence_ids.setter
    def aa_sequence_ids(self, value: List[str]) -> None:
        self._aa_sequence_ids = value

    @property
    def folder_id(self) -> str:
        """ID of the folder in which the back-translated sequences will be saved."""
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @property
    def avoided_cutsite_enzyme_ids(self) -> List[str]:
        """List of enzyme IDs whose recognition sites will be avoided when creating the back-translated sequence."""
        if isinstance(self._avoided_cutsite_enzyme_ids, Unset):
            raise NotPresentError(self, "avoided_cutsite_enzyme_ids")
        return self._avoided_cutsite_enzyme_ids

    @avoided_cutsite_enzyme_ids.setter
    def avoided_cutsite_enzyme_ids(self, value: List[str]) -> None:
        self._avoided_cutsite_enzyme_ids = value

    @avoided_cutsite_enzyme_ids.deleter
    def avoided_cutsite_enzyme_ids(self) -> None:
        self._avoided_cutsite_enzyme_ids = UNSET

    @property
    def codon_usage_table_id(self) -> str:
        """ ID of the codon usage table representing the target organism. """
        if isinstance(self._codon_usage_table_id, Unset):
            raise NotPresentError(self, "codon_usage_table_id")
        return self._codon_usage_table_id

    @codon_usage_table_id.setter
    def codon_usage_table_id(self, value: str) -> None:
        self._codon_usage_table_id = value

    @codon_usage_table_id.deleter
    def codon_usage_table_id(self) -> None:
        self._codon_usage_table_id = UNSET

    @property
    def gc_content(self) -> BackTranslateGcContent:
        """The amount of GC content in the back-translated sequence. If not specified, the back-translation will default to ANY (0-1). LOW is defined as below 0.33, MEDIUM as 0.33-0.66, and HIGH as above 0.66."""
        if isinstance(self._gc_content, Unset):
            raise NotPresentError(self, "gc_content")
        return self._gc_content

    @gc_content.setter
    def gc_content(self, value: BackTranslateGcContent) -> None:
        self._gc_content = value

    @gc_content.deleter
    def gc_content(self) -> None:
        self._gc_content = UNSET

    @property
    def hairpin_parameters(self) -> BackTranslateHairpinParameters:
        """These parameters are applied in the AvoidHairpins specification in DNAChisel. If hairpinParameters is not specified, hairpins will not be avoided."""
        if isinstance(self._hairpin_parameters, Unset):
            raise NotPresentError(self, "hairpin_parameters")
        return self._hairpin_parameters

    @hairpin_parameters.setter
    def hairpin_parameters(self, value: BackTranslateHairpinParameters) -> None:
        self._hairpin_parameters = value

    @hairpin_parameters.deleter
    def hairpin_parameters(self) -> None:
        self._hairpin_parameters = UNSET

    @property
    def reduced_patterns(self) -> List[ReducedPattern]:
        """List of patterns to avoid when creating the back-translated sequence, on the coding strand only."""
        if isinstance(self._reduced_patterns, Unset):
            raise NotPresentError(self, "reduced_patterns")
        return self._reduced_patterns

    @reduced_patterns.setter
    def reduced_patterns(self, value: List[ReducedPattern]) -> None:
        self._reduced_patterns = value

    @reduced_patterns.deleter
    def reduced_patterns(self) -> None:
        self._reduced_patterns = UNSET

    @property
    def schema_id(self) -> str:
        """ ID of the resulting DNA sequences' schemas """
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @schema_id.deleter
    def schema_id(self) -> None:
        self._schema_id = UNSET

    @property
    def should_deplete_uridine(self) -> bool:
        """If not specified, the back-translation will default to false, and mRNA uridine depletion will not be performed."""
        if isinstance(self._should_deplete_uridine, Unset):
            raise NotPresentError(self, "should_deplete_uridine")
        return self._should_deplete_uridine

    @should_deplete_uridine.setter
    def should_deplete_uridine(self, value: bool) -> None:
        self._should_deplete_uridine = value

    @should_deplete_uridine.deleter
    def should_deplete_uridine(self) -> None:
        self._should_deplete_uridine = UNSET
