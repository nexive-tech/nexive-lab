# nexive-lab

ネクシブログの記事で使うサンプルコード、SQL、CSV、確認スクリプト置き場です。

記事本文には考え方、確認手順、主要なコードを載せ、動かせる一式はこのリポジトリに置きます。

## Structure

- `python/`: Pythonによる業務データ確認、自動化、Excel/CSV処理
- `node/`: Node.jsによる検証用Webアプリ、デプロイ確認サンプル
- `sql/`: SQL例、検証用データ、実行計画確認メモ
- `laravel/`: Laravel / PHP の業務システム実装サンプル
- `csv/`: 記事で使うCSVサンプル、文字コード確認用データ

## Policy

- 本番データ、顧客データ、秘密情報は置かない。
- サンプルは小さくし、記事から見ても目的が分かる単位で分ける。
- 実行方法、入力例、確認結果は各サンプルの `README.md` に書く。

## Samples

- `python/openpyxl-excel-report-check`: Excel帳票の空欄と金額ズレを openpyxl で確認するサンプル
