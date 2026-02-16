# Bath Monitor Dashboard - お風呂見守りダッシュボード

独居高齢者の入浴中の安全を遠隔から見守るための Web アプリケーションです。
浴室に設置されたセンサーからのデータをリアルタイムで受信し、安全状態をわかりやすく表示します。

---

## このプロジェクトは何をするのか

一人暮らしの高齢者がお風呂に入っているとき、万が一溺水などの事故が起きた場合に、
離れた場所にいる家族や介護者がすぐに気付けるようにするためのシステムです。

浴室のセンサーが「今どこにいるか」「安全かどうか」を検知し、
このダッシュボード（Web画面）でリアルタイムに確認できます。

### 画面に表示される内容

| 表示項目 | 説明 |
|---------|------|
| 安全状態カード | 「安全」「不在」「危険」の3段階を色分けで大きく表示 |
| 現在位置 | 洗い場・浴槽・不在のどこにいるか |
| 最終更新 | センサーからの最後のデータが何秒/何分前か |
| 動作モード | 位置検知モード or 溺水検知モード |
| 状態履歴 | 状態が変化した記録（最大20件） |

### 2つの動作モード

1. **位置検知モード** - 人が浴室のどこにいるかを表示します（洗い場 or 浴槽）
2. **溺水検知モード** - 入浴中の人が安全かどうかを判定し、危険があれば警告します

---

## 使われている技術

このプロジェクトは主に3つの技術で構成されています。

### 1. Python

プログラミング言語です。このプロジェクトのすべてのコードは Python で書かれています。
ファイルは `app.py` の1つだけです。

### 2. Streamlit（ストリームリット）

Python だけで Web アプリケーションを作れるフレームワークです。
HTML や JavaScript を書かなくても、Python のコードだけでボタンやグラフを含む Web ページが作れます。

```python
# 例：Streamlitでテキストを表示する
import streamlit as st
st.write("こんにちは！")
```

公式サイト: https://streamlit.io

### 3. Supabase（スーパベース）

クラウド上のデータベースサービスです。
センサーが検知したデータはここに保存され、このアプリがそのデータを読み取って画面に表示します。

公式サイト: https://supabase.com

---

## プロジェクトのファイル構成

```
hurokenchi-dashboard/
├── app.py                          # アプリ本体（これが全てのコード）
├── requirements.txt                # 必要なライブラリの一覧
├── .streamlit/
│   ├── config.toml                 # アプリの見た目の設定（テーマカラーなど）
│   ├── secrets.toml                # データベースの接続情報（※非公開）
│   └── secrets.toml.example        # ↑のテンプレート（設定の書き方の例）
├── .gitignore                      # Gitで管理しないファイルの一覧
└── README.md                       # このファイル
```

### 各ファイルの役割

- **`app.py`** - アプリケーションのすべてのロジックが入っている唯一のソースコードです。約250行で構成されています。
- **`requirements.txt`** - `pip install` で導入する外部ライブラリを記載しています。
- **`.streamlit/config.toml`** - 画面の配色（テーマカラー）やサーバー設定を定義しています。
- **`.streamlit/secrets.toml`** - Supabase への接続に必要な URL と API キーを保存します。このファイルは `.gitignore` に登録されており、GitHub には公開されません。
- **`.streamlit/secrets.toml.example`** - `secrets.toml` をどう書けばよいかを示すテンプレートです。

---

## app.py のコード解説

`app.py` は大きく分けて以下の部分で構成されています。

### (1) ページ設定（12〜16行目）

```python
st.set_page_config(
    page_title="お風呂見守り",
    page_icon="🛁",
    layout="centered"
)
```

ブラウザのタブに表示されるタイトルやアイコンを設定しています。
**この関数は必ずファイルの一番最初に呼び出す必要があります**（Streamlit のルール）。

### (2) カスタム CSS（25〜64行目）

Streamlit の標準デザインだけでは表現できない見た目をCSSで追加しています。
安全状態ごとに色を変えるカード（緑＝安全、黄＝注意、赤＝危険）を定義しています。

### (3) データベース接続（67〜80行目）

```python
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
```

- `@st.cache_resource` は「この関数の結果をキャッシュ（保存）して、2回目以降は再実行しない」という意味のデコレータです。データベースへの接続は1回だけ行えば十分なので、こうすることで効率化しています。
- `st.secrets` は `.streamlit/secrets.toml` に書いた値を読み取る仕組みです。

### (4) 安全状態の判定（100〜128行目）

`get_safety_status()` 関数が、センサーから受け取ったデータ（モード・状態・溺水フラグ）を基に、
画面に表示する安全レベル（safe / caution / danger）とメッセージを決定しています。

