import streamlit as st
import logic  # <--- This imports Suvedhan's backend script

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PRISM - AI News Analyzer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (The "Dark/Neon" Look) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #00ffcc; /* Neon Cyan Text */
        border: 1px solid #00ffcc;
    }
    h1 {
        color: #00ffcc;
        text-align: center;
        font-family: 'Courier New', sans-serif;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("💎 PRISM")
st.markdown("<h3 style='text-align: center; color: white;'>The Anti-Echo Chamber News Engine</h3>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Controls")
    st.info("Status: ONLINE 🟢")
    if st.checkbox("Enable Demo Mode"):
        logic.DEMO_MODE = True
        st.warning("⚠️ Demo Mode Active (Using Backup Data)")
    else:
        logic.DEMO_MODE = False

# --- MAIN INPUT ---
query = st.text_input("Enter a controversial topic:", placeholder="e.g., Bitcoin, AI Regulation, Carbon Tax...")

if st.button("Analyze Bias 🚀", use_container_width=True):
    if not query:
        st.error("Please enter a topic first!")
    else:
        with st.spinner(f"🔍 Prism is refracting news on '{query}'..."):
            # CALL SUVEDHAN'S BACKEND FUNCTION
            data = logic.get_analysis(query)
            
            if "error" in data:
                st.error(data["error"])
            else:
                # --- DISPLAY RESULTS (The 3 Columns) ---
                col1, col2, col3 = st.columns(3)
                
                # COLUMN 1: THE CRITIC (Red)
                with col1:
                    st.markdown(f"<div class='metric-card' style='border-left: 5px solid #ff4b4b;'><h3>🛑 {data['critic']['title']}</h3></div>", unsafe_allow_html=True)
                    for point in data['critic']['points']:
                        st.write(f"• {point}")

                # COLUMN 2: THE FACTS (Blue/Grey)
                with col2:
                    st.markdown(f"<div class='metric-card' style='border-left: 5px solid #a6a6a6;'><h3>⚖️ {data['facts']['title']}</h3></div>", unsafe_allow_html=True)
                    for point in data['facts']['points']:
                        st.write(f"• {point}")

                # COLUMN 3: THE PROPONENT (Green)
                with col3:
                    st.markdown(f"<div class='metric-card' style='border-left: 5px solid #00cc00;'><h3>✅ {data['proponent']['title']}</h3></div>", unsafe_allow_html=True)
                    for point in data['proponent']['points']:
                        st.write(f"• {point}")