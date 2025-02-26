import streamlit as st
import google.generativeai as genai

st.title("✅ Schema Migration Review")

# Gemini API Keyの設定
api_key = st.text_input("Gemini API Key", type="password")
if api_key:
    # APIの設定を更新
    genai.configure(api_key=api_key)

# タブの作成
tab1, tab2 = st.tabs(["📝 スキーマレビュー", "⚙️ ルールブック"])

# ルールブック設定タブ
with tab2:
    st.subheader("ルールブック設定")

    # デフォルトのルール
    default_rules = """
1. NOT NULL制約を追加する場合は、既存のデータがNULLでないことを確認すること
2. 外部キー制約を追加する場合は、参照整合性が保たれていることを確認すること
3. カラムの型を変更する場合は、データの切り捨てが発生しないことを確認すること
4. インデックスを削除する場合は、パフォーマンスへの影響を確認すること
"""

    # セッションステートにルールを保存
    if 'rules' not in st.session_state:
        st.session_state.rules = default_rules

    rules = st.text_area(
        "レビュールールを入力してください",
        value=st.session_state.rules,
        height=300
    )

    if st.button("ルールを保存"):
        st.session_state.rules = rules
        st.success("ルールを保存しました！")

# スキーマレビュータブ
with tab1:
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
            # Geminiモデルの設定（変更しないでください）
            model = genai.GenerativeModel('gemini-2.0-flash')

            # プロンプトの作成
            prompt = f"""
            以下のSQLスキーマ変更の安全性を分析してください。

            現在のスキーマ:
            {current_schema}

            実行予定のDDL:
            {planned_ddl}

            以下のルールブックに基づいて分析してください：
            {st.session_state.rules}

            レビュー結果は以下の2つのセクションに分けて回答してください：

            セクション1: 一般的な観点での分析
            1. データ損失のリスク
            2. パフォーマンスへの影響
            3. ダウンタイムの必要性
            4. 推奨される実行方法

            セクション2: ルールブックに基づく分析
            - 各ルールに対する違反の有無
            - 違反がある場合の具体的な問題点
            - 改善のための推奨事項
            """

            # レビュー結果の生成
            response = model.generate_content(prompt)

            st.subheader("🔍 レビュー結果")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.error("Gemini APIの設定を確認してください。")
