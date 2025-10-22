from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.collaborations_paginated_list import CollaborationsPaginatedList
from ...models.list_folder_collaborations_role import ListFolderCollaborationsRole
from ...models.list_folder_collaborations_sort import ListFolderCollaborationsSort
from ...models.not_found_error import NotFoundError
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    folder_id: str,
    user_id: Union[Unset, str] = UNSET,
    app_id: Union[Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
    organization_id: Union[Unset, str] = UNSET,
    role: Union[Unset, ListFolderCollaborationsRole] = UNSET,
    ids: Union[Unset, str] = UNSET,
    created_atlt: Union[Unset, str] = UNSET,
    created_atgt: Union[Unset, str] = UNSET,
    modified_atlt: Union[Unset, str] = UNSET,
    modified_atgt: Union[Unset, str] = UNSET,
    modified_atlte: Union[Unset, str] = UNSET,
    modified_atgte: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListFolderCollaborationsSort] = ListFolderCollaborationsSort.MODIFIEDAT,
) -> Dict[str, Any]:
    url = "{}/folders/{folderId}/collaborations".format(client.base_url, folderId=folder_id)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_role: Union[Unset, int] = UNSET
    if not isinstance(role, Unset):
        json_role = role.value

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params: Dict[str, Any] = {}
    if not isinstance(user_id, Unset) and user_id is not None:
        params["userId"] = user_id
    if not isinstance(app_id, Unset) and app_id is not None:
        params["appId"] = app_id
    if not isinstance(team_id, Unset) and team_id is not None:
        params["teamId"] = team_id
    if not isinstance(organization_id, Unset) and organization_id is not None:
        params["organizationId"] = organization_id
    if not isinstance(json_role, Unset) and json_role is not None:
        params["role"] = json_role
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(created_atlt, Unset) and created_atlt is not None:
        params["createdAt.lt"] = created_atlt
    if not isinstance(created_atgt, Unset) and created_atgt is not None:
        params["createdAt.gt"] = created_atgt
    if not isinstance(modified_atlt, Unset) and modified_atlt is not None:
        params["modifiedAt.lt"] = modified_atlt
    if not isinstance(modified_atgt, Unset) and modified_atgt is not None:
        params["modifiedAt.gt"] = modified_atgt
    if not isinstance(modified_atlte, Unset) and modified_atlte is not None:
        params["modifiedAt.lte"] = modified_atlte
    if not isinstance(modified_atgte, Unset) and modified_atgte is not None:
        params["modifiedAt.gte"] = modified_atgte
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = CollaborationsPaginatedList.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json(), strict=False)

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    folder_id: str,
    user_id: Union[Unset, str] = UNSET,
    app_id: Union[Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
    organization_id: Union[Unset, str] = UNSET,
    role: Union[Unset, ListFolderCollaborationsRole] = UNSET,
    ids: Union[Unset, str] = UNSET,
    created_atlt: Union[Unset, str] = UNSET,
    created_atgt: Union[Unset, str] = UNSET,
    modified_atlt: Union[Unset, str] = UNSET,
    modified_atgt: Union[Unset, str] = UNSET,
    modified_atlte: Union[Unset, str] = UNSET,
    modified_atgte: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListFolderCollaborationsSort] = ListFolderCollaborationsSort.MODIFIEDAT,
) -> Response[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        folder_id=folder_id,
        user_id=user_id,
        app_id=app_id,
        team_id=team_id,
        organization_id=organization_id,
        role=role,
        ids=ids,
        created_atlt=created_atlt,
        created_atgt=created_atgt,
        modified_atlt=modified_atlt,
        modified_atgt=modified_atgt,
        modified_atlte=modified_atlte,
        modified_atgte=modified_atgte,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    folder_id: str,
    user_id: Union[Unset, str] = UNSET,
    app_id: Union[Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
    organization_id: Union[Unset, str] = UNSET,
    role: Union[Unset, ListFolderCollaborationsRole] = UNSET,
    ids: Union[Unset, str] = UNSET,
    created_atlt: Union[Unset, str] = UNSET,
    created_atgt: Union[Unset, str] = UNSET,
    modified_atlt: Union[Unset, str] = UNSET,
    modified_atgt: Union[Unset, str] = UNSET,
    modified_atlte: Union[Unset, str] = UNSET,
    modified_atgte: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListFolderCollaborationsSort] = ListFolderCollaborationsSort.MODIFIEDAT,
) -> Optional[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    """Returns information about collaborations on the specified Folders."""

    return sync_detailed(
        client=client,
        folder_id=folder_id,
        user_id=user_id,
        app_id=app_id,
        team_id=team_id,
        organization_id=organization_id,
        role=role,
        ids=ids,
        created_atlt=created_atlt,
        created_atgt=created_atgt,
        modified_atlt=modified_atlt,
        modified_atgt=modified_atgt,
        modified_atlte=modified_atlte,
        modified_atgte=modified_atgte,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    folder_id: str,
    user_id: Union[Unset, str] = UNSET,
    app_id: Union[Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
    organization_id: Union[Unset, str] = UNSET,
    role: Union[Unset, ListFolderCollaborationsRole] = UNSET,
    ids: Union[Unset, str] = UNSET,
    created_atlt: Union[Unset, str] = UNSET,
    created_atgt: Union[Unset, str] = UNSET,
    modified_atlt: Union[Unset, str] = UNSET,
    modified_atgt: Union[Unset, str] = UNSET,
    modified_atlte: Union[Unset, str] = UNSET,
    modified_atgte: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListFolderCollaborationsSort] = ListFolderCollaborationsSort.MODIFIEDAT,
) -> Response[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        folder_id=folder_id,
        user_id=user_id,
        app_id=app_id,
        team_id=team_id,
        organization_id=organization_id,
        role=role,
        ids=ids,
        created_atlt=created_atlt,
        created_atgt=created_atgt,
        modified_atlt=modified_atlt,
        modified_atgt=modified_atgt,
        modified_atlte=modified_atlte,
        modified_atgte=modified_atgte,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    folder_id: str,
    user_id: Union[Unset, str] = UNSET,
    app_id: Union[Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
    organization_id: Union[Unset, str] = UNSET,
    role: Union[Unset, ListFolderCollaborationsRole] = UNSET,
    ids: Union[Unset, str] = UNSET,
    created_atlt: Union[Unset, str] = UNSET,
    created_atgt: Union[Unset, str] = UNSET,
    modified_atlt: Union[Unset, str] = UNSET,
    modified_atgt: Union[Unset, str] = UNSET,
    modified_atlte: Union[Unset, str] = UNSET,
    modified_atgte: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListFolderCollaborationsSort] = ListFolderCollaborationsSort.MODIFIEDAT,
) -> Optional[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    """Returns information about collaborations on the specified Folders."""

    return (
        await asyncio_detailed(
            client=client,
            folder_id=folder_id,
            user_id=user_id,
            app_id=app_id,
            team_id=team_id,
            organization_id=organization_id,
            role=role,
            ids=ids,
            created_atlt=created_atlt,
            created_atgt=created_atgt,
            modified_atlt=modified_atlt,
            modified_atgt=modified_atgt,
            modified_atlte=modified_atlte,
            modified_atgte=modified_atgte,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
        )
    ).parsed
