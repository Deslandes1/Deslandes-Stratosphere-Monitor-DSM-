import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import requests

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
        # OFFICIAL HAITIAN FLAG (SVG INTEGRATION)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 30px;'>
                <img src='https://upload.wikimedia.org/wikipedia/commons/f/f4/Flag_of_Haiti.svg' width='400' style='border-radius: 10px; border: 1px solid #555; box-shadow: 0px 4px 15px rgba(0,0,0,0.5);'>
            </div>
            <h2 style='text-align: center; color: white;'>DESLANDES STRATOSPHERE MONITOR</h2>
            <p style='text-align: center; color: #aaa;'>Enterprise Surveillance by GlobaLInternet.py</p>
        """, unsafe_allow_html=True)
        
        st.text_input("Enter Access Key to Unlock", type="password", on_change=password_entered, key="password")
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
    
    count = 12 if mode == "Satellite" else 5
    return [{"ID": f"TGT-{mode[:3]}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(900, 27000)} for i in range(count)]

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    # Sidebar Official Flag Banner
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/f4/Flag_of_Haiti.svg", use_container_width=True)
    st.title("🌐 RADAR CONTROL")
    
    u_lat = st.number_input("Latitude", value=18.53, format="%.4f")
    u_lon = st.number_input("Longitude", value=-72.33, format="%.4f")
    m_range = st.slider("Max Range (km)", 50, 5000, 1000, 50)
    
    st.markdown("---")
    st.session_state.demo_mode = st.toggle("🛰️ Demo Mode", value=True)
    os_user = st.text_input("OpenSky User")
    os_pass = st.text_input("OpenSky Pass", type="password")
    
    st.markdown("---")
    st.write("**GlobaLInternet.py** / Gesner Deslandes")
    st.write("📞 (509)-4738-5663")
    if st.button("Lock System"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🔴 DSM: DESLANDES STRATOSPHERE MONITOR")

app_mode = st.radio("SENSORS", ["✈️ Aircraft", "🛰️ Satellite", "🚀 Missile"], horizontal=True, label_visibility="collapsed")
active_key = app_mode.split(" ")[1]

objects = get_radar_data(active_key, os_user, os_pass, u_lat, u_lon, m_range)

col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 {active_key} Sweep | Location: {u_lat}, {u_lon}")
    fig = go.Figure()
    sweep = (time.time() * 115) % 360
    
    fig.add_trace(go.Scatterpolar(r=[0, m_range], theta=[sweep, sweep], mode='lines', line=dict(color='#00FF41', width=5), showlegend=False))
    
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
    # Single Branding Instance - Official Flag Mini
    st.markdown("""
        <div style='display: flex; align-items: center; background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-left: 5px solid #d21034;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/f/f4/Flag_of_Haiti.svg' width='40' style='margin-right: 15px;'>
            <span style='color: white; font-weight: bold;'>MADE IN HAITI BY GLOBALINTERNET.PY</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.info(f"License: DSM-2026-PRO\nOwner: Gesner Deslandes")
    
    report_csv = pd.DataFrame(objects).to_csv(index=False)
    st.download_button("📥 Export Intelligence", report_csv, "DSM_Report.csv", "text/csv")

time.sleep(2)
st.rerun()
