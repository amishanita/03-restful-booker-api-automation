# RESTful Booker API Test Automation<br>RESTful Booker API テスト自動化

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-7.x-green)](https://docs.pytest.org/)
[![requests](https://img.shields.io/badge/requests-2.x-orange)](https://requests.readthedocs.io/)
[![Test cases](https://img.shields.io/badge/test%20cases-25-success)](docs/RTM-traceability-matrix.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#-license--ライセンス)

API test automation for the RESTful Booker booking service, built with Python and pytest.
25 traceable test cases, a requirements traceability matrix, five documented defects and a CI
workflow.

RESTful Booker を対象とした、Python と pytest による API テスト自動化プロジェクトです。
追跡可能な 25 件のテストケース、要件トレーサビリティマトリクス、5 件の不具合票、
CI ワークフローを含みます。

---

## 📖 Overview / 概要

**EN:** RESTful Booker ships with deliberate defects. Instead of asserting whatever the API
happens to do, this suite asserts the **specified** behaviour and records each deviation in
[`docs/known-issues.md`](docs/known-issues.md). Tests that hit a known defect are marked `xfail`
with the defect ID, so a fix on the API side turns the test green rather than leaving a stale
assertion in place.

**JA:** RESTful Booker は学習用に意図的な不具合を含む API です。本プロジェクトでは実際の挙動
ではなく**仕様上の期待値**でアサートし、乖離はすべて不具合票として記録しています。既知不具合
に該当するテストは不具合 ID を理由に `xfail` としているため、API が修正されればテストが自動的
に成功へ転じ、古いアサーションが残り続けることを防げます。

---

## 🎯 Objectives / 目的

| # | Objective | 目的 |
|---|-----------|------|
| 1 | Verify authentication, authorisation and the full booking CRUD lifecycle | 認証・認可および予約 CRUD の全ライフサイクルを検証する |
| 2 | Cover negative paths as seriously as happy paths | 異常系を正常系と同等の重要度で扱う |
| 3 | Trace every case to an endpoint, an expected status code and a defect | 全ケースをエンドポイント・期待値・不具合と対応付ける |
| 4 | Keep the framework maintainable: one client, schema validation, no duplicated request code | クライアントを一元化し、保守しやすい構成を維持する |
| 5 | Produce evidence a reviewer can verify in five minutes | 5 分で確認できるエビデンスを残す |

---

## 🌐 Application Under Test / テスト対象

**Base URL:** `https://restful-booker.herokuapp.com`
**Credentials / 認証情報:** `admin` / `password123` (public demo credentials published by the
API author / API 作者が公開しているデモ用アカウント)

| Method | Endpoint | Purpose / 用途 | Auth / 認証 | Success |
|--------|----------|----------------|-------------|---------|
| `GET` | `/ping` | Health check / ヘルスチェック | No / 不要 | 201 |
| `POST` | `/auth` | Create token / トークン発行 | No / 不要 | 200 |
| `GET` | `/booking` | List IDs, name filters / ID 一覧、氏名フィルタ | No / 不要 | 200 |
| `GET` | `/booking/{id}` | Get one booking / 予約詳細取得 | No / 不要 | 200 |
| `POST` | `/booking` | Create / 予約作成 | No / 不要 | 200 |
| `PUT` | `/booking/{id}` | Replace / 全体更新 | Yes / 必要 | 200 |
| `PATCH` | `/booking/{id}` | Update fields / 部分更新 | Yes / 必要 | 200 |
| `DELETE` | `/booking/{id}` | Delete / 削除 | Yes / 必要 | 201 |

**EN:** Authentication uses a cookie: `Cookie: token=<token>`. The documented Basic Auth
alternative is unreliable on the public instance, so the suite uses the cookie form throughout.

**JA:** 認証は Cookie ヘッダー（`Cookie: token=<token>`）で行います。ドキュメント記載の Basic
認証は公開インスタンスでは安定しないため、Cookie 方式に統一しています。

---

## 🔄 Testing Approach / テスト方針

```
   Read the API docs / API 仕様の確認
           │
           ▼
   Explore in Postman / Postman で探索的テスト  ──►  record actual behaviour
           │
           ▼
   Design cases from the spec / 仕様からケース設計 (TC_ID, priority)
           │
           ▼
   Automate / 自動化：happy → negative → auth boundaries
           │
           ▼
   Execute / 実行： pytest -rxX  →  HTML report + console log
           │
           ▼
   Deviation? / 乖離あり？ ──yes──►  docs/known-issues.md + xfail with defect ID
           │
           no
           ▼
   CI on push, pull request and nightly / push・PR・毎晩の定期実行
```

Full diagrams, including the pytest execution flow and the three-layer architecture, are in
[`docs/workflow-diagram.md`](docs/workflow-diagram.md).
pytest 実行フローと 3 層アーキテクチャの詳細図は同ファイルを参照してください。

**Three design principles / 設計の柱**

| Principle | 内容 |
|-----------|------|
| Assert the property, not the accident | 誤った認証情報では「トークンが発行されないこと」が本質。ステータスコードの乖離は別途不具合として管理する |
| Prove side effects, not just responses | 認証なしのリクエスト後にデータを再取得し変更がないことを確認。更新後も再取得して永続化を確認する |
| Fail fast on infrastructure | API 停止時は 25 件の失敗ではなく 1 件の明確なメッセージで終了する |

---

## ✅ Test Coverage / テストカバレッジ

**25 test cases across 4 modules / 4 モジュール・25 ケース。** Full traceability in
[`docs/RTM-traceability-matrix.md`](docs/RTM-traceability-matrix.md).

| Module | Cases | Test IDs | Focus / 対象 |
|--------|-------|----------|--------------|
| `test_auth.py` | 6 | TC_AUTH_001 - 006 | Token issuance, wrong credentials, missing fields / トークン発行、認証情報誤り、項目欠落 |
| `test_booking.py` | 8 | TC_BOOK_001 - 008 | Create, read, filter, multi-byte input, invalid payload / 作成、取得、フィルタ、日本語入力、異常データ |
| `test_update_booking.py` | 7 | TC_PUT_001 - 003, TC_PATCH_001 - 004 | Full and partial update, auth boundaries / 全体更新・部分更新、認証境界 |
| `test_delete_booking.py` | 4 | TC_DEL_001 - 004 | Delete, no token, forged token, missing ID / 削除、認証なし、偽造トークン、存在しない ID |
| **Total / 合計** | **25** | | |

| Split / 区分 | Count |
|--------------|-------|
| Positive / 正常系 | 11 |
| Negative / 異常系 | 14 |
| High priority / 優先度 High | 15 |
| Medium priority / 優先度 Medium | 10 |
| Tied to a known defect / 既知不具合に紐付く件数 | 11 |

### Markers / マーカー

| Marker | Purpose / 用途 | Command |
|--------|----------------|---------|
| `smoke` | Minimum viable check / 最小限の確認 | `pytest -m smoke` |
| `regression` | Full functional coverage / 機能網羅 | `pytest -m regression` |
| `negative` | Invalid input and error handling / 異常系 | `pytest -m negative` |
| `auth` | Authentication and authorisation / 認証・認可 | `pytest -m auth` |
| `crud` | Create, read, update, delete / CRUD 全般 | `pytest -m crud` |
| `known_bug` | Tests tied to a documented defect / 既知不具合 | `pytest -m known_bug -rxX` |

---

## 🛠 Tools and Technologies / 使用技術

| Tool | Version | Why it is here / 採用理由 |
|------|---------|---------------------------|
| Python | 3.11+ (run on 3.14.7) | Test language / テスト実装言語 |
| pytest | 7.x+ (run on 9.1.1) | Runner, fixtures, markers, xfail handling / 実行基盤、フィクスチャ、xfail 制御 |
| requests | 2.x | HTTP client, shared session and retry policy / セッション共有とリトライ制御 |
| pytest-html | 3.x | Self-contained HTML report as evidence / 単一ファイルの HTML レポート |
| jsonschema | 4.x | Contract validation of response bodies / レスポンス構造の契約検証 |
| python-dotenv | 1.x | Configuration without hardcoded credentials / 認証情報を埋め込まない設定管理 |
| Postman | 11.x | Manual and exploratory testing / 手動・探索的テスト |
| Newman | 6.x | Collection execution from the CLI / CLI でのコレクション実行 |
| GitHub Actions | - | Push, pull request and nightly runs / push・PR・定期実行 |

---

## 📁 Project Structure / ディレクトリ構成

```
restful-booker-api-portfolio/
├── .github/
│   └── workflows/
│       └── ci-tests.yml                # CI: push, PR, nightly / push・PR・毎晩
├── docs/
│   ├── RTM-traceability-matrix.md      # 25 cases → endpoint → status → defect
│   ├── workflow-diagram.md             # 3 ASCII diagrams / ASCII 図 3 種
│   └── known-issues.md                 # 5 documented defects / 不具合票 5 件
├── postman/
│   ├── RESTful_Booker_API.postman_collection.json
│   └── environment.json
├── reports/
│   └── .gitkeep                        # HTML reports / レポート出力先
├── test_data/
│   ├── booking_payload.json            # Valid payload / 正常系データ
│   ├── invalid_data.json               # Invalid payloads / 異常系データ
│   └── expected_data.json              # Expected codes and shapes / 期待値
├── tests/
│   ├── test_auth.py                    # 6 cases / 6 ケース
│   ├── test_booking.py                 # 8 cases / 8 ケース
│   ├── test_update_booking.py          # 7 cases / 7 ケース
│   └── test_delete_booking.py          # 4 cases / 4 ケース
├── utils/
│   ├── api_client.py                   # HTTP wrapper / HTTP ラッパー
│   ├── config.py                       # Environment-driven config / 設定
│   └── helpers.py                      # Data, schemas, validation / データ・スキーマ
├── .env.example
├── .gitignore
├── conftest.py                         # Fixtures / フィクスチャ
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## 🧪 Manual Testing / 手動テスト

**EN:** The Postman collection covers the same ground as the automated suite. Import the
collection and the environment, run "Auth - Create Token (valid)" first so the token is stored
in a collection variable, then run the rest.

**JA:** Postman コレクションは自動テストと同じ範囲を網羅しています。コレクションと環境を
インポートし、最初に「Auth - Create Token (valid)」を実行するとトークンが変数に保存され、
以降のリクエストで自動的に利用されます。

```bash
npm install -g newman newman-reporter-htmlextra

newman run postman/RESTful_Booker_API.postman_collection.json \
  -e postman/environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export reports/newman-report.html
```

---

## 🚀 Installation / セットアップ

**Prerequisites / 前提:** Python 3.11 or later, pip, git

```bash
# 1. Clone / クローン
git clone https://github.com/amishanita/restful-booker-api-portfolio.git
cd restful-booker-api-portfolio

# 2. Virtual environment / 仮想環境
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# 3. Dependencies / 依存パッケージ
pip install -r requirements.txt

# 4. Configuration (optional) / 設定（任意）
cp .env.example .env

# 5. Confirm the API is reachable / 疎通確認
curl -i https://restful-booker.herokuapp.com/ping   # expect 201 Created
```

---

## ▶️ Running Tests / テスト実行

```bash
# All 25 cases, with reasons for expected failures / 全 25 ケース
pytest -rxX

# Smoke only / スモークのみ
pytest -m smoke

# Negative paths only / 異常系のみ
pytest -m negative

# One module / モジュール単位
pytest tests/test_auth.py

# One test case / ケース単体
pytest tests/test_booking.py::test_tc_book_001_create_booking_with_full_payload

# Verbose, live logs, stop at first failure / 詳細ログ、最初の失敗で停止
pytest -v -x --log-cli-level=INFO
```

The HTML report is written to `reports/pytest-html-report.html` on every run.
HTML レポートは実行ごとに同パスへ出力されます。

---

## 📊 Test Results / テスト結果

Executed against the live API on 2026-09-05. Log: `reports/evidence/pytest-run.log`.
2026-09-05 に実 API に対して実行しました。ログは同パスを参照してください。

| Field | Value |
|-------|-------|
| Run date / 実行日 | 2026-09-05 15:39 JST |
| OS | macOS 15.7.9 |
| Python | 3.14.7 |
| pytest | 9.1.1 |
| Target / 対象 | https://restful-booker.herokuapp.com |

| Module | Cases / ケース | Passed / 成功 | xfail (known defect / 既知不具合) | Failed / 失敗 |
|--------|----------------|---------------|-----------------------------------|---------------|
| `test_auth.py` | 6 | 6 | 0 | 0 |
| `test_booking.py` | 8 | 7 | 1 | 0 |
| `test_update_booking.py` | 7 | 5 | 2 | 0 |
| `test_delete_booking.py` | 4 | 3 | 1 | 0 |
| **Total / 合計** | **25** | **21** | **4** | **0** |

| Metric / 指標 | Value |
|---------------|-------|
| Unexpected failures / 想定外の失敗 | 0 |
| Defects documented and reproduced / 文書化・再現済み不具合 | 5 |
| Endpoint and method combinations with dedicated cases / 専用ケースのある組み合わせ | 7 of 8 |
| Execution time / 実行時間 | 11.55 s |

**The four xfail cases / xfail の内訳:** TC_BOOK_004 (BUG-002, 500 instead of 400) and
TC_PUT_003, TC_PATCH_004, TC_DEL_004 (BUG-004, 405 instead of 404). Each asserted the specified
behaviour, the API deviated, and the deviation is recorded as a defect with a captured response
in `reports/evidence/`. A fix on the API side would turn these green.
いずれも仕様どおりにアサートした結果 API 側が乖離したケースで、実レスポンスを取得のうえ
不具合として起票済みです。

The suite was also re-run on pytest 9.1.1 and Python 3.14.7, newer than the versions it was
written against, with identical results.
本スイートは開発時より新しい pytest 9.1.1 / Python 3.14.7 でも同一の結果となりました。

---

## 📸 Evidence / エビデンス

Captured during the 2026-09-05 run. Every defect below is backed by a real response.
2026-09-05 の実行時に取得したものです。各不具合は実レスポンスに基づいています。

| Artefact / 成果物 | Path | How to produce it / 取得方法 |
|-------------------|------|------------------------------|
| Console log / コンソールログ | `reports/evidence/pytest-run.log` | Full run with OS, Python version and date |
| HTML report / HTML レポート | `reports/pytest-html-report.html` | Per-test results, durations, xfail reasons |
| Terminal screenshot / スクリーンショット | `reports/screenshots/01-pytest-run.png` | All 25 cases with the summary line |
| BUG-001 | `reports/evidence/bug-001-curl.txt` | 200 OK for invalid credentials |
| BUG-002 | `reports/evidence/bug-002-curl.txt` | 500 for a missing required field |
| BUG-003 | `reports/evidence/bug-003-curl.txt` | 200 on resource creation |
| BUG-004 | `reports/evidence/bug-004-curl.txt` | 405 for a non-existent ID |
| BUG-005 | `reports/evidence/bug-005-curl.txt` | 201 on successful delete |

`.gitignore` commits `reports/evidence/` and `reports/screenshots/` while ignoring the
regenerated HTML report.

---

## 💡 Key QA Skills / 実証したスキル

**Technical / 技術**

- [x] REST API testing across all HTTP methods, status code and body assertions / 全メソッドの検証
- [x] Authentication and authorisation testing, including forged tokens / 偽造トークンを含む認証テスト
- [x] Verification of side effects, not just response payloads / 副作用の検証
- [x] Contract validation with JSON Schema / JSON Schema による契約検証
- [x] Test data management: external JSON plus randomised generation / テストデータ管理
- [x] Fixture design and scoping, setup and teardown / フィクスチャ設計とスコープ管理
- [x] Python: PEP 8, type hints, bilingual docstrings, error handling / Python 実装品質

**Documentation / ドキュメント**

- [x] Test case design with traceable IDs and priority / TC_ID と優先度を持つ設計
- [x] Requirements traceability matrix / 要件トレーサビリティマトリクス
- [x] Defect reporting with steps, expected vs actual, severity and impact / 不具合報告
- [x] Workflow and architecture diagrams / ワークフロー図・アーキテクチャ図
- [x] Bilingual technical documentation / 日英併記の技術ドキュメント

**DevOps**

- [x] GitHub Actions workflow with scheduled runs / 定期実行の CI
- [x] Artifact upload and retention / レポートのアーティファクト保存
- [x] Environment-driven configuration, no secrets in the repository / 認証情報を含めない設定
- [x] Postman and Newman for CLI-driven runs / CLI 実行

---

## ⚠️ Limitations / 制約事項

| # | Limitation | 制約 |
|---|------------|------|
| 1 | The target is a shared public sandbox that resets every 10 minutes and sleeps under low traffic. A reset mid-run can cause a false failure. Rerun before investigating. | 対象は共有の公開サンドボックス。10 分ごとにリセットされ、実行中のリセットで偽陽性が発生しうる |
| 2 | No performance or load testing. The public host is not a valid environment for it. | 性能・負荷テストは対象外 |
| 3 | No security testing beyond authorisation boundaries. No injection, fuzzing or rate limits. | 認証境界を超えるセキュリティテストは未実施 |
| 4 | Single environment. No staging or production separation to exercise. | 単一環境のみ |
| 5 | Some negative cases accept a range of status codes where the API's behaviour is a documented defect. Each is tied to a defect ID. | 一部の異常系は複数コードを許容（すべて不具合 ID に紐付け） |
| 6 | No mocking layer. A network outage stops the run; the health check makes that obvious. | モック層なし |
| 7 | Date-range filtering and response header validation are not covered. Documented in the RTM rather than silently omitted. | 日付範囲フィルタとヘッダー検証は未カバー（RTM に明記） |

---

## 🏁 Conclusion / まとめ

**EN:** The suite covers seven of eight endpoint and method combinations with 25 traceable test
cases, a requirements traceability matrix, five documented defects and a CI workflow. The part
worth reviewing is the handling of deviations: each is asserted against the specification, tied
to a defect ID, and marked so that a fix on the API side turns the test green.

**JA:** 8 通りのエンドポイント・メソッドのうち 7 通りを、25 件の追跡可能なテストケースで検証
しています。要件トレーサビリティマトリクス、5 件の不具合票、CI ワークフローを含みます。
仕様との乖離は不具合 ID と紐付けて記録し、API 側の修正時に自然に検知できる形にしています。

---

## 📌 Project Status / 進捗状況

- [x] Test case design with TC_IDs and priority / TC_ID と優先度を持つ設計
- [x] Manual testing collection (Postman) / 手動テスト用コレクション
- [x] Framework structure and utilities / フレームワーク構成
- [x] Authentication tests, 6 cases / 認証テスト 6 ケース
- [x] Create and retrieve tests, 8 cases / 作成・取得テスト 8 ケース
- [x] Update tests, 7 cases / 更新テスト 7 ケース
- [x] Delete tests, 4 cases / 削除テスト 4 ケース
- [x] Requirements traceability matrix / トレーサビリティマトリクス
- [x] Workflow and architecture diagrams / 各種図
- [x] CI workflow / CI ワークフロー
- [x] Bilingual documentation / 日英併記ドキュメント
- [x] Live execution and evidence capture / 実 API での実行とエビデンス取得
- [x] Defect evidence, all 5 reproduced / 不具合 5 件すべて再現・証跡取得
- [ ] Date-range filter coverage / 日付範囲フィルタのカバー

---

## 📬 Contact / 連絡先

**Tamang Amish**

- GitHub: [github.com/amishanita](https://github.com/amishanita)
- Email: `<add your email address / メールアドレスを記入>`

---

## 📄 License / ライセンス

MIT License. Free to use, modify and distribute with attribution.
帰属表示のうえ、自由に利用・改変・配布いただけます。

---

## 🔗 Additional Resources / 参考リンク

- [RESTful Booker API documentation](https://restful-booker.herokuapp.com/apidoc/index.html)
- [pytest documentation](https://docs.pytest.org/)
- [requests documentation](https://requests.readthedocs.io/)
- [JSON Schema specification](https://json-schema.org/)
- [Postman learning centre](https://learning.postman.com/)
- [Newman documentation](https://github.com/postmanlabs/newman)
