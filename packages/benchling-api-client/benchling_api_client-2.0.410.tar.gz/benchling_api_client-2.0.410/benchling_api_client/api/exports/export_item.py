from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.async_task_link import AsyncTaskLink
from ...models.bad_request_error import BadRequestError
from ...models.export_item_request import ExportItemRequest
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ExportItemRequest,
) -> Dict[str, Any]:
    url = "{}/exports".format(client.base_url)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    if response.status_code == 202:
        response_202 = AsyncTaskLink.from_dict(response.json(), strict=False)

        return response_202
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ExportItemRequest,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
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
    json_body: ExportItemRequest,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """This endpoint launches a [long-running task](#/Tasks/getTask) and returns the Task ID of the launched task.
    The task response contains a link to download the exported item from Amazon S3. The download is a ZIP file that contains the exported PDFs.
    This endpoint is subject to throughput rate limiting. Due to the long running nature of these export requests, the endpoint may reject the request with an HTTP 429 error if the system is currently handling too many export requests simultaneously.
    Note that the rate limit is not a fixed limit based on number of requests per hour, but rather a dynamic limit based on current system load and complexity of the items being exported. If using this endpoint with a large number of requests, it is recommended to implement a backoff and retry strategy to handle HTTP 429 errors.
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: ExportItemRequest,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
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
    json_body: ExportItemRequest,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """This endpoint launches a [long-running task](#/Tasks/getTask) and returns the Task ID of the launched task.
    The task response contains a link to download the exported item from Amazon S3. The download is a ZIP file that contains the exported PDFs.
    This endpoint is subject to throughput rate limiting. Due to the long running nature of these export requests, the endpoint may reject the request with an HTTP 429 error if the system is currently handling too many export requests simultaneously.
    Note that the rate limit is not a fixed limit based on number of requests per hour, but rather a dynamic limit based on current system load and complexity of the items being exported. If using this endpoint with a large number of requests, it is recommended to implement a backoff and retry strategy to handle HTTP 429 errors.
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
