import streamlit as st
import logic

from backend.auth.auth_utils import (
    firebase_login,
    firebase_signup,
    firebase_logout
)

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------
st.set_page_config(
    page_title="PRISM - News Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

ACCENT_COLOR = "#00D2FF"

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #E0E0E0; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔐 Login to PRISM")

    tab_login, tab_signup = st.tabs(["Login", "Create Account"])

    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, msg = firebase_login(email, password)
            if success:
                st.session_state.authenticated = True
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
                st.success("Account created. You can now log in.")
            else:
                st.error(msg)

# --------------------------------------------------
# CORE LOGIC
# --------------------------------------------------
def run_analysis(topic):
    settings = {
        "region": st.session_state.region,
        "intensity": st.session_state.intensity
    }

    with st.spinner(f"💎 Refracting news for '{topic}'..."):
        data = logic.get_analysis(topic, settings)

        if "error" in data:
            st.error(data["error"])
            return

        if topic not in st.session_state.history:
            st.session_state.history.append(topic)

        st.session_state.results_cache[topic] = data
        st.session_state.active_tab = "results"

def click_history(topic):
    st.session_state.search_query = topic
    st.session_state.active_tab = "results"

    if topic not in st.session_state.results_cache:
        run_analysis(topic)

def clear_history():
    st.session_state.history = []
    st.session_state.results_cache = {}
    st.session_state.active_tab = "trending"

# --------------------------------------------------
# MAIN PRISM APP
# --------------------------------------------------
def render_prism_app():
    # ---------- CSS (RESTORED) ----------
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #0E1117; color: #E0E0E0; }}

        .stTextInput input {{
            background-color: #1A1C24;
            color: #E0E0E0;
            border-radius: 12px;
            border: 1px solid #333;
            padding: 12px;
        }}

        div.stButton > button {{
            background: linear-gradient(135deg, {ACCENT_COLOR}, #0072FF);
            color: white;
            border-radius: 12px;
            font-weight: bold;
            padding: 0.6rem 2rem;
            border: none;
        }}

        .news-card {{
            background-color: #1A1C24;
            border: 1px solid #333;
            border-radius: 15px;
            padding: 20px;
            height: 100%;
        }}

        .tip-box {{
            background-color: #1A1C24;
            border-left: 4px solid {ACCENT_COLOR};
            padding: 15px;
            border-radius: 8px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.success(f"👤 Logged in as\n{st.session_state.user_email}")

        if st.button("Logout"):
            firebase_logout()
            st.session_state.authenticated = False
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

        if st.checkbox("🔌 Offline Demo Mode", value=logic.DEMO_MODE):
            logic.DEMO_MODE = True
        else:
            logic.DEMO_MODE = False

        if st.button("🗑️ Purge Cache"):
            clear_history()
            st.rerun()

        st.divider()
        st.subheader("🕒 History")

        for topic in reversed(st.session_state.history):
            st.button(topic, on_click=click_history, args=(topic,))

    # ---------- HEADER ----------
    st.title("PRISM")
    st.caption("Refracting the Truth from the Noise")

    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input("Search", key="search_query", label_visibility="collapsed")
    with col2:
        if st.button("Analyze 🚀"):
            if st.session_state.search_query:
                run_analysis(st.session_state.search_query)

    st.divider()

    # ---------- RESULTS ----------
    if st.session_state.active_tab == "results":
        topic = st.session_state.search_query
        data = st.session_state.results_cache.get(topic)

        if not data:
            return

        st.markdown(f"## 🔍 Analysis for **{topic}**")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
                <div class="news-card">
                <h3 style="color:#FF4B4B">🛑 Concerns</h3>
                <ul>{''.join(f"<li>{p}</li>" for p in data["critic"]["points"])}</ul>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
                <div class="news-card">
                <h3 style="color:{ACCENT_COLOR}">⚖️ Key Data</h3>
                <ul>{''.join(f"<li>{p}</li>" for p in data["facts"]["points"])}</ul>
                </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
                <div class="news-card">
                <h3 style="color:#00D26A">✅ Benefits</h3>
                <ul>{''.join(f"<li>{p}</li>" for p in data["proponent"]["points"])}</ul>
                </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("## 🔥 Trending Debates")
        t1, t2, t3, t4 = st.columns(4)
        t1.button("AI Regulation", on_click=click_history, args=("AI Regulation",))
        t2.button("Climate Policy", on_click=click_history, args=("Climate Policy",))
        t3.button("Crypto Regulation", on_click=click_history, args=("Crypto Regulation",))
        t4.button("EV Transition", on_click=click_history, args=("EV Transition",))

# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if not st.session_state.authenticated:
    render_auth_page()
else:
    render_prism_app()
