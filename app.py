# -*- coding: utf-8 -*-
"""
Bath Sensor Dashboard - 独居高齢者見守りアプリ
安全状態を一目で確認できるシンプルなデザイン
"""
import streamlit as st
from supabase import create_client
from datetime import datetime
import time

# ページ設定 (must be first Streamlit command!)
st.set_page_config(
    page_title="お風呂見守り",
    page_icon="🛁",
    layout="centered"
)

# セッション履歴初期化
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_status' not in st.session_state:
    st.session_state.last_status = None

# カスタムCSS - 大きな状態表示
st.markdown("""
<style>
    /* メイン状態カード */
    .safety-card {
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    .safety-safe {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 3px solid #28a745;
    }
    .safety-caution {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border: 3px solid #ffc107;
    }
    .safety-danger {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 3px solid #dc3545;
    }
    .safety-text {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .safety-icon {
        font-size: 4rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    /* サブ情報 */
    .sub-info {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin: 0.5rem 0;
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
    """更新時刻を表示"""
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

def get_safety_status(mode, status, is_drowning):
    """
    安全状態を判定（3状態対応）

    Args:
        mode: 'location' または 'drowning'
        status: 0=不在, 1=シャワー/安全, 2=浴槽/危険
        is_drowning: 溺水フラグ
    """
    if mode == 'drowning':
        # 溺水検知モード
        if status == 0:
            return 'caution', '不在', '📡', '浴室に検知がありません'
        elif status == 1:
            return 'safe', '安全', '✅', '正常に入浴中です'
        elif status == 2 or is_drowning:
            return 'danger', '危険', '⚠️', '溺水の可能性があります！'
        else:
            return 'safe', '安全', '✅', '正常に入浴中です'
    else:
        # 位置検知モード
        if status == 0:
            return 'caution', '不在', '📡', '浴室に検知がありません'
        elif status == 1:
            return 'safe', '安全', '✅', 'シャワーエリアで検知中'
        elif status == 2:
            return 'safe', '安全', '✅', '浴槽エリアで検知中'
        else:
            return 'safe', '安全', '✅', '正常に検知中です'

def get_location_text(mode, status):
    """
    現在位置テキスト（3状態対応）

    Args:
        mode: 'location' または 'drowning'
        status: 0=不在, 1=シャワー/安全, 2=浴槽/危険
    """
    if mode == 'location':
        # 位置検知モード
        if status == 0:
            return '📡 不在'
        elif status == 1:
            return '🚿 洗い場'
        else:
            return '🛁 浴槽'
    else:
        # 溺水検知モード
        if status == 0:
            return '📡 不在'
        elif status == 1:
            return '🛁 浴槽 (安全)'
        else:
            return '🛁 浴槽 (危険)'

# =============================================================================
# メインUI
# =============================================================================

# ヘッダー
st.markdown("## 🛁 お風呂見守り")

# 状態取得
state = get_sensor_state()

if state is None:
    st.markdown("""
    <div class="safety-card safety-caution">
        <span class="safety-icon">📡</span>
        <p class="safety-text">接続待ち</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("センサーからのデータを待っています...")
else:
    mode = state.get('mode', 'location')
    status = state.get('status', 1)
    is_drowning = state.get('is_drowning', False)
    updated_at = state.get('updated_at')

    # 安全状態判定
    safety_level, safety_text, safety_icon, safety_desc = get_safety_status(mode, status, is_drowning)

    # メイン状態カード
    st.markdown(f"""
    <div class="safety-card safety-{safety_level}">
        <span class="safety-icon">{safety_icon}</span>
        <p class="safety-text">{safety_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # 状態説明
    st.markdown(f'<p class="sub-info">{safety_desc}</p>', unsafe_allow_html=True)

    st.divider()

    # サブ情報（2列）
    col1, col2 = st.columns(2)

    with col1:
        location = get_location_text(mode, status)
        st.metric(label="現在位置", value=location)

    with col2:
        st.metric(label="最終更新", value=format_time_ago(updated_at))

    # モード表示（小さく）
    mode_text = "📍 位置検知モード" if mode == 'location' else "🚨 溺水検知モード"
    st.caption(mode_text)

    # 履歴記録 (状態変化時のみ)
    current_key = f"{mode}_{status}_{is_drowning}"
    if st.session_state.last_status != current_key:
        st.session_state.history.insert(0, {
            'time': datetime.now().strftime('%H:%M:%S'),
            'status': safety_text,
            'icon': safety_icon,
            'location': get_location_text(mode, status),
            'level': safety_level
        })
        # 最大20件保持
        st.session_state.history = st.session_state.history[:20]
        st.session_state.last_status = current_key

    # 履歴表示
    if st.session_state.history:
        st.divider()
        with st.expander("📋 状態履歴", expanded=False):
            for h in st.session_state.history:
                if h['level'] == 'danger':
                    st.error(f"{h['time']} - {h['icon']} {h['status']} ({h['location']})")
                elif h['level'] == 'caution':
                    st.warning(f"{h['time']} - {h['icon']} {h['status']} ({h['location']})")
                else:
                    st.success(f"{h['time']} - {h['icon']} {h['status']} ({h['location']})")

# 自動更新
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    auto_refresh = st.checkbox("自動更新 (2秒)", value=True)
with col2:
    if st.button("🔄"):
        st.rerun()

if auto_refresh:
    time.sleep(2)
    st.rerun()

# フッター
st.caption("Bath Monitor v2.0 - 独居高齢者見守りシステム")
