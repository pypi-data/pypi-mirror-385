from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.oligo_upsert_request import OligoUpsertRequest
from ...models.rna_oligo import RnaOligo
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: OligoUpsertRequest,
) -> Dict[str, Any]:
    url = "{}/rna-oligos/{entity_registry_id}:upsert".format(
        client.base_url, entity_registry_id=entity_registry_id
    )

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[RnaOligo, RnaOligo, BadRequestError]]:
    if response.status_code == 200:
        response_200 = RnaOligo.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 201:
        response_201 = RnaOligo.from_dict(response.json(), strict=False)

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[RnaOligo, RnaOligo, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: OligoUpsertRequest,
) -> Response[Union[RnaOligo, RnaOligo, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entity_registry_id=entity_registry_id,
        json_body=json_body,
    )

    response = client.httpx_client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: OligoUpsertRequest,
) -> Optional[Union[RnaOligo, RnaOligo, BadRequestError]]:
    """Create or update a registered RNA oligo.

    Schema field links can be populated using entity registry IDs or API IDs. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the object `{\"entityRegistryId\": ENTITY_REGISTRY_ID}` may be provided instead of the API ID if desired (see example value).
    """

    return sync_detailed(
        client=client,
        entity_registry_id=entity_registry_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: OligoUpsertRequest,
) -> Response[Union[RnaOligo, RnaOligo, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entity_registry_id=entity_registry_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: OligoUpsertRequest,
) -> Optional[Union[RnaOligo, RnaOligo, BadRequestError]]:
    """Create or update a registered RNA oligo.

    Schema field links can be populated using entity registry IDs or API IDs. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the object `{\"entityRegistryId\": ENTITY_REGISTRY_ID}` may be provided instead of the API ID if desired (see example value).
    """

    return (
        await asyncio_detailed(
            client=client,
            entity_registry_id=entity_registry_id,
            json_body=json_body,
        )
    ).parsed
