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
        st.text_input("Enter Access Key", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- 3. LIVE DATA ENGINE (OPENSKY) ---
def fetch_live_flights(username, password):
    """Fetches real-time flight data from OpenSky Network."""
    url = "https://opensky-network.org/api/states/all"
    try:
        # If no credentials, OpenSky limits are very strict
        auth = (username, password) if username and password else None
        response = requests.get(url, auth=auth, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Convert first 10 states to radar format for demo/visuals
            states = data.get('states', [])[:10]
            real_objects = []
            for s in states:
                real_objects.append({
                    "id": s[1] or s[0], # Callsign or ICAO24
                    "r": np.random.randint(500, 2500), # Distance (Simulated for Polar)
                    "th": np.random.randint(0, 360),   # Bearing (Simulated for Polar)
                    "s": int(s[9] * 3.6) if s[9] else 0 # Velocity m/s to km/h
                })
            return real_objects
        else:
            st.sidebar.error(f"API Error: {response.status_code}. Using cache.")
            return None
    except Exception as e:
        return None

# --- 4. BRANDING & UI ---
TRANSLATIONS = {
    'en': {'title': '🔴 DSM: STRATOSPHERE MONITOR', 'live': 'LIVE SATELLITE/AIRCRAFT SCAN', 'demo_btn': 'Demo Mode Active'},
    'fr': {'title': '🔴 DSM: MONITORING STRATOSPHÉRIQUE', 'live': 'SCAN LIVE SATELLITE/AVION', 'demo_btn': 'Mode Démo Actif'},
    'ht': {'title': '🔴 DSM: RADAR SIVEYANS GLOBAL', 'live': 'LIVE SIVEYANS SATELIT/AVYON', 'demo_btn': 'Mòd Demo Aktif'}
}
def t(key): return TRANSLATIONS[st.session_state.language].get(key, key)

# --- 5. SIDEBAR CONTROLS ---
st.sidebar.title("DSM Control Center")
demo_mode = st.sidebar.toggle("Enable Demo Mode", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Global API Credentials")
os_user = st.sidebar.text_input("OpenSky Username", type="default", help="Required for worldwide detection")
os_pass = st.sidebar.text_input("OpenSky Password", type="password")

lang_choice = st.sidebar.selectbox("Language", ["English", "Français", "Kreyòl"])
st.session_state.language = {'English': 'en', 'Français': 'fr', 'Kreyòl': 'ht'}[lang_choice]

# --- 6. MAIN RADAR LOGIC ---
st.title(t('title'))

if demo_mode:
    st.info(f"📡 {t('demo_btn')}")
    objects = [
        {"id": "GAUL-01", "r": 1200, "th": 45, "s": 850},
        {"id": "INFINITY-X", "r": 2100, "th": 190, "s": 27000}
    ]
else:
    st.success(f"🌐 {t('live')}")
    live_data = fetch_live_flights(os_user, os_pass)
    objects = live_data if live_data else [{"id": "SCANNING...", "r": 0, "th": 0, "s": 0}]

# --- 7. RADAR VISUALIZATION ---
fig = go.Figure()
sweep = (time.time() * 80) % 360

# Radar Sweep Line
fig.add_trace(go.Scatterpolar(
    r=[0, 3000], theta=[sweep, sweep],
    mode='lines', line=dict(color='#00FF41', width=4), opacity=0.6, showlegend=False
))

# Object Plotting
fig.add_trace(go.Scatterpolar(
    r=[o['r'] for o in objects],
    theta=[o['th'] for o in objects],
    mode='markers+text',
    marker=dict(size=12, color='red', symbol='triangle-up'),
    text=[o['id'] for o in objects],
    textposition="top right"
))

fig.update_layout(
    polar=dict(bgcolor="black", radialaxis=dict(gridcolor="#004400", color="lime"),
    angularaxis=dict(gridcolor="#004400", color="lime")),
    paper_bgcolor="black", font_color="lime", height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- 8. LOGS & REPORTS ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Target Intelligence")
    st.dataframe(pd.DataFrame(objects), use_container_width=True)

with col2:
    st.subheader("System Status")
    st.write(f"**Last Pulse:** {datetime.now().strftime('%H:%M:%S')}")
    st.write(f"**Source:** {'Internal Cache' if demo_mode else 'OpenSky Live Feed'}")

time.sleep(3)
st.rerun()
