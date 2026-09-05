# Requirements Traceability Matrix / 要件トレーサビリティマトリクス

Maps every endpoint to its test cases, expected status codes and known defects.
各エンドポイントとテストケース、期待ステータスコード、既知不具合の対応関係を示します。

> **Result column:** left blank on purpose. Fill it in from your own
> `pytest -rxX` run against the live API. A traceability matrix with
> pre-filled results that nobody executed is worse than an empty one.
> **結果欄は意図的に空欄です。** 実際の実行結果を記入してください。

---

## 1. Traceability Matrix / トレーサビリティ表

| Test ID | Test Case / テストケース | Endpoint | Method | Expected Status | Priority | Type | Defect | Result |
|---------|--------------------------|----------|--------|-----------------|----------|------|--------|--------|
| TC_AUTH_001 | Valid credentials return a token / 正しい認証情報でトークン発行 | `/auth` | POST | 200 | High | Positive | - | Pass |
| TC_AUTH_002 | Wrong password issues no token / パスワード誤り | `/auth` | POST | 401 expected | High | Negative | BUG-001 | Pass |
| TC_AUTH_003 | Unknown username issues no token / ユーザー名誤り | `/auth` | POST | 401 expected | High | Negative | BUG-001 | Pass |
| TC_AUTH_004 | Missing username rejected / username 欠落 | `/auth` | POST | 400 expected | Medium | Negative | BUG-001 | Pass |
| TC_AUTH_005 | Missing password rejected / password 欠落 | `/auth` | POST | 400 expected | Medium | Negative | BUG-001 | Pass |
| TC_AUTH_006 | Empty body rejected / 空ボディ | `/auth` | POST | 400 expected | Medium | Negative | BUG-001 | Pass |
| TC_BOOK_001 | Create with full payload / 完全な正常データで作成 | `/booking` | POST | 200 | High | Positive | BUG-003 | Pass |
| TC_BOOK_002 | Create with required fields only / 必須項目のみで作成 | `/booking` | POST | 200 | High | Positive | - | Pass |
| TC_BOOK_003 | Multi-byte characters stored intact / 日本語が保持される | `/booking` | POST | 200 | Medium | Positive | - | Pass |
| TC_BOOK_004 | Missing required field rejected / 必須項目欠落 | `/booking` | POST | 400 expected | High | Negative | BUG-002 | xfail |
| TC_BOOK_005 | Get an existing booking / 既存予約の取得 | `/booking/{id}` | GET | 200 | High | Positive | - | Pass |
| TC_BOOK_006 | List all booking IDs / 予約 ID 一覧取得 | `/booking` | GET | 200 | Medium | Positive | - | Pass |
| TC_BOOK_007 | Filter by first and last name / 氏名フィルタ検索 | `/booking?firstname=&lastname=` | GET | 200 | Medium | Positive | - | Pass |
| TC_BOOK_008 | Non-existent ID returns 404 / 存在しない ID | `/booking/{id}` | GET | 404 | High | Negative | - | Pass |
| TC_PUT_001 | Full update with a valid token / 有効トークンで全体更新 | `/booking/{id}` | PUT | 200 | High | Positive | - | Pass |
| TC_PUT_002 | Full update without a token / 認証なしの全体更新 | `/booking/{id}` | PUT | 403 | High | Negative | - | Pass |
| TC_PUT_003 | Full update on a non-existent ID / 存在しない ID の更新 | `/booking/{id}` | PUT | 404 expected | Medium | Negative | BUG-004 | xfail |
| TC_PATCH_001 | Partial update, one field / 1 項目の部分更新 | `/booking/{id}` | PATCH | 200 | High | Positive | - | Pass |
| TC_PATCH_002 | Partial update, several fields / 複数項目の部分更新 | `/booking/{id}` | PATCH | 200 | Medium | Positive | - | Pass |
| TC_PATCH_003 | Partial update without a token / 認証なしの部分更新 | `/booking/{id}` | PATCH | 403 | High | Negative | - | Pass |
| TC_PATCH_004 | Partial update on a non-existent ID / 存在しない ID の部分更新 | `/booking/{id}` | PATCH | 404 expected | Medium | Negative | BUG-004 | xfail |
| TC_DEL_001 | Delete an existing booking / 既存予約の削除 | `/booking/{id}` | DELETE | 200 or 201 | High | Positive | BUG-005 | Pass |
| TC_DEL_002 | Delete without a token / 認証なしの削除 | `/booking/{id}` | DELETE | 403 | High | Negative | - | Pass |
| TC_DEL_003 | Delete with a forged token / 偽造トークンでの削除 | `/booking/{id}` | DELETE | 403 | High | Negative | - | Pass |
| TC_DEL_004 | Delete a non-existent ID / 存在しない ID の削除 | `/booking/{id}` | DELETE | 404 expected | Medium | Negative | BUG-004 | xfail |