```
status = 0 → 不在（注意）
status = 1 → 安全
status = 2 → 位置検知なら安全、溺水検知なら危険
```

### (5) 画面表示（159〜233行目）

Streamlit のコンポーネント（`st.metric`、`st.columns`、`st.expander` など）を使って情報を画面に並べています。

### (6) 自動更新（236〜246行目）

```python
if auto_refresh:
    time.sleep(2)
    st.rerun()
```

チェックボックスが ON の場合、2秒待ってからページを自動で再読み込みします。
これにより、センサーデータの変化をリアルタイムに反映できます。

---

## セットアップ手順

### 前提条件

- Python 3.9 以上がインストールされていること
- Supabase のアカウントがあること（無料プランで OK）

### 1. リポジトリをクローン

```bash
git clone <リポジトリのURL>
cd hurokenchi-dashboard
```

### 2. 仮想環境を作成して有効化（推奨）

```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux の場合
# venv\Scripts\activate         # Windows の場合
```

> **仮想環境とは？**
> プロジェクトごとにライブラリを分けて管理するための仕組みです。
> 他のプロジェクトに影響を与えずにライブラリをインストールできます。

### 3. ライブラリをインストール

```bash
pip install -r requirements.txt
```

このコマンドで以下のライブラリがインストールされます：

| ライブラリ | バージョン | 役割 |
|-----------|----------|------|
| streamlit | 1.28.0以上 | Web アプリのフレームワーク |
| supabase | 2.0.0以上 | データベースへの接続 |
| python-dotenv | 1.0.0以上 | 環境変数の管理 |

### 4. Supabase の設定

#### 4-1. Supabase でプロジェクトを作成

1. https://supabase.com にアクセスしてアカウントを作成
2. 「New Project」からプロジェクトを作成
3. 作成後、「Settings」→「API」から以下の2つの値をメモ：
   - **Project URL**（例: `https://xxxxx.supabase.co`）
   - **anon public key**（`eyJ...` で始まる長い文字列）

#### 4-2. データベースにテーブルを作成

Supabase の SQL Editor で以下を実行してください：

```sql
CREATE TABLE sensor_state (
    id INTEGER PRIMARY KEY DEFAULT 1,
    mode TEXT DEFAULT 'location',
    status INTEGER DEFAULT 0,
    is_drowning BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 初期データを挿入
INSERT INTO sensor_state (id, mode, status, is_drowning)
VALUES (1, 'location', 0, FALSE);
```

#### 4-3. 接続情報を設定

テンプレートファイルをコピーして、値を書き換えます。

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

`.streamlit/secrets.toml` を開いて、メモした値を記入：

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJxxxxxxxxx..."
```

> **注意**: このファイルには秘密の API キーが入っているため、Git にコミットしないでください。
> `.gitignore` に登録済みなので、通常は自動的に除外されます。

### 5. アプリを起動

```bash
streamlit run app.py
```

ブラウザが自動で開き、`http://localhost:8501` にダッシュボードが表示されます。

---

## データの流れ

```
浴室のセンサー（ESP32等）
        │
        │ データを送信（HTTP / MQTT など）
        ▼
   Supabase（クラウドDB）
     sensor_state テーブル
        │
        │ データを読み取り（2秒ごと）
        ▼
  Streamlit ダッシュボード（このアプリ）
        │
        │ ブラウザに表示
        ▼
   家族・介護者のスマホ / PC
```

---

## データベースのテーブル構造

`sensor_state` テーブル:

| カラム名 | 型 | 説明 |
|---------|-----|------|
| `id` | INTEGER | 常に1（1レコードのみ使用） |
| `mode` | TEXT | `'location'`（位置検知）or `'drowning'`（溺水検知） |
| `status` | INTEGER | `0`=不在, `1`=シャワー/安全, `2`=浴槽/危険 |
| `is_drowning` | BOOLEAN | 溺水検知フラグ（`TRUE`/`FALSE`） |
| `updated_at` | TIMESTAMPTZ | 最終更新日時 |

---

## よくある質問

### Q: センサーがなくても動かせますか？

はい。Supabase の管理画面から `sensor_state` テーブルの値を手動で変更すれば、
画面の表示が変わることを確認できます。

### Q: デプロイ（インターネットに公開）するには？

[Streamlit Community Cloud](https://share.streamlit.io) を使えば無料で公開できます。
GitHub リポジトリを連携するだけでデプロイが可能です。

### Q: `secrets.toml` を間違えて Git にコミットしてしまったら？

API キーが漏洩する可能性があります。すぐに Supabase の管理画面から API キーを再生成してください。

---

## ライセンス

このプロジェクトは学術研究目的で開発されています。
