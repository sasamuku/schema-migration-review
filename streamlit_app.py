import streamlit as st
import google.generativeai as genai
import json

st.title("✅ Schema Migration Review")

# Gemini API Keyの設定
api_key = st.text_input("Gemini API Key", type="password")
if api_key:
    # APIの設定を更新
    genai.configure(api_key=api_key)

# タブの作成
tab1, tab2, tab3 = st.tabs(["📝 スキーマレビュー", "⚙️ ルールブック", "📚 障害事例"])

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

# 障害事例タブ
with tab3:
    st.subheader("障害事例の登録")

    # デフォルトの障害事例
    default_incidents = """
1. users テーブルへのNOT NULL制約追加時のインシデント
- 発生日: 2024-01-15
- 影響: 本番環境でマイグレーションが失敗し、30分のダウンタイムが発生
- 原因: 既存データにNULL値が存在することを見落としていた
- 対策: マイグレーション前のデータチェックを必須化

2. orders テーブルのカラム型変更時のインシデント
- 発生日: 2024-02-20
- 影響: 一部のデータが切り捨てられ、復旧作業に2時間を要した
- 原因: decimal型からinteger型への変換時にデータ切り捨ての影響を見落としていた
- 対策: 型変更時は必ずデータの範囲チェックを実施
"""

    # セッションステートに障害事例を保存
    if 'incidents' not in st.session_state:
        st.session_state.incidents = default_incidents

    incidents = st.text_area(
        "過去の障害事例を入力してください",
        value=st.session_state.incidents,
        height=300
    )

    if st.button("障害事例を保存"):
        st.session_state.incidents = incidents
        st.success("障害事例を保存しました！")

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
            以下のSQLスキーマ変更の安全性を分析し、JSON形式で回答してください。

            現在のスキーマ:
            {current_schema}

            実行予定のDDL:
            {planned_ddl}

            以下のルールブックに基づいて分析してください：
            {st.session_state.rules}

            過去の障害事例：
            {st.session_state.incidents}

            以下の形式のJSONで回答してください：
            {{
                "general_analysis": {{
                    "data_loss_risk": {{
                        "score": 0-100の数値,
                        "description": "詳細な説明"
                    }},
                    "performance_impact": {{
                        "score": 0-100の数値,
                        "description": "詳細な説明"
                    }},
                    "downtime_required": {{
                        "score": 0-100の数値,
                        "description": "詳細な説明"
                    }}
                }},
                "rulebook_analysis": {{
                    "violations": [
                        {{
                            "rule": "違反したルール",
                            "severity": 0-100の数値,
                            "description": "詳細な説明",
                            "recommendation": "改善案"
                        }}
                    ],
                    "no_violations": "ルールに該当するものがない場合は、ここに記載してください"
                }},
                "incident_analysis": {{
                    "similar_incidents": [
                        {{
                            "incident": "類似インシデントの概要",
                            "risk_level": 0-100の数値,
                            "precautions": "必要な注意事項"
                        }}
                    ],
                    "no_similar_incidents": "過去のインシデントに類似するものがない場合は、ここに記載してください"
                }},
                "overall_score": 0-100の数値,
                "execution_recommendation": "実行推奨/要注意/実行非推奨のいずれか",
                "summary": "総括コメント"
            }}
            """

            # レビュー結果の生成
            response = model.generate_content(prompt)

            try:
                # レスポンステキストからJSON部分を抽出
                response_text = response.text.strip()
                # コードブロックで囲まれている場合の処理
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].strip()
                else:
                    json_str = response_text

                # JSONとしてパース
                review_result = json.loads(json_str)
            except json.JSONDecodeError as e:
                st.error("レスポンスの解析に失敗しました。もう一度試してください。")
                st.error(f"エラーの詳細: {str(e)}")
                st.code(response.text, language="json")
                st.stop()
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {str(e)}")
                st.stop()

            st.subheader("🔍 レビュー結果")

            # 全体評価の表示
            col1, col2 = st.columns(2)
            with col1:
                st.metric("総合評価スコア", f"{review_result['overall_score']}/100")
            with col2:
                recommendation = review_result['execution_recommendation']
                if recommendation == "実行推奨":
                    st.success("✅ 実行推奨")
                elif recommendation == "要注意":
                    st.warning("⚠️ 要注意")
                else:
                    st.error("❌ 実行非推奨")

            st.info(review_result['summary'])

            # 一般分析の表示
            st.subheader("一般的な観点での分析")
            general = review_result['general_analysis']

            cols = st.columns(3)
            with cols[0]:
                st.metric("データ損失リスク", f"{general['data_loss_risk']['score']}/100")
                st.write(general['data_loss_risk']['description'])

            with cols[1]:
                st.metric("パフォーマンスへの影響", f"{general['performance_impact']['score']}/100")
                st.write(general['performance_impact']['description'])

            with cols[2]:
                st.metric("ダウンタイムの必要性", f"{general['downtime_required']['score']}/100")
                st.write(general['downtime_required']['description'])

            # ルールブック分析の表示
            st.subheader("ルールブックに基づく分析")
            if review_result['rulebook_analysis'].get('violations') and len(review_result['rulebook_analysis']['violations']) > 0:
                for violation in review_result['rulebook_analysis']['violations']:
                    severity = violation['severity']
                    if severity < 30:
                        st.success(f"🟢 {violation['rule']}")
                    elif severity < 70:
                        st.warning(f"🟡 {violation['rule']}")
                    else:
                        st.error(f"🔴 {violation['rule']}")

                    with st.expander("詳細"):
                        st.write(violation['description'])
                        st.info(f"💡 推奨対策: {violation['recommendation']}")
            elif 'no_violations' in review_result['rulebook_analysis']:
                st.success("✅ " + review_result['rulebook_analysis']['no_violations'])

            # 過去の障害事例との比較
            st.subheader("過去の障害事例との比較")
            if review_result['incident_analysis'].get('similar_incidents') and len(review_result['incident_analysis']['similar_incidents']) > 0:
                for incident in review_result['incident_analysis']['similar_incidents']:
                    with st.expander(incident['incident']):
                        st.metric("リスクレベル", f"{incident['risk_level']}/100")
                        st.write(f"**必要な注意事項:**")
                        st.write(incident['precautions'])
            elif 'no_similar_incidents' in review_result['incident_analysis']:
                st.success("✅ " + review_result['incident_analysis']['no_similar_incidents'])

            # Geminiからの回答全文を表示
            with st.expander("🤖 Geminiからの回答全文"):
                st.code(response.text, language="json")

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.error("Gemini APIの設定を確認してください。")
