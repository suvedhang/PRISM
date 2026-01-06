import streamlit as st
import logic
# ===============================
# AUTH BRIDGE (DO NOT REMOVE)
# ===============================
from backend.auth.auth_utils import (
    firebase_login as _firebase_login,
    firebase_signup as _firebase_signup
)

def firebase_login(email: str, password: str):
    """
    Wrapper for Firebase login.
    Keeps app.py isolated from auth implementation.
    """
    try:
        return _firebase_login(email, password)
    except Exception as e:
        return False, str(e)

def firebase_signup(email: str, password: str):
    """
    Wrapper for Firebase signup.
    """
    try:
        return _firebase_signup(email, password)
    except Exception as e:
        return False, str(e)


# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="PRISM – News Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

ACCENT_COLOR = "#00D2FF"

# ===============================
# SESSION STATE INIT
# ===============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "results_cache" not in st.session_state:
    st.session_state.results_cache = {}

if "region" not in st.session_state:
    st.session_state.region = "Global"

if "intensity" not in st.session_state:
    st.session_state.intensity = "Standard"

# ===============================
# SHARED CSS (LOGIN + MAIN MATCH)
# ===============================
st.markdown(f"""
<style>
.stApp {{
    background-color: #0E1117;
    color: #E0E0E0;
}}

input {{
    background-color: #1A1C24 !important;
    color: #E0E0E0 !important;
    border-radius: 12px !important;
}}

button {{
    border-radius: 12px !important;
}}

.card {{
    background-color: #1A1C24;
    border: 1px solid #333;
    border-radius: 15px;
    padding: 20px;
}}

.accent {{
    color: {ACCENT_COLOR};
}}
</style>
""", unsafe_allow_html=True)

# ===============================
# AUTH PAGE
# ===============================
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login to **PRISM**")
    st.caption("Refracting the Truth from the Noise")

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            success, msg = logic.firebase_login(email, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.active_tab = "home"
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        email = st.text_input("New Email", key="signup_email")
        password = st.text_input("New Password", type="password", key="signup_pass")

        if st.button("Create Account"):
            success, msg = logic.firebase_signup(email, password)
            if success:
                st.success("Account created. Please login.")
            else:
                st.error(msg)

# ===============================
# LOGOUT
# ===============================
def logout():
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.active_tab = "home"
    st.session_state.search_query = ""
    st.rerun()

# ===============================
# CALLBACKS
# ===============================
def click_history(topic):
    st.session_state.search_query = topic
    run_analysis(topic)

def run_analysis(topic):
    cache_key = f"{topic}_{st.session_state.intensity}"

    settings = {
        "region": st.session_state.region,
        "intensity": st.session_state.intensity
    }

    with st.spinner(f"💎 Analyzing '{topic}'..."):
        if cache_key not in st.session_state.results_cache:
            data = logic.get_analysis(topic, settings)
            if "error" in data:
                st.error(data["error"])
                return

            st.session_state.results_cache[cache_key] = data
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)

        st.session_state.active_tab = "results"

# ===============================
# MAIN APP (AUTHENTICATED)
# ===============================
def render_app():
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.success(f"👤 Logged in as\n\n{st.session_state.user_email}")
        st.button("Logout", on_click=logout)

        st.divider()

        st.subheader("⚙️ Intelligence Config")
        st.selectbox(
            "🌍 Search Region",
            ["Global", "India", "USA", "UK", "Europe", "Asia"],
            key="region"
        )

        st.select_slider(
            "🔥 Critic Intensity",
            options=["Standard", "Skeptical", "Ruthless"],
            key="intensity"
        )

        st.checkbox("🔌 Offline Demo Mode", key="DEMO_MODE")
        logic.DEMO_MODE = st.session_state.DEMO_MODE

        if st.button("🗑️ Purge Cache"):
            st.session_state.results_cache.clear()
            st.session_state.active_tab = "home"
            st.rerun()

        st.divider()
        st.subheader("🕒 History")
        if st.session_state.history:
            for h in reversed(st.session_state.history):
                st.button(h, on_click=click_history, args=(h,))
        else:
            st.caption("No searches yet.")

    # ---------- HEADER ----------
    c1, c2 = st.columns([1, 8])
    with c1:
        st.markdown("### 🔺")
    with c2:
        st.markdown("# PRISM")
        st.caption("Refracting the Truth from the Noise")

    # ---------- SEARCH ----------
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input(
            "Search topic",
            placeholder="Enter topic (movie, tech, politics, crypto...)",
            key="search_query",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("Analyze 🚀"):
            if st.session_state.search_query:
                run_analysis(st.session_state.search_query)

    # ---------- HOME (TRENDING) ----------
    if st.session_state.active_tab == "home":
        st.markdown("## 🔥 Trending Topics")
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.button("🤖 AI Regulation", on_click=click_history, args=("AI Regulation",))
        with t2:
            st.button("🌍 Climate Policy", on_click=click_history, args=("Climate Policy",))
        with t3:
            st.button("🪙 Crypto Regulation", on_click=click_history, args=("Crypto Regulation",))
        with t4:
            st.button("🚗 EV Transition", on_click=click_history, args=("EV Transition",))

    # ---------- RESULTS ----------
    if st.session_state.active_tab == "results":
        key = f"{st.session_state.search_query}_{st.session_state.intensity}"
        data = st.session_state.results_cache.get(key)

        if data:
            st.markdown(f"## 🔍 Analysis for **{data['topic']}**")
            st.markdown(
                f"<span class='accent'>Region: {st.session_state.region} | "
                f"Intensity: {st.session_state.intensity}</span>",
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(
                    f"<div class='card'><h3>🛑 Concerns</h3>"
                    + "".join(f"<li>{p}</li>" for p in data["critic"]["points"])
                    + "</div>",
                    unsafe_allow_html=True
                )

            with c2:
                st.markdown(
                    f"<div class='card'><h3>⚖️ Key Data</h3>"
                    + "".join(f"<li>{p}</li>" for p in data["facts"]["points"])
                    + "</div>",
                    unsafe_allow_html=True
                )

            with c3:
                st.markdown(
                    f"<div class='card'><h3>✅ Benefits</h3>"
                    + "".join(f"<li>{p}</li>" for p in data["proponent"]["points"])
                    + "</div>",
                    unsafe_allow_html=True
                )

# ===============================
# ENTRY POINT
# ===============================
if not st.session_state.authenticated:
    render_login()
else:
    render_app()
