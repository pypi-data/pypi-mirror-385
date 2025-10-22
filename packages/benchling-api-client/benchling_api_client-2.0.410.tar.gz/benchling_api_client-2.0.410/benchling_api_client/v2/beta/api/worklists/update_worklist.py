from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.worklist import Worklist
from ...models.worklist_update import WorklistUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistUpdate,
) -> Dict[str, Any]:
    url = "{}/worklists/{worklist_id}".format(client.base_url, worklist_id=worklist_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[Worklist, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Worklist.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Worklist, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistUpdate,
) -> Response[Union[Worklist, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
        json_body=json_body,
    )

    response = client.httpx_client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistUpdate,
) -> Optional[Union[Worklist, BadRequestError]]:
    """ Update a worklist """

    return sync_detailed(
        client=client,
        worklist_id=worklist_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistUpdate,
) -> Response[Union[Worklist, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistUpdate,
) -> Optional[Union[Worklist, BadRequestError]]:
    """ Update a worklist """

    return (
        await asyncio_detailed(
            client=client,
            worklist_id=worklist_id,
            json_body=json_body,
        )
    ).parsed
