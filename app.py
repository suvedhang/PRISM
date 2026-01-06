import streamlit as st
import logic

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="PRISM - News Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================
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

ACCENT_COLOR = "#00D2FF"

# =========================================================
# CALLBACKS
# =========================================================
def click_history(topic):
    st.session_state.search_query = topic
    st.session_state.active_tab = "results"
    if topic not in st.session_state.results_cache:
        run_analysis(topic)


def run_analysis(topic):
    settings = {
        "region": st.session_state.region,
        "intensity": st.session_state.intensity,
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


def clear_history():
    st.session_state.history.clear()
    st.session_state.results_cache.clear()
    st.session_state.active_tab = "trending"

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 💎 PRISM")
    st.caption("Media Bias & News Intelligence")

    st.divider()

    with st.expander("⚙️ Intelligence Config", expanded=True):
        st.selectbox(
            "🌍 Search Region",
            ["Global", "India", "USA", "UK", "Europe", "Canada", "Australia"],
            key="region",
        )
        st.select_slider(
            "🔥 Critic Intensity",
            ["Standard", "Skeptical", "Ruthless"],
            key="intensity",
        )

        demo = st.checkbox("🔌 Offline Demo Mode", value=logic.DEMO_MODE)
        logic.DEMO_MODE = demo

        if st.button("🗑️ Purge Cache"):
            clear_history()
            st.rerun()

    st.divider()

    st.subheader("🕒 History")
    if st.session_state.history:
        for topic in reversed(st.session_state.history):
            st.button(f"📄 {topic}", on_click=click_history, args=(topic,))
    else:
        st.caption("No searches yet.")

# =========================================================
# GLOBAL CSS (FIXED UI POLISH)
# =========================================================
st.markdown(
    f"""
<style>
.stApp {{
    background-color: #0E1117;
    color: #E0E0E0;
}}

.news-card {{
    background-color: #1A1C24;
    border: 1px solid #333;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}}

.meta-bar {{
    color: {ACCENT_COLOR};
    font-size: 0.85rem;
    margin-bottom: 15px;
}}

.badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 8px;
    background: #1A1C24;
    border: 1px solid #333;
    margin-right: 8px;
}}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HEADER
# =========================================================
c1, c2 = st.columns([1, 8])
with c1:
    st.markdown(
        f"""
<svg width="60" height="60" viewBox="0 0 24 24" fill="none">
<path d="M12 2L2 22H22L12 2Z" stroke="#E0E0E0" stroke-width="2"/>
<path d="M12 6L12 22" stroke="{ACCENT_COLOR}" stroke-width="2"/>
</svg>
""",
        unsafe_allow_html=True,
    )

with c2:
    st.title("PRISM")
    st.caption("Refracting Truth from Media Noise")

# =========================================================
# SEARCH BAR
# =========================================================
col1, col2 = st.columns([5, 1])
with col1:
    st.text_input(
        "Search",
        placeholder="Enter topic (movie, tech, politics, crypto...)",
        label_visibility="collapsed",
        key="search_query",
    )

with col2:
    analyze_clicked = st.button("Analyze 🚀")

if analyze_clicked and st.session_state.search_query:
    run_analysis(st.session_state.search_query)

# =========================================================
# RESULTS VIEW
# =========================================================
if (
    st.session_state.active_tab == "results"
    and st.session_state.search_query
    and st.session_state.search_query in st.session_state.results_cache
):
    data = st.session_state.results_cache[st.session_state.search_query]

    st.markdown(f"### 🔍 Analysis for **{data['topic']}**")

    st.markdown(
        f"""
<div class="meta-bar">
<span class="badge">Bias: {data.get('bias', 'Neutral')}</span>
<span class="badge">Confidence: {data.get('confidence', 'N/A')}</span>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(f"**Why this matters:** {data.get('why_it_matters', '')}")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
<div class="news-card">
<h3 style="color:#FF4B4B">🛑 Concerns</h3>
<ul>{"".join(f"<li>{p}</li>" for p in data["critic"]["points"])}</ul>
</div>
""",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
<div class="news-card">
<h3 style="color:{ACCENT_COLOR}">⚖️ Key Data</h3>
<ul>{"".join(f"<li>{p}</li>" for p in data["facts"]["points"])}</ul>
</div>
""",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
<div class="news-card">
<h3 style="color:#00D26A">✅ Benefits</h3>
<ul>{"".join(f"<li>{p}</li>" for p in data["proponent"]["points"])}</ul>
</div>
""",
            unsafe_allow_html=True,
        )

    if data.get("sources"):
        st.markdown(
            f"**Sources:** {', '.join(data['sources'])}"
        )

# =========================================================
# TRENDING VIEW
# =========================================================
else:
    st.markdown("### 🔥 Trending Topics")

    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.button("🤖 AI Regulation", on_click=click_history, args=("AI Regulation",))
    with t2:
        st.button("🌍 Climate Policy", on_click=click_history, args=("Climate Policy",))
    with t3:
        st.button("🪙 Crypto Regulation", on_click=click_history, args=("Crypto Regulation",))
    with t4:
        st.button("🚗 EV Transition", on_click=click_history, args=("EV Transition",))
