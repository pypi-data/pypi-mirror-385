from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.containers_paginated_list import ContainersPaginatedList
from ...models.list_containers_checkout_status import ListContainersCheckoutStatus
from ...models.list_containers_sort import ListContainersSort
from ...models.sample_restriction_status import SampleRestrictionStatus
from ...models.schema_fields_query_param import SchemaFieldsQueryParam
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListContainersSort] = ListContainersSort.MODIFIEDAT,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    checkout_status: Union[Unset, ListContainersCheckoutStatus] = UNSET,
    checkout_assignee_idsany_of: Union[Unset, str] = UNSET,
    restriction_status: Union[Unset, SampleRestrictionStatus] = UNSET,
    sample_owner_idsall_of: Union[Unset, str] = UNSET,
    sample_owner_idsany_of: Union[Unset, str] = UNSET,
    sample_owner_idsnone_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsall_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsany_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsnone_of: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/containers".format(client.base_url)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    json_schema_fields: Union[Unset, Dict[str, Any]] = UNSET
    if not isinstance(schema_fields, Unset):
        json_schema_fields = schema_fields.to_dict()

    json_checkout_status: Union[Unset, int] = UNSET
    if not isinstance(checkout_status, Unset):
        json_checkout_status = checkout_status.value

    json_restriction_status: Union[Unset, int] = UNSET
    if not isinstance(restriction_status, Unset):
        json_restriction_status = restriction_status.value

    params: Dict[str, Any] = {}
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort
    if not isinstance(schema_id, Unset) and schema_id is not None:
        params["schemaId"] = schema_id
    if not isinstance(json_schema_fields, Unset) and json_schema_fields is not None:
        params.update(json_schema_fields)
    if not isinstance(created_at, Unset) and created_at is not None:
        params["createdAt"] = created_at
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(name_includes, Unset) and name_includes is not None:
        params["nameIncludes"] = name_includes
    if not isinstance(ancestor_storage_id, Unset) and ancestor_storage_id is not None:
        params["ancestorStorageId"] = ancestor_storage_id
    if not isinstance(storage_contents_id, Unset) and storage_contents_id is not None:
        params["storageContentsId"] = storage_contents_id
    if not isinstance(storage_contents_ids, Unset) and storage_contents_ids is not None:
        params["storageContentsIds"] = storage_contents_ids
    if not isinstance(archive_reason, Unset) and archive_reason is not None:
        params["archiveReason"] = archive_reason
    if not isinstance(json_checkout_status, Unset) and json_checkout_status is not None:
        params["checkoutStatus"] = json_checkout_status
    if not isinstance(checkout_assignee_idsany_of, Unset) and checkout_assignee_idsany_of is not None:
        params["checkoutAssigneeIds.anyOf"] = checkout_assignee_idsany_of
    if not isinstance(json_restriction_status, Unset) and json_restriction_status is not None:
        params["restrictionStatus"] = json_restriction_status
    if not isinstance(sample_owner_idsall_of, Unset) and sample_owner_idsall_of is not None:
        params["sampleOwnerIds.allOf"] = sample_owner_idsall_of
    if not isinstance(sample_owner_idsany_of, Unset) and sample_owner_idsany_of is not None:
        params["sampleOwnerIds.anyOf"] = sample_owner_idsany_of
    if not isinstance(sample_owner_idsnone_of, Unset) and sample_owner_idsnone_of is not None:
        params["sampleOwnerIds.noneOf"] = sample_owner_idsnone_of
    if (
        not isinstance(restricted_sample_party_idsall_of, Unset)
        and restricted_sample_party_idsall_of is not None
    ):
        params["restrictedSamplePartyIds.allOf"] = restricted_sample_party_idsall_of
    if (
        not isinstance(restricted_sample_party_idsany_of, Unset)
        and restricted_sample_party_idsany_of is not None
    ):
        params["restrictedSamplePartyIds.anyOf"] = restricted_sample_party_idsany_of
    if (
        not isinstance(restricted_sample_party_idsnone_of, Unset)
        and restricted_sample_party_idsnone_of is not None
    ):
        params["restrictedSamplePartyIds.noneOf"] = restricted_sample_party_idsnone_of
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(barcodes, Unset) and barcodes is not None:
        params["barcodes"] = barcodes
    if not isinstance(namesany_of, Unset) and namesany_of is not None:
        params["names.anyOf"] = namesany_of
    if not isinstance(namesany_ofcase_sensitive, Unset) and namesany_ofcase_sensitive is not None:
        params["names.anyOf.caseSensitive"] = namesany_ofcase_sensitive
    if not isinstance(creator_ids, Unset) and creator_ids is not None:
        params["creatorIds"] = creator_ids
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[ContainersPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = ContainersPaginatedList.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[ContainersPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListContainersSort] = ListContainersSort.MODIFIEDAT,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    checkout_status: Union[Unset, ListContainersCheckoutStatus] = UNSET,
    checkout_assignee_idsany_of: Union[Unset, str] = UNSET,
    restriction_status: Union[Unset, SampleRestrictionStatus] = UNSET,
    sample_owner_idsall_of: Union[Unset, str] = UNSET,
    sample_owner_idsany_of: Union[Unset, str] = UNSET,
    sample_owner_idsnone_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsall_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsany_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsnone_of: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[ContainersPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        schema_fields=schema_fields,
        created_at=created_at,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
        checkout_status=checkout_status,
        checkout_assignee_idsany_of=checkout_assignee_idsany_of,
        restriction_status=restriction_status,
        sample_owner_idsall_of=sample_owner_idsall_of,
        sample_owner_idsany_of=sample_owner_idsany_of,
        sample_owner_idsnone_of=sample_owner_idsnone_of,
        restricted_sample_party_idsall_of=restricted_sample_party_idsall_of,
        restricted_sample_party_idsany_of=restricted_sample_party_idsany_of,
        restricted_sample_party_idsnone_of=restricted_sample_party_idsnone_of,
        ids=ids,
        barcodes=barcodes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        creator_ids=creator_ids,
        returning=returning,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListContainersSort] = ListContainersSort.MODIFIEDAT,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    checkout_status: Union[Unset, ListContainersCheckoutStatus] = UNSET,
    checkout_assignee_idsany_of: Union[Unset, str] = UNSET,
    restriction_status: Union[Unset, SampleRestrictionStatus] = UNSET,
    sample_owner_idsall_of: Union[Unset, str] = UNSET,
    sample_owner_idsany_of: Union[Unset, str] = UNSET,
    sample_owner_idsnone_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsall_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsany_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsnone_of: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[ContainersPaginatedList, BadRequestError]]:
    """ List containers """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        schema_fields=schema_fields,
        created_at=created_at,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
        checkout_status=checkout_status,
        checkout_assignee_idsany_of=checkout_assignee_idsany_of,
        restriction_status=restriction_status,
        sample_owner_idsall_of=sample_owner_idsall_of,
        sample_owner_idsany_of=sample_owner_idsany_of,
        sample_owner_idsnone_of=sample_owner_idsnone_of,
        restricted_sample_party_idsall_of=restricted_sample_party_idsall_of,
        restricted_sample_party_idsany_of=restricted_sample_party_idsany_of,
        restricted_sample_party_idsnone_of=restricted_sample_party_idsnone_of,
        ids=ids,
        barcodes=barcodes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        creator_ids=creator_ids,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListContainersSort] = ListContainersSort.MODIFIEDAT,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    checkout_status: Union[Unset, ListContainersCheckoutStatus] = UNSET,
    checkout_assignee_idsany_of: Union[Unset, str] = UNSET,
    restriction_status: Union[Unset, SampleRestrictionStatus] = UNSET,
    sample_owner_idsall_of: Union[Unset, str] = UNSET,
    sample_owner_idsany_of: Union[Unset, str] = UNSET,
    sample_owner_idsnone_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsall_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsany_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsnone_of: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[ContainersPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        schema_fields=schema_fields,
        created_at=created_at,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
        checkout_status=checkout_status,
        checkout_assignee_idsany_of=checkout_assignee_idsany_of,
        restriction_status=restriction_status,
        sample_owner_idsall_of=sample_owner_idsall_of,
        sample_owner_idsany_of=sample_owner_idsany_of,
        sample_owner_idsnone_of=sample_owner_idsnone_of,
        restricted_sample_party_idsall_of=restricted_sample_party_idsall_of,
        restricted_sample_party_idsany_of=restricted_sample_party_idsany_of,
        restricted_sample_party_idsnone_of=restricted_sample_party_idsnone_of,
        ids=ids,
        barcodes=barcodes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        creator_ids=creator_ids,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListContainersSort] = ListContainersSort.MODIFIEDAT,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    checkout_status: Union[Unset, ListContainersCheckoutStatus] = UNSET,
    checkout_assignee_idsany_of: Union[Unset, str] = UNSET,
    restriction_status: Union[Unset, SampleRestrictionStatus] = UNSET,
    sample_owner_idsall_of: Union[Unset, str] = UNSET,
    sample_owner_idsany_of: Union[Unset, str] = UNSET,
    sample_owner_idsnone_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsall_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsany_of: Union[Unset, str] = UNSET,
    restricted_sample_party_idsnone_of: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[ContainersPaginatedList, BadRequestError]]:
    """ List containers """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            schema_id=schema_id,
            schema_fields=schema_fields,
            created_at=created_at,
            modified_at=modified_at,
            name=name,
            name_includes=name_includes,
            ancestor_storage_id=ancestor_storage_id,
            storage_contents_id=storage_contents_id,
            storage_contents_ids=storage_contents_ids,
            archive_reason=archive_reason,
            checkout_status=checkout_status,
            checkout_assignee_idsany_of=checkout_assignee_idsany_of,
            restriction_status=restriction_status,
            sample_owner_idsall_of=sample_owner_idsall_of,
            sample_owner_idsany_of=sample_owner_idsany_of,
            sample_owner_idsnone_of=sample_owner_idsnone_of,
            restricted_sample_party_idsall_of=restricted_sample_party_idsall_of,
            restricted_sample_party_idsany_of=restricted_sample_party_idsany_of,
            restricted_sample_party_idsnone_of=restricted_sample_party_idsnone_of,
            ids=ids,
            barcodes=barcodes,
            namesany_of=namesany_of,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            creator_ids=creator_ids,
            returning=returning,
        )
    ).parsed
