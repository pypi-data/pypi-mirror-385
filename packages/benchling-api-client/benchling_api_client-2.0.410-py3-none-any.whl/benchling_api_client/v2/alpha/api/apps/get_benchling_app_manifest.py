from typing import Any, Dict, Optional, Union

import httpx
import yaml

from ...client import Client
from ...models.benchling_app_manifest_alpha import BenchlingAppManifestAlpha
from ...models.forbidden_error import ForbiddenError
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    app_id: str,
) -> Dict[str, Any]:
    url = "{}/apps/{app_id}/manifest.yaml".format(client.base_url, app_id=app_id)

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


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[BenchlingAppManifestAlpha, ForbiddenError, NotFoundError]]:
    if response.status_code == 200:
        yaml_dict = yaml.safe_load(response.text.encode("utf-8"))
        response_200 = BenchlingAppManifestAlpha.from_dict(yaml_dict)

        return response_200
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json(), strict=False)

        return response_403
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json(), strict=False)

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[BenchlingAppManifestAlpha, ForbiddenError, NotFoundError]]:
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
) -> Response[Union[BenchlingAppManifestAlpha, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    app_id: str,
) -> Optional[Union[BenchlingAppManifestAlpha, ForbiddenError, NotFoundError]]:
    """ Get app manifest """

    return sync_detailed(
        client=client,
        app_id=app_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    app_id: str,
) -> Response[Union[BenchlingAppManifestAlpha, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    app_id: str,
) -> Optional[Union[BenchlingAppManifestAlpha, ForbiddenError, NotFoundError]]:
    """ Get app manifest """

    return (
        await asyncio_detailed(
            client=client,
            app_id=app_id,
        )
    ).parsed
