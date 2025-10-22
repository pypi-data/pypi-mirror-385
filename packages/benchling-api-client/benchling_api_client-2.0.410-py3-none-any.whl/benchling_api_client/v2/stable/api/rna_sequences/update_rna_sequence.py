from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.rna_sequence import RnaSequence
from ...models.rna_sequence_update import RnaSequenceUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    rna_sequence_id: str,
    json_body: RnaSequenceUpdate,
) -> Dict[str, Any]:
    url = "{}/rna-sequences/{rna_sequence_id}".format(client.base_url, rna_sequence_id=rna_sequence_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[RnaSequence, BadRequestError]]:
    if response.status_code == 200:
        response_200 = RnaSequence.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[RnaSequence, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    rna_sequence_id: str,
    json_body: RnaSequenceUpdate,
) -> Response[Union[RnaSequence, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        rna_sequence_id=rna_sequence_id,
        json_body=json_body,
    )

    response = client.httpx_client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    rna_sequence_id: str,
    json_body: RnaSequenceUpdate,
) -> Optional[Union[RnaSequence, BadRequestError]]:
    """ Update an RNA sequence """

    return sync_detailed(
        client=client,
        rna_sequence_id=rna_sequence_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    rna_sequence_id: str,
    json_body: RnaSequenceUpdate,
) -> Response[Union[RnaSequence, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        rna_sequence_id=rna_sequence_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    rna_sequence_id: str,
    json_body: RnaSequenceUpdate,
) -> Optional[Union[RnaSequence, BadRequestError]]:
    """ Update an RNA sequence """

    return (
        await asyncio_detailed(
            client=client,
            rna_sequence_id=rna_sequence_id,
            json_body=json_body,
        )
    ).parsed
