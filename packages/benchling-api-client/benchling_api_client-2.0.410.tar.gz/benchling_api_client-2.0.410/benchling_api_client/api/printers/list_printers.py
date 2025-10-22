from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.not_found_error import NotFoundError
from ...models.printers_list import PrintersList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    registry_id: str,
    name: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/registries/{registry_id}/label-printers".format(client.base_url, registry_id=registry_id)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    params: Dict[str, Any] = {}
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[PrintersList, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = PrintersList.from_dict(response.json(), strict=False)

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
) -> Response[Union[PrintersList, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    registry_id: str,
    name: Union[Unset, str] = UNSET,
) -> Response[Union[PrintersList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        name=name,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    registry_id: str,
    name: Union[Unset, str] = UNSET,
) -> Optional[Union[PrintersList, BadRequestError, NotFoundError]]:
    """ List printers """

    return sync_detailed(
        client=client,
        registry_id=registry_id,
        name=name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    registry_id: str,
    name: Union[Unset, str] = UNSET,
) -> Response[Union[PrintersList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        name=name,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    registry_id: str,
    name: Union[Unset, str] = UNSET,
) -> Optional[Union[PrintersList, BadRequestError, NotFoundError]]:
    """ List printers """

    return (
        await asyncio_detailed(
            client=client,
            registry_id=registry_id,
            name=name,
        )
    ).parsed
