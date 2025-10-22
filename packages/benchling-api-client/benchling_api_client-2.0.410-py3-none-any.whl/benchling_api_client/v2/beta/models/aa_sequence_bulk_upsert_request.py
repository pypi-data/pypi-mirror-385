from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_annotation import AaAnnotation
from ..models.archive_record_set import ArchiveRecordSet
from ..models.custom_fields import CustomFields
from ..models.fields_with_resolution import FieldsWithResolution
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequenceBulkUpsertRequest")


@attr.s(auto_attribs=True, repr=False)
class AaSequenceBulkUpsertRequest:
    """  """

    _name: str
    _schema_id: str
    _registry_id: str
    _aliases: Union[Unset, List[str]] = UNSET
    _amino_acids: Union[Unset, str] = UNSET
    _annotations: Union[Unset, List[AaAnnotation]] = UNSET
    _author_ids: Union[Unset, List[str]] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _fields: Union[Unset, FieldsWithResolution] = UNSET
    _folder_id: Union[Unset, str] = UNSET
    _entity_registry_id: Union[Unset, str] = UNSET
    _archive_record: Union[Unset, ArchiveRecordSet] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("aliases={}".format(repr(self._aliases)))
        fields.append("amino_acids={}".format(repr(self._amino_acids)))
        fields.append("annotations={}".format(repr(self._annotations)))
        fields.append("author_ids={}".format(repr(self._author_ids)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AaSequenceBulkUpsertRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        schema_id = self._schema_id
        registry_id = self._registry_id
        aliases: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aliases, Unset):
            aliases = self._aliases

        amino_acids = self._amino_acids
        annotations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._annotations, Unset):
            annotations = []
            for annotations_item_data in self._annotations:
                annotations_item = annotations_item_data.to_dict()

                annotations.append(annotations_item)

        author_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._author_ids, Unset):
            author_ids = self._author_ids

        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        folder_id = self._folder_id
        entity_registry_id = self._entity_registry_id
        archive_record: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if name is not UNSET:
            field_dict["name"] = name
        if schema_id is not UNSET:
            field_dict["schemaId"] = schema_id
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if amino_acids is not UNSET:
            field_dict["aminoAcids"] = amino_acids
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if author_ids is not UNSET:
            field_dict["authorIds"] = author_ids
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if fields is not UNSET:
            field_dict["fields"] = fields
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if entity_registry_id is not UNSET:
            field_dict["entityRegistryId"] = entity_registry_id
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        try:
            name = get_name()
        except KeyError:
            if strict:
                raise
            name = cast(str, UNSET)

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        try:
            schema_id = get_schema_id()
        except KeyError:
            if strict:
                raise
            schema_id = cast(str, UNSET)

        def get_registry_id() -> str:
            registry_id = d.pop("registryId")
            return registry_id

        try:
            registry_id = get_registry_id()
        except KeyError:
            if strict:
                raise
            registry_id = cast(str, UNSET)

        def get_aliases() -> Union[Unset, List[str]]:
            aliases = cast(List[str], d.pop("aliases"))

            return aliases

        try:
            aliases = get_aliases()
        except KeyError:
            if strict:
                raise
            aliases = cast(Union[Unset, List[str]], UNSET)

        def get_amino_acids() -> Union[Unset, str]:
            amino_acids = d.pop("aminoAcids")
            return amino_acids

        try:
            amino_acids = get_amino_acids()
        except KeyError:
            if strict:
                raise
            amino_acids = cast(Union[Unset, str], UNSET)

        def get_annotations() -> Union[Unset, List[AaAnnotation]]:
            annotations = []
            _annotations = d.pop("annotations")
            for annotations_item_data in _annotations or []:
                annotations_item = AaAnnotation.from_dict(annotations_item_data, strict=False)

                annotations.append(annotations_item)

            return annotations

        try:
            annotations = get_annotations()
        except KeyError:
            if strict:
                raise
            annotations = cast(Union[Unset, List[AaAnnotation]], UNSET)

        def get_author_ids() -> Union[Unset, List[str]]:
            author_ids = cast(List[str], d.pop("authorIds"))

            return author_ids

        try:
            author_ids = get_author_ids()
        except KeyError:
            if strict:
                raise
            author_ids = cast(Union[Unset, List[str]], UNSET)

        def get_custom_fields() -> Union[Unset, CustomFields]:
            custom_fields: Union[Unset, Union[Unset, CustomFields]] = UNSET
            _custom_fields = d.pop("customFields")

            if not isinstance(_custom_fields, Unset):
                custom_fields = CustomFields.from_dict(_custom_fields)

            return custom_fields

        try:
            custom_fields = get_custom_fields()
        except KeyError:
            if strict:
                raise
            custom_fields = cast(Union[Unset, CustomFields], UNSET)

        def get_fields() -> Union[Unset, FieldsWithResolution]:
            fields: Union[Unset, Union[Unset, FieldsWithResolution]] = UNSET
            _fields = d.pop("fields")

            if not isinstance(_fields, Unset):
                fields = FieldsWithResolution.from_dict(_fields)

            return fields

        try:
            fields = get_fields()
        except KeyError:
            if strict:
                raise
            fields = cast(Union[Unset, FieldsWithResolution], UNSET)

        def get_folder_id() -> Union[Unset, str]:
            folder_id = d.pop("folderId")
            return folder_id

        try:
            folder_id = get_folder_id()
        except KeyError:
            if strict:
                raise
            folder_id = cast(Union[Unset, str], UNSET)

        def get_entity_registry_id() -> Union[Unset, str]:
            entity_registry_id = d.pop("entityRegistryId")
            return entity_registry_id

        try:
            entity_registry_id = get_entity_registry_id()
        except KeyError:
            if strict:
                raise
            entity_registry_id = cast(Union[Unset, str], UNSET)

        def get_archive_record() -> Union[Unset, ArchiveRecordSet]:
            archive_record: Union[Unset, Union[Unset, ArchiveRecordSet]] = UNSET
            _archive_record = d.pop("archiveRecord")

            if not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecordSet.from_dict(_archive_record)

            return archive_record

        try:
            archive_record = get_archive_record()
        except KeyError:
            if strict:
                raise
            archive_record = cast(Union[Unset, ArchiveRecordSet], UNSET)

        aa_sequence_bulk_upsert_request = cls(
            name=name,
            schema_id=schema_id,
            registry_id=registry_id,
            aliases=aliases,
            amino_acids=amino_acids,
            annotations=annotations,
            author_ids=author_ids,
            custom_fields=custom_fields,
            fields=fields,
            folder_id=folder_id,
            entity_registry_id=entity_registry_id,
            archive_record=archive_record,
        )

        aa_sequence_bulk_upsert_request.additional_properties = d
        return aa_sequence_bulk_upsert_request

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
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def schema_id(self) -> str:
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def registry_id(self) -> str:
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @property
    def aliases(self) -> List[str]:
        """ Aliases to add to the AA sequence """
        if isinstance(self._aliases, Unset):
            raise NotPresentError(self, "aliases")
        return self._aliases

    @aliases.setter
    def aliases(self, value: List[str]) -> None:
        self._aliases = value

    @aliases.deleter
    def aliases(self) -> None:
        self._aliases = UNSET

    @property
    def amino_acids(self) -> str:
        """Amino acids for the AA sequence."""
        if isinstance(self._amino_acids, Unset):
            raise NotPresentError(self, "amino_acids")
        return self._amino_acids

    @amino_acids.setter
    def amino_acids(self, value: str) -> None:
        self._amino_acids = value

    @amino_acids.deleter
    def amino_acids(self) -> None:
        self._amino_acids = UNSET

    @property
    def annotations(self) -> List[AaAnnotation]:
        """Annotations to create on the AA sequence."""
        if isinstance(self._annotations, Unset):
            raise NotPresentError(self, "annotations")
        return self._annotations

    @annotations.setter
    def annotations(self, value: List[AaAnnotation]) -> None:
        self._annotations = value

    @annotations.deleter
    def annotations(self) -> None:
        self._annotations = UNSET

    @property
    def author_ids(self) -> List[str]:
        """ IDs of users to set as the AA sequence's authors. """
        if isinstance(self._author_ids, Unset):
            raise NotPresentError(self, "author_ids")
        return self._author_ids

    @author_ids.setter
    def author_ids(self, value: List[str]) -> None:
        self._author_ids = value

    @author_ids.deleter
    def author_ids(self) -> None:
        self._author_ids = UNSET

    @property
    def custom_fields(self) -> CustomFields:
        if isinstance(self._custom_fields, Unset):
            raise NotPresentError(self, "custom_fields")
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, value: CustomFields) -> None:
        self._custom_fields = value

    @custom_fields.deleter
    def custom_fields(self) -> None:
        self._custom_fields = UNSET

    @property
    def fields(self) -> FieldsWithResolution:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: FieldsWithResolution) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def folder_id(self) -> str:
        """ID of the folder containing the AA sequence."""
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET

    @property
    def entity_registry_id(self) -> str:
        """ Registry ID of the entity in Benchling. """
        if isinstance(self._entity_registry_id, Unset):
            raise NotPresentError(self, "entity_registry_id")
        return self._entity_registry_id

    @entity_registry_id.setter
    def entity_registry_id(self, value: str) -> None:
        self._entity_registry_id = value

    @entity_registry_id.deleter
    def entity_registry_id(self) -> None:
        self._entity_registry_id = UNSET

    @property
    def archive_record(self) -> ArchiveRecordSet:
        """ Currently, we only support setting a null value for archiveRecord, which unarchives the item """
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: ArchiveRecordSet) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET
