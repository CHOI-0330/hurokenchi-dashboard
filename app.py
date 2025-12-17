# -*- coding: utf-8 -*-
"""
Bath Sensor Dashboard - Streamlit App (Native Components)
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

# 상태 카드 크기 확대 CSS
st.markdown("""
<style>
    /* 상태 카드 텍스트 크기 확대 */
    div[data-testid="stAlert"] p {
        font-size: 1.5rem !important;
        padding: 0.5rem 0 !important;
    }
    /* 컨테이너 내 텍스트 크기 확대 */
    div[data-testid="stVerticalBlock"] .stMarkdown p {
        font-size: 1.3rem;
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
st.title("🛁 お風呂センサー")
st.caption("リモート状態モニター")

# 状態取得
state = get_sensor_state()

if state is None:
    st.error("センサーに接続できません")
    st.info("ローカルのFlaskサーバーが起動しているか確認してください")
else:
    mode = state.get('mode', 'location')
    status = state.get('status', 1)
    is_drowning = state.get('is_drowning', False)
    connected = state.get('connected', False)
    updated_at = state.get('updated_at')

    # モード表示
    if mode == 'location':
        st.info("📍 **位置検知モード**")
    else:
        st.warning("🚨 **溺水検知モード**")

    st.divider()

    # ステータス表示 (大きいカード)
    col1, col2 = st.columns(2)

    if mode == 'location':
        # 位置検知モード
        with col1:
            if status == 1:
                st.success("## 🚿 洗い場")
            else:
                st.container(border=True).markdown("## 🚿 洗い場")

        with col2:
            if status == 2:
                st.success("## 🛁 浴槽")
            else:
                st.container(border=True).markdown("## 🛁 浴槽")

    else:
        # 溺水検知モード
        with col1:
            if status == 1:
                st.success("## 🛁 正常")
            else:
                st.container(border=True).markdown("## 🛁 浴槽")

        with col2:
            if is_drowning:
                st.error("## ⚠️ 溺水検知！")
            elif status == 2:
                st.warning("## ⚠️ 注意")
            else:
                st.container(border=True).markdown("## ✅ 安全")

    st.divider()

    # メトリクス表示
    col1, col2 = st.columns(2)

    with col1:
        if connected:
            st.metric(label="接続状態", value="🟢 接続中")
        else:
            st.metric(label="接続状態", value="🔴 未接続")

    with col2:
        st.metric(label="最終更新", value=format_time_ago(updated_at))

# 自動更新オプション
st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    auto_refresh = st.checkbox("自動更新 (2秒間隔)", value=True)
with col2:
    if st.button("🔄 更新"):
        st.rerun()

if auto_refresh:
    time.sleep(2)
    st.rerun()

# フッター
st.divider()
st.caption("Bath Sensor Monitor v1.0")
