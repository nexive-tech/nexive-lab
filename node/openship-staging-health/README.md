# OpenShip staging health sample

OpenShipで検証環境デプロイを試すための最小Node.jsアプリです。

OpenShipの公式fixtureと同じく、実行時に注入される`PORT`環境変数で待ち受けます。業務システムの検証環境で確認したい、環境名、リリース番号、ヘルスチェック、ログ出力だけを持たせています。

## エンドポイント

| path | 用途 |
| ---- | ---- |
| `/` | 環境名とリリース番号を返す |
| `/health` | ヘルスチェック用JSONを返す |
| `/config-check` | 設定値が入っているかを返す。秘密値そのものは返さない |

## ローカル実行

```powershell
copy .env.example .env
npm install
npm start
```

別ターミナルで確認します。

```powershell
curl http://localhost:3000/
curl http://localhost:3000/health
curl http://localhost:3000/config-check
```

## Dockerで確認

```powershell
docker build -t openship-staging-health .
docker run --rm -p 3000:3000 --env-file .env openship-staging-health
```

## OpenShipで見ること

- `PORT`が注入されてもアプリが起動するか
- `APP_ENV`や`RELEASE_VERSION`を検証環境用に差し替えられるか
- ログにリクエストパスとステータスが出るか
- `/health`でデプロイ後の疎通確認ができるか
- 秘密情報を画面やログに出していないか

## 注意

`.env`は検証用のローカル設定です。DBパスワードやAPIキーを入れた`.env`をGitにコミットしません。
