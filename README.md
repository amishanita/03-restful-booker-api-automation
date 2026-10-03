# 03 / RESTful Booker API テスト

公開API [RESTful Booker](https://restful-booker.herokuapp.com/apidoc/index.html) を対象に、公式ドキュメントに書いてある仕様と、実際に返ってくるレスポンスを突き合わせました。

ライブAPIに対して実行して、仕様と違う挙動を5件見つけています。全件、curl で再現できる形で記録しました。

![Python](https://img.shields.io/badge/Python-3.12-blue)
![requests](https://img.shields.io/badge/requests-2CA5E0)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)

## 結果

| 項目 | 数 |
|---|---:|
| テストケース | 25 |
| 成功 | 21 |
| xfail（既知の差分） | 4 |
| 失敗 | 0 |
| 記録した不具合 | 5 |

実行日：2026年9月5日（ライブAPIに対して実行）

見つけた差分は `xfail` としてテストに残しています。落ちたまま放置すると、そのうち誰も結果を見なくなります。把握済みの差分であることをコードに書いておけば、修正されたときに `xpass` になって気づけます。

## この題材を選んだ理由

UIだけ見ていると、画面の裏で何が起きているか分かりません。APIを直接叩けば、ドキュメントに書いてあることと実装が合っているかを直接確認できます。

RESTful Booker にしたのは、公式のAPIドキュメントが公開されているからです。合否を自分の想像ではなく、書かれている仕様に対して判定できます。

## テストした範囲

| エンドポイント | 確認した内容 |
|---|---|
| `POST /auth` | トークン発行、不正な認証情報 |
| `GET /booking` | 全件取得、名前・日付でのフィルタ |
| `GET /booking/{id}` | 単一取得、存在しないID |
| `POST /booking` | 新規作成、必須項目の欠落、型違い、境界値 |
| `PUT /booking/{id}` | 全項目更新、認証なし、存在しないID |
| `PATCH /booking/{id}` | 部分更新、認証なし |
| `DELETE /booking/{id}` | 削除、認証なし、二重削除 |

各エンドポイントを、正常系、認証エラー、存在しないリソース、不正な入力の4つの観点で見ています。

## 不具合の記録方法

5件とも次の形式で書いています。

- 概要
- 対象エンドポイント
- curl での再現コマンド（コピーして実行できる形）
- ドキュメントの記載（期待結果）
- 実際のレスポンス（ステータスコードとボディ）
- 影響と重大度

### 例

【要確認：実際に見つけた1件を、上の形式でここに書く。面接で必ず聞かれるので、自分の言葉で説明できる1件を選ぶ】

```bash
curl -i -X POST 'https://restful-booker.herokuapp.com/booking' \
  -H 'Content-Type: application/json' \
  -d '{ ... }'
```

| | 内容 |
|---|---|
| ドキュメントの記載 | 【要確認】 |
| 実際のレスポンス | 【要確認】 |
| 影響 | 【要確認】 |

## 要件トレーサビリティマトリクス

APIドキュメントの記述を要件として書き出し、どの要件をどのテストケースで確認しているかの対応表を作りました（`docs/rtm.md`）。

これを作ると、ドキュメントに書いてあるのに誰も確認していない項目が見えます。テストケースが何件あるかではなく、仕様のどこを押さえているかで話せるようになります。

## 実行方法

```bash
pip install -r requirements.txt

pytest -v
pytest -v -rxX      # 既知の差分の詳細も表示
pytest --html=report.html --self-contained-html
```

## リポジトリ構成

```
.
├── tests/
│   ├── test_auth.py
│   ├── test_booking_read.py
│   ├── test_booking_create.py
│   ├── test_booking_update.py
│   └── test_booking_delete.py
├── docs/
│   ├── rtm.md           要件トレーサビリティマトリクス
│   └── defects/         不具合報告（curl再現手順つき）
├── evidence/
│   ├── curl/
│   └── logs/
├── .github/workflows/
├── conftest.py
├── requirements.txt
└── README.md
```

【要確認：実際のファイル構成に合わせて書き換える】

## 環境

Python 3.12、requests、pytest、Postman、curl、macOS 15.7（Intel MacBook Pro）

## やってみて分かったこと

仕様書を基準にすると、テストの合否で揉めなくなります。「おかしい気がする」ではなく「ドキュメントのこの記述と違う」と言えるので、話が早いです。

落ちているテストを放置すると結果を見る人がいなくなるので、把握済みの差分と未知の失敗を分けておく必要がありました。`xfail` を使った理由はそれです。

APIテストはUIテストより実行が速いので、先に流す価値があります。壊れている箇所をUIより手前で見つけられます。

## 次にやること

- JSTQB Foundation Level 受験（2026年11月11日）
- スキーマ検証の追加

## 関連リポジトリ

| | 内容 |
|---|---|
| [01](https://github.com/amishanita/01-eccube-manual-qa) | EC-CUBE 手動テスト設計・不具合報告 |
| [02](https://github.com/amishanita/02-saucedemo-playwright-python) | Playwright と pytest によるUI自動テスト |
| 03（このリポジトリ） | REST API のテストと不具合検出 |
| [04](https://github.com/amishanita/04-saucedemo-ci-cd-qa) | GitHub Actions による自動実行 |

---

# English

# 03 / RESTful Booker API Testing

API tests for the public [RESTful Booker](https://restful-booker.herokuapp.com/apidoc/index.html) service, comparing what its documentation says against what the service actually returns.

Run against the live API, the suite found 5 discrepancies. Each one is recorded with a curl command that reproduces it.

## Results

| Item | Count |
|---|---:|
| Test cases | 25 |
| Passed | 21 |
| xfail (known gaps) | 4 |
| Failed | 0 |
| Defects recorded | 5 |

Run on 5 September 2026.

The gaps are kept as `xfail` rather than deleted or left red. A suite that's always failing stops being read. Marked as known, they stay visible in the code, and if the service gets fixed they turn into `xpass` and I find out.

## Why this subject

UI tests can't see what happens behind the screen. More to the point, RESTful Booker publishes its API documentation, so pass and fail can be judged against something written down rather than against my own assumption.

## Scope

Auth (token issue, bad credentials). GET all, filtered, by id, missing id. POST with missing fields, wrong types, boundary values. PUT and PATCH with and without auth. DELETE including unauthenticated and double delete. Each endpoint from four angles: happy path, auth failure, missing resource, invalid input.

## Defect format

Summary, endpoint, curl reproduction, documented expectation, actual response with status and body, impact and severity.

## Requirements traceability matrix

Every statement in the API documentation is written out as a requirement and mapped to the tests that cover it (`docs/rtm.md`). It shows which documented behaviour nobody is checking, and it lets coverage be discussed against the spec instead of against a test count.

## Running it

```bash
pip install -r requirements.txt
pytest -v
pytest -v -rxX
```

## Environment

Python 3.12, requests, pytest, Postman, curl, macOS 15.7.

## What I learned

With a written spec as the standard, nobody argues about whether something is a bug. You point at the line.

Separating known gaps from unknown failures is what keeps a suite worth looking at.

API tests run fast enough to put in front of the UI suite, which catches breakage earlier.

## Next

JSTQB Foundation Level on 11 November 2026. Schema validation.

**Tamang Amish** — [GitHub](https://github.com/amishanita) / [LinkedIn](https://www.linkedin.com/in/tamang-amish-669289250)
