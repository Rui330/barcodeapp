# barcodeapp
成分判定アプリ（Prototype）
食品のバーコードをカメラで読み取り、原材料から簡易的な健康スコア（100点満点）を表示するWebアプリです。

デモ： https://＿＿＿＿＿＿.streamlit.app

主な機能
スマホやPCのカメラでバーコード（JANコード）を読み取る

バーコード番号から商品名と原材料を検索する

注意成分の有無から100点満点のスコアを計算する

見つかった注意成分を画面に表示する

使った技術
役割	技術
言語	Python
画面・Webサーバー	Streamlit
画像の読み込み	Pillow
バーコード読取	pyzbar ＋ zbar
データベース	SQLite（メモリ上）
公開	Streamlit Community Cloud
判定のしくみ
原材料に次の4つの注意成分が含まれているかを調べ、1つ見つかるごとに25点ずつ減点します。

text
スコア = 100 − 25 × 見つかった注意成分の数
人工甘味料

着色料

保存料

果糖ぶどう糖液糖

※ スコアはこのアプリ独自の簡易ルールで、医学的・栄養学的な評価ではありません。

ファイル構成
text
.
├── app.py             # アプリ本体（画面・読取・DB・判定）
├── requirements.txt   # Pythonライブラリの一覧
├── packages.txt       # Linuxに入れる部品（libzbar0）
└── README.md
手元のPCで動かす方法（Mac）
bash
# 1. バーコード読取エンジンを入れる
brew install zbar

# 2. リポジトリを取得する
git clone https://github.com/Rui330/barcodeapp.git
cd barcodeapp

# 3. 仮想環境を作ってライブラリを入れる
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. 起動する
streamlit run app.py
ブラウザで http://localhost:8501 が開きます。

Apple Silicon（M1以降）のMacで Unable to find zbar shared library と表示される場合は、次のように起動してください。

bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib streamlit run app.py
登録している商品
試作のため、15商品（ダミー商品10件、実在する商品5件）を登録しています。実演用のバーコード番号は app.py の dummy_data で変更できます。

現状の課題
キーワードの完全一致で判定しているため、物質名だけの表記（例：アスパルテーム）は検出できない

減点が一律で、成分ごとの影響の大きさや量を考慮していない

登録商品が少ない

メモリ上のデータベースのため、再起動するとデータが初期状態に戻る

今後の予定
Open Food Facts APIと連携し、商品データを自動で取得する

OCR（文字認識）で原材料ラベルを直接読み取る

自然言語処理で表記の違いを吸収する

外部のデータベースにデータを保存する

参考にしたサービス
バーコードで食品を採点するという発想は、Yuka などの既存のアプリから着想を得ています。このアプリのコードと判定ルールは、すべて独自に作成したものです。Yukaは日本では配信されていないため、本アプリは日本の商品と日本語の原材料表示を対象にしています。
