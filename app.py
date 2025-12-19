import streamlit as st
import logic

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PRISM - News Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'history' not in st.session_state: st.session_state['history'] = []
if 'results_cache' not in st.session_state: st.session_state['results_cache'] = {}
if 'search_query' not in st.session_state: st.session_state['search_query'] = ""
if 'active_tab' not in st.session_state: st.session_state['active_tab'] = "trending"

# --- DEFAULTS ---
if 'region' not in st.session_state: st.session_state['region'] = "Global"
if 'intensity' not in st.session_state: st.session_state['intensity'] = "Standard"

# --- FIXED THEME (Cyber Blue) ---
ACCENT_COLOR = "#00D2FF"

# --- CALLBACKS ---
def perform_search(topic=None):
    if topic: st.session_state['search_query'] = topic
    current_topic = st.session_state['search_query']
    
    if current_topic:
        if current_topic in st.session_state['results_cache']:
            st.session_state['active_tab'] = "results"
            return

        settings = {
            "region": st.session_state['region'],
            "intensity": st.session_state['intensity']
        }

        data = logic.get_analysis(current_topic, settings)
        
        if "error" not in data:
            if current_topic not in st.session_state['history']:
                st.session_state['history'].append(current_topic)
            st.session_state['results_cache'][current_topic] = data
            st.session_state['active_tab'] = "results"
        else:
            st.error(data['error'])

def clear_history():
    st.session_state['history'] = []
    st.session_state['results_cache'] = {}
    st.session_state['active_tab'] = "trending"

# --- SIDEBAR (Settings) ---
with st.sidebar:
    model_name = "Auto-Detect"
    if hasattr(logic, 'model') and hasattr(logic.model, 'model_name'):
            model_name = logic.model.model_name
    
    st.info(f"● SYSTEM ONLINE\n\nAPI: {model_name}")
    st.divider()

    # --- INTELLIGENCE PANEL ---
    with st.expander("⚙️ INTELLIGENCE CONFIG", expanded=True):
        
        # 1. REGION FILTER (Expanded List)
        st.selectbox(
            "🌍 Search Region", 
            ["Global", "India", "USA", "UK", "Europe", "Canada", "Australia", "Middle East", "Asia"], 
            key='region'
        )
        
        # 2. CRITIC INTENSITY
        st.select_slider(
            "🔥 Critic Intensity", 
            options=["Standard", "Skeptical", "Ruthless"], 
            key='intensity'
        )
        
        # 3. DEMO & PURGE
        if st.checkbox("🔌 Offline Demo Mode", value=logic.DEMO_MODE):
            logic.DEMO_MODE = True
        else:
            logic.DEMO_MODE = False
            
        if st.button("🗑️ Purge Cache"):
            clear_history()
            st.rerun()

    st.divider()
    st.subheader("🕒 History")
    if st.session_state['history']:
        for topic in reversed(st.session_state['history']):
            st.button(f"📄 {topic}", on_click=perform_search, args=(topic,))
    else:
        st.caption("No history yet.")

