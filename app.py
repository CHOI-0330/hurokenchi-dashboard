# -*- coding: utf-8 -*-
"""
Bath Sensor Dashboard - Streamlit App
リモートからセンサー状態を確認するためのダッシュボード
"""
import streamlit as st
from supabase import create_client
from datetime import datetime
import time

# ページ設定
st.set_page_config(
    page_title="お風呂センサー",
    page_icon="🛁",
    layout="centered"
)

# カスタムCSS（和色テーマ）
st.markdown("""
<style>
    /* 和色パレット */
    :root {
        --wasurenagusa: #7DB9DE;  /* 勿忘草色 */
        --sakura: #FEDFE1;         /* 桜色 */
        --wakakusa: #A5BA93;       /* 若草色 */
        --benihi: #E83929;         /* 紅緋 */
        --sumi: #3D3D3D;           /* 墨色 */
        --kinari: #F7F5F2;         /* 生成り */
    }

    /* メインコンテナ */
    .main .block-container {
        padding-top: 2rem;
        max-width: 600px;
    }

    /* ヘッダー */
    .header-title {
        text-align: center;
        color: var(--sumi);
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

    /* ステータスカード */
    .status-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    .status-card.active {
        border: 3px solid var(--wasurenagusa);
    }

    .status-card.inactive {
        opacity: 0.5;
    }

    .status-card.alert {
        background: linear-gradient(135deg, #fff5f5, #ffe0e0);
        border: 3px solid var(--benihi);
        animation: pulse 1s infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }

    .status-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .status-label {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--sumi);
    }

    /* モードバッジ */
    .mode-badge {
        display: inline-block;
        background: var(--wasurenagusa);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }

    /* 接続状態 */
    .connection-status {
        text-align: center;
        padding: 0.5rem;
        border-radius: 8px;
        margin-top: 1rem;
    }

    .connection-status.connected {
        background: #e8f5e9;
        color: #2e7d32;
    }

    .connection-status.disconnected {
        background: #ffebee;
        color: #c62828;
    }

    /* 更新時刻 */
    .update-time {
        text-align: center;
        color: #888;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }

    /* フッター */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.75rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# Supabase接続
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def get_sensor_state():
    """センサー状態を取得"""
    try:
        supabase = get_supabase()
        response = supabase.table('sensor_state').select('*').eq('id', 1).single().execute()
        return response.data
    except Exception as e:
        return None

def format_time_ago(timestamp_str):
    """更新時刻を「〇秒前」形式で表示"""
    if not timestamp_str:
        return "不明"
    try:
        updated = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(updated.tzinfo)
        diff = (now - updated).total_seconds()

        if diff < 60:
            return f"{int(diff)}秒前"
        elif diff < 3600:
            return f"{int(diff // 60)}分前"
        else:
            return f"{int(diff // 3600)}時間前"
    except:
        return "不明"

# ヘッダー
st.markdown('<div class="header-title">🛁 お風呂センサー</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">リモート状態モニター</div>', unsafe_allow_html=True)

# 状態取得
state = get_sensor_state()

if state is None:
    st.error("⚠️ センサーに接続できません")
    st.info("ローカルのFlaskサーバーが起動しているか確認してください")
else:
    mode = state.get('mode', 'location')
    status = state.get('status', 1)
    is_drowning = state.get('is_drowning', False)
    connected = state.get('connected', False)
    updated_at = state.get('updated_at')

    # モードバッジ
    mode_name = "📍 位置検知モード" if mode == 'location' else "🚨 溺水検知モード"
    badge_color = "#7DB9DE" if mode == 'location' else "#E8A87C"
    st.markdown(f'''
        <div style="text-align: center;">
            <span style="background: {badge_color}; color: white; padding: 0.4rem 1.2rem;
                         border-radius: 20px; font-size: 0.9rem;">{mode_name}</span>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ステータスカード
    col1, col2 = st.columns(2)

    if mode == 'location':
        # 位置検知モード
        with col1:
            card_class = "active" if status == 1 else "inactive"
            st.markdown(f'''
                <div class="status-card {card_class}">
                    <div class="status-icon">🚿</div>
                    <div class="status-label">洗い場</div>
                </div>
            ''', unsafe_allow_html=True)

        with col2:
            card_class = "active" if status == 2 else "inactive"
            st.markdown(f'''
                <div class="status-card {card_class}">
                    <div class="status-icon">🛁</div>
                    <div class="status-label">浴槽</div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        # 溺水検知モード
        with col1:
            card_class = "active" if status == 1 else "inactive"
            st.markdown(f'''
                <div class="status-card {card_class}">
                    <div class="status-icon">🛁</div>
                    <div class="status-label">正常</div>
                </div>
            ''', unsafe_allow_html=True)

        with col2:
            if is_drowning:
                st.markdown('''
                    <div class="status-card alert">
                        <div class="status-icon">⚠️</div>
                        <div class="status-label" style="color: #E83929;">溺水検知!</div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                card_class = "active" if status == 2 else "inactive"
                st.markdown(f'''
                    <div class="status-card {card_class}">
                        <div class="status-icon">✅</div>
                        <div class="status-label">安全</div>
                    </div>
                ''', unsafe_allow_html=True)

    # 接続状態
    if connected:
        st.markdown('''
            <div class="connection-status connected">
                🟢 センサー接続中
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div class="connection-status disconnected">
                🔴 センサー未接続
            </div>
        ''', unsafe_allow_html=True)

    # 更新時刻
    st.markdown(f'''
        <div class="update-time">
            最終更新: {format_time_ago(updated_at)}
        </div>
    ''', unsafe_allow_html=True)

# 区切り線
st.markdown("<br>", unsafe_allow_html=True)

# 自動更新
col1, col2 = st.columns([3, 1])
with col1:
    auto_refresh = st.checkbox("自動更新 (2秒間隔)", value=True)
with col2:
    if st.button("🔄"):
        st.rerun()

if auto_refresh:
    time.sleep(2)
    st.rerun()

# フッター
st.markdown('''
    <div class="footer">
        Bath Sensor Monitor v1.0<br>
        Remote Dashboard
    </div>
''', unsafe_allow_html=True)
