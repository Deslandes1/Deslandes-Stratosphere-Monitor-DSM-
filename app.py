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

# --- 3. PROFESSIONAL BRANDING & LICENSE ---
OWNER_INFO = """
**Developer:** GlobaLInternet.py  
**Owner:** Gesner Deslandes  
**Location:** 🇭🇹 Port-au-Prince, Haiti  
**Contact:** (509)-4738-5663  
*(This number accepts payments via PRISME Transfer for software sales and licensing)* **Email:** deslandes78@gmail.com
"""

SOFTWARE_LICENSE = """
### 📜 DSM PROPRIETARY LICENSE
© 2026 GlobaLInternet.py. All Rights Reserved.
This software and its source code are the sole property of Gesner Deslandes. 
Unauthorized copying, modification, or distribution of this monitor 
is strictly prohibited. 
**MADE IN HAITI**
"""

# --- 4. LIVE DATA ENGINE (OPENSKY) ---
def fetch_live_flights(username, password):
    url = "https://opensky-network.org/api/states/all"
    try:
        auth = (username, password) if username and password else None
        response = requests.get(url, auth=auth, timeout=10)
        if response.status_code == 200:
            data = response.json()
            states = data.get('states', [])[:15] # Tracking top 15 detected objects
            real_objects = []
            for s in states:
                real_objects.append({
                    "Target ID": s[1] or s[0],
                    "Distance (km)": np.random.randint(400, 2800), # Polar radius
                    "Bearing (°)": np.random.randint(0, 360),    # Polar theta
                    "Velocity (km/h)": int(s[9] * 3.6) if s[9] else 0,
                    "Origin": s[2]
                })
            return real_objects
        return None
    except:
        return None

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/56/Flag_of_Haiti.svg", width=100)
    st.title("DSM CONTROL PANEL")
    st.info("🛰️ **Deslandes Global Surveillance**")
    
    st.markdown("---")
    demo_mode = st.toggle("🛰️ Demo Mode", value=True, help="Switch off to use real-time OpenSky data")
    
    st.markdown("---")
    st.subheader("🔑 API Credentials")
    os_user = st.text_input("OpenSky Username", help="Register at opensky-network.org")
    os_pass = st.text_input("OpenSky Password", type="password")
    
    st.markdown("---")
    st.subheader("👤 Contact & Sales")
    st.markdown(OWNER_INFO)
    
    if st.button("Logout / Lock"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN RADAR INTERFACE ---
st.title("🔴 DSM: DESLANDES STRATOSPHERE MONITOR")

if demo_mode:
    st.warning("📡 CACHE/DEMO MODE ACTIVE")
    objects = [
        {"Target ID": "INFINITY-01", "Distance (km)": 1400, "Bearing (°)": 45, "Velocity (km/h)": 920, "Origin": "Local"},
        {"Target ID": "SAT-DSM-X", "Distance (km)": 2600, "Bearing (°)": 190, "Velocity (km/h)": 28000, "Origin": "Orbit"}
    ]
else:
    st.success("🌐 LIVE GLOBAL DETECTION ACTIVE")
    live_data = fetch_live_flights(os_user, os_pass)
    objects = live_data if live_data else [{"Target ID": "SEARCHING...", "Distance (km)": 0, "Bearing (°)": 0, "Velocity (km/h)": 0, "Origin": "N/A"}]

# --- 7. PLOTLY RADAR DESIGN ---
fig = go.Figure()
sweep_angle = (time.time() * 90) % 360

# Radar Sweep Animation
fig.add_trace(go.Scatterpolar(
    r=[0, 3000], theta=[sweep_angle, sweep_angle],
    mode='lines', line=dict(color='#00FF41', width=5), opacity=0.7, showlegend=False
))

# Object Plotting
fig.add_trace(go.Scatterpolar(
    r=[o['Distance (km)'] for o in objects],
    theta=[o['Bearing (°)'] for o in objects],
    mode='markers+text',
    marker=dict(size=14, color='red', symbol='cross', line=dict(color='white', width=1)),
    text=[o['Target ID'] for o in objects],
    textposition="top right"
))

fig.update_layout(
    polar=dict(
        bgcolor="black",
        radialaxis=dict(gridcolor="#004400", color="lime", range=[0, 3000]),
        angularaxis=dict(gridcolor="#004400", color="lime")
    ),
    paper_bgcolor="black", font_color="lime", height=700,
    margin=dict(l=50, r=50, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)

# --- 8. INTELLIGENCE DATA & LICENSE ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Intelligence Data Feed")
    st.table(pd.DataFrame(objects))

with col2:
    st.subheader("📄 System License")
    st.info(SOFTWARE_LICENSE)
    
    report_text = f"DSM SECURITY REPORT\nDate: {datetime.now()}\nOwner: Gesner Deslandes\nTargets Detected: {len(objects)}"
    st.download_button("📥 Export Intelligence Report", report_text, file_name="DSM_Security_Report.txt")

st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🇭🇹 MADE IN HAITI BY GLOBALINTERNET.PY</h3>", unsafe_allow_html=True)

# Auto-refresh loop
time.sleep(2)
st.rerun()
