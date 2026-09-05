"""
HTTP client wrapper for the RESTful Booker API.

RESTful Booker への HTTP リクエストをまとめたクライアント。

The client wraps `requests.Session` so that every test shares one connection
pool, a single timeout policy and a retry policy for the transient 5xx errors
that the public Heroku instance produces under load.

Responses are returned as plain `requests.Response` objects, so tests keep
access to `status_code`, `headers`, `text` and `json()`. Use
`APIClient.safe_json()` when an endpoint may return plain text instead of JSON
(RESTful Booker does this for DELETE and for some error paths).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class APIClientError(RuntimeError):
    """Raised when a request cannot be completed at the transport layer.

    This covers DNS failures, connection resets and timeouts. HTTP error
    status codes are *not* raised as exceptions: they are legitimate test
    results and are returned to the caller for assertion.
    """


class APIClient:
    """Thin, reusable HTTP client for REST endpoints.

    Args:
        base_url: Root URL of the service, e.g. ``https://restful-booker.herokuapp.com``.
        timeout: Per-request timeout in seconds.
        max_retries: Number of automatic retries for connection errors and 5xx
            responses on idempotent methods.

    Example:
        >>> client = APIClient("https://restful-booker.herokuapp.com")
        >>> response = client.get("/booking/1")
        >>> response.status_code
        200
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

        # The public instance is a free-tier Heroku app. Retrying idempotent
        # verbs on 502/503/504 removes most flaky failures without hiding real
        # application bugs (4xx responses are never retried).
        retry_policy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "PUT", "DELETE", "HEAD", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_policy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _url(self, endpoint: str) -> str:
        """Join the base URL and an endpoint into an absolute URL."""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Send a request and return the raw response.

        Raises:
            APIClientError: If the request fails before an HTTP status is received.
        """
        url = self._url(endpoint)
        logger.debug("%s %s payload=%s headers=%s", method, url, json, headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise APIClientError(f"{method} {url} failed: {exc}") from exc

        logger.debug(
            "%s %s -> %s (%.0f ms)",
            method,
            url,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )
        return response

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------
    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Send a POST request."""
        return self._request("POST", endpoint, json=json, headers=headers)

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Send a GET request."""
        return self._request("GET", endpoint, headers=headers, params=params)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Send a PUT request (full update)."""
        return self._request("PUT", endpoint, json=json, headers=headers)

    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Send a PATCH request (partial update)."""
        return self._request("PATCH", endpoint, json=json, headers=headers)

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Send a DELETE request."""
        return self._request("DELETE", endpoint, headers=headers)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def safe_json(response: requests.Response) -> Optional[Dict[str, Any]]:
        """Return the parsed JSON body, or ``None`` if the body is not JSON.

        RESTful Booker replies with plain text for several endpoints
        (``Created``, ``Not Found``, ``Forbidden``), so calling ``.json()``
        directly would raise and mask the real assertion failure.
        """
        try:
            return response.json()
        except ValueError:
            return None

    def close(self) -> None:
        """Close the underlying session and release pooled connections."""
        self.session.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
