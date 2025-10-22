import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.custom_fields import CustomFields
from ..models.fields import Fields
from ..models.registration_origin import RegistrationOrigin
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="Molecule")


@attr.s(auto_attribs=True, repr=False)
class Molecule:
    """  """

    _aliases: Union[Unset, List[str]] = UNSET
    _api_url: Union[Unset, str] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _authors: Union[Unset, List[UserSummary]] = UNSET
    _canonicalized_smiles: Union[Unset, str] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _entity_registry_id: Union[Unset, None, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _folder_id: Union[Unset, None, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET
    _original_smiles: Union[Unset, None, str] = UNSET
    _registration_origin: Union[Unset, None, RegistrationOrigin] = UNSET
    _registry_id: Union[Unset, None, str] = UNSET
    _schema: Union[Unset, None, SchemaSummary] = UNSET
    _web_url: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("aliases={}".format(repr(self._aliases)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("authors={}".format(repr(self._authors)))
        fields.append("canonicalized_smiles={}".format(repr(self._canonicalized_smiles)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("original_smiles={}".format(repr(self._original_smiles)))
        fields.append("registration_origin={}".format(repr(self._registration_origin)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("web_url={}".format(repr(self._web_url)))
        return "Molecule({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aliases: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aliases, Unset):
            aliases = self._aliases

        api_url = self._api_url
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        authors: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._authors, Unset):
            authors = []
            for authors_item_data in self._authors:
                authors_item = authors_item_data.to_dict()

                authors.append(authors_item)

        canonicalized_smiles = self._canonicalized_smiles
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        entity_registry_id = self._entity_registry_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        folder_id = self._folder_id
        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name
        original_smiles = self._original_smiles
        registration_origin: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._registration_origin, Unset):
            registration_origin = self._registration_origin.to_dict() if self._registration_origin else None

        registry_id = self._registry_id
        schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict() if self._schema else None

        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if authors is not UNSET:
            field_dict["authors"] = authors
        if canonicalized_smiles is not UNSET:
            field_dict["canonicalizedSmiles"] = canonicalized_smiles
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if entity_registry_id is not UNSET:
            field_dict["entityRegistryId"] = entity_registry_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if original_smiles is not UNSET:
            field_dict["originalSmiles"] = original_smiles
        if registration_origin is not UNSET:
            field_dict["registrationOrigin"] = registration_origin
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id
        if schema is not UNSET:
            field_dict["schema"] = schema
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_aliases() -> Union[Unset, List[str]]:
            aliases = cast(List[str], d.pop("aliases"))

            return aliases

        try:
            aliases = get_aliases()
        except KeyError:
            if strict:
                raise
            aliases = cast(Union[Unset, List[str]], UNSET)

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        try:
            api_url = get_api_url()
        except KeyError:
            if strict:
                raise
            api_url = cast(Union[Unset, str], UNSET)

        def get_archive_record() -> Union[Unset, None, ArchiveRecord]:
            archive_record = None
            _archive_record = d.pop("archiveRecord")

            if _archive_record is not None and not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecord.from_dict(_archive_record)

            return archive_record

        try:
            archive_record = get_archive_record()
        except KeyError:
            if strict:
                raise
            archive_record = cast(Union[Unset, None, ArchiveRecord], UNSET)

        def get_authors() -> Union[Unset, List[UserSummary]]:
            authors = []
            _authors = d.pop("authors")
            for authors_item_data in _authors or []:
                authors_item = UserSummary.from_dict(authors_item_data, strict=False)

                authors.append(authors_item)

            return authors

        try:
            authors = get_authors()
        except KeyError:
            if strict:
                raise
            authors = cast(Union[Unset, List[UserSummary]], UNSET)

        def get_canonicalized_smiles() -> Union[Unset, str]:
            canonicalized_smiles = d.pop("canonicalizedSmiles")
            return canonicalized_smiles

        try:
            canonicalized_smiles = get_canonicalized_smiles()
        except KeyError:
            if strict:
                raise
            canonicalized_smiles = cast(Union[Unset, str], UNSET)

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        try:
            created_at = get_created_at()
        except KeyError:
            if strict:
                raise
            created_at = cast(Union[Unset, datetime.datetime], UNSET)

        def get_creator() -> Union[Unset, UserSummary]:
            creator: Union[Unset, Union[Unset, UserSummary]] = UNSET
            _creator = d.pop("creator")

            if not isinstance(_creator, Unset):
                creator = UserSummary.from_dict(_creator)

            return creator

        try:
            creator = get_creator()
        except KeyError:
            if strict:
                raise
            creator = cast(Union[Unset, UserSummary], UNSET)

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

        def get_entity_registry_id() -> Union[Unset, None, str]:
            entity_registry_id = d.pop("entityRegistryId")
            return entity_registry_id

        try:
            entity_registry_id = get_entity_registry_id()
        except KeyError:
            if strict:
                raise
            entity_registry_id = cast(Union[Unset, None, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Union[Unset, Fields]] = UNSET
            _fields = d.pop("fields")

            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        try:
            fields = get_fields()
        except KeyError:
            if strict:
                raise
            fields = cast(Union[Unset, Fields], UNSET)

        def get_folder_id() -> Union[Unset, None, str]:
            folder_id = d.pop("folderId")
            return folder_id

        try:
            folder_id = get_folder_id()
        except KeyError:
            if strict:
                raise
            folder_id = cast(Union[Unset, None, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        try:
            id = get_id()
        except KeyError:
            if strict:
                raise
            id = cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        try:
            modified_at = get_modified_at()
        except KeyError:
            if strict:
                raise
            modified_at = cast(Union[Unset, datetime.datetime], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        try:
            name = get_name()
        except KeyError:
            if strict:
                raise
            name = cast(Union[Unset, str], UNSET)

        def get_original_smiles() -> Union[Unset, None, str]:
            original_smiles = d.pop("originalSmiles")
            return original_smiles

        try:
            original_smiles = get_original_smiles()
        except KeyError:
            if strict:
                raise
            original_smiles = cast(Union[Unset, None, str], UNSET)

        def get_registration_origin() -> Union[Unset, None, RegistrationOrigin]:
            registration_origin = None
            _registration_origin = d.pop("registrationOrigin")

            if _registration_origin is not None and not isinstance(_registration_origin, Unset):
                registration_origin = RegistrationOrigin.from_dict(_registration_origin)

            return registration_origin

        try:
            registration_origin = get_registration_origin()
        except KeyError:
            if strict:
                raise
            registration_origin = cast(Union[Unset, None, RegistrationOrigin], UNSET)

        def get_registry_id() -> Union[Unset, None, str]:
            registry_id = d.pop("registryId")
            return registry_id

        try:
            registry_id = get_registry_id()
        except KeyError:
            if strict:
                raise
            registry_id = cast(Union[Unset, None, str], UNSET)

        def get_schema() -> Union[Unset, None, SchemaSummary]:
            schema = None
            _schema = d.pop("schema")

            if _schema is not None and not isinstance(_schema, Unset):
                schema = SchemaSummary.from_dict(_schema)

            return schema

        try:
            schema = get_schema()
        except KeyError:
            if strict:
                raise
            schema = cast(Union[Unset, None, SchemaSummary], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        try:
            web_url = get_web_url()
        except KeyError:
            if strict:
                raise
            web_url = cast(Union[Unset, str], UNSET)

        molecule = cls(
            aliases=aliases,
            api_url=api_url,
            archive_record=archive_record,
            authors=authors,
            canonicalized_smiles=canonicalized_smiles,
            created_at=created_at,
            creator=creator,
            custom_fields=custom_fields,
            entity_registry_id=entity_registry_id,
            fields=fields,
            folder_id=folder_id,
            id=id,
            modified_at=modified_at,
            name=name,
            original_smiles=original_smiles,
            registration_origin=registration_origin,
            registry_id=registry_id,
            schema=schema,
            web_url=web_url,
        )

        return molecule

    @property
    def aliases(self) -> List[str]:
        """ Array of aliases. """
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
    def api_url(self) -> str:
        """ The canonical url of the Molecule in the API. """
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def archive_record(self) -> Optional[ArchiveRecord]:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

    @property
    def authors(self) -> List[UserSummary]:
        if isinstance(self._authors, Unset):
            raise NotPresentError(self, "authors")
        return self._authors

    @authors.setter
    def authors(self, value: List[UserSummary]) -> None:
        self._authors = value

    @authors.deleter
    def authors(self) -> None:
        self._authors = UNSET

    @property
    def canonicalized_smiles(self) -> str:
        """ The canonicalized chemical structure in SMILES format. """
        if isinstance(self._canonicalized_smiles, Unset):
            raise NotPresentError(self, "canonicalized_smiles")
        return self._canonicalized_smiles

    @canonicalized_smiles.setter
    def canonicalized_smiles(self, value: str) -> None:
        self._canonicalized_smiles = value

    @canonicalized_smiles.deleter
    def canonicalized_smiles(self) -> None:
        self._canonicalized_smiles = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        """ DateTime the Molecule was created. """
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

    @property
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

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
    def entity_registry_id(self) -> Optional[str]:
        """ Registry ID of the Molecule if registered. """
        if isinstance(self._entity_registry_id, Unset):
            raise NotPresentError(self, "entity_registry_id")
        return self._entity_registry_id

    @entity_registry_id.setter
    def entity_registry_id(self, value: Optional[str]) -> None:
        self._entity_registry_id = value

    @entity_registry_id.deleter
    def entity_registry_id(self) -> None:
        self._entity_registry_id = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def folder_id(self) -> Optional[str]:
        """ ID of the folder that contains the Molecule. """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: Optional[str]) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET

    @property
    def id(self) -> str:
        """ ID of the Molecule. """
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
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Molecule was last modified. """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def name(self) -> str:
        """ Name of the Molecule. """
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
    def original_smiles(self) -> Optional[str]:
        """ The original chemical structure supplied by the user in SMILES format. Null if the user did not originally supply SMILES. """
        if isinstance(self._original_smiles, Unset):
            raise NotPresentError(self, "original_smiles")
        return self._original_smiles

    @original_smiles.setter
    def original_smiles(self, value: Optional[str]) -> None:
        self._original_smiles = value

    @original_smiles.deleter
    def original_smiles(self) -> None:
        self._original_smiles = UNSET

    @property
    def registration_origin(self) -> Optional[RegistrationOrigin]:
        if isinstance(self._registration_origin, Unset):
            raise NotPresentError(self, "registration_origin")
        return self._registration_origin

    @registration_origin.setter
    def registration_origin(self, value: Optional[RegistrationOrigin]) -> None:
        self._registration_origin = value

    @registration_origin.deleter
    def registration_origin(self) -> None:
        self._registration_origin = UNSET

    @property
    def registry_id(self) -> Optional[str]:
        """ Registry the Molecule is registered in. """
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: Optional[str]) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET

    @property
    def schema(self) -> Optional[SchemaSummary]:
        if isinstance(self._schema, Unset):
            raise NotPresentError(self, "schema")
        return self._schema

    @schema.setter
    def schema(self, value: Optional[SchemaSummary]) -> None:
        self._schema = value

    @schema.deleter
    def schema(self) -> None:
        self._schema = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the Molecule. """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
