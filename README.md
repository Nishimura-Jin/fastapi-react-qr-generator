# 注釈付きQRコード生成ツール（フルスタック版）

URLを入力するだけで、QRコードとその上下に日本語の注釈を付けた画像を生成・ダウンロードできるWebアプリです。
Streamlit で作った同名アプリを、フロントエンドとバックエンドを分けた構成に作り直したポートフォリオ作品です。

---

## Streamlit版との違い

[Streamlit版（元の実装）](https://github.com/あなたのユーザー名/qr-generator-streamlit)はシンプルな単一スクリプトで動いていましたが、「Streamlitでは画面の自由度に限界がある」「他の場所からAPIとして呼び出せない」という点が気になっていました。

そこで、就職後の開発現場で使われる構成に近づけることを目標に、React（フロントエンド）+ FastAPI（バックエンド）+ Docker という構成に作り直しました。

---

## 開発の背景

Streamlit版を作った後、「動くものができた」だけで満足するのではなく、**もう一歩踏み込んで、実際の開発現場に近い構成で作り直してみたい**と思ったことが出発点です。

独学でフロントエンドとバックエンドを別々に勉強してきたので、それを一つのアプリとしてつなげて動かす経験がしたかったという気持ちもありました。

### 作り直す中でこだわった点

- **ファイルを役割ごとに分ける**
  - Streamlit版は `app.py` 一枚にロジックが全部書かれていました。今回は UI・API・DB処理・QR生成をそれぞれ別ファイルに分けて、どこに何が書いてあるかわかりやすい構成にしました。

- **フロントとバックをAPIで繋ぐ**
  - React から FastAPI に fetch でリクエストを送る構成にしました。フロントとバックが独立しているので、将来どちらかだけ差し替えることもできます。

- **Dockerで環境をまとめる**
  - `docker compose up --build` の1コマンドで、バックエンドもフロントエンドも立ち上がるようにしました。自分のPCでしか動かない、という状況をなくすのが目的です。

- **データとアプリケーションの分離**
  - SQLiteのデータベースファイルは `data/` フォルダに配置し、コードとデータを分離しました。

---

## 機能一覧

- QRコード生成（URLまたは任意のテキスト）
- 日本語注釈の追加（QRコードの上または下に配置）
- 生成画像のPNGダウンロード
- 生成後にリンク先をブラウザで確認できるボタン
- 生成履歴の保存・一覧表示（クリックで入力欄に自動セット）
- 履歴の個別削除
- URLの形式チェック（http / https で始まっているか）

---

## 使用技術

- **Language:** Python 3.11 / JavaScript
- **Frontend:** React 19 + Vite 8
- **Backend:** FastAPI
- **Libraries:**
  - `qrcode`（QRコード生成）
  - `Pillow`（画像処理・日本語テキスト描画）
  - `sqlite3`（履歴の保存・取得）
- **Infrastructure:** Docker / Docker Compose
- **Dev Environment:** WSL2 (Ubuntu)

---

## フォルダ構成

```
qr-generator-fullstack/
├── backend/
│   ├── data/
│   │   └── history.db           # 生成履歴のデータベース
│   ├── src/
│   │   ├── fonts/
│   │   │   └── NotoSansJP-Medium.ttf
│   │   ├── database.py          # SQLiteの操作（保存・取得・削除）
│   │   ├── main_api.py          # FastAPIのエンドポイント定義
│   │   └── qr_service.py        # QRコード生成の処理
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # メインのUI
│   │   ├── api.js               # バックエンドへのリクエスト関数
│   │   ├── index.css
│   │   └── main.jsx
│   ├── vite.config.js           # 開発時のプロキシ設定
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## APIエンドポイント

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/` | 動作確認用 |
| `POST` | `/api/qr` | QRコードを生成してPNG画像を返す |
| `GET` | `/api/history` | 生成履歴を取得（新しい順・最大20件） |
| `DELETE` | `/api/history/{id}` | 指定した履歴を削除 |

リクエスト例（POST /api/qr）:
```json
{
  "url": "https://example.com",
  "label_text": "公式LINEはこちら",
  "label_position": "Top"
}
```

`http://localhost:8000/docs` でFastAPIの自動生成ドキュメントを確認できます。

---

## セットアップ

### 必要なもの

- Docker / Docker Compose
- （Windowsの場合）WSL2

### 起動手順

```bash
# リポジトリをクローン
git clone https://github.com/あなたのユーザー名/qr-generator-fullstack.git
cd qr-generator-fullstack

# コンテナを起動
docker compose up --build
```

起動後、以下のURLにアクセスできます。

- フロントエンド: http://localhost:5173
- APIドキュメント: http://localhost:8000/docs

### Dockerを使わない場合

```bash
# バックエンド
cd backend
pip install -r requirements.txt
uvicorn src.main_api:app --reload --port 8000

# フロントエンド（別ターミナルで）
cd frontend
npm install
npm run dev
```

---

## 作者

GitHub: [Nishimura-Jin](https://github.com/Nishimura-Jin)