from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.data_frame_create_manifest_manifest_item import DataFrameCreateManifestManifestItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataFrameCreateManifest")


@attr.s(auto_attribs=True, repr=False)
class DataFrameCreateManifest:
    """  """

    _manifest: Union[Unset, List[DataFrameCreateManifestManifestItem]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("manifest={}".format(repr(self._manifest)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DataFrameCreateManifest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        manifest: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._manifest, Unset):
            manifest = []
            for manifest_item_data in self._manifest:
                manifest_item = manifest_item_data.to_dict()

                manifest.append(manifest_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if manifest is not UNSET:
            field_dict["manifest"] = manifest

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_manifest() -> Union[Unset, List[DataFrameCreateManifestManifestItem]]:
            manifest = []
            _manifest = d.pop("manifest")
            for manifest_item_data in _manifest or []:
                manifest_item = DataFrameCreateManifestManifestItem.from_dict(
                    manifest_item_data, strict=False
                )

                manifest.append(manifest_item)

            return manifest

        try:
            manifest = get_manifest()
        except KeyError:
            if strict:
                raise
            manifest = cast(Union[Unset, List[DataFrameCreateManifestManifestItem]], UNSET)

        data_frame_create_manifest = cls(
            manifest=manifest,
        )

        data_frame_create_manifest.additional_properties = d
        return data_frame_create_manifest

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
    def manifest(self) -> List[DataFrameCreateManifestManifestItem]:
        if isinstance(self._manifest, Unset):
            raise NotPresentError(self, "manifest")
        return self._manifest

    @manifest.setter
    def manifest(self, value: List[DataFrameCreateManifestManifestItem]) -> None:
        self._manifest = value

    @manifest.deleter
    def manifest(self) -> None:
        self._manifest = UNSET
