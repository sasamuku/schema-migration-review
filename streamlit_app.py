import streamlit as st
import google.generativeai as genai

st.title("✅ Schema Migration Review")

# Gemini API Keyの設定
api_key = st.text_input("Gemini API Key", type="password")
if api_key:
    # APIの設定を更新
    genai.configure(api_key=api_key)

# 入力フォームの作成
st.subheader("📄 現在のスキーマ")
current_schema = st.text_area(
    "現在のスキーマ定義を入力してください",
    height=200,
    placeholder="CREATE TABLE users (...);"
)

st.subheader("📝 実行予定のDDL")
planned_ddl = st.text_area(
    "実行予定のDDLを入力してください",
    height=200,
    placeholder="ALTER TABLE users ADD COLUMN..."
)

# レビュー実行
if st.button("レビュー実行") and api_key and current_schema and planned_ddl:
    try:
        # Geminiモデルの設定（モデル名を修正）
        model = genai.GenerativeModel('gemini-2.0-flash')

        # プロンプトの作成
        prompt = f"""
        以下のSQLスキーマ変更の安全性を分析してください。

        現在のスキーマ:
        {current_schema}

        実行予定のDDL:
        {planned_ddl}

        以下の観点で分析してください：
        1. データ損失のリスク
        2. パフォーマンスへの影響
        3. ダウンタイムの必要性
        4. 推奨される実行方法
        """

        # レビュー結果の生成
        response = model.generate_content(prompt)

        st.subheader("🔍 レビュー結果")
        st.markdown(response.text)

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.error("Gemini APIの設定を確認してください。")

# 使い方の説明
with st.sidebar:
    st.header("💡 使い方")
    st.markdown("""
    1. Gemini API Keyを入力
    2. 現在のスキーマ定義を入力
    3. 実行予定のDDLを入力
    4. 「レビュー実行」ボタンをクリック
    """)


