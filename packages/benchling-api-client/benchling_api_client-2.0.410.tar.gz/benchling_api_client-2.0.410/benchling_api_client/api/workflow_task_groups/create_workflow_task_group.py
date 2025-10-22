from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.workflow_task_group import WorkflowTaskGroup
from ...models.workflow_task_group_create import WorkflowTaskGroupCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: WorkflowTaskGroupCreate,
) -> Dict[str, Any]:
    url = "{}/workflow-task-groups".format(client.base_url)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[WorkflowTaskGroup, BadRequestError]]:
    if response.status_code == 201:
        response_201 = WorkflowTaskGroup.from_dict(response.json(), strict=False)

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[WorkflowTaskGroup, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: WorkflowTaskGroupCreate,
) -> Response[Union[WorkflowTaskGroup, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = client.httpx_client.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: WorkflowTaskGroupCreate,
) -> Optional[Union[WorkflowTaskGroup, BadRequestError]]:
    """ Create a new workflow task group. If no name is specified, uses the workflow schema name and a unique incrementor separated by a single whitespace. """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: WorkflowTaskGroupCreate,
) -> Response[Union[WorkflowTaskGroup, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: WorkflowTaskGroupCreate,
) -> Optional[Union[WorkflowTaskGroup, BadRequestError]]:
    """ Create a new workflow task group. If no name is specified, uses the workflow schema name and a unique incrementor separated by a single whitespace. """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
