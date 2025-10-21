# src/backend_common/http/client.py
"""
HTTP client implementations for service communication.

Provides robust HTTP clients with retry logic, timeout handling,
circuit breaker pattern, and service authentication.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from httpx import AsyncClient, Response

from ..auth.manager import AuthManager
from ..exceptions import (
    ServiceUnavailableError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    Base HTTP client with retry logic and timeout handling.

    Provides standardized HTTP communication with automatic retries,
    timeout management, and error handling for service interactions.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            headers: Default headers for all requests
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.default_headers = headers or {}

        self._client = AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout),
            headers=self.default_headers,
        )

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for httpx request

        Returns:
            httpx.Response: The HTTP response

        Raises:
            ServiceUnavailableError: If service is unavailable after retries
            TimeoutError: If request times out
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)

                # Check if we should retry based on status code
                if response.status_code >= 500 and attempt < self.max_retries:
                    logger.warning(
                        f"HTTP {response.status_code} on attempt {attempt + 1}, retrying..."
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue

                return response

            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Request timeout on attempt {attempt + 1}, retrying..."
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise TimeoutError(
                        operation=f"{method} {url}",
                        timeout_seconds=self.timeout,
                    )

            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Request error on attempt {attempt + 1}: {e}"
                    )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise ServiceUnavailableError(
                        service_name=str(self.base_url or url),
                        reason=str(e),
                    )

        # This should never be reached, but just in case
        raise ServiceUnavailableError(
            service_name=str(self.base_url or url),
            reason=str(last_exception) if last_exception else "Unknown error",
        )

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Response:
        """Make GET request."""
        return await self._make_request(
            "GET", url, params=params, headers=headers, **kwargs
        )

    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Response:
        """Make POST request."""
        return await self._make_request(
            "POST", url, json=json, data=data, headers=headers, **kwargs
        )

    async def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Response:
        """Make PUT request."""
        return await self._make_request(
            "PUT", url, json=json, data=data, headers=headers, **kwargs
        )

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Response:
        """Make DELETE request."""
        return await self._make_request(
            "DELETE", url, headers=headers, **kwargs
        )

    async def patch(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Response:
        """Make PATCH request."""
        return await self._make_request(
            "PATCH", url, json=json, data=data, headers=headers, **kwargs
        )


class ServiceClient(HTTPClient):
    """
    HTTP client for authenticated service-to-service communication.

    Extends HTTPClient with automatic service authentication using JWT tokens.
    """

    def __init__(
        self,
        service_name: str,
        base_url: str,
        auth_manager: Optional[AuthManager] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize service client.

        Args:
            service_name: Name of this service for authentication
            base_url: Base URL of the target service
            auth_manager: Authentication manager for token generation
            **kwargs: Additional arguments for HTTPClient
        """
        super().__init__(base_url=base_url, **kwargs)
        self.service_name = service_name
        self.auth_manager = auth_manager
        self._service_token: Optional[str] = None

    async def _get_service_token(self) -> str:
        """Get or refresh service authentication token."""
        if self.auth_manager and hasattr(
            self.auth_manager, "create_service_token"
        ):
            self._service_token = await self.auth_manager.create_service_token(
                self.service_name
            )
            return self._service_token
        return ""

    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Response:
        """Make authenticated service request."""
        # Add service authentication header
        headers = kwargs.get("headers", {})

        if self.auth_manager:
            token = await self._get_service_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"

        # Add service identification header
        headers["X-Service-Name"] = self.service_name
        kwargs["headers"] = headers

        return await super()._make_request(method, url, **kwargs)