# --- CSS STYLING (Fixed Blue Theme) ---
st.markdown(f"""
    <style>
    /* GLOBAL DARK THEME */
    .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
    
    /* INPUT BOX */
    .stTextInput > div > div > input {{
        background-color: #1A1C24; color: #E0E0E0; border: 1px solid #333; 
        border-radius: 12px; padding: 12px;
    }}
    .stTextInput > div > div > input:focus {{ 
        border-color: {ACCENT_COLOR}; 
        box-shadow: 0 0 10px {ACCENT_COLOR}40; 
    }}
    
    /* MAIN BUTTONS (Blue Gradient) */
    div.stButton > button {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #0072FF 100%);
        color: white !important; border: none; border-radius: 12px;
        font-weight: bold; padding: 0.6rem 2rem; width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    div.stButton > button:hover {{ transform: scale(1.02); }}
    
    /* SIDEBAR BUTTONS */
    [data-testid="stSidebar"] div.stButton > button {{
        background: #1A1C24; color: #E0E0E0 !important; border: 1px solid #333;
        background-image: none; text-align: left; padding-left: 15px; box-shadow: none;
    }}
    
    /* NEWS CARDS */
    .news-card {{
        background-color: #1A1C24; border: 1px solid #333; border-radius: 15px; padding: 20px; height: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* TIP BOXES */
    .tip-box {{
        background-color: #1A1C24; border-left: 4px solid {ACCENT_COLOR};
        padding: 15px; border-radius: 8px; font-size: 0.95rem; margin-top: 10px;
    }}
    
    /* EXPANDER HEADER FONT */
    .streamlit-expanderHeader {{ font-family: 'Courier New'; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([1, 8])
with c1:
    st.markdown(f'<svg width="60" height="60" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 22H22L12 2Z" stroke="#E0E0E0" stroke-width="2"/><path d="M12 6L12 22" stroke="{ACCENT_COLOR}" stroke-width="2"/></svg>', unsafe_allow_html=True)
with c2:
    st.title("PRISM")
    st.caption("Refracting the Truth from the Noise")

# --- SEARCH BAR ---
col1, col2 = st.columns([5, 1])
with col1: st.text_input("Search", placeholder="Enter topic...", label_visibility="collapsed", key="search_query")
with col2: st.button("Analyze 🚀", on_click=perform_search)

# --- MAIN CONTENT ---
if st.session_state['active_tab'] == "results" and st.session_state['search_query']:
    topic = st.session_state['search_query']
    if topic in st.session_state['results_cache']:
        data = st.session_state['results_cache'][topic]
        
        reg = st.session_state['region']
        inte = st.session_state['intensity']
        st.markdown(f"### 🔍 Analysis for: **{data.get('topic', topic)}**")
        st.markdown(f"<div style='color: {ACCENT_COLOR}; font-size: 0.8rem; margin-top: -10px; margin-bottom: 20px;'>REGION: {reg.upper()} | INTENSITY: {inte.upper()}</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"""<div class="news-card" style="border-top: 5px solid #FF4B4B;"><h3 style="color:#FF4B4B">🛑 Concerns</h3><p>{data['critic']['title']}</p><ul>{''.join([f'<li>{p}</li>' for p in data['critic']['points']])}</ul></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="news-card" style="border-top: 5px solid {ACCENT_COLOR};"><h3 style="color:{ACCENT_COLOR}">⚖️ Key Data</h3><p>{data['facts']['title']}</p><ul>{''.join([f'<li>{p}</li>' for p in data['facts']['points']])}</ul></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="news-card" style="border-top: 5px solid #00D26A;"><h3 style="color:#00D26A">✅ Benefits</h3><p>{data['proponent']['title']}</p><ul>{''.join([f'<li>{p}</li>' for p in data['proponent']['points']])}</ul></div>""", unsafe_allow_html=True)
    else: st.error("Data missing. Please try searching again.")

else:
    st.markdown("### 🔥 Trending Debates")
    t1, t2, t3, t4 = st.columns(4)
    with t1: st.button("🤖 AI Regulation", on_click=perform_search, args=("AI Regulation",))
    with t2: st.button("🌍 Climate Policy", on_click=perform_search, args=("Climate Policy",))
    with t3: st.button("🪙 Crypto Laws", on_click=perform_search, args=("Crypto Regulation",))
    with t4: st.button("🚗 EV Transition", on_click=perform_search, args=("EV Transition",))
    st.markdown("---")
    st.markdown("### 💡 Analyst Pro Tips")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"""<div class="tip-box"><b>🔍 Be Specific</b><br>Try "AI Safety Bill" vs "Tech".</div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="tip-box"><b>⚡ Real-Time</b><br>Fetching live data...</div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="tip-box"><b>⚖️ Bias Check</b><br>Review the Critic card.</div>""", unsafe_allow_html=True)