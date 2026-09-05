"""
Central configuration / 設定の一元管理

Values are read from environment variables first (loaded from a local `.env`
file when present), with the public RESTful Booker demo settings as fallback.

環境変数を優先して読み込み（`.env` があれば自動的に反映）、未設定の場合は
RESTful Booker の公開デモ設定を既定値として使用します。

Note on naming: the credential variables are prefixed `RB_` because a bare
`USERNAME` collides with an operating-system variable on Windows, which would
silently send the wrong value to the API.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# override=False means a real environment variable (for example one set in CI)
# always takes precedence over the .env file.
load_dotenv(PROJECT_ROOT / ".env", override=False)

# --- Target system / テスト対象 -------------------------------------------
BASE_URL: str = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")

# --- Credentials / 認証情報 -----------------------------------------------
USERNAME: str = os.getenv("RB_USERNAME", "admin")
PASSWORD: str = os.getenv("RB_PASSWORD", "password123")

# --- Request behaviour / リクエスト設定 ------------------------------------
TIMEOUT: int = int(os.getenv("TIMEOUT", "15"))
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))

# --- Endpoints / エンドポイント --------------------------------------------
AUTH_ENDPOINT: str = "/auth"
BOOKING_ENDPOINT: str = "/booking"
PING_ENDPOINT: str = "/ping"

# --- Paths / パス ----------------------------------------------------------
TEST_DATA_DIR: Path = PROJECT_ROOT / "test_data"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"

# An ID that is very unlikely to exist, used by negative tests.
# 存在しない想定の ID（異常系テスト用）
NON_EXISTENT_BOOKING_ID: int = int(os.getenv("NON_EXISTENT_BOOKING_ID", "99999999"))
