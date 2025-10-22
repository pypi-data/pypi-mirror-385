from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.list_plates_sort import ListPlatesSort
from ...models.plates_paginated_list import PlatesPaginatedList
from ...models.schema_fields_query_param import SchemaFieldsQueryParam
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListPlatesSort] = ListPlatesSort.MODIFIEDATDESC,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    empty_positions: Union[Unset, int] = UNSET,
    empty_positionsgte: Union[Unset, int] = UNSET,
    empty_positionsgt: Union[Unset, int] = UNSET,
    empty_positionslte: Union[Unset, int] = UNSET,
    empty_positionslt: Union[Unset, int] = UNSET,
    empty_containers: Union[Unset, int] = UNSET,
    empty_containersgte: Union[Unset, int] = UNSET,
    empty_containersgt: Union[Unset, int] = UNSET,
    empty_containerslte: Union[Unset, int] = UNSET,
    empty_containerslt: Union[Unset, int] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/plates".format(client.base_url)

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
    if not isinstance(empty_positions, Unset) and empty_positions is not None:
        params["emptyPositions"] = empty_positions
    if not isinstance(empty_positionsgte, Unset) and empty_positionsgte is not None:
        params["emptyPositions.gte"] = empty_positionsgte
    if not isinstance(empty_positionsgt, Unset) and empty_positionsgt is not None:
        params["emptyPositions.gt"] = empty_positionsgt
    if not isinstance(empty_positionslte, Unset) and empty_positionslte is not None:
        params["emptyPositions.lte"] = empty_positionslte
    if not isinstance(empty_positionslt, Unset) and empty_positionslt is not None:
        params["emptyPositions.lt"] = empty_positionslt
    if not isinstance(empty_containers, Unset) and empty_containers is not None:
        params["emptyContainers"] = empty_containers
    if not isinstance(empty_containersgte, Unset) and empty_containersgte is not None:
        params["emptyContainers.gte"] = empty_containersgte
    if not isinstance(empty_containersgt, Unset) and empty_containersgt is not None:
        params["emptyContainers.gt"] = empty_containersgt
    if not isinstance(empty_containerslte, Unset) and empty_containerslte is not None:
        params["emptyContainers.lte"] = empty_containerslte
    if not isinstance(empty_containerslt, Unset) and empty_containerslt is not None:
        params["emptyContainers.lt"] = empty_containerslt
    if not isinstance(ancestor_storage_id, Unset) and ancestor_storage_id is not None:
        params["ancestorStorageId"] = ancestor_storage_id
    if not isinstance(storage_contents_id, Unset) and storage_contents_id is not None:
        params["storageContentsId"] = storage_contents_id
    if not isinstance(storage_contents_ids, Unset) and storage_contents_ids is not None:
        params["storageContentsIds"] = storage_contents_ids
    if not isinstance(archive_reason, Unset) and archive_reason is not None:
        params["archiveReason"] = archive_reason
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(barcodes, Unset) and barcodes is not None:
        params["barcodes"] = barcodes
    if not isinstance(namesany_of, Unset) and namesany_of is not None:
        params["names.anyOf"] = namesany_of
    if not isinstance(namesany_ofcase_sensitive, Unset) and namesany_ofcase_sensitive is not None:
        params["names.anyOf.caseSensitive"] = namesany_ofcase_sensitive
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning
    if not isinstance(creator_ids, Unset) and creator_ids is not None:
        params["creatorIds"] = creator_ids

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[PlatesPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = PlatesPaginatedList.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[PlatesPaginatedList, BadRequestError]]:
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
    sort: Union[Unset, ListPlatesSort] = ListPlatesSort.MODIFIEDATDESC,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    empty_positions: Union[Unset, int] = UNSET,
    empty_positionsgte: Union[Unset, int] = UNSET,
    empty_positionsgt: Union[Unset, int] = UNSET,
    empty_positionslte: Union[Unset, int] = UNSET,
    empty_positionslt: Union[Unset, int] = UNSET,
    empty_containers: Union[Unset, int] = UNSET,
    empty_containersgte: Union[Unset, int] = UNSET,
    empty_containersgt: Union[Unset, int] = UNSET,
    empty_containerslte: Union[Unset, int] = UNSET,
    empty_containerslt: Union[Unset, int] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Response[Union[PlatesPaginatedList, BadRequestError]]:
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
        empty_positions=empty_positions,
        empty_positionsgte=empty_positionsgte,
        empty_positionsgt=empty_positionsgt,
        empty_positionslte=empty_positionslte,
        empty_positionslt=empty_positionslt,
        empty_containers=empty_containers,
        empty_containersgte=empty_containersgte,
        empty_containersgt=empty_containersgt,
        empty_containerslte=empty_containerslte,
        empty_containerslt=empty_containerslt,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
        ids=ids,
        barcodes=barcodes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        returning=returning,
        creator_ids=creator_ids,
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
    sort: Union[Unset, ListPlatesSort] = ListPlatesSort.MODIFIEDATDESC,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    empty_positions: Union[Unset, int] = UNSET,
    empty_positionsgte: Union[Unset, int] = UNSET,
    empty_positionsgt: Union[Unset, int] = UNSET,
    empty_positionslte: Union[Unset, int] = UNSET,
    empty_positionslt: Union[Unset, int] = UNSET,
    empty_containers: Union[Unset, int] = UNSET,
    empty_containersgte: Union[Unset, int] = UNSET,
    empty_containersgt: Union[Unset, int] = UNSET,
    empty_containerslte: Union[Unset, int] = UNSET,
    empty_containerslt: Union[Unset, int] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[PlatesPaginatedList, BadRequestError]]:
    """ List plates """

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
        empty_positions=empty_positions,
        empty_positionsgte=empty_positionsgte,
        empty_positionsgt=empty_positionsgt,
        empty_positionslte=empty_positionslte,
        empty_positionslt=empty_positionslt,
        empty_containers=empty_containers,
        empty_containersgte=empty_containersgte,
        empty_containersgt=empty_containersgt,
        empty_containerslte=empty_containerslte,
        empty_containerslt=empty_containerslt,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
        ids=ids,
        barcodes=barcodes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        returning=returning,
        creator_ids=creator_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListPlatesSort] = ListPlatesSort.MODIFIEDATDESC,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    empty_positions: Union[Unset, int] = UNSET,
    empty_positionsgte: Union[Unset, int] = UNSET,
    empty_positionsgt: Union[Unset, int] = UNSET,
    empty_positionslte: Union[Unset, int] = UNSET,
    empty_positionslt: Union[Unset, int] = UNSET,
    empty_containers: Union[Unset, int] = UNSET,
    empty_containersgte: Union[Unset, int] = UNSET,
    empty_containersgt: Union[Unset, int] = UNSET,
    empty_containerslte: Union[Unset, int] = UNSET,
    empty_containerslt: Union[Unset, int] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Response[Union[PlatesPaginatedList, BadRequestError]]:
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
        empty_positions=empty_positions,
        empty_positionsgte=empty_positionsgte,
        empty_positionsgt=empty_positionsgt,
        empty_positionslte=empty_positionslte,
        empty_positionslt=empty_positionslt,
        empty_containers=empty_containers,
        empty_containersgte=empty_containersgte,
        empty_containersgt=empty_containersgt,
        empty_containerslte=empty_containerslte,
        empty_containerslt=empty_containerslt,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
        ids=ids,
        barcodes=barcodes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        returning=returning,
        creator_ids=creator_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListPlatesSort] = ListPlatesSort.MODIFIEDATDESC,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    empty_positions: Union[Unset, int] = UNSET,
    empty_positionsgte: Union[Unset, int] = UNSET,
    empty_positionsgt: Union[Unset, int] = UNSET,
    empty_positionslte: Union[Unset, int] = UNSET,
    empty_positionslt: Union[Unset, int] = UNSET,
    empty_containers: Union[Unset, int] = UNSET,
    empty_containersgte: Union[Unset, int] = UNSET,
    empty_containersgt: Union[Unset, int] = UNSET,
    empty_containerslte: Union[Unset, int] = UNSET,
    empty_containerslt: Union[Unset, int] = UNSET,
    ancestor_storage_id: Union[Unset, str] = UNSET,
    storage_contents_id: Union[Unset, str] = UNSET,
    storage_contents_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[PlatesPaginatedList, BadRequestError]]:
    """ List plates """

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
            empty_positions=empty_positions,
            empty_positionsgte=empty_positionsgte,
            empty_positionsgt=empty_positionsgt,
            empty_positionslte=empty_positionslte,
            empty_positionslt=empty_positionslt,
            empty_containers=empty_containers,
            empty_containersgte=empty_containersgte,
            empty_containersgt=empty_containersgt,
            empty_containerslte=empty_containerslte,
            empty_containerslt=empty_containerslt,
            ancestor_storage_id=ancestor_storage_id,
            storage_contents_id=storage_contents_id,
            storage_contents_ids=storage_contents_ids,
            archive_reason=archive_reason,
            ids=ids,
            barcodes=barcodes,
            namesany_of=namesany_of,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            returning=returning,
            creator_ids=creator_ids,
        )
    ).parsed
