from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.app_session import AppSession
from ...models.app_session_create import AppSessionCreate
from ...models.bad_request_error import BadRequestError
from ...models.forbidden_error import ForbiddenError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: AppSessionCreate,
) -> Dict[str, Any]:
    url = "{}/app-sessions".format(client.base_url)

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


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[AppSession, BadRequestError, ForbiddenError]]:
    if response.status_code == 201:
        response_201 = AppSession.from_dict(response.json(), strict=False)

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json(), strict=False)

        return response_403
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[AppSession, BadRequestError, ForbiddenError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: AppSessionCreate,
) -> Response[Union[AppSession, BadRequestError, ForbiddenError]]:
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
    json_body: AppSessionCreate,
) -> Optional[Union[AppSession, BadRequestError, ForbiddenError]]:
    """Create a new app session. Sessions cannot be archived once created."""

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: AppSessionCreate,
) -> Response[Union[AppSession, BadRequestError, ForbiddenError]]:
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
    json_body: AppSessionCreate,
) -> Optional[Union[AppSession, BadRequestError, ForbiddenError]]:
    """Create a new app session. Sessions cannot be archived once created."""

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
