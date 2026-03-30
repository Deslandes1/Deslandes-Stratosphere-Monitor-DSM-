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

# --- 2. AUTHENTICATION & OFFICIAL FLAG UI ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "20082010":
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.error("❌ Access Denied")

    if not st.session_state["authenticated"]:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src='https://upload.wikimedia.org/wikipedia/commons/f/f4/Flag_of_Haiti.svg' width='350' style='border-radius: 5px; box-shadow: 0px 10px 30px rgba(0,0,0,0.5);'>
            </div>
            <h1 style='text-align: center; color: #00FF41; font-family: monospace;'>SYSTEM LOCKED: DSM-2026</h1>
            <p style='text-align: center; color: white;'>GlobaLInternet.py Security Protocol</p>
        """, unsafe_allow_html=True)
        
        st.text_input("ENTER ACCESS KEY", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- 3. DATA ENGINE ---
def get_radar_data(mode, user, pw, lat, lon, r_max):
    if mode == "Aircraft" and not st.session_state.get('demo_mode', True):
        lat_delta = r_max / 111.0
        lon_delta = r_max / (111.0 * np.cos(np.radians(lat)))
        url = f"https://opensky-network.org/api/states/all?lamin={lat-lat_delta}&lomin={lon-lon_delta}&lamax={lat+lat_delta}&lomax={lon+lon_delta}"
        try:
            auth = (user, pw) if user and pw else None
            response = requests.get(url, auth=auth, timeout=5)
            if response.status_code == 200:
                states = response.json().get('states', [])[:20]
                return [{"ID": s[1] or s[0], "Dist": np.random.randint(5, r_max), "Deg": np.random.randint(0, 360), "Spd": int(s[9]*3.6) if s[9] else 0} for s in states]
        except: pass
    
    count = 15 if mode == "Satellite" else 6
    return [{"ID": f"TGT-{mode[:3]}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(900, 28000)} for i in range(count)]

# --- 4. SIDEBAR (PROFESSIONAL CONTROLS) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/f4/Flag_of_Haiti.svg", caption="DSM Official Origin")
    st.title("📡 RADAR CONTROL")
    
    st.markdown("### 📍 COORDINATES")
    u_lat = st.number_input("Latitude", value=18.53, format="%.4f")
    u_lon = st.number_input("Longitude", value=-72.33, format="%.4f")
    
    st.markdown("### 📏 SCAN RADIUS")
    m_range = st.slider("Max Range (km)", 50, 5000, 1000, 50)
    
    st.markdown("---")
    st.session_state.demo_mode = st.toggle("🛰️ Demo Mode", value=True)
    os_user = st.text_input("OpenSky User")
    os_pass = st.text_input("OpenSky Pass", type="password")
    
    st.markdown("---")
    st.write("**Owner:** Gesner Deslandes")
    st.write("📞 (509)-4738-5663")
    if st.button("🔴 SHUTDOWN SYSTEM"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.markdown("<h1 style='color: #00FF41; text-align: center;'>🔴 DESLANDES STRATOSPHERE MONITOR</h1>", unsafe_allow_html=True)

app_mode = st.radio("ACTIVE SENSORS", ["✈️ Aircraft", "🛰️ Satellite", "🚀 Missile"], horizontal=True, label_visibility="collapsed")
active_key = app_mode.split(" ")[1]

objects = get_radar_data(active_key, os_user, os_pass, u_lat, u_lon, m_range)

col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 {active_key} Sweep | Center: {u_lat}, {u_lon}")
    fig = go.Figure()
    sweep = (time.time() * 120) % 360 # High speed sweep
    
    # Glow Radar Sweep
    fig.add_trace(go.Scatterpolar(r=[0, m_range], theta=[sweep, sweep], mode='lines', line=dict(color='#00FF41', width=6), opacity=0.8, showlegend=False))
    
    # Plot Targets
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
    st.error(f"⚠️ {active_key.upper()} TARGET INTELLIGENCE")
    st.dataframe(pd.DataFrame(objects), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    # THE PROFESSIONAL BRANDING
    st.success("🇭🇹 **MADE IN HAITI BY GLOBALINTERNET.PY**")
    
    with st.container(border=True):
        st.write(f"**License ID:** DSM-2026-X")
        st.write(f"**Developer:** Gesner Deslandes")
        st.write(f"**Status:** System Operational")
    
    report_data = pd.DataFrame(objects).to_csv(index=False)
    st.download_button("📥 DOWNLOAD INTEL REPORT", report_data, f"DSM_{active_key}_INTEL.csv")

# Automatic refresh for the radar sweep effect
time.sleep(1)
st.rerun()
