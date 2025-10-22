from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    worklist_id: str,
) -> Dict[str, Any]:
    url = "{}/worklists/{worklist_id}".format(client.base_url, worklist_id=worklist_id)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[None, NotFoundError]]:
    if response.status_code == 204:
        response_204 = None

        return response_204
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json(), strict=False)

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[None, NotFoundError]]:
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
) -> Response[Union[None, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
    )

    response = client.httpx_client.delete(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    worklist_id: str,
) -> Optional[Union[None, NotFoundError]]:
    """ Permanently deletes a worklist """

    return sync_detailed(
        client=client,
        worklist_id=worklist_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    worklist_id: str,
) -> Response[Union[None, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    worklist_id: str,
) -> Optional[Union[None, NotFoundError]]:
    """ Permanently deletes a worklist """

    return (
        await asyncio_detailed(
            client=client,
            worklist_id=worklist_id,
        )
    ).parsed
