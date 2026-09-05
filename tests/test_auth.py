"""
Authentication tests / 認証テスト

Endpoint: POST /auth
Test cases: TC_AUTH_001 to TC_AUTH_006 (6 cases)

Known deviation: the API returns HTTP 200 for invalid credentials instead of
401 Unauthorized. See docs/known-issues.md (BUG-001).
既知の乖離: 誤った認証情報でも 200 が返ります（BUG-001）。
"""

from __future__ import annotations

import pytest

from utils.api_client import APIClient
from utils.config import AUTH_ENDPOINT, PASSWORD, USERNAME
from utils.helpers import AUTH_SCHEMA, validate_response_structure

pytestmark = pytest.mark.auth


@pytest.mark.smoke
def test_tc_auth_001_valid_credentials_return_token(api_client: APIClient) -> None:
    """TC_AUTH_001: Valid credentials return HTTP 200 and a usable token.

    TC_AUTH_001: 正しい認証情報で 200 と有効なトークンが返ることを確認する。

    Expected / 期待結果:
        status 200, body contains a non-empty "token" string
    """
    response = api_client.post(
        AUTH_ENDPOINT, json={"username": USERNAME, "password": PASSWORD}
    )

    assert response.status_code == 200, (
        f"Expected 200 for valid credentials, got {response.status_code}"
    )

    body = APIClient.safe_json(response)
    validate_response_structure(body, AUTH_SCHEMA)

    # The API issues a 15-character token. Asserted loosely so a future format
    # change does not break the suite.
    assert isinstance(body["token"], str) and len(body["token"]) >= 10, (
        f"Token looks malformed: {body['token']!r}"
    )


@pytest.mark.negative
def test_tc_auth_002_wrong_password_issues_no_token(api_client: APIClient) -> None:
    """TC_AUTH_002: A wrong password must not produce a token.

    TC_AUTH_002: パスワードが誤っている場合、トークンが発行されないことを確認する。

    Expected / 期待結果:
        no "token" field; a "reason" field explains the rejection
        (401 would be correct; the API returns 200, tracked as BUG-001)
    """
    response = api_client.post(
        AUTH_ENDPOINT, json={"username": USERNAME, "password": "wrong_password"}
    )
    body = APIClient.safe_json(response) or {}

    assert "token" not in body, (
        "Security issue: a token was issued for an incorrect password"
    )
    assert "reason" in body, f"Expected a rejection reason, got {body}"


@pytest.mark.negative
def test_tc_auth_003_wrong_username_issues_no_token(api_client: APIClient) -> None:
    """TC_AUTH_003: An unknown username must not produce a token.

    TC_AUTH_003: 存在しないユーザー名の場合、トークンが発行されないことを確認する。
    """
    response = api_client.post(
        AUTH_ENDPOINT, json={"username": "unknown_user", "password": PASSWORD}
    )
    body = APIClient.safe_json(response) or {}

    assert "token" not in body, (
        "Security issue: a token was issued for an unknown username"
    )
    assert "reason" in body, f"Expected a rejection reason, got {body}"


@pytest.mark.negative
def test_tc_auth_004_missing_username_rejected(api_client: APIClient) -> None:
    """TC_AUTH_004: A request without the username field is rejected.

    TC_AUTH_004: username 項目がないリクエストが拒否されることを確認する。

    Expected / 期待結果:
        status 200 with a reason, or 400 Bad Request. No token either way.
    """
    response = api_client.post(AUTH_ENDPOINT, json={"password": PASSWORD})

    assert response.status_code in (200, 400), (
        f"Unexpected status {response.status_code} for a missing username"
    )
    assert "token" not in (APIClient.safe_json(response) or {}), (
        "Security issue: a token was issued without a username"
    )


@pytest.mark.negative
def test_tc_auth_005_missing_password_rejected(api_client: APIClient) -> None:
    """TC_AUTH_005: A request without the password field is rejected.

    TC_AUTH_005: password 項目がないリクエストが拒否されることを確認する。
    """
    response = api_client.post(AUTH_ENDPOINT, json={"username": USERNAME})

    assert response.status_code in (200, 400), (
        f"Unexpected status {response.status_code} for a missing password"
    )
    assert "token" not in (APIClient.safe_json(response) or {}), (
        "Security issue: a token was issued without a password"
    )


@pytest.mark.negative
def test_tc_auth_006_empty_body_rejected(api_client: APIClient) -> None:
    """TC_AUTH_006: An empty request body is rejected.

    TC_AUTH_006: 空のリクエストボディが拒否されることを確認する。
    """
    response = api_client.post(AUTH_ENDPOINT, json={})

    assert response.status_code in (200, 400), (
        f"Unexpected status {response.status_code} for an empty body"
    )
    assert "token" not in (APIClient.safe_json(response) or {}), (
        "Security issue: a token was issued for an empty request body"
    )
