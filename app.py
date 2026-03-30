import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import requests
from datetime import datetime

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="DSM - Deslandes Stratosphere Monitor", layout="wide", page_icon="🇭🇹")

# Initialize session state to prevent refresh errors
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

# --- 2. AUTHENTICATION & START OF PAGE (OFFICIAL HAITIAN FLAG) ---
def check_password():
    def password_entered():
        # FIX: Safety check to prevent KeyError during high-speed refresh
        if "password" in st.session_state:
            if st.session_state["password"] == "20082010":
                st.session_state["authenticated"] = True
                del st.session_state["password"]
            else:
                st.error("❌ Access Denied: Invalid Authorization Key")

    if not st.session_state["authenticated"]:
        # THE START OF THE PAGE - OFFICIAL NATIONAL FLAG (High Definition)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src='https://flagcdn.com/w640/ht.png' width='450' style='border-radius: 8px; box-shadow: 0px 8px 25px rgba(0,0,0,0.7); border: 1px solid #333;'>
            </div>
            <h1 style='text-align: center; color: #00FF41; font-family: "Courier New", Courier, monospace;'>DSM-2026: SYSTEM SECURED</h1>
            <p style='text-align: center; color: #bbbbbb;'>GlobalInternet.py Security Infrastructure | Made in Haiti</p>
        """, unsafe_allow_html=True)
        
        st.text_input("INPUT AUTHORIZATION KEY", type="password", on_change=password_entered, key="password")
        st.stop()

# Run the secure login
check_password()

# --- 3. DATA ENGINE (AIRCRAFT, SATELLITE, MISSILE) ---
def get_radar_data(mode, user, pw, lat, lon, r_max):
    if mode == "Aircraft" and not st.session_state.demo_mode:
        lat_delta = r_max / 111.0
        lon_delta = r_max / (111.0 * np.cos(np.radians(lat)))
        url = f"https://opensky-network.org/api/states/all?lamin={lat-lat_delta}&lomin={lon-lon_delta}&lamax={lat+lat_delta}&lomax={lon+lon_delta}"
        try:
            auth = (user, pw) if user and pw else None
            response = requests.get(url, auth=auth, timeout=5)
            if response.status_code == 200:
                states = response.json().get('states', [])[:25]
                return [{"ID": s[1] or s[0], "Dist": np.random.randint(5, r_max), "Deg": np.random.randint(0, 360), "Spd": int(s[9]*3.6) if s[9] else 0} for s in states]
        except: pass
    
    # Tactical Simulations for Premium Display
    count = 18 if mode == "Satellite" else 7
    return [{"ID": f"TGT-{mode[:3].upper()}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(900, 28000)} for i in range(count)]

# --- 4. SIDEBAR (COMMERCIAL LICENSE & PURCHASE INFO) ---
with st.sidebar:
    # OFFICIAL FLAG ABOVE SIDEBAR TITLE
    st.markdown("""
        <div style='text-align: center;'>
            <img src='https://flagcdn.com/w320/ht.png' width='220' style='border-radius: 4px; border: 1px solid #444;'>
            <h2 style='margin-top: 15px; color: #00FF41; font-family: monospace;'>DSM RADAR CONTROL</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # VISIBLE COMMERCIAL LICENSE
    st.info("""
    **📜 OFFICIAL LICENSE** **Company Name:** GlobalInternet.py  
    **Owner:** Gesner Deslandes  
    **Email:** deslandes78@gmail.com  
    *All Rights Reserved Professionals © 2026*
    """)
    
    # PURCHASE TERMS
    st.success("""
    **🛒 PURCHASE THIS APP** To purchase this full package, check the owner information above.  
    **Delivery:** Full source code sent via email within **24 hours**.
    """)
    
    st.markdown("---")
    st.markdown("### 📍 COORDINATES & RANGE")
    u_lat = st.number_input("Latitude", value=18.53, format="%.4f")
    u_lon = st.number_input("Longitude", value=-72.33, format="%.4f")
    m_range = st.slider("Range Radius (km)", 50, 5000, 1500, 50)
    
    st.markdown("---")
    st.session_state.demo_mode = st.toggle("🛰️ Demo Mode (Simulation)", value=True)
    os_user = st.text_input("OpenSky Username")
    os_pass = st.text_input("OpenSky Password", type="password")
    
    if st.button("TERMINATE SESSION"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. MAIN RADAR INTERFACE ---
st.markdown("<h1 style='color: #00FF41; text-align: center; border-bottom: 2px solid #004400; padding-bottom: 10px;'>🔴 DESLANDES STRATOSPHERE MONITOR</h1>", unsafe_allow_html=True)

# Application Mode Selector (The 3 functionalities)
app_mode = st.radio("SELECT SENSOR MODE", ["✈️ Aircraft", "🛰️ Satellite", "🚀 Missile"], horizontal=True, label_visibility="collapsed")
active_key = app_mode.split(" ")[1]

# Retrieve Target Data
objects = get_radar_data(active_key, os_user, os_pass, u_lat, u_lon, m_range)

col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 {active_key.upper()} SCANNING... [CENTER: {u_lat}, {u_lon}]")
    fig = go.Figure()
    sweep_pos = (time.time() * 125) % 360 
    
    # Animated Tactical Radar Sweep
    fig.add_trace(go.Scatterpolar(r=[0, m_range], theta=[sweep_pos, sweep_pos], mode='lines', line=dict(color='#00FF41', width=7), opacity=0.9, showlegend=False))
    
    # Plot Tactical Targets
    fig.add_trace(go.Scatterpolar(
        r=[o['Dist'] for o in objects], theta=[o['Deg'] for o in objects],
        mode='markers+text', marker=dict(size=14, color='red', symbol='cross', line=dict(color='white', width=1)),
        text=[o['ID'] for o in objects], textposition="top right"
    ))

    fig.update_layout(
        polar=dict(bgcolor="black", 
                   radialaxis=dict(gridcolor="#004400", color="lime", range=[0, m_range], ticksuffix="km"),
                   angularaxis=dict(gridcolor="#004400", color="lime")),
        paper_bgcolor="black", font_color="lime", height=750, margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.error(f"🔴 {active_key.upper()} TARGET LOG")
    st.dataframe(pd.DataFrame(objects), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    # THE PROFESSIONAL BRANDING (Haitian Bicolour Style)
    st.markdown("""
        <div style='background-color: #00209F; padding: 5px; text-align: center; border-radius: 5px 5px 0 0;'>
            <span style='color: white; font-weight: bold;'>MADE IN HAITI</span>
        </div>
        <div style='background-color: #D21034; padding: 5px; text-align: center; border-radius: 0 0 5px 5px;'>
            <span style='color: white; font-weight: bold;'>GLOBALINTERNET.PY</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.write(f"**Developer:** Gesner Deslandes")
        st.write(f"**Owner Info:** (509)-4738-5663")
        st.write(f"**Official Email:** deslandes78@gmail.com")
        st.caption("Review information above for purchase inquiries.")
    
    # Data Export Capability
    report_data = pd.DataFrame(objects).to_csv(index=False)
    st.download_button("📥 DOWNLOAD TACTICAL DATA", report_data, f"DSM_INTEL_{active_key}.csv")

# Dynamic Refresh Loop
time.sleep(1)
st.rerun()
