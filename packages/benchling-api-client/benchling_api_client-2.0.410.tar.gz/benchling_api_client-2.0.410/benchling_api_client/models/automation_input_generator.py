import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.automation_file_automation_file_config import AutomationFileAutomationFileConfig
from ..models.automation_file_status import AutomationFileStatus
from ..models.blob import Blob
from ..models.lab_automation_transform import LabAutomationTransform
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationInputGenerator")


@attr.s(auto_attribs=True, repr=False)
class AutomationInputGenerator:
    """  """

    _api_url: Union[Unset, str] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _transforms: Union[Unset, List[Optional[LabAutomationTransform]]] = UNSET
    _assay_run_id: Union[Unset, str] = UNSET
    _automation_file_config: Union[Unset, AutomationFileAutomationFileConfig] = UNSET
    _file: Union[Unset, None, Blob] = UNSET
    _status: Union[Unset, AutomationFileStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("transforms={}".format(repr(self._transforms)))
        fields.append("assay_run_id={}".format(repr(self._assay_run_id)))
        fields.append("automation_file_config={}".format(repr(self._automation_file_config)))
        fields.append("file={}".format(repr(self._file)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AutomationInputGenerator({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_url = self._api_url
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        transforms: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._transforms, Unset):
            transforms = []
            for transforms_item_data in self._transforms:
                transforms_item = transforms_item_data.to_dict() if transforms_item_data else None

                transforms.append(transforms_item)

        assay_run_id = self._assay_run_id
        automation_file_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._automation_file_config, Unset):
            automation_file_config = self._automation_file_config.to_dict()

        file: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._file, Unset):
            file = self._file.to_dict() if self._file else None

        status: Union[Unset, int] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if transforms is not UNSET:
            field_dict["transforms"] = transforms
        if assay_run_id is not UNSET:
            field_dict["assayRunId"] = assay_run_id
        if automation_file_config is not UNSET:
            field_dict["automationFileConfig"] = automation_file_config
        if file is not UNSET:
            field_dict["file"] = file
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        try:
            api_url = get_api_url()
        except KeyError:
            if strict:
                raise
            api_url = cast(Union[Unset, str], UNSET)

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

        def get_transforms() -> Union[Unset, List[Optional[LabAutomationTransform]]]:
            transforms = []
            _transforms = d.pop("transforms")
            for transforms_item_data in _transforms or []:
                transforms_item = None
                _transforms_item = transforms_item_data

                if _transforms_item is not None:
                    transforms_item = LabAutomationTransform.from_dict(_transforms_item)

                transforms.append(transforms_item)

            return transforms

        try:
            transforms = get_transforms()
        except KeyError:
            if strict:
                raise
            transforms = cast(Union[Unset, List[Optional[LabAutomationTransform]]], UNSET)

        def get_assay_run_id() -> Union[Unset, str]:
            assay_run_id = d.pop("assayRunId")
            return assay_run_id

        try:
            assay_run_id = get_assay_run_id()
        except KeyError:
            if strict:
                raise
            assay_run_id = cast(Union[Unset, str], UNSET)

        def get_automation_file_config() -> Union[Unset, AutomationFileAutomationFileConfig]:
            automation_file_config: Union[Unset, Union[Unset, AutomationFileAutomationFileConfig]] = UNSET
            _automation_file_config = d.pop("automationFileConfig")

            if not isinstance(_automation_file_config, Unset):
                automation_file_config = AutomationFileAutomationFileConfig.from_dict(_automation_file_config)

            return automation_file_config

        try:
            automation_file_config = get_automation_file_config()
        except KeyError:
            if strict:
                raise
            automation_file_config = cast(Union[Unset, AutomationFileAutomationFileConfig], UNSET)

        def get_file() -> Union[Unset, None, Blob]:
            file = None
            _file = d.pop("file")

            if _file is not None and not isinstance(_file, Unset):
                file = Blob.from_dict(_file)

            return file

        try:
            file = get_file()
        except KeyError:
            if strict:
                raise
            file = cast(Union[Unset, None, Blob], UNSET)

        def get_status() -> Union[Unset, AutomationFileStatus]:
            status = UNSET
            _status = d.pop("status")
            if _status is not None and _status is not UNSET:
                try:
                    status = AutomationFileStatus(_status)
                except ValueError:
                    status = AutomationFileStatus.of_unknown(_status)

            return status

        try:
            status = get_status()
        except KeyError:
            if strict:
                raise
            status = cast(Union[Unset, AutomationFileStatus], UNSET)

        automation_input_generator = cls(
            api_url=api_url,
            created_at=created_at,
            id=id,
            modified_at=modified_at,
            transforms=transforms,
            assay_run_id=assay_run_id,
            automation_file_config=automation_file_config,
            file=file,
            status=status,
        )

        automation_input_generator.additional_properties = d
        return automation_input_generator

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
    def api_url(self) -> str:
        """ The canonical url of the Automation Input Generator in the API. """
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
    def created_at(self) -> datetime.datetime:
        """ DateTime the Automation Input Generator was last modified """
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
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Automation Input Generator was last modified """
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
    def transforms(self) -> List[Optional[LabAutomationTransform]]:
        if isinstance(self._transforms, Unset):
            raise NotPresentError(self, "transforms")
        return self._transforms

    @transforms.setter
    def transforms(self, value: List[Optional[LabAutomationTransform]]) -> None:
        self._transforms = value

    @transforms.deleter
    def transforms(self) -> None:
        self._transforms = UNSET

    @property
    def assay_run_id(self) -> str:
        if isinstance(self._assay_run_id, Unset):
            raise NotPresentError(self, "assay_run_id")
        return self._assay_run_id

    @assay_run_id.setter
    def assay_run_id(self, value: str) -> None:
        self._assay_run_id = value

    @assay_run_id.deleter
    def assay_run_id(self) -> None:
        self._assay_run_id = UNSET

    @property
    def automation_file_config(self) -> AutomationFileAutomationFileConfig:
        if isinstance(self._automation_file_config, Unset):
            raise NotPresentError(self, "automation_file_config")
        return self._automation_file_config

    @automation_file_config.setter
    def automation_file_config(self, value: AutomationFileAutomationFileConfig) -> None:
        self._automation_file_config = value

    @automation_file_config.deleter
    def automation_file_config(self) -> None:
        self._automation_file_config = UNSET

    @property
    def file(self) -> Optional[Blob]:
        if isinstance(self._file, Unset):
            raise NotPresentError(self, "file")
        return self._file

    @file.setter
    def file(self, value: Optional[Blob]) -> None:
        self._file = value

    @file.deleter
    def file(self) -> None:
        self._file = UNSET

    @property
    def status(self) -> AutomationFileStatus:
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: AutomationFileStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET
