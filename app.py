import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2, pi, asin, degrees
import time
from datetime import datetime

# --- 1. SESSION STATE & CONFIG ---
st.set_page_config(page_title="DSM - Deslandes Stratosphere Monitor", layout="wide", page_icon="🇭🇹")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# --- 2. AUTHENTICATION SYSTEM ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "20082010":
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.error("❌ Access Denied: Incorrect Password")

    if not st.session_state["authenticated"]:
        # Presentation Page with Haitian Flag
        st.markdown("<h1 style='text-align: center;'>🇭🇹</h1>", unsafe_allow_html=True)
        st.markdown("""
            <div style='height: 100px; background-color: #00209F; border-radius: 10px 10px 0 0;'></div>
            <div style='height: 100px; background-color: #D21034; border-radius: 0 0 10px 10px;'></div>
            <br>
            <h2 style='text-align: center;'>Deslandes Stratosphere Monitor</h2>
            <p style='text-align: center;'>Licensed Software by GlobaLInternet.py</p>
        """, unsafe_allow_html=True)
        
        st.text_input("Enter Access Key to Unlock DSM System", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- 3. BRANDING & LICENSE ---
LICENSE_TEXT = """
© 2026 GlobaLInternet.py | ALL RIGHTS RESERVED
Owner: Gesner Deslandes
Phone: (509)-4738-5663 | Email: deslandes78@gmail.com
MADE IN HAITI
"""

TRANSLATIONS = {
    'en': {
        'title': '🔴 DSM: DESLANDES STRATOSPHERE MONITOR',
        'm1': '✈️ Aircraft Radar', 'm2': '🛰️ Satellite Tracker', 'm3': '🚀 Missile Detector',
        'threat': '⚠️ THREAT DETECTED', 'demo': '📡 CACHE/DEMO MODE ACTIVE',
        'report': '📥 Download Intelligence Report', 'owner': '🇭🇹 Made in Haiti by GlobaLInternet.py'
    },
    'fr': {
        'title': '🔴 DSM: MONITORING STRATOSPHÉRIQUE',
        'm1': '✈️ Radar Aéronefs', 'm2': '🛰️ Traqueur Satellites', 'm3': '🚀 Détecteur de Missiles',
        'threat': '⚠️ MENACE DÉTECTÉE', 'demo': '📡 MODE DÉMO/CACHE ACTIF',
        'report': '📥 Télécharger le rapport', 'owner': '🇭🇹 Fait en Haïti par GlobaLInternet.py'
    },
    'ht': {
        'title': '🔴 DSM: RADAR SIVEYANS GLOBAL',
        'm1': '✈️ Radar Avyon', 'm2': '🛰️ Swiv Satelit', 'm3': '🚀 Detektè Misil',
        'threat': '⚠️ MENAS DETEKTE', 'demo': '📡 MÒD DEMO AKTIF',
        'report': '📥 Telechaje Rapò a', 'owner': '🇭🇹 Fèt an Ayiti pa GlobaLInternet.py'
    }
}

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# --- 4. DATA ENGINE (LIVE + CACHED DEMO) ---
@st.cache_data(ttl=60)
def get_cached_threats(mode):
    # Simulated/Cached objects for Demo Mode
    if mode == "Missile":
        return [{"id": "DEMO-MSL-1", "r": 1400, "th": 45, "s": 6500}, {"id": "DEMO-MSL-2", "r": 2200, "th": 190, "s": 9200}]
    elif mode == "Aircraft":
        return [{"id": "DEMO-FLIGHT-X", "r": 800, "th": 120, "s": 850}]
    else: # Satellites
        return [{"id": "DEMO-SAT-Z", "r": 2800, "th": 330, "s": 27000}]

# --- 5. MAIN INTERFACE ---
st.sidebar.title("DSM Control")
st.sidebar.info(LICENSE_TEXT)
lang = st.sidebar.selectbox("Language", ["English", "Français", "Kreyòl"])
st.session_state.language = {'English': 'en', 'Français': 'fr', 'Kreyòl': 'ht'}[lang]

if st.sidebar.button("Logout / Lock System"):
    st.session_state.authenticated = False
    st.rerun()

st.title(t('title'))
mode = st.radio("", [t('m1'), t('m2'), t('m3')], horizontal=True, index=2)

# Logic mapping
if mode == t('m1'): active_mode, label = "Aircraft", "ALTITUDE MONITOR"
elif mode == t('m2'): active_mode, label = "Satellite", "ORBITAL SWEEP"
else: active_mode, label = "Missile", "TACTICAL DEFENSE"

# Display Logic
col1, col2 = st.columns([2, 1])
objects = get_cached_threats(active_mode)
r_max = 3000

with col1:
    st.subheader(f"📡 {label} ({t('demo')})")
    fig = go.Figure()
    # Rotating Dual Needle Animation
    sweep = (time.time() * 90) % 360
    for offset in [0, 180]:
        fig.add_trace(go.Scatterpolar(r=[0, r_max], theta=[(sweep + offset) % 360]*2,
                                     mode='lines', line=dict(color='#00FF41', width=4), opacity=0.6, showlegend=False))
    # Plot Detected Objects
    fig.add_trace(go.Scatterpolar(
        r=[o['r'] for o in objects], theta=[o['th'] for o in objects],
        mode='markers+text', marker=dict(size=15, color='red', symbol='cross'),
        text=[o['id'] for o in objects], textposition="top right"
    ))
    fig.update_layout(polar=dict(bgcolor="black", radialaxis=dict(gridcolor="#004400", color="lime"),
                                angularaxis=dict(gridcolor="#004400", color="lime")),
                      paper_bgcolor="black", font_color="lime", height=700)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.warning(t('threat'))
    report = f"DSM Report - {active_mode}\nResearcher: Gesner Deslandes\n"
    for o in objects:
        with st.container(border=True):
            st.write(f"**Target ID:** {o['id']}")
            st.write(f"**Speed:** {o['s']} km/h")
            report += f"ID: {o['id']} | Speed: {o['s']}\n"
    
    st.download_button(t('report'), report, file_name=f"DSM_{active_mode}_Report.txt")

st.caption(f"--- \n {t('owner')}")
time.sleep(1)
st.rerun()
