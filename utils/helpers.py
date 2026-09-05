"""
Shared helpers / 共通ヘルパー

Test data generation, JSON Schema definitions, response validation and date
formatting.

テストデータ生成、JSON Schema 定義、レスポンス検証、日付整形。
"""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from jsonschema import ValidationError, validate

from utils.config import TEST_DATA_DIR

FIRST_NAMES: List[str] = [
    "Amish", "Sakura", "Kenji", "Maria", "Hiroshi",
    "Anita", "David", "Yuki", "Priya", "Thomas",
]
LAST_NAMES: List[str] = [
    "Tamang", "Sato", "Suzuki", "Garcia", "Tanaka",
    "Gurung", "Miller", "Nakamura", "Sharma", "Brown",
]
ADDITIONAL_NEEDS: List[str] = [
    "Breakfast", "Late checkout", "Airport transfer", "Extra bed", "Non-smoking room",
]

# JSON Schema for a single booking object as returned by GET /booking/{id}.
BOOKING_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "number"},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string", "format": "date"},
                "checkout": {"type": "string", "format": "date"},
            },
        },
        "additionalneeds": {"type": "string"},
    },
}

# JSON Schema for the wrapper returned by POST /booking.
CREATE_BOOKING_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["bookingid", "booking"],
    "properties": {
        "bookingid": {"type": "integer"},
        "booking": BOOKING_SCHEMA,
    },
}

AUTH_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["token"],
    "properties": {"token": {"type": "string", "minLength": 1}},
}


def format_timestamp(value: Optional[date] = None, fmt: str = "%Y-%m-%d") -> str:
    """Format a date for the RESTful Booker `bookingdates` fields.

    Args:
        value: The date to format. Defaults to today.
        fmt: strftime pattern. The API expects ``YYYY-MM-DD``.

    Returns:
        The formatted date string.

    Example:
        >>> format_timestamp(date(2026, 4, 1))
        '2026-04-01'
    """
    target = value or date.today()
    if isinstance(target, datetime):
        target = target.date()
    return target.strftime(fmt)


def generate_random_booking_data(
    with_additional_needs: bool = True,
    stay_length_days: int = 3,
) -> Dict[str, Any]:
    """Build a valid, randomised booking payload.

    Random data keeps tests independent of each other and surfaces bugs that
    fixed fixtures hide (for example encoding problems in names).

    Args:
        with_additional_needs: Include the optional ``additionalneeds`` field.
        stay_length_days: Number of nights between check-in and check-out.

    Returns:
        A dictionary ready to be sent as the JSON body of ``POST /booking``.
    """
    checkin = date.today() + timedelta(days=random.randint(1, 60))
    checkout = checkin + timedelta(days=stay_length_days)

    payload: Dict[str, Any] = {
        "firstname": random.choice(FIRST_NAMES),
        "lastname": random.choice(LAST_NAMES),
        "totalprice": random.randint(50, 2000),
        "depositpaid": random.choice([True, False]),
        "bookingdates": {
            "checkin": format_timestamp(checkin),
            "checkout": format_timestamp(checkout),
        },
    }
    if with_additional_needs:
        payload["additionalneeds"] = random.choice(ADDITIONAL_NEEDS)
    return payload


def validate_response_structure(
    payload: Optional[Dict[str, Any]],
    schema: Dict[str, Any],
) -> bool:
    """Validate a response body against a JSON Schema.

    Args:
        payload: Parsed JSON body. ``None`` fails validation immediately.
        schema: JSON Schema to validate against.

    Returns:
        True if the payload matches the schema.

    Raises:
        AssertionError: With the schema path and message, so pytest output
            points at the exact field that broke the contract.
    """
    if payload is None:
        raise AssertionError("Response body was empty or not valid JSON")

    try:
        validate(instance=payload, schema=schema)
    except ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        raise AssertionError(
            f"Response does not match the expected schema at '{path}': {exc.message}"
        ) from exc
    return True


def load_test_data(filename: str) -> Dict[str, Any]:
    """Load a JSON file from the ``test_data`` directory.

    Args:
        filename: File name, e.g. ``booking_payload.json``.

    Returns:
        The parsed JSON content.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path: Path = TEST_DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Test data file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def auth_cookie_header(token: str) -> Dict[str, str]:
    """Build the Cookie header RESTful Booker requires for write operations.

    The API accepts ``Cookie: token=<token>``. The documented Basic Auth
    alternative is unreliable on the public instance, so the suite uses the
    cookie form everywhere.
    """
    return {"Cookie": f"token={token}"}
