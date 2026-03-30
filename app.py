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
        st.text_input("Enter Access Key", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- 3. DATA ENGINE ---
def get_radar_data(mode, user, pw, lat, lon, r_max):
    """Fetches or simulates data based on geo-location and range."""
    if mode == "Aircraft" and not st.session_state.get('demo_mode', True):
        # OpenSky API Logic with Geo-Bounding Box
        # Conversion: 1 degree lat is approx 111km
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

    # Fallback/Simulation for Satellites & Missiles
    count = 8 if mode == "Satellite" else 3
    return [{"ID": f"TGT-{mode[:3]}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(800, 28000)} for i in range(count)]

# --- 4. SIDEBAR (GEO & RANGE CONTROLS) ---
with st.sidebar:
    st.title("🌐 GEOGRAPHIC CONTROL")
    st.info("Set Radar Center & Detection Radius")
    
    # LAT/LON INPUTS
    col_lat, col_lon = st.columns(2)
    with col_lat:
        user_lat = st.number_input("Latitude", value=18.53, format="%.4f", help="Haiti center: 18.53")
    with col_lon:
        user_lon = st.number_input("Longitude", value=-72.33, format="%.4f", help="Haiti center: -72.33")
    
    # MAX RANGE SLIDER
    max_range = st.slider("Detection Range (km)", min_value=50, max_value=5000, value=1000, step=50)
    
    st.markdown("---")
    st.session_state.demo_mode = st.toggle("🛰️ Demo Mode", value=True)
    os_user = st.text_input("OpenSky User")
    os_pass = st.text_input("OpenSky Pass", type="password")
    
    st.markdown("---")
    st.markdown("**GlobaLInternet.py** / Owner: Gesner Deslandes")
    st.markdown("Payment: (509)-4738-5663")
    if st.button("Lock System"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🔴 DSM: STRATOSPHERE MONITOR")

app_mode = st.radio("SENSORS", ["✈️ Aircraft", "🛰️ Satellite", "🚀 Missile"], horizontal=True, label_visibility="collapsed")
active_key = app_mode.split(" ")[1]

objects = get_radar_data(active_key, os_user, os_pass, user_lat, user_lon, max_range)

col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 Radar Center: {user_lat}, {user_lon} | Range: {max_range}km")
    
    fig = go.Figure()
    sweep = (time.time() * 100) % 360
    
    # Radar Sweep Line
    fig.add_trace(go.Scatterpolar(r=[0, max_range], theta=[sweep, sweep], mode='lines', line=dict(color='#00FF41', width=5), showlegend=False))
    
    # Plot Detected Targets
    fig.add_trace(go.Scatterpolar(
        r=[o['Dist'] for o in objects], theta=[o['Deg'] for o in objects],
        mode='markers+text', marker=dict(size=12, color='red', symbol='cross'),
        text=[o['ID'] for o in objects], textposition="top right"
    ))

    fig.update_layout(
        polar=dict(bgcolor="black", 
                   radialaxis=dict(gridcolor="#004400", color="lime", range=[0, max_range], ticksuffix="km"),
                   angularaxis=dict(gridcolor="#004400", color="lime")),
        paper_bgcolor="black", font_color="lime", height=700, margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.warning("⚠️ TARGET INTELLIGENCE")
    df = pd.DataFrame(objects)
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.success("© 2026 GlobaLInternet.py\n\n**MADE IN HAITI**")
    
    report = f"DSM SECURITY REPORT\nCenter: {user_lat}, {user_lon}\nRange: {max_range}km\nTargets: {len(objects)}"
    st.download_button("📥 Export Data", report, file_name=f"DSM_{active_key}_Report.txt")

time.sleep(2)
st.rerun()
