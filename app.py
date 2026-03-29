import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2, pi, asin, degrees
import time
from datetime import datetime

# --- CONFIGURATION & TRANSLATIONS ---
st.set_page_config(page_title="DSM - Deslandes Stratosphere Monitor", layout="wide", page_icon="🔴")

if 'language' not in st.session_state:
    st.session_state.language = 'en'

TRANSLATIONS = {
    'en': {
        'title': '🔴 DSM: DESLANDES STRATOSPHERE MONITOR',
        'm1': '✈️ Aircraft Radar', 'm2': '🛰️ Satellite Tracker', 'm3': '🚀 Missile Detector',
        'threat': '⚠️ THREAT DETECTED', 'speed': 'Velocity', 'target': 'Impact Zone',
        'report': '📥 Download Intelligence Report', 'owner': '🇭🇹 Owner: Gesner Deslandes'
    },
    'fr': {
        'title': '🔴 DSM: MONITORING STRATOSPHÉRIQUE',
        'm1': '✈️ Radar Aéronefs', 'm2': '🛰️ Traqueur Satellites', 'm3': '🚀 Détecteur de Missiles',
        'threat': '⚠️ MENACE DÉTECTÉE', 'speed': 'Vitesse', 'target': 'Zone d\'Impact',
        'report': '📥 Télécharger le rapport de renseignement', 'owner': '🇭🇹 Propriétaire: Gesner Deslandes'
    },
    'ht': {
        'title': '🔴 DSM: RADAR SIVEYANS GLOBAL',
        'm1': '✈️ Radar Avyon', 'm2': '🛰️ Swiv Satelit', 'm3': '🚀 Detektè Misil',
        'threat': '⚠️ MENAS DETEKTE', 'speed': 'Vitès', 'target': 'Zòn Enpak',
        'report': '📥 Telechaje Rapò Entelijans la', 'owner': '🇭🇹 Pwopriyetè: Gesner Deslandes'
    }
}

def t(key):
    lang = st.session_state.language
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# --- UTILITY FUNCTIONS ---
def get_impact_coords(lat, lon, dist, brng):
    R = 6371
    lat1, lon1, brng = radians(lat), radians(lon), radians(brng)
    d = dist / R
    lat2 = asin(sin(lat1)*cos(d) + cos(lat1)*sin(d)*cos(brng))
    lon2 = lon1 + atan2(sin(brng)*sin(d)*cos(lat1), cos(d)-sin(lat1)*sin(lat2))
    return degrees(lat2), degrees(lon2)

# --- SIDEBAR ---
st.sidebar.title("DSM Control Center")
lang_select = st.sidebar.selectbox("Language / Langue", ["English", "Français", "Kreyòl"])
st.session_state.language = {'English': 'en', 'Français': 'fr', 'Kreyòl': 'ht'}[lang_select]

st.title(t('title'))
mode = st.radio("", [t('m1'), t('m2'), t('m3')], horizontal=True, index=2)

# --- MODE 3: MISSILE DETECTOR ---
if mode == t('m3'):
    col1, col2 = st.columns([2, 1])
    r_lat, r_lon, r_range = 18.53, -72.33, 2500
    
    # Persistent Threat Data for the session
    threats = [
        {"id": "MSL-DELTA-1", "type": "Hypersonic", "dist": 940, "brng": 15, "speed": 6200},
        {"id": "MSL-ZETA-9", "type": "ICBM", "dist": 2100, "brng": 195, "speed": 7800}
    ]

    with col1:
        fig = go.Figure()
        
        # Dual-Needle Animation (Rotates every rerun)
        sweep = (time.time() * 100) % 360
        for offset in [0, 180]:
            fig.add_trace(go.Scatterpolar(r=[0, r_range], theta=[(sweep + offset) % 360]*2,
                         mode='lines', line=dict(color='#00FF41', width=5), opacity=0.8, showlegend=False))
        
        # Plot Radar Markers
        fig.add_trace(go.Scatterpolar(
            r=[m['dist'] for m in threats], theta=[m['brng'] for m in threats],
            mode='markers+text', marker=dict(size=18, color='red', symbol='x'),
            text=[f"{m['id']}" for m in threats], textfont=dict(color="red", size=14), textposition="top right"
        ))

        fig.update_layout(polar=dict(bgcolor="black", radialaxis=dict(gridcolor="#004400", color="lime"),
                                    angularaxis=dict(gridcolor="#004400", color="lime")),
                          paper_bgcolor="black", font_color="lime", height=750, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.error(t('threat'))
        report_text = f"--- DSM INTELLIGENCE REPORT ---\nDate: {datetime.now()}\nResearcher: Gesner Deslandes\n\n"
        
        for m in threats:
            i_lat, i_lon = get_impact_coords(r_lat, r_lon, m['dist']*0.1, m['brng'])
            with st.container(border=True):
                st.subheader(f"🚀 {m['id']}")
                st.write(f"**Classification:** {m['type']}")
                st.write(f"**{t('speed')}:** {m['speed']} km/h")
                st.write(f"**{t('target')}:** `{i_lat:.4f}, {i_lon:.4f}`")
                report_text += f"Target: {m['id']} | Type: {m['type']} | Speed: {m['speed']} | Impact: {i_lat}, {i_lon}\n"
        
        st.download_button(label=t('report'), data=report_text, file_name=f"DSM_Report_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")

    time.sleep(1.5)
    st.rerun()

else:
    st.info("System stand-by. Mode processing requires specialized satellite/aircraft API keys.")
    st.write("Ensure your N2YO and OpenSky credentials are configured in your GitHub secrets.")

st.sidebar.markdown(f"--- \n {t('owner')}")
