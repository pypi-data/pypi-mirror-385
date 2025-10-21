from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.aspect_idrt import AspectIDRT
from ...models.aspectupdate_body import AspectupdateBody
from ...models.bad_request_t import BadRequestT
from ...models.invalid_parameter_t import InvalidParameterT
from ...models.invalid_scopes_t import InvalidScopesT
from ...models.not_implemented_t import NotImplementedT
from ...models.not_unique_resource_t import NotUniqueResourceT
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: AspectupdateBody,
    entity: str,
    schema: str,
    policy: Union[Unset, str] = UNSET,
    content_type: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Content-Type"] = content_type

    params: dict[str, Any] = {}

    params["entity"] = entity

    params["schema"] = schema

    params["policy"] = policy

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/1/aspects",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
]:
    if response.status_code == 200:
        response_200 = AspectIDRT.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestT.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == 403:
        response_403 = InvalidScopesT.from_dict(response.json())

        return response_403
    if response.status_code == 422:
        response_422 = InvalidParameterT.from_dict(response.json())

        return response_422
    if response.status_code == 424:
        response_424 = NotUniqueResourceT.from_dict(response.json())

        return response_424
    if response.status_code == 501:
        response_501 = NotImplementedT.from_dict(response.json())

        return response_501
    if response.status_code == 503:
        response_503 = cast(Any, None)
        return response_503
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: AspectupdateBody,
    entity: str,
    schema: str,
    policy: Union[Unset, str] = UNSET,
    content_type: str,
) -> Response[
    Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
]:
    """update aspect

     A convenience method which will create a new aspect, but will also
                retract a potentially existing aspect for the same entity with the same schema.

    Args:
        entity (str): Entity to which attach aspect Example: urn:some_ns:schema:some_schema.1.
        schema (str): Schema of aspect Example: urn:url:.....
        policy (Union[Unset, str]): Policy guiding visibility and actions performed Example:
            urn:ivcap:policy:some_policy.1.
        content_type (str): Content-Type header, MUST be of application/json. Example:
            application/json.
        body (AspectupdateBody): Aspect content Example: {"$schema": ...}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]]
    """

    kwargs = _get_kwargs(
        body=body,
        entity=entity,
        schema=schema,
        policy=policy,
        content_type=content_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: AspectupdateBody,
    entity: str,
    schema: str,
    policy: Union[Unset, str] = UNSET,
    content_type: str,
) -> Optional[
    Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
]:
    """update aspect

     A convenience method which will create a new aspect, but will also
                retract a potentially existing aspect for the same entity with the same schema.

    Args:
        entity (str): Entity to which attach aspect Example: urn:some_ns:schema:some_schema.1.
        schema (str): Schema of aspect Example: urn:url:.....
        policy (Union[Unset, str]): Policy guiding visibility and actions performed Example:
            urn:ivcap:policy:some_policy.1.
        content_type (str): Content-Type header, MUST be of application/json. Example:
            application/json.
        body (AspectupdateBody): Aspect content Example: {"$schema": ...}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
    """

    return sync_detailed(
        client=client,
        body=body,
        entity=entity,
        schema=schema,
        policy=policy,
        content_type=content_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: AspectupdateBody,
    entity: str,
    schema: str,
    policy: Union[Unset, str] = UNSET,
    content_type: str,
) -> Response[
    Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
]:
    """update aspect

     A convenience method which will create a new aspect, but will also
                retract a potentially existing aspect for the same entity with the same schema.

    Args:
        entity (str): Entity to which attach aspect Example: urn:some_ns:schema:some_schema.1.
        schema (str): Schema of aspect Example: urn:url:.....
        policy (Union[Unset, str]): Policy guiding visibility and actions performed Example:
            urn:ivcap:policy:some_policy.1.
        content_type (str): Content-Type header, MUST be of application/json. Example:
            application/json.
        body (AspectupdateBody): Aspect content Example: {"$schema": ...}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]]
    """

    kwargs = _get_kwargs(
        body=body,
        entity=entity,
        schema=schema,
        policy=policy,
        content_type=content_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: AspectupdateBody,
    entity: str,
    schema: str,
    policy: Union[Unset, str] = UNSET,
    content_type: str,
) -> Optional[
    Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
]:
    """update aspect

     A convenience method which will create a new aspect, but will also
                retract a potentially existing aspect for the same entity with the same schema.

    Args:
        entity (str): Entity to which attach aspect Example: urn:some_ns:schema:some_schema.1.
        schema (str): Schema of aspect Example: urn:url:.....
        policy (Union[Unset, str]): Policy guiding visibility and actions performed Example:
            urn:ivcap:policy:some_policy.1.
        content_type (str): Content-Type header, MUST be of application/json. Example:
            application/json.
        body (AspectupdateBody): Aspect content Example: {"$schema": ...}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AspectIDRT, BadRequestT, InvalidParameterT, InvalidScopesT, NotImplementedT, NotUniqueResourceT]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            entity=entity,
            schema=schema,
            policy=policy,
            content_type=content_type,
        )
    ).parsed
