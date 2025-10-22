from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.legacy_workflow_sample import LegacyWorkflowSample
from ..types import UNSET, Unset

T = TypeVar("T", bound="LegacyWorkflowSampleList")


@attr.s(auto_attribs=True, repr=False)
class LegacyWorkflowSampleList:
    """  """

    _samples: Union[Unset, List[LegacyWorkflowSample]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("samples={}".format(repr(self._samples)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LegacyWorkflowSampleList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        samples: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._samples, Unset):
            samples = []
            for samples_item_data in self._samples:
                samples_item = samples_item_data.to_dict()

                samples.append(samples_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if samples is not UNSET:
            field_dict["samples"] = samples

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_samples() -> Union[Unset, List[LegacyWorkflowSample]]:
            samples = []
            _samples = d.pop("samples")
            for samples_item_data in _samples or []:
                samples_item = LegacyWorkflowSample.from_dict(samples_item_data, strict=False)

                samples.append(samples_item)

            return samples

        try:
            samples = get_samples()
        except KeyError:
            if strict:
                raise
            samples = cast(Union[Unset, List[LegacyWorkflowSample]], UNSET)

        legacy_workflow_sample_list = cls(
            samples=samples,
        )

        legacy_workflow_sample_list.additional_properties = d
        return legacy_workflow_sample_list

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
    def samples(self) -> List[LegacyWorkflowSample]:
        if isinstance(self._samples, Unset):
            raise NotPresentError(self, "samples")
        return self._samples

    @samples.setter
    def samples(self, value: List[LegacyWorkflowSample]) -> None:
        self._samples = value

    @samples.deleter
    def samples(self) -> None:
        self._samples = UNSET
