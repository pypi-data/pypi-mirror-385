from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.async_task_errors import AsyncTaskErrors
from ..models.async_task_errors_item import AsyncTaskErrorsItem
from ..models.async_task_status import AsyncTaskStatus
from ..models.bulk_update_containers_async_task_response import BulkUpdateContainersAsyncTaskResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkUpdateContainersAsyncTask")


@attr.s(auto_attribs=True, repr=False)
class BulkUpdateContainersAsyncTask:
    """  """

    _status: AsyncTaskStatus
    _response: Union[Unset, BulkUpdateContainersAsyncTaskResponse] = UNSET
    _errors: Union[Unset, List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType] = UNSET
    _message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("status={}".format(repr(self._status)))
        fields.append("response={}".format(repr(self._response)))
        fields.append("errors={}".format(repr(self._errors)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkUpdateContainersAsyncTask({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        status = self._status.value

        response: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._response, Unset):
            response = self._response.to_dict()

        errors: Union[Unset, List[Any], Dict[str, Any]]
        if isinstance(self._errors, Unset):
            errors = UNSET
        elif isinstance(self._errors, UnknownType):
            errors = self._errors.value
        elif isinstance(self._errors, list):
            errors = UNSET
            if not isinstance(self._errors, Unset):
                errors = []
                for errors_item_data in self._errors:
                    errors_item = errors_item_data.to_dict()

                    errors.append(errors_item)

        else:
            errors = UNSET
            if not isinstance(self._errors, Unset):
                errors = self._errors.to_dict()

        message = self._message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if status is not UNSET:
            field_dict["status"] = status
        if response is not UNSET:
            field_dict["response"] = response
        if errors is not UNSET:
            field_dict["errors"] = errors
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_status() -> AsyncTaskStatus:
            _status = d.pop("status")
            try:
                status = AsyncTaskStatus(_status)
            except ValueError:
                status = AsyncTaskStatus.of_unknown(_status)

            return status

        try:
            status = get_status()
        except KeyError:
            if strict:
                raise
            status = cast(AsyncTaskStatus, UNSET)

        def get_response() -> Union[Unset, BulkUpdateContainersAsyncTaskResponse]:
            response: Union[Unset, Union[Unset, BulkUpdateContainersAsyncTaskResponse]] = UNSET
            _response = d.pop("response")

            if not isinstance(_response, Unset):
                response = BulkUpdateContainersAsyncTaskResponse.from_dict(_response)

            return response

        try:
            response = get_response()
        except KeyError:
            if strict:
                raise
            response = cast(Union[Unset, BulkUpdateContainersAsyncTaskResponse], UNSET)

        def get_errors() -> Union[Unset, List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType]:
            def _parse_errors(
                data: Union[Unset, List[Any], Dict[str, Any]]
            ) -> Union[Unset, List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType]:
                errors: Union[Unset, List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType]
                if isinstance(data, Unset):
                    return data
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    errors = []
                    _errors = data
                    for errors_item_data in _errors or []:
                        errors_item = AsyncTaskErrorsItem.from_dict(errors_item_data, strict=False)

                        errors.append(errors_item)

                    return errors
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    errors = UNSET
                    _errors = data

                    if not isinstance(_errors, Unset):
                        errors = AsyncTaskErrors.from_dict(_errors)

                    return errors
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            errors = _parse_errors(d.pop("errors"))

            return errors

        try:
            errors = get_errors()
        except KeyError:
            if strict:
                raise
            errors = cast(Union[Unset, List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType], UNSET)

        def get_message() -> Union[Unset, str]:
            message = d.pop("message")
            return message

        try:
            message = get_message()
        except KeyError:
            if strict:
                raise
            message = cast(Union[Unset, str], UNSET)

        bulk_update_containers_async_task = cls(
            status=status,
            response=response,
            errors=errors,
            message=message,
        )

        bulk_update_containers_async_task.additional_properties = d
        return bulk_update_containers_async_task

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
    def status(self) -> AsyncTaskStatus:
        """ The current state of the task. """
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: AsyncTaskStatus) -> None:
        self._status = value

    @property
    def response(self) -> BulkUpdateContainersAsyncTaskResponse:
        if isinstance(self._response, Unset):
            raise NotPresentError(self, "response")
        return self._response

    @response.setter
    def response(self, value: BulkUpdateContainersAsyncTaskResponse) -> None:
        self._response = value

    @response.deleter
    def response(self) -> None:
        self._response = UNSET

    @property
    def errors(self) -> Union[List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType]:
        if isinstance(self._errors, Unset):
            raise NotPresentError(self, "errors")
        return self._errors

    @errors.setter
    def errors(self, value: Union[List[AsyncTaskErrorsItem], AsyncTaskErrors, UnknownType]) -> None:
        self._errors = value

    @errors.deleter
    def errors(self) -> None:
        self._errors = UNSET

    @property
    def message(self) -> str:
        """ Present only when status is FAILED. Contains information about the error. """
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = UNSET
