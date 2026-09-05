# Known Issues / 既知不具合一覧

Defects found in the RESTful Booker API during exploratory and automated testing.
RESTful Booker API に対する探索的テストおよび自動テストで検出した不具合の一覧です。

**Status: not yet verified against the live API.** These deviations are documented in the API's
public issue history and are asserted by the test suite, but the evidence column below is empty
until you run the suite yourself and capture the responses.
**現状、実 API での検証は未実施です。** 実行後にエビデンスを追記してください。

RESTful Booker is a practice API that intentionally ships with defects. The value of this
document is not the defects themselves but the record of how they were found, isolated and
handled in the automation: each one is asserted against the *expected* behaviour and marked
`xfail` or scoped so that a future fix turns the test green instead of leaving it silently wrong.

| ID | Title | Severity | Priority | Status | Reproduced | Evidence |
|----|-------|----------|----------|--------|------------|----------|
| BUG-001 | Invalid credentials return 200 OK instead of 401 Unauthorized | Medium | High | Open | 2026-09-05 | `bug-001-curl.txt` |
| BUG-002 | Missing required fields return 500 instead of 400 Bad Request | High | High | Open | 2026-09-05 | `bug-002-curl.txt` |
| BUG-003 | Successful booking creation returns 200 instead of 201 Created | Low | Low | Open | 2026-09-05 | `bug-003-curl.txt` |
| BUG-004 | Write operations on a non-existent ID return 405 instead of 404 | Medium | Medium | Open | 2026-09-05 | `bug-004-curl.txt` |
| BUG-005 | Successful DELETE returns 201 Created | Low | Low | Open | 2026-09-05 | `bug-005-curl.txt` |

---

## BUG-001: Invalid credentials return 200 OK

- **Endpoint:** `POST /auth`
- **Severity:** Medium **Priority:** High
- **Environment:** https://restful-booker.herokuapp.com, tested via pytest + requests

**Steps to reproduce**

1. `POST /auth` with `{"username": "admin", "password": "wrong_password"}`

**Expected:** `401 Unauthorized` with an error body.
**Actual:** `200 OK` with `{"reason": "Bad credentials"}`.

**Impact:** Clients that branch on the status code treat a failed login as a success. Monitoring
and WAF rules that count 401s cannot detect credential stuffing against this endpoint.

**Covered by:** `tests/test_auth.py::test_invalid_auth`. The test asserts the security-relevant
property (no token is issued) rather than the status code, so it stays meaningful while the
defect is open.

**日本語:** 誤った認証情報でも HTTP 200 が返る。401 Unauthorized が期待値。ステータスコードで
分岐するクライアントは認証失敗を成功と誤認する。

---

## BUG-002: Missing required fields return 500

- **Endpoint:** `POST /booking`
- **Severity:** High **Priority:** High

**Steps to reproduce**

1. `POST /booking` with a payload that omits `firstname`.

**Expected:** `400 Bad Request` naming the missing field.
**Actual:** `500 Internal Server Error` with no useful body.

**Impact:** A client input error is reported as a server fault. It pollutes error dashboards,
triggers false alerts, and gives the caller no way to correct the request.

**Covered by:** `tests/test_booking.py::test_create_booking_invalid_data` (xfail with reason).

**日本語:** 必須項目が欠けた場合に 500 が返る。本来はクライアント起因のため 400 が正しい。
サーバー障害としてアラートが発火し、原因調査のノイズになる。

---

## BUG-003: Booking creation returns 200 instead of 201

- **Endpoint:** `POST /booking`
- **Severity:** Low **Priority:** Low

**Expected:** `201 Created`, ideally with a `Location` header.
**Actual:** `200 OK`.

**Impact:** Cosmetic and conventional. Clients that follow REST conventions cannot distinguish
"created" from "handled".

**日本語:** リソース作成時に 201 ではなく 200 が返る。REST の慣例に反する。

---

## BUG-004: PUT / PATCH / DELETE on a non-existent ID return 405

- **Endpoints:** `PUT /booking/{id}`, `PATCH /booking/{id}`, `DELETE /booking/{id}`
- **Severity:** Medium **Priority:** Medium

**Steps to reproduce**

1. Obtain a token via `POST /auth`.
2. `DELETE /booking/99999999` with `Cookie: token=<token>`.

**Expected:** `404 Not Found`.
**Actual:** `405 Method Not Allowed`.

