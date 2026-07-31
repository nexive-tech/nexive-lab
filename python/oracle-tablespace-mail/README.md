# Oracle tablespace mail monitor

Oracle の表領域使用率を SQL で取得し、毎朝の確認メールとして送るための Python サンプルです。

実運用では Windows タスクスケジューラや cron から `monitor_tablespaces.py` を実行します。Oracle に接続できない環境でもメール本文を確認できるよう、サンプルデータで動く `--sample --dry-run` を用意しています。

## できること

- `DBA_TABLESPACE_USAGE_METRICS` と `DBA_TABLESPACES` から表領域使用率を取得する
- `WARNING_PERCENT`、`CRITICAL_PERCENT` のしきい値で状態を分ける
- 毎朝メールを送る、または警告時だけ送る
- メール送信前に `--dry-run` で本文を確認する
- 実行結果をログに残す

## 必要なもの

- Python 3.10 以降
- Oracle Database に接続できるユーザー
- `DBA_TABLESPACE_USAGE_METRICS` と `DBA_TABLESPACES` を参照できる権限
- SMTP サーバー

`python-oracledb` は Thin mode で動くため、基本的な接続では Oracle Client のインストールなしで利用できます。

## セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env` に Oracle と SMTP の接続情報を設定します。

## サンプルデータでメール本文を確認する

```powershell
python monitor_tablespaces.py --sample --dry-run
```

## Oracle に接続してメール本文だけ確認する

```powershell
python monitor_tablespaces.py --dry-run
```

## メールを送る

```powershell
python monitor_tablespaces.py
```

`MAIL_ALWAYS=false` の場合、警告または危険の表領域があるときだけメールを送ります。毎朝必ずメールを送りたい場合は `MAIL_ALWAYS=true` にします。

## Windows タスクスケジューラ例

プログラム:

```markdown
C:\path\to\nexive-lab\python\oracle-tablespace-mail\.venv\Scripts\python.exe
```

引数:

```markdown
C:\path\to\nexive-lab\python\oracle-tablespace-mail\monitor_tablespaces.py
```

開始:

```markdown
C:\path\to\nexive-lab\python\oracle-tablespace-mail
```

## 注意

`.env` には DB パスワードや SMTP パスワードを入れるため、Git にコミットしません。`.env.example` だけを共有します。
