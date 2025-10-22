from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.benchling_app import BenchlingApp
from ...models.benchling_app_update import BenchlingAppUpdate
from ...models.forbidden_error import ForbiddenError
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    app_id: str,
    json_body: BenchlingAppUpdate,
) -> Dict[str, Any]:
    url = "{}/apps/{app_id}".format(client.base_url, app_id=app_id)

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
) -> Optional[Union[BenchlingApp, BadRequestError, ForbiddenError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = BenchlingApp.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json(), strict=False)

        return response_403
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json(), strict=False)

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[BenchlingApp, BadRequestError, ForbiddenError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    app_id: str,
    json_body: BenchlingAppUpdate,
) -> Response[Union[BenchlingApp, BadRequestError, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
        json_body=json_body,
    )

    response = client.httpx_client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    app_id: str,
    json_body: BenchlingAppUpdate,
) -> Optional[Union[BenchlingApp, BadRequestError, ForbiddenError, NotFoundError]]:
    """ Update an app """

    return sync_detailed(
        client=client,
        app_id=app_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    app_id: str,
    json_body: BenchlingAppUpdate,
) -> Response[Union[BenchlingApp, BadRequestError, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    app_id: str,
    json_body: BenchlingAppUpdate,
) -> Optional[Union[BenchlingApp, BadRequestError, ForbiddenError, NotFoundError]]:
    """ Update an app """

    return (
        await asyncio_detailed(
            client=client,
            app_id=app_id,
            json_body=json_body,
        )
    ).parsed
