"""
Update tests / 更新テスト

Endpoints: PUT /booking/{id}, PATCH /booking/{id}
Test cases: TC_PUT_001 to TC_PUT_003, TC_PATCH_001 to TC_PATCH_004 (7 cases)

Both verbs require authentication via the Cookie header.
どちらのメソッドも Cookie ヘッダーによる認証が必要です。

Known deviation / 既知の乖離:
    BUG-004  a write to a non-existent ID returns 405 instead of 404
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from utils.api_client import APIClient
from utils.config import BOOKING_ENDPOINT, NON_EXISTENT_BOOKING_ID
from utils.helpers import (
    BOOKING_SCHEMA,
    generate_random_booking_data,
    validate_response_structure,
)

pytestmark = pytest.mark.crud


@pytest.mark.smoke
def test_tc_put_001_full_update_with_valid_token(
    api_client: APIClient, booking_id: int, auth_headers: Dict[str, str]
) -> None:
    """TC_PUT_001: PUT with a valid token replaces every field.

    TC_PUT_001: 有効なトークンによる PUT で全項目が置き換わることを確認する。

    The change is verified with a follow-up GET, because an echoed response
    does not prove the record was persisted.
    レスポンスの反射だけでは永続化の証明にならないため、再取得して確認する。
    """
    new_payload: Dict[str, Any] = generate_random_booking_data()

    response = api_client.put(
        f"{BOOKING_ENDPOINT}/{booking_id}", json=new_payload, headers=auth_headers
    )

    assert response.status_code == 200, (
        f"PUT failed: {response.status_code} {response.text[:200]}"
    )

    body = APIClient.safe_json(response)
    validate_response_structure(body, BOOKING_SCHEMA)

    for field, expected in new_payload.items():
        assert body[field] == expected, (
            f"Field '{field}' not updated: sent {expected!r}, got {body.get(field)!r}"
        )

    verification = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}")
    assert verification.status_code == 200
    assert verification.json()["firstname"] == new_payload["firstname"], (
        "PUT reported success but the stored record was not updated"
    )


@pytest.mark.negative
@pytest.mark.auth
def test_tc_put_002_full_update_without_authentication(
    api_client: APIClient, booking_id: int
) -> None:
    """TC_PUT_002: PUT without a token is rejected and changes nothing.

    TC_PUT_002: トークンなしの PUT が拒否され、データが変更されないことを確認する。

    Expected / 期待結果:
        status 403 Forbidden, and the record identical to its previous state
    """
    before = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}").json()

    response = api_client.put(
        f"{BOOKING_ENDPOINT}/{booking_id}", json=generate_random_booking_data()
    )

    assert response.status_code == 403, (
        f"Unauthenticated PUT should return 403, got {response.status_code}"
    )

    after = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}").json()
    assert after == before, (
        f"An unauthenticated PUT modified the booking: {before} -> {after}"
    )


@pytest.mark.negative
@pytest.mark.known_bug
def test_tc_put_003_full_update_non_existent_id(
    api_client: APIClient, auth_headers: Dict[str, str]
) -> None:
    """TC_PUT_003: PUT to a non-existent ID does not succeed.

    TC_PUT_003: 存在しない ID への PUT が成功しないことを確認する。

    Expected / 期待結果:
        404 Not Found. The API returns 405 Method Not Allowed (BUG-004).
    """
    response = api_client.put(
        f"{BOOKING_ENDPOINT}/{NON_EXISTENT_BOOKING_ID}",
        json=generate_random_booking_data(),
        headers=auth_headers,
    )

    assert response.status_code != 200, (
        "PUT to a non-existent booking ID unexpectedly succeeded"
    )

    if response.status_code == 405:
        pytest.xfail(
            "BUG-004: a write to a non-existent ID returns 405 Method Not Allowed "
            "where 404 Not Found is expected"
        )

    assert response.status_code == 404, (
        f"Unexpected status {response.status_code} for a non-existent ID"
    )


@pytest.mark.smoke
def test_tc_patch_001_partial_update_single_field(
    api_client: APIClient, booking_id: int, auth_headers: Dict[str, str]
) -> None:
    """TC_PATCH_001: PATCH updates one field and leaves the others untouched.

    TC_PATCH_001: PATCH で 1 項目のみ更新され、他の項目が変化しないことを確認する。
    """
    original = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}").json()

    response = api_client.patch(
        f"{BOOKING_ENDPOINT}/{booking_id}",
        json={"firstname": "Amish"},
        headers=auth_headers,
    )

    assert response.status_code == 200, (
        f"PATCH failed: {response.status_code} {response.text[:200]}"
    )

    body = APIClient.safe_json(response)
    validate_response_structure(body, BOOKING_SCHEMA)
    assert body["firstname"] == "Amish", (
        f"PATCH did not apply the new first name: {body.get('firstname')!r}"
    )

    for field in set(original) - {"firstname"}:
        assert body[field] == original[field], (
            f"PATCH modified '{field}', which was not part of the request: "
            f"{original[field]!r} -> {body.get(field)!r}"
        )


@pytest.mark.regression
def test_tc_patch_002_partial_update_multiple_fields(
    api_client: APIClient, booking_id: int, auth_headers: Dict[str, str]
) -> None:
    """TC_PATCH_002: PATCH applies several fields in one request.

    TC_PATCH_002: 複数項目を 1 リクエストで更新できることを確認する。
    """
    updates = {"firstname": "Yuki", "lastname": "Nakamura", "totalprice": 777}

    response = api_client.patch(
        f"{BOOKING_ENDPOINT}/{booking_id}", json=updates, headers=auth_headers
    )

    assert response.status_code == 200, (
        f"PATCH failed: {response.status_code} {response.text[:200]}"
    )

    body = APIClient.safe_json(response)
    for field, expected in updates.items():
        assert body[field] == expected, (
            f"PATCH did not apply '{field}': expected {expected!r}, "
            f"got {body.get(field)!r}"
        )


@pytest.mark.negative
@pytest.mark.auth
def test_tc_patch_003_partial_update_without_authentication(
    api_client: APIClient, booking_id: int
) -> None:
    """TC_PATCH_003: PATCH without a token is rejected and changes nothing.

    TC_PATCH_003: トークンなしの PATCH が拒否され、データが変更されないことを確認する。
    """
    before = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}").json()

    response = api_client.patch(
        f"{BOOKING_ENDPOINT}/{booking_id}", json={"firstname": "Unauthorised"}
    )

    assert response.status_code == 403, (
        f"Unauthenticated PATCH should return 403, got {response.status_code}"
    )

    after = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}").json()
    assert after == before, (
        f"An unauthenticated PATCH modified the booking: {before} -> {after}"
    )


@pytest.mark.negative
@pytest.mark.known_bug
def test_tc_patch_004_partial_update_non_existent_id(
    api_client: APIClient, auth_headers: Dict[str, str]
) -> None:
    """TC_PATCH_004: PATCH to a non-existent ID does not succeed.

    TC_PATCH_004: 存在しない ID への PATCH が成功しないことを確認する（BUG-004）。
    """
    response = api_client.patch(
        f"{BOOKING_ENDPOINT}/{NON_EXISTENT_BOOKING_ID}",
        json={"firstname": "Ghost"},
        headers=auth_headers,
    )

    assert response.status_code != 200, (
        "PATCH to a non-existent booking ID unexpectedly succeeded"
    )

    if response.status_code == 405:
        pytest.xfail(
            "BUG-004: a write to a non-existent ID returns 405 Method Not Allowed "
            "where 404 Not Found is expected"
        )

    assert response.status_code == 404, (
        f"Unexpected status {response.status_code} for a non-existent ID"
    )
