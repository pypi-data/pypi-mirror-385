from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.operation_status_response import OperationStatusResponse
from ...types import Response


def _get_kwargs(
    job_guid: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/operation/{job_guid}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[OperationStatusResponse]:
    if response.status_code == 200:
        response_200 = OperationStatusResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[OperationStatusResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[OperationStatusResponse]:
    """
    Args:
        job_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OperationStatusResponse]
    """

    kwargs = _get_kwargs(
        job_guid=job_guid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[OperationStatusResponse]:
    """
    Args:
        job_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OperationStatusResponse
    """

    return sync_detailed(
        job_guid=job_guid,
        client=client,
    ).parsed


async def asyncio_detailed(
    job_guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[OperationStatusResponse]:
    """
    Args:
        job_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OperationStatusResponse]
    """

    kwargs = _get_kwargs(
        job_guid=job_guid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[OperationStatusResponse]:
    """
    Args:
        job_guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OperationStatusResponse
    """

    return (
        await asyncio_detailed(
            job_guid=job_guid,
            client=client,
        )
    ).parsed
