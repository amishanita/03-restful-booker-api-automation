"""
Delete tests / 削除テスト

Endpoint: DELETE /booking/{id}
Test cases: TC_DEL_001 to TC_DEL_004 (4 cases)

Known deviations / 既知の乖離:
    BUG-004  deleting a non-existent ID returns 405 instead of 404
    BUG-005  a successful delete returns 201 Created
"""

from __future__ import annotations

from typing import Dict

import pytest

from utils.api_client import APIClient
from utils.config import BOOKING_ENDPOINT, NON_EXISTENT_BOOKING_ID
from utils.helpers import generate_random_booking_data

pytestmark = pytest.mark.crud


@pytest.mark.smoke
def test_tc_del_001_delete_existing_booking(
    api_client: APIClient, auth_headers: Dict[str, str]
) -> None:
    """TC_DEL_001: A booking deleted with a valid token is no longer retrievable.

    TC_DEL_001: 有効なトークンで削除した予約が取得できなくなることを確認する。

    The booking is created inside the test rather than through the booking_id
    fixture, because the fixture teardown would attempt a second delete.
    フィクスチャの teardown と二重削除にならないよう、テスト内で作成する。

    Expected / 期待結果:
        200 or 201 (204 No Content would be correct, see BUG-005),
        and a follow-up GET returning 404
    """
    created = api_client.post(BOOKING_ENDPOINT, json=generate_random_booking_data())
    assert created.status_code == 200, "Setup failed: could not create a booking"
    target_id = created.json()["bookingid"]

    response = api_client.delete(f"{BOOKING_ENDPOINT}/{target_id}", headers=auth_headers)

    assert response.status_code in (200, 201), (
        f"Delete failed: {response.status_code} {response.text[:200]}"
    )

    verification = api_client.get(f"{BOOKING_ENDPOINT}/{target_id}")
    assert verification.status_code == 404, (
        f"Booking {target_id} still exists after delete "
        f"(GET returned {verification.status_code})"
    )


@pytest.mark.negative
@pytest.mark.auth
def test_tc_del_002_delete_without_authentication(
    api_client: APIClient, booking_id: int
) -> None:
    """TC_DEL_002: Delete without a token is rejected and the record survives.

    TC_DEL_002: トークンなしの削除が拒否され、データが残ることを確認する。
    """
    response = api_client.delete(f"{BOOKING_ENDPOINT}/{booking_id}")

    assert response.status_code == 403, (
        f"Unauthenticated DELETE should return 403, got {response.status_code}"
    )

    verification = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}")
    assert verification.status_code == 200, (
        "The booking was removed by an unauthenticated DELETE request"
    )


@pytest.mark.negative
@pytest.mark.auth
def test_tc_del_003_delete_with_invalid_token(
    api_client: APIClient, booking_id: int
) -> None:
    """TC_DEL_003: A forged token is rejected the same way as no token.

    TC_DEL_003: 偽造トークンがトークンなしと同様に拒否されることを確認する。
    """
    response = api_client.delete(
        f"{BOOKING_ENDPOINT}/{booking_id}",
        headers={"Cookie": "token=invalid_token_000"},
    )

    assert response.status_code == 403, (
        f"A forged token should be rejected with 403, got {response.status_code}"
    )

    verification = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}")
    assert verification.status_code == 200, (
        "The booking was removed by a request carrying a forged token"
    )


@pytest.mark.negative
@pytest.mark.known_bug
def test_tc_del_004_delete_non_existent_booking(
    api_client: APIClient, auth_headers: Dict[str, str]
) -> None:
    """TC_DEL_004: Deleting a non-existent ID does not report success.

    TC_DEL_004: 存在しない ID の削除が成功と報告されないことを確認する。

    Expected / 期待結果:
        404 Not Found. The API returns 405 Method Not Allowed (BUG-004).
    """
    response = api_client.delete(
        f"{BOOKING_ENDPOINT}/{NON_EXISTENT_BOOKING_ID}", headers=auth_headers
    )

    assert response.status_code not in (200, 201), (
        "Deleting a non-existent booking reported success"
    )

    if response.status_code == 405:
        pytest.xfail(
            "BUG-004: deleting a non-existent ID returns 405 Method Not Allowed "
            "where 404 Not Found is expected"
        )

    assert response.status_code == 404, (
        f"Unexpected status {response.status_code} for a non-existent ID"
    )
