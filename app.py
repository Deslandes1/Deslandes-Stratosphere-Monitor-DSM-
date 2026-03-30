import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import requests
from datetime import datetime

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="DSM - Deslandes Stratosphere Monitor", layout="wide", page_icon="🇭🇹")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# --- 2. AUTHENTICATION ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "20082010":
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.error("❌ Access Denied")

    if not st.session_state["authenticated"]:
        st.markdown("<h1 style='text-align: center;'>🇭🇹</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>DESLANDES STRATOSPHERE MONITOR</h2>", unsafe_allow_html=True)
        st.text_input("Enter Access Key to Unlock System", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- 3. BRANDING & LICENSE ---
OWNER_INFO = """
**Developer:** GlobaLInternet.py  
**Owner:** Gesner Deslandes  
**Location:** 🇭🇹 Port-au-Prince, Haiti  
**Contact:** (509)-4738-5663  
*(Accepted: PRISME Transfer for Sales)* **Email:** deslandes78@gmail.com
"""

SOFTWARE_LICENSE = """
### 📜 DSM PROPRIETARY LICENSE
© 2026 GlobaLInternet.py. All Rights Reserved.
Owner: Gesner Deslandes.
Unauthorized distribution is prohibited.
**MADE IN HAITI**
"""

# --- 4. MULTI-MODE DATA ENGINE ---
def get_radar_data(mode, username, password):
    """Unified engine for Aircraft, Satellite, and Missile detection."""
    if mode == "Aircraft" and not st.session_state.get('demo_mode', True):
        # REAL-TIME OPENSKY INTEGRATION
        url = "https://opensky-network.org/api/states/all"
        try:
            auth = (username, password) if username and password else None
            response = requests.get(url, auth=auth, timeout=5)
            if response.status_code == 200:
                states = response.json().get('states', [])[:15]
                return [{"ID": s[1] or s[0], "Dist": np.random.randint(500, 2500), "Deg": np.random.randint(0, 360), "Spd": int(s[9]*3.6) if s[9] else 0, "Type": "Live Aircraft"} for s in states]
        except: pass
    
    # SIMULATED / CACHED MODES (Satellites & Missiles)
    if mode == "Satellite":
        return [
            {"ID": "ISS-CORE", "Dist": 2800, "Deg": (time.time()*5)%360, "Spd": 27600, "Type": "LEO Satellite"},
            {"ID": "STARLINK-A1", "Dist": 2400, "Deg": (time.time()*8)%360, "Spd": 27000, "Type": "Communication"},
            {"ID": "GPS-NAV-04", "Dist": 2900, "Deg": (time.time()*2)%360, "Spd": 14000, "Type": "Navigation"}
        ]
    elif mode == "Missile":
        return [
            {"ID": "T-BALLISTIC-1", "Dist": 1200, "Deg": 45, "Spd": 15000, "Type": "Hypersonic"},
            {"ID": "T-CRUISE-X", "Dist": 800, "Deg": 310, "Spd": 950, "Type": "Subsonic"}
        ]
    else: # Demo Aircraft
        return [{"ID": f"DEMO-FLT-{i}", "Dist": np.random.randint(400, 2800), "Deg": np.random.randint(0, 360), "Spd": 850, "Type": "Commercial"} for i in range(5)]

# --- 5. SIDEBAR & SETTINGS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/56/Flag_of_Haiti.svg", width=80)
    st.title("DSM SETTINGS")
    st.session_state.demo_mode = st.toggle("🛰️ Demo Mode", value=True)
    
    st.markdown("---")
    st.subheader("Global Credentials")
    os_user = st.text_input("OpenSky User")
    os_pass = st.text_input("OpenSky Pass", type="password")
    
    st.markdown("---")
    st.markdown(OWNER_INFO)
    if st.button("Lock System"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN UI & MODE SELECTOR ---
st.title("🔴 DSM: DESLANDES STRATOSPHERE MONITOR")

# Mode Selection (Functions for all 3 applications integrated)
app_mode = st.radio("SELECT MONITORING DOMAIN", ["✈️ Aircraft Radar", "🛰️ Satellite Tracker", "🚀 Missile Detector"], horizontal=True)
active_key = app_mode.split(" ")[1] # Extracts Aircraft, Satellite, or Missile

objects = get_radar_data(active_key, os_user, os_pass)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📡 Tactical Sweep: {app_mode}")
    fig = go.Figure()
    sweep = (time.time() * 90) % 360
    
    # Animated Radar Pulse
    fig.add_trace(go.Scatterpolar(r=[0, 3000], theta=[sweep, sweep], mode='lines', line=dict(color='#00FF41', width=5), opacity=0.7, showlegend=False))
    
    # Plot Targets
    fig.add_trace(go.Scatterpolar(
        r=[o['Dist'] for o in objects], theta=[o['Deg'] for o in objects],
        mode='markers+text', marker=dict(size=14, color='red', symbol='cross'),
        text=[o['ID'] for o in objects], textposition="top right"
    ))

    fig.update_layout(
        polar=dict(bgcolor="black", radialaxis=dict(gridcolor="#004400", color="lime", range=[0, 3000]),
                   angularaxis=dict(gridcolor="#004400", color="lime")),
        paper_bgcolor="black", font_color="lime", height=650
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.warning("⚠️ TARGET ANALYSIS ACTIVE")
    st.dataframe(pd.DataFrame(objects), hide_index=True)
    
    st.markdown("---")
    st.info(SOFTWARE_LICENSE)
    
    report_data = f"DSM SECURITY REPORT\nSource: GlobaLInternet.py\nDate: {datetime.now()}\nMode: {app_mode}\n"
    st.download_button("📥 Export Intelligence", report_data, file_name=f"DSM_{active_key}_Report.txt")

st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🇭🇹 MADE IN HAITI BY GLOBALINTERNET.PY</h3>", unsafe_allow_html=True)

time.sleep(2)
st.rerun()
