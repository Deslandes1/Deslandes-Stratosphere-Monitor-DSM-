import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2, pi, asin, degrees
import time
import random
from datetime import datetime

# --- 1. SETTINGS & TRANSLATIONS ---
st.set_page_config(page_title="DSM - Deslandes Stratosphere Monitor", layout="wide", page_icon="🔴")

if 'language' not in st.session_state:
    st.session_state.language = 'en'

TRANSLATIONS = {
    'en': {'title': '🔴 DSM: DESLANDES STRATOSPHERE MONITOR', 'm1': '✈️ Aircraft Radar', 'm2': '🛰️ Satellite Tracker', 'm3': '🚀 Missile Detector', 'threat': '⚠️ THREAT DETECTED', 'owner': '🇭🇹 Owner: Gesner Deslandes'},
    'fr': {'title': '🔴 DSM: MONITORING DE LA STRATOSPHÈRE', 'm1': '✈️ Radar Aéronefs', 'm2': '🛰️ Traqueur Satellites', 'm3': '🚀 Détecteur de Missiles', 'threat': '⚠️ MENACE DÉTECTÉE', 'owner': '🇭🇹 Propriétaire: Gesner Deslandes'},
    'ht': {'title': '🔴 DSM: RADAR SIVEYANS GLOBAL', 'm1': '✈️ Radar Avyon', 'm2': '🛰️ Swiv Satelit', 'm3': '🚀 Detektè Misil', 'threat': '⚠️ MENAS DETEKTE', 'owner': '🇭🇹 Pwopriyetè: Gesner Deslandes'}
}

def t(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# --- 2. UI LAYOUT ---
st.sidebar.title("Configuration")
lang = st.sidebar.selectbox("Language / Langue", ["English", "Français", "Kreyòl"])
st.session_state.language = {'English': 'en', 'Français': 'fr', 'Kreyòl': 'ht'}[lang]

st.title(t('title'))
mode = st.radio("", [t('m1'), t('m2'), t('m3')], horizontal=True)

# --- 3. MODE LOGIC ---
if mode == t('m3'): # MISSILE DETECTOR (The New Mode)
    col1, col2 = st.columns([2, 1])
    r_range = 2000
    
    with col1:
        # Dual-Needle Radar UI
        fig = go.Figure()
        angle = (time.time() * 70) % 360
        for offset in [0, 180]: # Dual needles
            fig.add_trace(go.Scatterpolar(r=[0, r_range], theta=[(angle+offset)%360]*2,
                         mode='lines', line=dict(color='lime', width=4), opacity=0.6, showlegend=False))
        
        # Simulated Missile Data
        m_data = [{"id": "MSL-99", "r": 1200, "th": 45, "s": "6,500 km/h"}]
        fig.add_trace(go.Scatterpolar(r=[m['r'] for m in m_data], theta=[m['th'] for m in m_data],
                                     mode='markers', marker=dict(size=15, color='red', symbol='x')))
        
        fig.update_layout(polar=dict(bgcolor="black", radialaxis=dict(gridcolor="green"), angularaxis=dict(gridcolor="green")),
                          paper_bgcolor="black", font_color="lime", height=600)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.error(t('threat'))
        for m in m_data:
            st.write(f"**ID:** {m['id']}")
            st.write(f"**Speed:** {m['s']}")
            st.write(f"**Status:** Incoming / High Velocity")
    
    time.sleep(2)
    st.rerun()

else:
    st.info("Original Aircraft/Satellite logic placeholder. (Integrate your previous fetch functions here).")

st.sidebar.write(f"--- \n {t('owner')}")
