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
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- PERMANENT DARK THEME PALETTE ---
bg_color = "#0E1117"      # Deep Black/Blue Background
text_color = "#E0E0E0"    # Soft White Text
card_bg = "#1A1C24"       # Dark Grey Card Background
border_color = "#333333"  # Subtle Border
accent_color = "#00D2FF"  # Neon Cyan Accent
shadow_color = "rgba(0,0,0,0.3)"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    /* MAIN BACKGROUND */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}

    /* INPUT FIELD Styling */
    .stTextInput > div > div > input {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 12px;
        font-size: 1.1rem;
    }}
    
    /* === BUTTON STYLING (Permanent Blue Gradient) === */
    div.stButton > button {{
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        padding: 0.6rem 2rem !important;
        transition: transform 0.2s !important;
        box-shadow: 0 4px 6px {shadow_color} !important;
    }}
    
    div.stButton > button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 6px 15px rgba(0, 114, 255, 0.4) !important;
    }}
    
    /* NEWS CARDS */
    .news-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px {shadow_color};
        height: 100%;
        transition: transform 0.2s;
    }}
    .news-card:hover {{
        transform: translateY(-3px);
    }}
    
    /* TRENDING PILLS */
    .trend-pill {{
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: {card_bg};
        border: 1px solid {border_color};
        color: {text_color};
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px {shadow_color};
        font-weight: 500;
        height: 100px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- HEADER WITH LOGO ---
col_logo, col_title = st.columns([1, 8])

with col_logo:
    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 22H22L12 2Z" stroke="{text_color}" stroke-width="2" stroke-linejoin="round"/>
                <path d="M12 6L12 22" stroke="{accent_color}" stroke-width="2"/>
                <path d="M12 6L7 22" stroke="{text_color}" stroke-width="1" opacity="0.5"/>
                <path d="M12 6L17 22" stroke="{text_color}" stroke-width="1" opacity="0.5"/>
            </svg>
        </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown(f"""
        <div style="padding-top: 10px;">
            <h1 style="margin: 0; color: {text_color}; font-size: 2.5rem;">PRISM</h1>
            <p style="margin: 0; color: {text_color}; opacity: 0.7; font-size: 1.1rem;">
                Refracting the Truth from the Noise
            </p>
        </div>
    """, unsafe_allow_html=True)

st.write("") 

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Controls")
    # Toggle Removed - Dark Mode is now Standard
    
    if st.checkbox("Enable Demo Mode"):
        logic.DEMO_MODE = True
        st.caption("Using Offline Backup Data")
    else:
        logic.DEMO_MODE = False
    
    st.divider()
    st.subheader("Recent Searches")
    if st.session_state['history']:
        for item in reversed(st.session_state['history'][-5:]):
            st.caption(f"• {item}")
    else:
        st.caption("No history yet.")

# --- SEARCH BAR ---
with st.form(key='search_form'):
    col1, col2 = st.columns([5, 1])
    with col1:
        query_input = st.text_input("Search", placeholder="Enter topic (e.g. AI Regulation, Bitcoin...)", label_visibility="collapsed")
    with col2:
        submit_btn = st.form_submit_button("Analyze 🚀")

# --- MAIN CONTENT ---
if not query_input:
    st.markdown("### 🔥 Trending Debates")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown(f"<div class='trend-pill'>🤖 AI Regulation<br><span style='font-size:0.8em; opacity:0.7'>Safety vs Speed</span></div>", unsafe_allow_html=True)
    with t2:
        st.markdown(f"<div class='trend-pill'>🌍 Climate Policies<br><span style='font-size:0.8em; opacity:0.7'>Growth vs Green</span></div>", unsafe_allow_html=True)
    with t3:
        st.markdown(f"<div class='trend-pill'>🪙 Crypto Future<br><span style='font-size:0.8em; opacity:0.7'>Freedom vs Control</span></div>", unsafe_allow_html=True)
    with t4:
        st.markdown(f"<div class='trend-pill'>🚗 EV Transition<br><span style='font-size:0.8em; opacity:0.7'>Cost vs Clean</span></div>", unsafe_allow_html=True)
        
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.info("💡 **Tip:** Try searching for 'Border Gavaskar Trophy' to see live news analysis.")
    with c2:
        # Safe model name check
        model_name = "Auto-Detect"
        if hasattr(logic, 'model') and hasattr(logic.model, 'model_name'):
             model_name = logic.model.model_name
        st.success(f"⚡ **Status:** System Online")

if query_input and submit_btn:
    if query_input not in st.session_state['history']:
        st.session_state['history'].append(query_input)

    with st.spinner(f"🔍 Prism is refracting news on '{query_input}'..."):
        data = logic.get_analysis(query_input)
        
        if "error" in data:
            st.error(data["error"])
        else:
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown(f"""
                <div class="news-card" style="border-top: 5px solid #FF4B4B;">
                    <h3 style="color: #FF4B4B;">🛑 Concerns</h3>
                    <p style="font-weight: bold; font-size: 1.1rem;">{data['critic']['title']}</p>
                    <ul style="padding-left: 20px;">
                    {''.join([f'<li style="margin-bottom: 8px;">{p}</li>' for p in data['critic']['points']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="news-card" style="border-top: 5px solid {accent_color};">
                    <h3 style="color: {accent_color};">⚖️ Key Data</h3>
                    <p style="font-weight: bold; font-size: 1.1rem;">{data['facts']['title']}</p>
                    <ul style="padding-left: 20px;">
                    {''.join([f'<li style="margin-bottom: 8px;">{p}</li>' for p in data['facts']['points']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="news-card" style="border-top: 5px solid #00D26A;">
                    <h3 style="color: #00D26A;">✅ Benefits</h3>
                    <p style="font-weight: bold; font-size: 1.1rem;">{data['proponent']['title']}</p>
                    <ul style="padding-left: 20px;">
                    {''.join([f'<li style="margin-bottom: 8px;">{p}</li>' for p in data['proponent']['points']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)