**Impact:** 405 means "this verb is not supported on this resource", which is untrue: the verb
works on existing IDs. Client retry logic that treats 405 as permanent will stop retrying valid
requests.

**Covered by:** `test_full_update_invalid_id`, `test_partial_update_invalid_id`,
`test_delete_invalid_id`.

**日本語:** 存在しない ID への更新・削除で 405 が返る。期待値は 404。405 は「メソッド自体が
非対応」を意味するため、クライアントのリトライ制御が誤動作する。

---

## BUG-005: Successful DELETE returns 201 Created

- **Endpoint:** `DELETE /booking/{id}`
- **Severity:** Low **Priority:** Low

**Expected:** `200 OK` or `204 No Content`.
**Actual:** `201 Created`.

**Impact:** A delete that reports "Created" is misleading in logs and in any client that maps
status codes to user-facing messages.

**日本語:** 削除成功時に 201 Created が返る。204 No Content もしくは 200 が妥当。

---

---

## To confirm on the first live run / 初回実行時に確認する項目

These are open questions, not defects. Resolve them from your own run and either promote them to
a numbered defect or delete them.
以下は不具合ではなく未確認事項です。実行結果に基づき、不具合として起票するか削除してください。

| Item | Question | Affects |
|------|----------|---------|
| Missing credential fields | Does `POST /auth` return 200 with a `reason`, or 400 Bad Request, when `username` or `password` is absent? | TC_AUTH_004, TC_AUTH_005, TC_AUTH_006 (resolved 2026-09-05: returns 200 OK, same defect as BUG-001) |
| Type validation | Is `totalprice` accepted as a string? `test_data/invalid_data.json` holds the payload; no test currently sends it. | Not covered |
| Date validation | Is `checkout` earlier than `checkin` accepted? Payload exists in `invalid_data.json`; no test sends it. | Not covered |

### Evidence / エビデンス

Every defect below needs one captured request and response before this file is credible.
各不具合には、リクエストとレスポンスの実キャプチャが必要です。

```bash
mkdir -p reports/evidence

# BUG-001  invalid credentials
curl -i -X POST https://restful-booker.herokuapp.com/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong_password"}' \
  > reports/evidence/bug-001-curl.txt 2>&1

# BUG-002  missing required field
curl -i -X POST https://restful-booker.herokuapp.com/booking \
  -H "Content-Type: application/json" \
  -d '{"lastname":"Tamang","totalprice":500,"depositpaid":true,"bookingdates":{"checkin":"2026-10-01","checkout":"2026-10-05"}}' \
  > reports/evidence/bug-002-curl.txt 2>&1

# BUG-003  creation returns 200, not 201
curl -i -X POST https://restful-booker.herokuapp.com/booking \
  -H "Content-Type: application/json" \
  -d '{"firstname":"Amish","lastname":"Tamang","totalprice":850,"depositpaid":true,"bookingdates":{"checkin":"2026-10-01","checkout":"2026-10-05"},"additionalneeds":"Breakfast"}' \
  > reports/evidence/bug-003-curl.txt 2>&1

# Token needed for BUG-004 and BUG-005
TOKEN=$(curl -s -X POST https://restful-booker.herokuapp.com/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' | sed 's/.*"token"[ :"]*\([^"]*\).*/\1/')
echo "token=$TOKEN"

# BUG-004  delete a non-existent ID
curl -i -X DELETE https://restful-booker.herokuapp.com/booking/99999999 \
  -H "Content-Type: application/json" -H "Cookie: token=$TOKEN" \
  > reports/evidence/bug-004-curl.txt 2>&1

# BUG-005  successful delete returns 201
BID=$(curl -s -X POST https://restful-booker.herokuapp.com/booking \
  -H "Content-Type: application/json" \
  -d '{"firstname":"Evidence","lastname":"Capture","totalprice":100,"depositpaid":true,"bookingdates":{"checkin":"2026-10-01","checkout":"2026-10-02"}}' \
  | sed 's/.*"bookingid"[ :]*\([0-9]*\).*/\1/')
curl -i -X DELETE "https://restful-booker.herokuapp.com/booking/$BID" \
  -H "Content-Type: application/json" -H "Cookie: token=$TOKEN" \
  > reports/evidence/bug-005-curl.txt 2>&1
```

After capturing, update the **Verified locally** column to `Yes (YYYY-MM-DD)` for each defect that
reproduced, and correct or delete any that did not.
再現した不具合は「Yes（日付）」に更新し、再現しなかったものは修正または削除してください。
