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
        st.text_input("Enter Access Key", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- 3. DATA ENGINE ---
def get_radar_data(mode, user, pw, lat, lon, r_max):
    if mode == "Aircraft" and not st.session_state.get('demo_mode', True):
        # Calculate bounding box for OpenSky API
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
    
    # Fallback/Simulation
    count = 10 if mode == "Satellite" else 4
    return [{"ID": f"TGT-{mode[:3]}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(900, 27000)} for i in range(count)]

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🌐 RADAR CONTROL")
    
    # Geo-Location Center
    st.subheader("Center Coordinates")
    u_lat = st.number_input("Latitude", value=18.53, format="%.4f")
    u_lon = st.number_input("Longitude", value=-72.33, format="%.4f")
    
    # Max Range Control
    st.subheader("Detection Parameters")
    m_range = st.slider("Max Range (km)", 50, 5000, 1000, 50)
    
    st.markdown("---")
    st.session_state.demo_mode = st.toggle("🛰️ Demo Mode", value=True)
    os_user = st.text_input("OpenSky User")
    os_pass = st.text_input("OpenSky Pass", type="password")
    
    st.markdown("---")
    st.markdown("### Owner Information")
    st.write("**GlobaLInternet.py**")
    st.write("Contact: (509)-4738-5663")
    st.caption("Payment via PRISME Transfer")

# --- 5. MAIN INTERFACE ---
st.title("🔴 DSM: DESLANDES STRATOSPHERE MONITOR")

# Switcher for the three applications
app_mode = st.radio("SENSORS", ["✈️ Aircraft", "🛰️ Satellite", "🚀 Missile"], horizontal=True, label_visibility="collapsed")
active_key = app_mode.split(" ")[1]

objects = get_radar_data(active_key, os_user, os_pass, u_lat, u_lon, m_range)

col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 {active_key} Sweep | Center: {u_lat}, {u_lon}")
    fig = go.Figure()
    sweep = (time.time() * 110) % 360
    
    # Radar Sweep Line
    fig.add_trace(go.Scatterpolar(r=[0, m_range], theta=[sweep, sweep], mode='lines', line=dict(color='#00FF41', width=5), showlegend=False))
    
    # Target Plotting
    fig.add_trace(go.Scatterpolar(
        r=[o['Dist'] for o in objects], theta=[o['Deg'] for o in objects],
        mode='markers+text', marker=dict(size=12, color='red', symbol='cross'),
        text=[o['ID'] for o in objects], textposition="top right"
    ))

    fig.update_layout(
        polar=dict(bgcolor="black", 
                   radialaxis=dict(gridcolor="#004400", color="lime", range=[0, m_range], ticksuffix="km"),
                   angularaxis=dict(gridcolor="#004400", color="lime")),
        paper_bgcolor="black", font_color="lime", height=700, margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.warning("⚠️ TARGET ANALYSIS")
    st.table(pd.DataFrame(objects))
    
    st.markdown("---")
    # Single Branding Instance
    st.success("🇭🇹 **MADE IN HAITI BY GLOBALINTERNET.PY**")
    
    st.info(f"License Holder: Gesner Deslandes\nSoftware ID: DSM-2026-PRO")
    
    report_csv = pd.DataFrame(objects).to_csv(index=False)
    st.download_button("📥 Export Intelligence Report", report_csv, "DSM_Report.csv", "text/csv")

# Final auto-refresh
time.sleep(2)
st.rerun()
