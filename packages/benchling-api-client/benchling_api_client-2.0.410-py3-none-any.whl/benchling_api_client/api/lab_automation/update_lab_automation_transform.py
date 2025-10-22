from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.lab_automation_transform import LabAutomationTransform
from ...models.lab_automation_transform_update import LabAutomationTransformUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    transform_id: str,
    json_body: LabAutomationTransformUpdate,
) -> Dict[str, Any]:
    url = "{}/automation-file-transforms/{transform_id}".format(client.base_url, transform_id=transform_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[LabAutomationTransform, BadRequestError]]:
    if response.status_code == 200:
        response_200 = LabAutomationTransform.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[LabAutomationTransform, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    transform_id: str,
    json_body: LabAutomationTransformUpdate,
) -> Response[Union[LabAutomationTransform, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        transform_id=transform_id,
        json_body=json_body,
    )

    response = client.httpx_client.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    transform_id: str,
    json_body: LabAutomationTransformUpdate,
) -> Optional[Union[LabAutomationTransform, BadRequestError]]:
    """ Update a Lab Automation Transform step """

    return sync_detailed(
        client=client,
        transform_id=transform_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    transform_id: str,
    json_body: LabAutomationTransformUpdate,
) -> Response[Union[LabAutomationTransform, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        transform_id=transform_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    transform_id: str,
    json_body: LabAutomationTransformUpdate,
) -> Optional[Union[LabAutomationTransform, BadRequestError]]:
    """ Update a Lab Automation Transform step """

    return (
        await asyncio_detailed(
            client=client,
            transform_id=transform_id,
            json_body=json_body,
        )
    ).parsed
