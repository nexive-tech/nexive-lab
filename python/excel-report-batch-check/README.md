# excel-report-batch-check

業務システムから出力されたExcel請求書を、Pythonとopenpyxlでまとめてチェックするサンプルです。

## What This Checks

- 指定したシートが存在するか
- 請求書番号、請求日、請求先名が空でないか
- 明細行の数量、単価、金額が入っているか
- 明細行の金額が `数量 * 単価` と一致するか
- 小計、消費税、合計金額が明細と一致するか

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python check_reports.py samples rules.json --out result.csv
```

問題がある場合は、`result.csv` にファイル名、セル、内容が出力されます。

## Files

- `check_reports.py`: Excel帳票をまとめて確認するスクリプト
- `rules.json`: シート名、セル位置、明細範囲、税率などの設定
- `samples/`: 確認用のサンプル請求書
