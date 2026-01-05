import streamlit as st
import logic

from backend.auth.auth_utils import (
    firebase_login,
    firebase_signup,
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="PRISM - News Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACCENT_COLOR = "#00D2FF"

# --------------------------------------------------
# GLOBAL CSS (SHARED FOR LOGIN + MAIN APP)
# --------------------------------------------------
def inject_global_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background: radial-gradient(circle at top, #0E1117 0%, #05070D 65%);
        color: #E0E0E0;
        font-family: 'Inter', sans-serif;
    }}

    h1, h2, h3 {{
        letter-spacing: -0.5px;
    }}

    input {{
        background-color: #1A1C24 !important;
        color: #E0E0E0 !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        padding: 12px !important;
    }}

    input:focus {{
        border-color: {ACCENT_COLOR} !important;
        box-shadow: 0 0 10px {ACCENT_COLOR}40;
    }}

    div.stButton > button {{
        background: linear-gradient(135deg, {ACCENT_COLOR}, #0072FF);
        color: white !important;
        border: none !important;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1.8rem;
        transition: 0.2s ease-in-out;
    }}

    div.stButton > button:hover {{
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(0,210,255,0.25);
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0B0F1A, #070A12);
        padding: 20px;
    }}

    section[data-testid="stSidebar"] button {{
        background: #1A1C24 !important;
        color: #E0E0E0 !important;
        border: 1px solid #2A2D3A !important;
        text-align: left;
        width: 100%;
    }}

    .news-card {{
        background: #1A1C24;
        border: 1px solid #2A2D3A;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        height: 100%;
    }}

    .auth-box {{
        max-width: 520px;
        margin: auto;
        padding: 40px;
        background: #0F1320;
        border-radius: 20px;
        border: 1px solid #2A2D3A;
        box-shadow: 0 25px 60px rgba(0,0,0,0.6);
    }}
    </style>
    """, unsafe_allow_html=True)

inject_global_css()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "history" not in st.session_state:
    st.session_state.history = []

if "results_cache" not in st.session_state:
    st.session_state.results_cache = {}

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "trending"

if "region" not in st.session_state:
    st.session_state.region = "Global"

if "intensity" not in st.session_state:
    st.session_state.intensity = "Standard"

# --------------------------------------------------
# AUTH UI
# --------------------------------------------------
def render_auth_page():
    inject_global_css()

    # --- BRAND HEADER ---
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:40px; margin-bottom:30px;">
            <svg width="70" height="70" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 22H22L12 2Z"
                      stroke="#E0E0E0" stroke-width="2"/>
                <path d="M12 6L12 22"
                      stroke="{ACCENT_COLOR}" stroke-width="2"/>
            </svg>
            <h1 style="margin-top:10px;">PRISM</h1>
            <p style="color:#9AA4B2; margin-top:-8px;">
                Refracting the Truth from the Noise
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- AUTH SECTION ---
    st.markdown("## 🔐 Login to PRISM")

    tab_login, tab_signup = st.tabs(["Login", "Create Account"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, msg = firebase_login(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error(msg)

    with tab_signup:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Sign Up"):
            success, msg = firebase_signup(new_email, new_password)
            if success:
                st.success("Account created. Please login.")
            else:
                st.error(msg)



# --------------------------------------------------
# CALLBACKS
# --------------------------------------------------
def click_history(topic):
    st.session_state.search_query = topic
    st.session_state.active_tab = "results"
    if topic not in st.session_state.results_cache:
        run_analysis(topic)

def run_analysis(topic):
    settings = {
        "region": st.session_state.region,
        "intensity": st.session_state.intensity
    }
    with st.spinner(f"💎 Refracting news for '{topic}'..."):
        data = logic.get_analysis(topic, settings)
        if "error" not in data:
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
            st.session_state.results_cache[topic] = data
            st.session_state.active_tab = "results"
        else:
            st.error(data["error"])

# --------------------------------------------------
# MAIN APP UI
# --------------------------------------------------
def render_main_app():
    inject_global_css()

    with st.sidebar:
        st.success(f"👤 Logged in as\n{st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.rerun()

        st.divider()

        st.selectbox(
            "🌍 Search Region",
            ["Global", "India", "USA", "UK", "Europe", "Canada", "Australia", "Asia"],
            key="region"
        )

        st.select_slider(
            "🔥 Critic Intensity",
            ["Standard", "Skeptical", "Ruthless"],
            key="intensity"
        )

        st.divider()
        st.subheader("🕒 History")

        if st.session_state.history:
            for topic in reversed(st.session_state.history):
                st.button(topic, on_click=click_history, args=(topic,))
        else:
            st.caption("No history yet.")

    # HEADER
    c1, c2 = st.columns([1, 8])
    with c1:
        st.markdown(
            f'<svg width="60" height="60" viewBox="0 0 24 24">'
            f'<path d="M12 2L2 22H22L12 2Z" stroke="#E0E0E0" stroke-width="2"/>'
            f'<path d="M12 6L12 22" stroke="{ACCENT_COLOR}" stroke-width="2"/>'
            f'</svg>',
            unsafe_allow_html=True,
        )
    with c2:
        st.title("PRISM")
        st.caption("Refracting the Truth from the Noise")

    # SEARCH
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input(
            "Search",
            placeholder="Enter topic...",
            label_visibility="collapsed",
            key="search_query",
        )
    with col2:
        analyze_clicked = st.button("Analyze 🚀")

    if analyze_clicked and st.session_state.search_query:
        run_analysis(st.session_state.search_query)

    # RESULTS / TRENDING
    if st.session_state.active_tab == "results" and st.session_state.search_query:
        topic = st.session_state.search_query
        data = st.session_state.results_cache.get(topic)

        if data:
            st.markdown(f"### 🔍 Analysis for **{topic}**")
            st.markdown("---")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(
                    f"<div class='news-card'><h3>🛑 Concerns</h3>"
                    f"<ul>{''.join([f'<li>{p}</li>' for p in data['critic']['points']])}</ul></div>",
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown(
                    f"<div class='news-card'><h3>⚖️ Key Data</h3>"
                    f"<ul>{''.join([f'<li>{p}</li>' for p in data['facts']['points']])}</ul></div>",
                    unsafe_allow_html=True,
                )

            with c3:
                st.markdown(
                    f"<div class='news-card'><h3>✅ Benefits</h3>"
                    f"<ul>{''.join([f'<li>{p}</li>' for p in data['proponent']['points']])}</ul></div>",
                    unsafe_allow_html=True,
                )

    else:
        st.markdown("### 🔥 Trending Debates")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.button("AI Regulation", on_click=click_history, args=("AI Regulation",))
        with c2: st.button("Climate Policy", on_click=click_history, args=("Climate Policy",))
        with c3: st.button("Crypto Laws", on_click=click_history, args=("Crypto Regulation",))
        with c4: st.button("EV Transition", on_click=click_history, args=("EV Transition",))

# --------------------------------------------------
# ROUTER
# --------------------------------------------------
if not st.session_state.logged_in:
    render_auth_page()
else:
    render_main_app()
