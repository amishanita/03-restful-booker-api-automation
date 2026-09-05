# Before Pushing / プッシュ前チェックリスト

Everything in this repository is complete except the parts that require running the suite.
Work through this file top to bottom, then push once.

実行を伴う項目以外はすべて完了しています。上から順に実施し、最後に一度だけ push してください。

---

## 1. Run / 実行

```bash
cd ~/Projects/restful-booker-api-portfolio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

curl -i https://restful-booker.herokuapp.com/ping     # must return 201 before continuing

{ echo "=== $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
  sw_vers -productVersion | sed 's/^/macOS /'
  python --version
  echo "Target: https://restful-booker.herokuapp.com"
  echo
  pytest -rxX
} 2>&1 | tee reports/evidence/pytest-run.log
```

Expected: `21 passed, 4 xfailed`. If different, do not edit the tests until you know why.
Rerun once first: a mid-run data reset on the shared host causes one-off failures.

---

## 2. Capture evidence / エビデンス取得

```bash
open reports/pytest-html-report.html
```

| File | How |
|------|-----|
| `reports/screenshots/01-pytest-run.png` | Screenshot of the terminal, including the header block and the summary line |
| `reports/screenshots/02-html-report.png` | Screenshot of the HTML report summary bar |
| `reports/screenshots/03-defect-evidence.png` | Screenshot of one expanded xfail row showing the defect reason |
| `reports/evidence/bug-00X-curl.txt` | Run the curl block at the bottom of `docs/known-issues.md` |

---

## 3. Fill in the numbers / 数値の記入

| File | What to replace |
|------|-----------------|
| `README.md` line ~280 | `XXXX-XX-XX` → run date, `3.XX` → your Python version |
| `README.md` lines ~284-288 | Per-module passed / xfail / failed counts |
| `README.md` lines ~292-295 | Unexpected failures, execution time |
| `docs/RTM-traceability-matrix.md` | Result column, all 25 rows: `Pass`, `xfail`, or `Fail` |
| `docs/known-issues.md` | Verified locally column: `Yes (YYYY-MM-DD)` per reproduced defect |
| `docs/known-issues.md` | To-confirm table: resolve the three open questions |
| `README.md` Project Status | Tick the last three boxes |

Confirm nothing is left:

```bash
grep -rn "XX\|TBD\|Not yet" README.md docs/*.md
```

Should return nothing except the word "TBD" if you genuinely left an item open.

---

## 4. Consistency check / 整合性確認

```bash
# Test IDs in code vs RTM: both should print 25
grep -rhoE "TC_(AUTH|BOOK|PUT|PATCH|DEL)_[0-9]{3}" tests/ | sort -u | wc -l
grep -cE "^\| TC_" docs/RTM-traceability-matrix.md

# Every defect referenced in code exists in known-issues.md
grep -rhoE "BUG-[0-9]{3}" tests/ | sort -u
grep -oE "^\| BUG-[0-9]{3}" docs/known-issues.md | sort -u
```

Also verify by hand: the totals in the README coverage table match the RTM rows
(11 positive, 14 negative, 15 High, 10 Medium, 8 tied to a defect).

---

## 5. Push / プッシュ

Only after steps 1 to 4 are complete.

```bash
git init
git add .
git commit -m "Add RESTful Booker API test suite: 25 cases, RTM, defect log"
git branch -M main
git remote add origin https://github.com/amishanita/restful-booker-api-portfolio.git
git push -u origin main
```

Then on GitHub:

- README renders correctly, tables and diagrams intact
- `reports/evidence/` and `reports/screenshots/` are present with your files
- Actions tab: the workflow ran. If it failed, open the log before doing anything else
- No `.env`, no `venv/`, no `__pycache__` in the file list

```bash
git ls-files | grep -E "\.env$|venv/|__pycache__"   # must return nothing
```

---

## 6. Optional but worth it / 任意

Commit in stages rather than one bulk commit. A single commit containing an entire project
tells a reviewer the work was generated, not developed.

```bash
git add utils/ conftest.py requirements.txt pytest.ini .gitignore .env.example
git commit -m "Add API client, config and fixtures"

git add tests/ test_data/
git commit -m "Add 25 test cases across auth and booking CRUD"

git add docs/ postman/
git commit -m "Add RTM, defect log, workflow diagrams and Postman collection"

git add reports/ README.md
git commit -m "Add execution results and evidence"
```
