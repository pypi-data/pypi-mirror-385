import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.fields import Fields
from ..models.request_sample_group_create import RequestSampleGroupCreate
from ..models.request_status import RequestStatus
from ..models.request_write_team_assignee import RequestWriteTeamAssignee
from ..models.request_write_user_assignee import RequestWriteUserAssignee
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestUpdate")


@attr.s(auto_attribs=True, repr=False)
class RequestUpdate:
    """  """

    _request_status: Union[Unset, RequestStatus] = UNSET
    _assignees: Union[
        Unset, List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]]
    ] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _requestor_id: Union[Unset, None, str] = UNSET
    _sample_groups: Union[Unset, List[RequestSampleGroupCreate]] = UNSET
    _scheduled_on: Union[Unset, datetime.date] = UNSET

    def __repr__(self):
        fields = []
        fields.append("request_status={}".format(repr(self._request_status)))
        fields.append("assignees={}".format(repr(self._assignees)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("requestor_id={}".format(repr(self._requestor_id)))
        fields.append("sample_groups={}".format(repr(self._sample_groups)))
        fields.append("scheduled_on={}".format(repr(self._scheduled_on)))
        return "RequestUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        request_status: Union[Unset, int] = UNSET
        if not isinstance(self._request_status, Unset):
            request_status = self._request_status.value

        assignees: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assignees, Unset):
            assignees = []
            for assignees_item_data in self._assignees:
                if isinstance(assignees_item_data, UnknownType):
                    assignees_item = assignees_item_data.value
                elif isinstance(assignees_item_data, RequestWriteUserAssignee):
                    assignees_item = assignees_item_data.to_dict()

                else:
                    assignees_item = assignees_item_data.to_dict()

                assignees.append(assignees_item)

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        project_id = self._project_id
        requestor_id = self._requestor_id
        sample_groups: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._sample_groups, Unset):
            sample_groups = []
            for sample_groups_item_data in self._sample_groups:
                sample_groups_item = sample_groups_item_data.to_dict()

                sample_groups.append(sample_groups_item)

        scheduled_on: Union[Unset, str] = UNSET
        if not isinstance(self._scheduled_on, Unset):
            scheduled_on = self._scheduled_on.isoformat()

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if request_status is not UNSET:
            field_dict["requestStatus"] = request_status
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if fields is not UNSET:
            field_dict["fields"] = fields
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if requestor_id is not UNSET:
            field_dict["requestorId"] = requestor_id
        if sample_groups is not UNSET:
            field_dict["sampleGroups"] = sample_groups
        if scheduled_on is not UNSET:
            field_dict["scheduledOn"] = scheduled_on

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_request_status() -> Union[Unset, RequestStatus]:
            request_status = UNSET
            _request_status = d.pop("requestStatus")
            if _request_status is not None and _request_status is not UNSET:
                try:
                    request_status = RequestStatus(_request_status)
                except ValueError:
                    request_status = RequestStatus.of_unknown(_request_status)

            return request_status

        try:
            request_status = get_request_status()
        except KeyError:
            if strict:
                raise
            request_status = cast(Union[Unset, RequestStatus], UNSET)

        def get_assignees() -> Union[
            Unset, List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]]
        ]:
            assignees = []
            _assignees = d.pop("assignees")
            for assignees_item_data in _assignees or []:

                def _parse_assignees_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]:
                    assignees_item: Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        assignees_item = RequestWriteUserAssignee.from_dict(data, strict=True)

                        return assignees_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        assignees_item = RequestWriteTeamAssignee.from_dict(data, strict=True)

                        return assignees_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                assignees_item = _parse_assignees_item(assignees_item_data)

                assignees.append(assignees_item)

            return assignees

        try:
            assignees = get_assignees()
        except KeyError:
            if strict:
                raise
            assignees = cast(
                Union[Unset, List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]]],
                UNSET,
            )

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

        def get_project_id() -> Union[Unset, str]:
            project_id = d.pop("projectId")
            return project_id

        try:
            project_id = get_project_id()
        except KeyError:
            if strict:
                raise
            project_id = cast(Union[Unset, str], UNSET)

        def get_requestor_id() -> Union[Unset, None, str]:
            requestor_id = d.pop("requestorId")
            return requestor_id

        try:
            requestor_id = get_requestor_id()
        except KeyError:
            if strict:
                raise
            requestor_id = cast(Union[Unset, None, str], UNSET)

        def get_sample_groups() -> Union[Unset, List[RequestSampleGroupCreate]]:
            sample_groups = []
            _sample_groups = d.pop("sampleGroups")
            for sample_groups_item_data in _sample_groups or []:
                sample_groups_item = RequestSampleGroupCreate.from_dict(sample_groups_item_data, strict=False)

                sample_groups.append(sample_groups_item)

            return sample_groups

        try:
            sample_groups = get_sample_groups()
        except KeyError:
            if strict:
                raise
            sample_groups = cast(Union[Unset, List[RequestSampleGroupCreate]], UNSET)

        def get_scheduled_on() -> Union[Unset, datetime.date]:
            scheduled_on: Union[Unset, datetime.date] = UNSET
            _scheduled_on = d.pop("scheduledOn")
            if _scheduled_on is not None and not isinstance(_scheduled_on, Unset):
                scheduled_on = isoparse(cast(str, _scheduled_on)).date()

            return scheduled_on

        try:
            scheduled_on = get_scheduled_on()
        except KeyError:
            if strict:
                raise
            scheduled_on = cast(Union[Unset, datetime.date], UNSET)

        request_update = cls(
            request_status=request_status,
            assignees=assignees,
            fields=fields,
            project_id=project_id,
            requestor_id=requestor_id,
            sample_groups=sample_groups,
            scheduled_on=scheduled_on,
        )

        return request_update

    @property
    def request_status(self) -> RequestStatus:
        if isinstance(self._request_status, Unset):
            raise NotPresentError(self, "request_status")
        return self._request_status

    @request_status.setter
    def request_status(self, value: RequestStatus) -> None:
        self._request_status = value

    @request_status.deleter
    def request_status(self) -> None:
        self._request_status = UNSET

    @property
    def assignees(self) -> List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]]:
        """ Array of assignees """
        if isinstance(self._assignees, Unset):
            raise NotPresentError(self, "assignees")
        return self._assignees

    @assignees.setter
    def assignees(
        self, value: List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee, UnknownType]]
    ) -> None:
        self._assignees = value

    @assignees.deleter
    def assignees(self) -> None:
        self._assignees = UNSET

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
    def project_id(self) -> str:
        """ The ID of the project to which the Legacy Request belongs. """
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: str) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET

    @property
    def requestor_id(self) -> Optional[str]:
        """ID of the user making the Legacy Request. If unspecified, the requestor is the request creator."""
        if isinstance(self._requestor_id, Unset):
            raise NotPresentError(self, "requestor_id")
        return self._requestor_id

    @requestor_id.setter
    def requestor_id(self, value: Optional[str]) -> None:
        self._requestor_id = value

    @requestor_id.deleter
    def requestor_id(self) -> None:
        self._requestor_id = UNSET

    @property
    def sample_groups(self) -> List[RequestSampleGroupCreate]:
        if isinstance(self._sample_groups, Unset):
            raise NotPresentError(self, "sample_groups")
        return self._sample_groups

    @sample_groups.setter
    def sample_groups(self, value: List[RequestSampleGroupCreate]) -> None:
        self._sample_groups = value

    @sample_groups.deleter
    def sample_groups(self) -> None:
        self._sample_groups = UNSET

    @property
    def scheduled_on(self) -> datetime.date:
        """ Date the Legacy Request is scheduled to be executed on, in YYYY-MM-DD format. """
        if isinstance(self._scheduled_on, Unset):
            raise NotPresentError(self, "scheduled_on")
        return self._scheduled_on

    @scheduled_on.setter
    def scheduled_on(self, value: datetime.date) -> None:
        self._scheduled_on = value

    @scheduled_on.deleter
    def scheduled_on(self) -> None:
        self._scheduled_on = UNSET
