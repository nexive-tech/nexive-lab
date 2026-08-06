# openpyxl-excel-report-check

Excel請求書の空欄と金額ズレを、Python と openpyxl で確認するサンプルです。

ネクシブログの記事「openpyxlでExcel帳票の空欄と金額ズレをチェックする」で使った検証用コードです。

## What This Checks

- 請求番号、取引先名、請求日、請求金額が空欄でないか
- 明細行の品目コード、作業内容、数量、単価、金額が空欄でないか
- 明細行の金額合計と帳票上の請求金額が一致するか
- 見つけた不備を CSV に出せるか

## Files

- `create_sample_workbook.py`: 不備を含む検証用 Excel を作るスクリプト
- `check_invoice_report.py`: Excel を読み取り、空欄と金額ズレを CSV に出すスクリプト
- `samples/sample_invoice_report_check.xlsx`: 検証用 Excel
- `expected/check_results.csv`: チェック結果の例
- `requirements.txt`: Python 依存ライブラリ

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run

検証用 Excel を作り直す場合:

```powershell
.\.venv\Scripts\python create_sample_workbook.py
```

帳票チェックを実行する場合:

```powershell
.\.venv\Scripts\python check_invoice_report.py samples\sample_invoice_report_check.xlsx --out check_results.csv
```

問題がある場合は、`check_results.csv` にセル、項目、理由が出力されます。

## Expected Result

このサンプルでは、次の4件が出ます。

- `B4`: 取引先名が空欄
- `C12`: 明細3の作業内容が空欄
- `F13`: 明細4の金額が空欄
- `B6`: 請求金額 `120000` と明細合計 `115000` が一致しない

