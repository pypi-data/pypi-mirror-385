from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.upload_response import UploadResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    guid: str,
    configuration_name: str,
    *,
    depends_on: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_depends_on: Union[None, Unset, str]
    if isinstance(depends_on, Unset):
        json_depends_on = UNSET
    else:
        json_depends_on = depends_on
    params["dependsOn"] = json_depends_on

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/document/process/{guid}/with-configuration/{configuration_name}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[UploadResponse]:
    if response.status_code == 200:
        response_200 = UploadResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[UploadResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    guid: str,
    configuration_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    depends_on: Union[None, Unset, str] = UNSET,
) -> Response[UploadResponse]:
    """
    Args:
        guid (str):
        configuration_name (str):
        depends_on (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        guid=guid,
        configuration_name=configuration_name,
        depends_on=depends_on,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    guid: str,
    configuration_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    depends_on: Union[None, Unset, str] = UNSET,
) -> Optional[UploadResponse]:
    """
    Args:
        guid (str):
        configuration_name (str):
        depends_on (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return sync_detailed(
        guid=guid,
        configuration_name=configuration_name,
        client=client,
        depends_on=depends_on,
    ).parsed


async def asyncio_detailed(
    guid: str,
    configuration_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    depends_on: Union[None, Unset, str] = UNSET,
) -> Response[UploadResponse]:
    """
    Args:
        guid (str):
        configuration_name (str):
        depends_on (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
    """

    kwargs = _get_kwargs(
        guid=guid,
        configuration_name=configuration_name,
        depends_on=depends_on,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    guid: str,
    configuration_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    depends_on: Union[None, Unset, str] = UNSET,
) -> Optional[UploadResponse]:
    """
    Args:
        guid (str):
        configuration_name (str):
        depends_on (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
    """

    return (
        await asyncio_detailed(
            guid=guid,
            configuration_name=configuration_name,
            client=client,
            depends_on=depends_on,
        )
    ).parsed
