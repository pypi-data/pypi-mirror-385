from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_last_routes_for_devices_body import GetLastRoutesForDevicesBody
from ...models.uplink_route_and_device_id import UplinkRouteAndDeviceId
from ...types import Response


def _get_kwargs(
    *,
    body: GetLastRoutesForDevicesBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/device/lastRoute",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["UplinkRouteAndDeviceId"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UplinkRouteAndDeviceId.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["UplinkRouteAndDeviceId"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GetLastRoutesForDevicesBody,
) -> Response[list["UplinkRouteAndDeviceId"]]:
    """Get last routes for a group of devices

    Args:
        body (GetLastRoutesForDevicesBody): Body for getting last routes for devices

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UplinkRouteAndDeviceId']]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GetLastRoutesForDevicesBody,
) -> Optional[list["UplinkRouteAndDeviceId"]]:
    """Get last routes for a group of devices

    Args:
        body (GetLastRoutesForDevicesBody): Body for getting last routes for devices

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UplinkRouteAndDeviceId']
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GetLastRoutesForDevicesBody,
) -> Response[list["UplinkRouteAndDeviceId"]]:
    """Get last routes for a group of devices

    Args:
        body (GetLastRoutesForDevicesBody): Body for getting last routes for devices

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['UplinkRouteAndDeviceId']]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: GetLastRoutesForDevicesBody,
) -> Optional[list["UplinkRouteAndDeviceId"]]:
    """Get last routes for a group of devices

    Args:
        body (GetLastRoutesForDevicesBody): Body for getting last routes for devices

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['UplinkRouteAndDeviceId']
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
