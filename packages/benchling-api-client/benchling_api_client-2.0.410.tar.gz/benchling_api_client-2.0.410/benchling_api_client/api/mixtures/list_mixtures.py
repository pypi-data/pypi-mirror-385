from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.list_mixtures_sort import ListMixturesSort
from ...models.mixtures_paginated_list import MixturesPaginatedList
from ...models.schema_fields_query_param import SchemaFieldsQueryParam
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListMixturesSort] = ListMixturesSort.MODIFIEDATDESC,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, None, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    entity_registry_idsany_of: Union[Unset, str] = UNSET,
    ingredient_component_entity_ids: Union[Unset, str] = UNSET,
    ingredient_component_entity_idsany_of: Union[Unset, str] = UNSET,
    author_idsany_of: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/mixtures".format(client.base_url)

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
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort
    if not isinstance(created_at, Unset) and created_at is not None:
        params["createdAt"] = created_at
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(name_includes, Unset) and name_includes is not None:
        params["nameIncludes"] = name_includes
    if not isinstance(folder_id, Unset) and folder_id is not None:
        params["folderId"] = folder_id
    if not isinstance(mentioned_in, Unset) and mentioned_in is not None:
        params["mentionedIn"] = mentioned_in
    if not isinstance(project_id, Unset) and project_id is not None:
        params["projectId"] = project_id
    if not isinstance(registry_id, Unset) and registry_id is not None:
        params["registryId"] = registry_id
    if not isinstance(schema_id, Unset) and schema_id is not None:
        params["schemaId"] = schema_id
    if not isinstance(json_schema_fields, Unset) and json_schema_fields is not None:
        params.update(json_schema_fields)
    if not isinstance(archive_reason, Unset) and archive_reason is not None:
        params["archiveReason"] = archive_reason
    if not isinstance(mentions, Unset) and mentions is not None:
        params["mentions"] = mentions
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(namesany_of, Unset) and namesany_of is not None:
        params["names.anyOf"] = namesany_of
    if not isinstance(namesany_ofcase_sensitive, Unset) and namesany_ofcase_sensitive is not None:
        params["names.anyOf.caseSensitive"] = namesany_ofcase_sensitive
    if not isinstance(entity_registry_idsany_of, Unset) and entity_registry_idsany_of is not None:
        params["entityRegistryIds.anyOf"] = entity_registry_idsany_of
    if not isinstance(ingredient_component_entity_ids, Unset) and ingredient_component_entity_ids is not None:
        params["ingredientComponentEntityIds"] = ingredient_component_entity_ids
    if (
        not isinstance(ingredient_component_entity_idsany_of, Unset)
        and ingredient_component_entity_idsany_of is not None
    ):
        params["ingredientComponentEntityIds.anyOf"] = ingredient_component_entity_idsany_of
    if not isinstance(author_idsany_of, Unset) and author_idsany_of is not None:
        params["authorIds.anyOf"] = author_idsany_of

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[MixturesPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = MixturesPaginatedList.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[MixturesPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListMixturesSort] = ListMixturesSort.MODIFIEDATDESC,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, None, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    entity_registry_idsany_of: Union[Unset, str] = UNSET,
    ingredient_component_entity_ids: Union[Unset, str] = UNSET,
    ingredient_component_entity_idsany_of: Union[Unset, str] = UNSET,
    author_idsany_of: Union[Unset, str] = UNSET,
) -> Response[Union[MixturesPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        created_at=created_at,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        project_id=project_id,
        registry_id=registry_id,
        schema_id=schema_id,
        schema_fields=schema_fields,
        archive_reason=archive_reason,
        mentions=mentions,
        ids=ids,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        entity_registry_idsany_of=entity_registry_idsany_of,
        ingredient_component_entity_ids=ingredient_component_entity_ids,
        ingredient_component_entity_idsany_of=ingredient_component_entity_idsany_of,
        author_idsany_of=author_idsany_of,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListMixturesSort] = ListMixturesSort.MODIFIEDATDESC,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, None, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    entity_registry_idsany_of: Union[Unset, str] = UNSET,
    ingredient_component_entity_ids: Union[Unset, str] = UNSET,
    ingredient_component_entity_idsany_of: Union[Unset, str] = UNSET,
    author_idsany_of: Union[Unset, str] = UNSET,
) -> Optional[Union[MixturesPaginatedList, BadRequestError]]:
    """ List mixtures """

    return sync_detailed(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        created_at=created_at,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        project_id=project_id,
        registry_id=registry_id,
        schema_id=schema_id,
        schema_fields=schema_fields,
        archive_reason=archive_reason,
        mentions=mentions,
        ids=ids,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        entity_registry_idsany_of=entity_registry_idsany_of,
        ingredient_component_entity_ids=ingredient_component_entity_ids,
        ingredient_component_entity_idsany_of=ingredient_component_entity_idsany_of,
        author_idsany_of=author_idsany_of,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListMixturesSort] = ListMixturesSort.MODIFIEDATDESC,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, None, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    entity_registry_idsany_of: Union[Unset, str] = UNSET,
    ingredient_component_entity_ids: Union[Unset, str] = UNSET,
    ingredient_component_entity_idsany_of: Union[Unset, str] = UNSET,
    author_idsany_of: Union[Unset, str] = UNSET,
) -> Response[Union[MixturesPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        created_at=created_at,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        project_id=project_id,
        registry_id=registry_id,
        schema_id=schema_id,
        schema_fields=schema_fields,
        archive_reason=archive_reason,
        mentions=mentions,
        ids=ids,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        entity_registry_idsany_of=entity_registry_idsany_of,
        ingredient_component_entity_ids=ingredient_component_entity_ids,
        ingredient_component_entity_idsany_of=ingredient_component_entity_idsany_of,
        author_idsany_of=author_idsany_of,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListMixturesSort] = ListMixturesSort.MODIFIEDATDESC,
    created_at: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, None, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    entity_registry_idsany_of: Union[Unset, str] = UNSET,
    ingredient_component_entity_ids: Union[Unset, str] = UNSET,
    ingredient_component_entity_idsany_of: Union[Unset, str] = UNSET,
    author_idsany_of: Union[Unset, str] = UNSET,
) -> Optional[Union[MixturesPaginatedList, BadRequestError]]:
    """ List mixtures """

    return (
        await asyncio_detailed(
            client=client,
            next_token=next_token,
            page_size=page_size,
            sort=sort,
            created_at=created_at,
            modified_at=modified_at,
            name=name,
            name_includes=name_includes,
            folder_id=folder_id,
            mentioned_in=mentioned_in,
            project_id=project_id,
            registry_id=registry_id,
            schema_id=schema_id,
            schema_fields=schema_fields,
            archive_reason=archive_reason,
            mentions=mentions,
            ids=ids,
            namesany_of=namesany_of,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            entity_registry_idsany_of=entity_registry_idsany_of,
            ingredient_component_entity_ids=ingredient_component_entity_ids,
            ingredient_component_entity_idsany_of=ingredient_component_entity_idsany_of,
            author_idsany_of=author_idsany_of,
        )
    ).parsed
