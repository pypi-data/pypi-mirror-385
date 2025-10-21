"""
Module providing clients for listing available models, either synchronously or asynchronously.
All responses are validated using Pydantic models.

This module includes:
  - `ModelsClient` for synchronous calls.
  - `AsyncModelsClient` for asynchronous calls.

All clients call the `/v1/models` endpoint, and all responses
are validated using Pydantic models.

Example usage:

    from air.models.client import ModelsClient, AsyncModelsClient

    # Synchronous usage:
    sync_client = ModelsClient(
        base_url="https://api.airefinery.accenture.com",
        api_key="...",
        default_headers={"X-Client-Version": "1.2.3"}
    )
    models_page = sync_client.list(
        timeout=10.0,
        extra_headers={"X-Request-Id": "abc123"},
        organization="MyOrg"  # Example extra GET parameter
    )

    # Asynchronous usage:
    async_client = AsyncModelsClient(
        base_url="https://api.airefinery.accenture.com",
        api_key="...",
        default_headers={"X-Client-Version": "1.2.3"}
    )
    models_page = await async_client.list(
        timeout=10.0,
        extra_headers={"X-Request-Id": "xyz789"},
        organization="MyOrg"
    )
"""

import aiohttp
import requests

from air import BASE_URL, __version__
from air.auth.token_provider import TokenProvider
from air.types import AsyncPage, Model, SyncPage
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_MODELS = "{base_url}/v1/models"


class ModelsClient:  # pylint: disable=too-few-public-methods
    """
    A synchronous client for listing models.

    This class handles sending GET requests to the models endpoint
    and converts the responses into Pydantic models for type safety.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        """
        Initializes the synchronous models client.

        Args:
            api_key (str | TokenProvider): Credential that will be placed in the
                ``Authorization`` header of every request.
                * **str** – a raw bearer token / API key.
                * **TokenProvider** – an object whose ``token()`` (and
                  ``token_async()``) method returns a valid bearer token.  The
                  client calls the provider automatically before each request.

            base_url (str): Base URL of the API (e.g., "https://api.airefinery.accenture.com").
            default_headers (dict[str, str] | None): Headers that apply to
                every request from this client.
        """
        self.base_url = base_url

        self.api_key = api_key
        self.default_headers = default_headers or {}

    def list(
        self,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
        **kwargs,
    ) -> SyncPage[Model]:
        """
        Lists available models synchronously.

        Args:
            timeout (float | None): Maximum time (in seconds) to wait for a response
                before timing out. If None, defaults to 60 seconds.
            extra_headers (dict[str, str] | None): Request-specific headers to include
                or override on this call.
            **kwargs: Additional parameters to include in the GET request. These
                will be sent as JSON in the body (though typically GET parameters
                go in the query string).

        Returns:
            SyncPage[Model]: A Pydantic model containing the list of models.
        """
        endpoint = ENDPOINT_MODELS.format(base_url=self.base_url)
        payload = kwargs

        # Built-in authorization/JSON headers
        headers = get_base_headers(self.api_key)
        # Merge default_headers
        headers.update(self.default_headers)
        # Merge request-specific extra_headers last
        if extra_headers:
            headers.update(extra_headers)

        effective_timeout = 60 if timeout is None else timeout
        response = requests.get(
            endpoint,
            json=payload,
            headers=headers,
            timeout=effective_timeout,
        )
        response.raise_for_status()
        json_data = response.json()
        return SyncPage[Model].model_validate(json_data)


class AsyncModelsClient:  # pylint: disable=too-few-public-methods
    """
    An asynchronous client for listing models.

    This class handles sending GET requests to the models endpoint
    and converts the responses into Pydantic models for type safety.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str,
        default_headers: dict[str, str] | None = None,
    ):
        """
        Initializes the asynchronous models client.

        Args:
            api_key (str | TokenProvider): Credential that will be placed in the
                ``Authorization`` header of every request.
                * **str** – a raw bearer token / API key.
                * **TokenProvider** – an object whose ``token()`` (and
                  ``token_async()``) method returns a valid bearer token.  The
                  client calls the provider automatically before each request.

            base_url (str): Base URL of the API (e.g., "https://api.airefinery.accenture.com").
            default_headers (dict[str, str] | None): Headers that apply to
                every request from this client.
        """
        self.base_url = base_url

        self.api_key = api_key
        self.default_headers = default_headers or {}

    async def list(
        self,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
        **kwargs,
    ) -> AsyncPage[Model]:
        """
        Lists available models asynchronously.

        Args:
            timeout (float | None): Maximum time (in seconds) to wait for a response
                before timing out. If None, defaults to 60 seconds.
            extra_headers (dict[str, str] | None): Request-specific headers to include
                or override on this call.
            **kwargs: Additional parameters to include in the GET request. These
                will be sent as JSON in the body (though typically GET parameters
                go in the query string).

        Returns:
            AsyncPage[Model]: A Pydantic model containing the list of models.
        """
        endpoint = ENDPOINT_MODELS.format(base_url=self.base_url)

        payload = kwargs

        headers = await get_base_headers_async(self.api_key)

        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        effective_timeout = 60 if timeout is None else timeout
        client_timeout = aiohttp.ClientTimeout(total=effective_timeout)

        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(endpoint, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                json_data = await resp.json()
                return AsyncPage[Model].model_validate(json_data)