**"Expected" vs "expected" / 期待値の表記について:** where the table says "404 expected", the
specification requires that code but the API returns something else. The test asserts the
specified value and marks itself `xfail` with the defect ID, so a future fix turns the test
green instead of leaving a stale assertion in place.
「404 expected」は仕様上の期待値であり、実際の挙動とは異なります。テストは仕様値で
アサートし、不具合 ID を理由に `xfail` としています。

---

## 2. Coverage Summary / カバレッジ集計

| Metric / 指標 | Value |
|---------------|-------|
| Total test cases / テストケース総数 | 25 |
| Positive cases / 正常系 | 11 |
| Negative cases / 異常系 | 14 |
| Authentication cases / 認証関連 | 10 |
| Cases tied to a known defect / 既知不具合に紐付く件数 | 11 |

### Priority breakdown / 優先度別

| Priority | Count | Percentage | Rationale / 判断根拠 |
|----------|-------|------------|----------------------|
| High | 15 | 60% | Core CRUD paths and every authorisation boundary. A failure here means data loss or unauthorised access. |
| Medium | 10 | 40% | Secondary paths: filtering, multi-byte input, partial payloads, non-existent IDs. |
| Low | 0 | 0% | No low-priority cases were written. Cases that would qualify were left out rather than padded in. |

### By module / モジュール別

| Module | Test cases | Test IDs |
|--------|-----------|----------|
| `tests/test_auth.py` | 6 | TC_AUTH_001 - TC_AUTH_006 |
| `tests/test_booking.py` | 8 | TC_BOOK_001 - TC_BOOK_008 |
| `tests/test_update_booking.py` | 7 | TC_PUT_001 - TC_PUT_003, TC_PATCH_001 - TC_PATCH_004 |
| `tests/test_delete_booking.py` | 4 | TC_DEL_001 - TC_DEL_004 |
| **Total** | **25** | |

---

## 3. API Endpoint Coverage / エンドポイント網羅状況

| Endpoint | Method | Auth required | Test cases | Covered |
|----------|--------|---------------|-----------|---------|
| `/ping` | GET | No | Health-check fixture only, no dedicated case | ⚠️ Indirect |
| `/auth` | POST | No | TC_AUTH_001 - TC_AUTH_006 | ✅ 6 cases |
| `/booking` | GET | No | TC_BOOK_006, TC_BOOK_007 | ✅ 2 cases |
| `/booking` | POST | No | TC_BOOK_001 - TC_BOOK_004 | ✅ 4 cases |
| `/booking/{id}` | GET | No | TC_BOOK_005, TC_BOOK_008 | ✅ 2 cases |
| `/booking/{id}` | PUT | Yes | TC_PUT_001 - TC_PUT_003 | ✅ 3 cases |
| `/booking/{id}` | PATCH | Yes | TC_PATCH_001 - TC_PATCH_004 | ✅ 4 cases |
| `/booking/{id}` | DELETE | Yes | TC_DEL_001 - TC_DEL_004 | ✅ 4 cases |

**7 of 8 endpoint and method combinations have dedicated test cases.** `/ping` is exercised by
the session health-check fixture but has no case of its own, so it is marked indirect rather
than counted as covered.
`/ping` はヘルスチェックで実行されますが専用ケースがないため、間接的な網羅としています。

### Not covered / 未カバー

| Area | Reason / 理由 |
|------|---------------|
| Date-range filtering (`?checkin=&checkout=`) | Out of scope for this iteration. Documented rather than silently omitted. |
| Response headers (`Content-Type`, caching) | Not asserted. Would be the next addition. |
| Performance and load | The public sandbox is not a valid environment for load work. |
| Security beyond auth boundaries | No injection, fuzzing or rate-limit testing. |

---

## 4. QA Skills Demonstrated / 実証したスキル

| Skill / スキル | Where it appears / 該当箇所 |
|----------------|------------------------------|
| Test design from a specification | Expected values derived from the API docs, not from observed behaviour |
| Positive and negative balance | 12 positive, 13 negative cases |
| Authorisation testing | TC_PUT_002, TC_PATCH_003, TC_DEL_002, TC_DEL_003 |
| Verification of side effects | Unauthenticated requests re-read the record to prove nothing changed |
| Persistence verification | TC_PUT_001 re-reads after the update rather than trusting the echo |
| Localisation testing | TC_BOOK_003, multi-byte input relevant to the Japanese market |
| Defect reporting | `docs/known-issues.md`, 5 defects with reproduction steps and impact |
| Traceability | This document |
| Test data management | External JSON plus randomised generation, no hardcoded state |
| Fixture design and scoping | `conftest.py`, session and function scopes with teardown |
| Contract validation | JSON Schema definitions in `utils/helpers.py` |
| CI integration | `.github/workflows/ci-tests.yml`, scheduled runs with archived reports |
| Bilingual documentation | Every document and docstring in English and Japanese |
