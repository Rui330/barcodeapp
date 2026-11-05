import streamlit as st
import sqlite3
from PIL import Image
from pyzbar.pyzbar import decode

# --- 1. データベースの初期化とダミーデータ作成 ---
def init_db():
    # 発表用のプロトタイプとして、ファイルを作らずメモリ上で軽量に動かします
    conn = sqlite3.connect(':memory:') 
    c = conn.cursor()
    c.execute('''CREATE TABLE products (barcode TEXT, name TEXT, ingredients TEXT)''')
    
    # プレゼンの実演で使うバーコード番号に合わせて、ここを書き換えてください
    dummy_data = [
        # --- 成分がシンプルで高スコアになる商品 ---
        ('4900000000011', 'オーガニック オーツミルク', 'オーツ麦、食塩'),
        ('4900000000028', 'クラフトコーラ', '炭酸水、きび砂糖、レモン果汁、スパイスミックス'),
        ('4900000000035', '本格タコスシェル', 'とうもろこし粉、植物油脂、食塩'),
        ('4900000000042', '無塩ミックスナッツ', 'アーモンド、カシューナッツ、くるみ'),
        ('4900000000059', '天然水', '水（鉱水）'),

        # --- 添加物が多くて減点対象（NGキーワード）を含む商品 ---
        ('4901111111118', '激安コーラ', '果糖ぶどう糖液糖、炭酸、酸味料、人工甘味料（スクラロース）、着色料（カラメル色素）'),
        ('4901111111125', '甘いカフェラテ飲料', '牛乳、果糖ぶどう糖液糖、コーヒー、乳化剤、香料、人工甘味料（アセスルファムK）'),
        ('4901111111132', 'コンビニ弁当（ハンバーグ）', '精白米、ハンバーグ、果糖ぶどう糖液糖、植物油脂、増粘剤、保存料（ソルビン酸K）、着色料（赤102）'),
        ('4901111111149', 'エナジーゼリー', '果糖ぶどう糖液糖、寒天、酸味料、ゲル化剤、人工甘味料（アスパルテーム）、保存料（安息香酸Na）、着色料（黄色4号）'),
        ('4901111111156', '激辛スナック菓子', '小麦粉、植物油脂、砂糖、食塩、たんぱく加水分解物、着色料（パプリカ色素）、調味料（アミノ酸等）、保存料')
    # プレゼン用の実在商品データ（コンビニやスーパーで買えます）
        # --- 成分がシンプルで高スコアになる商品 ---
        ('4902102091866', 'い・ろ・は・す 天然水 (540ml)', '水（鉱水）'),
        ('4901306017449', 'カゴメ サルサ (240g)', 'トマト、たまねぎ、ピーマン、ハラペーニョ、食塩、醸造酢、香辛料、にんにく'),
        ('4901033006764', 'マルサン 毎日おいしいローストアーモンドミルク (200ml)', 'アーモンドペースト、食物繊維、食塩 / 乳化剤、pH調整剤、ビタミンE'),

        # --- 判定アルゴリズムの減点対象キーワードを含む商品 ---
        ('4902102070403', 'コカ・コーラ (500ml)', '糖類（果糖ぶどう糖液糖、砂糖）/ 炭酸、着色料（カラメル色素）、酸味料、香料、カフェイン'),
        ('4897036690017', 'モンスターエナジー (355ml)', '砂糖類、高麗人参根エキス / クエン酸、炭酸、香料、保存料（安息香酸）、人工甘味料（スクラロース）、着色料（アントシアニン）'),
    ]

    c.executemany('INSERT INTO products VALUES (?,?,?)', dummy_data)
    conn.commit()
    return conn

# --- 2. 簡易的な成分判定アルゴリズム ---
def evaluate_ingredients(ingredients):
    # 減点対象とするキーワードのリスト（将来のNLPによる表記ゆれ吸収の伏線になります）
    ng_keywords = ['人工甘味料', '着色料', '保存料', '果糖ぶどう糖液糖']
    score = 100
    detected_ng = []
    
    for kw in ng_keywords:
        if kw in ingredients:
            score -= 25
            detected_ng.append(kw)
            
    return score, detected_ng

# --- 3. Streamlit UIとメイン処理 ---
st.title("成分判定アプリ (Prototype)")
st.write("バーコードを読み取り、成分に基づく健康スコアを算出します。")

# DB接続
conn = init_db()

# PCのカメラを起動して画像を取得
img_file = st.camera_input("商品のバーコードをカメラに映してください")

if img_file is not None:
    image = Image.open(img_file)
    decoded_objects = decode(image)
    
    if decoded_objects:
        barcode_data = decoded_objects[0].data.decode('utf-8')
        st.success(f"読取成功: {barcode_data}")
        
        # データベース検索
        c = conn.cursor()
        c.execute('SELECT name, ingredients FROM products WHERE barcode=?', (barcode_data,))
        result = c.fetchone()
        
        if result:
            name, ingredients = result
            score, detected_ng = evaluate_ingredients(ingredients)
            
            # 結果の描画
            st.subheader(f"商品名: {name}")
            st.write(f"**原材料:** {ingredients}")
            st.metric(label="スコア", value=f"{score} / 100")
            
            if detected_ng:
                st.warning(f"⚠️ 注意成分を検出: {', '.join(detected_ng)}")
            else:
                st.info("✅ 懸念される添加物は検出されませんでした。")
        else:
            st.error("データベースに未登録の商品です。")
            
            # 展望に繋げるためのUIモック
            st.info("【将来の実装予定】OCR機能とOpen Food Facts APIを連携し、未登録データを自動収集してDBを拡張します。")
    else:
        st.error("バーコードが認識できません。ピントを合わせてください。")
