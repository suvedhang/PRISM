import streamlit as st
import logic

# --- PAGE SETUP ---
st.set_page_config(page_title="PRISM", page_icon="💎", layout="wide")
ACCENT = "#00D2FF"

# --- STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "results_cache" not in st.session_state: st.session_state.results_cache = {}
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "region" not in st.session_state: st.session_state.region = "Global"
if "intensity" not in st.session_state: st.session_state.intensity = "Standard"
if "active_tab" not in st.session_state: st.session_state.active_tab = "home"

# --- CSS ---
st.markdown(f"""
<style>
.stApp {{ background-color: #0E1117; color: #E0E0E0; }}
input {{ background-color: #1A1C24 !important; color: white !important; border-radius: 10px !important; }}
.card {{ background-color: #1A1C24; border: 1px solid #333; border-radius: 15px; padding: 20px; height: 100%; }}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def run_analysis(topic):
    st.session_state.search_query = topic
    st.session_state.active_tab = "results"
    
    with st.spinner(f"💎 Analyzing {topic}..."):
        settings = {"region": st.session_state.region, "intensity": st.session_state.intensity}
        data = logic.get_analysis(topic, settings)
        
        if "error" in data:
            st.error(data["error"])
        else:
            st.session_state.results_cache[topic] = data
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 PRISM")
    st.selectbox("Region", ["Global", "India", "USA"], key="region")
    st.select_slider("Intensity", ["Standard", "Skeptical", "Ruthless"], key="intensity")
    
    # DEMO SWITCH
    demo_on = st.checkbox("🔌 Demo Mode", value=logic.DEMO_MODE)
    logic.DEMO_MODE = demo_on

    if st.button("🗑️ Reset"):
        st.session_state.results_cache = {}
        st.rerun()
        
    st.subheader("History")
    for h in reversed(st.session_state.history):
        if st.button(h): run_analysis(h)

# --- MAIN ---
st.title("PRISM Analyzer")
q = st.text_input("Search", placeholder="Topic...", key="search_input")
if st.button("Analyze 🚀") or q:
    if st.session_state.search_input: run_analysis(st.session_state.search_input)

# --- RESULTS ---
if st.session_state.active_tab == "results" and st.session_state.search_query:
    topic = st.session_state.search_query
    data = st.session_state.results_cache.get(topic)
    
    if data and "error" not in data:
        st.subheader(f"Results for: {data.get('topic', topic)}")
        c1, c2, c3 = st.columns(3)
        
        # SAFE RENDERING - NO CRASHES
        critic = data.get("critic", {}).get("points", ["No data"])
        facts = data.get("facts", {}).get("points", ["No data"])
        benefits = data.get("proponent", {}).get("points", ["No data"])
        
        with c1: st.markdown(f"<div class='card'><h3 style='color:#FF4B4B'>🛑 Concerns</h3>{''.join([f'<li>{p}</li>' for p in critic])}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='card'><h3 style='color:#00D2FF'>⚖️ Facts</h3>{''.join([f'<li>{p}</li>' for p in facts])}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='card'><h3 style='color:#00D26A'>✅ Benefits</h3>{''.join([f'<li>{p}</li>' for p in benefits])}</div>", unsafe_allow_html=True)

else:
    st.subheader("🔥 Trending")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🤖 AI Regulation"): run_analysis("AI Regulation")
    if c2.button("🌍 Climate"): run_analysis("Climate Policy")
    if c3.button("🪙 Crypto"): run_analysis("Crypto Regulation")
    if c4.button("🚗 EVs"): run_analysis("EV Transition")