import streamlit as st
import random
import time
import pandas as pd

# ページ設定
st.set_page_config(page_title="かけ算チャレンジ", layout="centered")

# カスタムCSS（文字サイズ調整と入力欄の最適化）
st.markdown("""
    <style>
    /* 入力欄の文字サイズと高さを最適化 */
    .stTextInput input {
        font-size: 35px !important; 
        text-align: center !important;
        height: 70px !important;
        color: #2c3e50 !important;
    }
    /* 問題の文字を大きく、青色に */
    .question-text {
        font-size: 70px;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-top: -20px;
        margin-bottom: 20px;
    }
    /* 判定の文字を大きく */
    .result-badge {
        font-size: 24px;
        font-weight: bold;
        padding: 5px 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.current_index = 0
    st.session_state.results = []
    st.session_state.finished = False

def finish_game():
    st.session_state.finished = True
    st.session_state.end_time = time.time()

# --- 1. スタート画面 ---
if not st.session_state.started:
    st.title("🧠 かけ算 50問 チャレンジ")
    st.write("なまえをいれて、「スタート」をおしてね！")
    user_name = st.text_input("なまえ", value="ゲスト")
    if st.button("スタート！", type="primary", use_container_width=True):
        nums = [i for i in range(2, 10)]
        pairs = [(a, b) for a in nums for b in nums]
        st.session_state.problems = random.sample(pairs, 50)
        st.session_state.user_name = user_name
        st.session_state.start_time = time.time()
        st.session_state.started = True
        st.rerun()

# --- 2. 結果発表（答え合わせ）画面 ---
elif st.session_state.finished:
    st.title("🎊 けっかはっぴょう！")
    elapsed = st.session_state.end_time - st.session_state.start_time
    
    # 未回答の処理
    if len(st.session_state.results) < 50:
        for i in range(len(st.session_state.results), 50):
            a, b = st.session_state.problems[i]
            st.session_state.results.append({"問題": f"{a} × {b}", "こたえ": "なし", "正解": a * b, "判定": "❌"})

    df = pd.DataFrame(st.session_state.results)
    score = df[df["判定"] == "⭕"].count()["判定"]
    
    st.header(f"🌟 {st.session_state.user_name} さん")
    st.subheader(f"てんすう: {score} / 50 てん （じかん: {elapsed:.1f} びょう）")
    
    # 視覚的な答え合わせ
    st.write("### 答え合わせをしよう！")
    
    # スタイリング関数
    def style_table(row):
        color = 'background-color: #e6ffed' if row.判定 == '⭕' else 'background-color: #fff5f5'
        text_color = 'color: #28a745' if row.判定 == '⭕' else 'color: #e41e31'
        return [f'{color}; {text_color}; font-weight: bold; font-size: 20px;'] * len(row)

    st.dataframe(df.style.apply(style_table, axis=1), use_container_width=True, height=600)

    if st.button("もういちど やる！"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. クイズ画面 ---
else:
    # 右上に小さく「やめる」ボタン
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("やめる"):
            finish_game()
            st.rerun()
            
    idx = st.session_state.current_index
    a, b = st.session_state.problems[idx]
    
    st.write(f"第 {idx + 1} 問 / 50")
    st.markdown(f'<div class="question-text">{a} × {b}</div>', unsafe_allow_html=True)
    
    # 【重要】keyを切り替えることでStreamlitに「新しい入力」と認識させ、オートフォーカスを維持します
    # また、入力ボックスを空にするために label を活用
    ans = st.text_input("ここに こたえを いれてね", key=f"input_box_{idx}", help="数字をいれてEnterをおしてね")

    # 入力があったら次の問題へ
    if ans:
        correct_ans = a * b
        is_correct = ans.strip() == str(correct_ans)
        
        st.session_state.results.append({
            "問題": f"{a} × {b}",
            "こたえ": ans,
            "正解": correct_ans,
            "判定": "⭕" if is_correct else "❌"
        })
        
        if idx + 1 < 50:
            st.session_state.current_index += 1
            # 少しだけ待ち時間を入れるとタブレットでの動作が安定します
            st.rerun()
        else:
            finish_game()
            st.rerun()