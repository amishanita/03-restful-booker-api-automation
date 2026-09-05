"""
Create and retrieve tests / 予約作成・取得テスト

Endpoints: POST /booking, GET /booking, GET /booking/{id}
Test cases: TC_BOOK_001 to TC_BOOK_008 (8 cases)

Known deviations / 既知の乖離:
    BUG-002  missing required fields return 500 instead of 400
    BUG-003  successful creation returns 200 instead of 201
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from utils.api_client import APIClient
from utils.config import BOOKING_ENDPOINT, NON_EXISTENT_BOOKING_ID
from utils.helpers import (
    BOOKING_SCHEMA,
    CREATE_BOOKING_SCHEMA,
    generate_random_booking_data,
    validate_response_structure,
)

pytestmark = pytest.mark.crud


@pytest.mark.smoke
def test_tc_book_001_create_booking_with_full_payload(
    api_client: APIClient, booking_payload: Dict[str, Any]
) -> None:
    """TC_BOOK_001: A complete valid payload creates a booking.

    TC_BOOK_001: 完全な正常データで予約が作成されることを確認する。

    Expected / 期待結果:
        status 200 (201 would be correct, see BUG-003),
        a positive integer bookingid, and every submitted field stored unchanged
    """
    response = api_client.post(BOOKING_ENDPOINT, json=booking_payload)

    assert response.status_code == 200, (
        f"Expected 200 on create, got {response.status_code}: {response.text[:200]}"
    )

    body = APIClient.safe_json(response)
    validate_response_structure(body, CREATE_BOOKING_SCHEMA)

    assert isinstance(body["bookingid"], int) and body["bookingid"] > 0, (
        f"bookingid should be a positive integer, got {body.get('bookingid')!r}"
    )

    # Every submitted field must come back unchanged / 送信した全項目が保持されること
    for field, expected in booking_payload.items():
        assert body["booking"][field] == expected, (
            f"Field '{field}' was not stored correctly: "
            f"sent {expected!r}, received {body['booking'].get(field)!r}"
        )


@pytest.mark.regression
def test_tc_book_002_create_booking_with_required_fields_only(
    api_client: APIClient,
) -> None:
    """TC_BOOK_002: A payload without the optional field is accepted.

    TC_BOOK_002: 任意項目 additionalneeds なしでも予約が作成されることを確認する。
    """
    payload = generate_random_booking_data(with_additional_needs=False)
    response = api_client.post(BOOKING_ENDPOINT, json=payload)

    assert response.status_code == 200, (
        f"Required-fields-only payload was rejected: {response.status_code}"
    )

    body = APIClient.safe_json(response)
    validate_response_structure(body, CREATE_BOOKING_SCHEMA)
    assert body["booking"]["firstname"] == payload["firstname"]


@pytest.mark.regression
def test_tc_book_003_create_booking_with_multibyte_characters(
    api_client: APIClient,
) -> None:
    """TC_BOOK_003: Japanese characters are stored and returned without corruption.

    TC_BOOK_003: 日本語（マルチバイト文字）が文字化けせず保存されることを確認する。

    Relevant to Japanese-market products, where encoding defects are common and
    cheap to catch at the API boundary.
    日本市場向け製品では文字コード起因の不具合が発生しやすく、API 層で検出できる。
    """
    payload = generate_random_booking_data()
    payload.update({"firstname": "太郎", "lastname": "田中", "additionalneeds": "朝食付き"})

    response = api_client.post(BOOKING_ENDPOINT, json=payload)
    assert response.status_code == 200, (
        f"Multi-byte payload was rejected: {response.status_code}"
    )

    created = response.json()["booking"]
    assert created["firstname"] == "太郎", (
        f"Multi-byte first name was corrupted: {created['firstname']!r}"
    )
    assert created["lastname"] == "田中", (
        f"Multi-byte last name was corrupted: {created['lastname']!r}"
    )
    assert created["additionalneeds"] == "朝食付き", (
        f"Multi-byte free text was corrupted: {created['additionalneeds']!r}"
    )


@pytest.mark.negative
@pytest.mark.known_bug
def test_tc_book_004_create_booking_without_required_field(
    api_client: APIClient, invalid_data: Dict[str, Any]
) -> None:
    """TC_BOOK_004: A payload missing a required field must be rejected.

    TC_BOOK_004: 必須項目が欠落したデータが拒否されることを確認する。

    Expected / 期待結果:
        400 Bad Request. The API returns 500 Internal Server Error, so the test
        marks itself xfail with the defect ID rather than failing silently.
        期待値は 400。実際は 500 のため、不具合 ID を理由に xfail とする。
    """
    payload = invalid_data["missing_firstname"]
    response = api_client.post(BOOKING_ENDPOINT, json=payload)

    assert response.status_code != 200, (
        f"A payload missing 'firstname' was accepted with 200: {payload}"
    )

    if response.status_code == 500:
        pytest.xfail(
            "BUG-002: a missing required field returns 500 Internal Server Error "
            "where 400 Bad Request is expected"
        )

    assert response.status_code == 400, (
        f"Unexpected status {response.status_code} for a missing required field"
    )


@pytest.mark.smoke
def test_tc_book_005_get_booking_by_id(api_client: APIClient, booking_id: int) -> None:
    """TC_BOOK_005: An existing booking is returned with the documented structure.

    TC_BOOK_005: 既存の予約が仕様どおりの構造で取得できることを確認する。
    """
    response = api_client.get(f"{BOOKING_ENDPOINT}/{booking_id}")

    assert response.status_code == 200, (
        f"Expected 200 for booking {booking_id}, got {response.status_code}"
    )

    body = APIClient.safe_json(response)
    validate_response_structure(body, BOOKING_SCHEMA)

    # Business rule: check-out must not precede check-in / 業務ルールの確認
    dates = body["bookingdates"]
    assert dates["checkin"] <= dates["checkout"], (
        f"Invalid date range stored: {dates}"
    )


@pytest.mark.regression
def test_tc_book_006_get_all_booking_ids(api_client: APIClient) -> None:
    """TC_BOOK_006: The list endpoint returns an array of booking IDs.

    TC_BOOK_006: 一覧取得エンドポイントが予約 ID の配列を返すことを確認する。
    """
    response = api_client.get(BOOKING_ENDPOINT)

    assert response.status_code == 200, (
        f"Expected 200 from the list endpoint, got {response.status_code}"
    )

    body = APIClient.safe_json(response)
    assert isinstance(body, list) and body, "Expected a non-empty list of bookings"
    assert "bookingid" in body[0], (
        f"List items should contain 'bookingid', got {body[0]}"
    )


@pytest.mark.regression
def test_tc_book_007_filter_bookings_by_name(api_client: APIClient) -> None:
    """TC_BOOK_007: Name filters return the matching booking.

    TC_BOOK_007: 氏名によるフィルタ検索で該当予約が返ることを確認する。

    A booking is created with a distinctive name, then retrieved through the
    query parameters, which verifies the filter rather than the list endpoint.
    識別しやすい氏名で予約を作成し、クエリパラメータで取得できるか検証する。
    """
    payload = generate_random_booking_data()
    payload.update({"firstname": "Qafilter", "lastname": "Testcase"})

    created = api_client.post(BOOKING_ENDPOINT, json=payload)
    assert created.status_code == 200, "Setup failed: could not create a booking"
    created_id = created.json()["bookingid"]

    response = api_client.get(
        BOOKING_ENDPOINT, params={"firstname": "Qafilter", "lastname": "Testcase"}
    )

    assert response.status_code == 200, (
        f"Filter query returned {response.status_code}, expected 200"
    )

    returned_ids = [item["bookingid"] for item in response.json()]
    assert created_id in returned_ids, (
        f"Booking {created_id} was not returned by the name filter. "
        f"Returned IDs: {returned_ids[:20]}"
    )


@pytest.mark.negative
def test_tc_book_008_get_non_existent_booking(api_client: APIClient) -> None:
    """TC_BOOK_008: A non-existent booking ID returns 404 Not Found.

    TC_BOOK_008: 存在しない予約 ID で 404 が返ることを確認する。
    """
    response = api_client.get(f"{BOOKING_ENDPOINT}/{NON_EXISTENT_BOOKING_ID}")

    assert response.status_code == 404, (
        f"Expected 404 for ID {NON_EXISTENT_BOOKING_ID}, got {response.status_code}"
    )
