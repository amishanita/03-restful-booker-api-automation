# Workflow Diagrams / ワークフロー図

Three views of the same project: the QA process, the pytest execution flow, and the code
architecture.

同一プロジェクトの 3 つの視点: QA プロセス、pytest 実行フロー、コード構成。

---

## 1. API Testing Workflow / API テストワークフロー (8 steps)

```
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1: Read the API documentation / API 仕様の確認                 │
│  Endpoints, request bodies, status codes, auth mechanism             │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 2: Explore manually in Postman / Postman による探索的テスト     │
│  Send each request once; record what the API actually does           │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 3: Design test cases / テストケース設計                         │
│  Derived from the specification, not from observed behaviour         │
│  Assign TC_IDs, priority, positive and negative paths                │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 4: Prepare test data / テストデータ準備                         │
│  Valid payloads, invalid payloads, randomised generation             │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 5: Automate / 自動化                                            │
│  Happy paths → negative paths → authentication boundaries            │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 6: Execute / 実行                                               │
│  pytest -rxX   →   HTML report + console log as evidence             │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
                    ┌───────────────────────┐
                    │ Deviation from spec?  │
                    │  仕様との乖離あり?     │
                    └───────┬───────────┬───┘
                        YES │           │ NO
                            ▼           ▼
┌──────────────────────────────────┐  ┌────────────────────────────────┐
│  STEP 7: Report the defect       │  │  STEP 7: Record the pass       │
│  docs/known-issues.md            │  │  Attach the report as evidence │
│  Mark the test xfail with the    │  │                                │
│  defect ID so a fix flips it     │  │                                │
└───────────────┬──────────────────┘  └────────────────┬───────────────┘
                └──────────────┬───────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 8: Run in CI / CI での継続実行                                  │
│  push, pull request, nightly schedule; archive the HTML report        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. pytest Execution Flow / pytest 実行フロー (8 phases)

```
  PHASE 1  Collection / 収集
           pytest reads pytest.ini, walks testpaths, finds test_*.py
                                │
                                ▼
  PHASE 2  Session setup / セッション開始
           api_client fixture      → one requests.Session, one connection pool
                                │
                                ▼
  PHASE 3  Health check / ヘルスチェック  (autouse)
           GET /ping  ──not 201──►  pytest.exit  "API is unreachable"
                                │  201
                                ▼
  PHASE 4  Authentication / 認証
           auth_token fixture      → POST /auth  → token
           auth_headers fixture    → Cookie: token=<token>
                                │
                                ▼
  PHASE 5  Per-test setup / テストごとの準備
           booking_id fixture      → POST /booking  → a fresh booking
                                │
                                ▼
  PHASE 6  Test execution / テスト実行
           request → response → status assertion → schema validation
                              → field assertions → persistence re-check
                                │
                                ▼
  PHASE 7  Per-test teardown / テストごとの後始末
           booking_id fixture      → DELETE /booking/{id}
                                │
                                ▼
  PHASE 8  Reporting / レポート出力
           reports/pytest-html-report.html
           console summary:  passed / xfailed (known defects) / failed
```

---

## 3. Test Automation Architecture / テスト自動化アーキテクチャ (3 layers)

```
╔══════════════════════════════════════════════════════════════════════╗
║  LAYER 1: TEST LAYER / テスト層                                      ║
║  What is verified. No HTTP code lives here.                          ║
║  検証内容のみを記述し、HTTP の詳細は持たない。                        ║
║                                                                      ║
║   tests/test_auth.py            TC_AUTH_001 - TC_AUTH_006            ║
║   tests/test_booking.py         TC_BOOK_001 - TC_BOOK_008            ║
║   tests/test_update_booking.py  TC_PUT_001 - TC_PATCH_004            ║
║   tests/test_delete_booking.py  TC_DEL_001 - TC_DEL_004              ║
╚═════════════════════════════════╤════════════════════════════════════╝
                                  │  fixtures (conftest.py)
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║  LAYER 2: SUPPORT LAYER / 共通処理層                                 ║
║  How requests are sent and how responses are judged.                 ║
║  リクエスト送信とレスポンス判定の共通処理。                            ║
║                                                                      ║
║   utils/api_client.py   session, timeout, retry, safe_json           ║
║   utils/helpers.py      data generation, JSON Schema, validation     ║
║   utils/config.py       BASE_URL, credentials, endpoints (from .env) ║
╚═════════════════════════════════╤════════════════════════════════════╝
                                  │  HTTPS
                                  ▼
╔══════════════════════════════════════════════════════════════════════╗
║  LAYER 3: SYSTEM UNDER TEST / テスト対象層                           ║
║                                                                      ║
║   RESTful Booker API   https://restful-booker.herokuapp.com          ║
║   /ping   /auth   /booking   /booking/{id}                           ║
╚══════════════════════════════════════════════════════════════════════╝

Data flows down, results flow up. Changing the base URL touches one file;
changing an assertion touches one test.
データは下へ、結果は上へ流れます。URL 変更は 1 ファイル、
アサーション変更は 1 テストのみの修正で済みます。
```
