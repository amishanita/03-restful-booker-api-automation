"""
Shared pytest fixtures / 共通フィクスチャ

Fixture scopes / スコープ:
    api_client      session   one HTTP session for the whole run
    auth_token      session   one token reused by every write operation
    auth_headers    session   ready-made Cookie header
    booking_payload session   valid payload loaded from test_data/
    booking_id      function  a booking created and cleaned up per test
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Generator

import pytest

from utils.api_client import APIClient, APIClientError
from utils.config import (
    AUTH_ENDPOINT,
    BASE_URL,
    BOOKING_ENDPOINT,
    MAX_RETRIES,
    PASSWORD,
    PING_ENDPOINT,
    TIMEOUT,
    USERNAME,
)
from utils.helpers import auth_cookie_header, generate_random_booking_data, load_test_data

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    """Single HTTP client shared by the whole session / 全テストで共有する HTTP クライアント."""
    client = APIClient(base_url=BASE_URL, timeout=TIMEOUT, max_retries=MAX_RETRIES)
    logger.info("API client created for %s", BASE_URL)
    yield client
    client.close()


@pytest.fixture(scope="session", autouse=True)
def api_health_check(api_client: APIClient) -> None:
    """Stop the run with one clear message if the API is unreachable.

    API に接続できない場合、25 件の失敗ではなく 1 件の明確なメッセージで終了します。
    """
    try:
        response = api_client.get(PING_ENDPOINT)
    except APIClientError as exc:
        pytest.exit(f"API is unreachable at {BASE_URL}: {exc}", returncode=3)

    if response.status_code != 201:
        pytest.exit(
            f"Health check failed: GET {PING_ENDPOINT} returned "
            f"{response.status_code}, expected 201",
            returncode=3,
        )
    logger.info("Health check passed (%s)", response.status_code)


@pytest.fixture(scope="session")
def auth_token(api_client: APIClient) -> str:
    """Create one auth token and reuse it / トークンを 1 回だけ発行して再利用."""
    response = api_client.post(
        AUTH_ENDPOINT, json={"username": USERNAME, "password": PASSWORD}
    )
    token = (APIClient.safe_json(response) or {}).get("token")

    if not token:
        pytest.fail(
            f"Could not obtain an auth token. Status={response.status_code}, "
            f"body={response.text[:200]}. Check RB_USERNAME and RB_PASSWORD in .env"
        )
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> Dict[str, str]:
    """Cookie header required by PUT, PATCH and DELETE / 更新・削除に必要な Cookie ヘッダー."""
    return auth_cookie_header(auth_token)


@pytest.fixture(scope="session")
def booking_payload() -> Dict[str, Any]:
    """Valid payload from test_data/booking_payload.json / 正常系データ."""
    return load_test_data("booking_payload.json")


@pytest.fixture(scope="session")
def invalid_data() -> Dict[str, Any]:
    """Invalid payloads from test_data/invalid_data.json / 異常系データ."""
    return load_test_data("invalid_data.json")


@pytest.fixture(scope="session")
def expected_data() -> Dict[str, Any]:
    """Expected status codes and shapes / 期待ステータスコードと構造."""
    return load_test_data("expected_data.json")


@pytest.fixture
def booking_id(
    api_client: APIClient, auth_headers: Dict[str, str]
) -> Generator[int, None, None]:
    """Create a booking for one test, then delete it in teardown.

    テストごとに予約を作成し、終了時に削除します。テストの独立性を保つためです。

    Yields:
        The ID of a freshly created booking / 作成した予約の ID
    """
    response = api_client.post(BOOKING_ENDPOINT, json=generate_random_booking_data())
    assert response.status_code == 200, (
        f"Fixture setup failed: could not create a booking. "
        f"Status={response.status_code}, body={response.text[:200]}"
    )
    created_id = response.json()["bookingid"]
    logger.info("Created booking %s for test", created_id)

    yield created_id

    # 405 during teardown is expected when the test already deleted the record.
    cleanup = api_client.delete(f"{BOOKING_ENDPOINT}/{created_id}", headers=auth_headers)
    if cleanup.status_code not in (200, 201, 404, 405):
        logger.warning(
            "Teardown of booking %s returned unexpected status %s",
            created_id,
            cleanup.status_code,
        )
