import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2, pi, asin, degrees
import time
from datetime import datetime

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(
    page_title="DSM - Deslandes Stratosphere Monitor", 
    layout="wide", 
    page_icon="🔴"
)

if 'language' not in st.session_state:
    st.session_state.language = 'en'

# --- MULTILINGUAL DICTIONARY ---
TRANSLATIONS = {
    'en': {
        'title': '🔴 DSM: DESLANDES STRATOSPHERE MONITOR',
        'm1': '✈️ Aircraft Radar', 
        'm2': '🛰️ Satellite Tracker', 
        'm3': '🚀 Missile Detector',
        'threat_header': '⚠️ TACTICAL THREAT ALERT',
        'speed': 'Velocity', 
        'target': 'Predicted Impact Zone',
        'report': '📥 Download Intelligence Report',
        'owner': '🇭🇹 Owner: Gesner Deslandes – Licensed Software',
        'status': 'System Status: ACTIVE SCANNING',
        'radar_label': '📡 STRATOSPHERIC SWEEP'
    },
    'fr': {
        'title': '🔴 DSM: MONITORING STRATOSPHÉRIQUE',
        'm1': '✈️ Radar Aéronefs', 
        'm2': '🛰️ Traqueur Satellites', 
        'm3': '🚀 Détecteur de Missiles',
        'threat_header': '⚠️ ALERTE DE MENACE TACTIQUE',
        'speed': 'Vitesse', 
        'target': 'Zone d\'Impact Prédite',
        'report': '📥 Télécharger le rapport de renseignement',
        'owner': '🇭🇹 Propriétaire: Gesner Deslandes – Logiciel Sous Licence',
        'status': 'État du système: BALAYAGE ACTIF',
        'radar_label': '📡 BALAYAGE STRATOSPHÉRIQUE'
    },
    'ht': {
        'title': '🔴 DSM: RADAR SIVEYANS GLOBAL',
        'm1': '✈️ Radar Avyon', 
        'm2': '🛰️ Swiv Satelit', 
        'm3': '🚀 Detektè Misil',
        'threat_header': '⚠️ MENAS DETEKTE',
        'speed': 'Vitès', 
        'target': 'Zòn Enpak Estimé',
        'report': '📥 Telechaje Rapò Entelijans la',
        'owner': '🇭🇹 Pwopriyetè: Gesner Deslandes – Lisansye',
        'status': 'Sistèm: AP SCANNE KONFYA',
        'radar_label': '📡 VIZUALIZASYON RADAR'
    }
}

def t(key):
    lang = st.session_state.language
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# --- TACTICAL MATH ENGINE ---
def calculate_impact(lat, lon, dist_km, brng_deg):
    R = 6371
    lat1, lon1, brng = radians(lat), radians(lon), radians(brng_deg)
    d = dist_km / R
    lat2 = asin(sin(lat1)*cos(d) + cos(lat1)*sin(d)*cos(brng))
    lon2 = lon1 + atan2(sin(brng)*sin(d)*cos(lat1), cos(d)-sin(lat1)*sin(lat2))
    return degrees(lat2), degrees(lon2)

# --- SIDEBAR CONTROL ---
st.sidebar.title("DSM Control Center")
st.sidebar.markdown(f"**{t('owner')}**")
lang_select = st.sidebar.selectbox("Language / Langue", ["English", "Français", "Kreyòl"])
st.session_state.language = {'English': 'en', 'Français': 'fr', 'Kreyòl': 'ht'}[lang_select]

# Custom CSS for the "Military/Tactical" look
st.markdown("""
    <style>
    .main { background-color: #050505; }
    .stMetric { color: #00FF41 !important; }
    div[data-testid="stExpander"] { border: 1px solid #00FF41; background-color: #001100; }
    </style>
    """, unsafe_allow_html=True)

st.title(t('title'))
mode = st.radio("", [t('m1'), t('m2'), t('m3')], horizontal=True, index=2)

# --- MAIN MODE: MISSILE DETECTOR ---
if mode == t('m3'):
    col_radar, col_intel = st.columns([2, 1])
    
    # Coordinates for Port-au-Prince focus
    HOME_LAT, HOME_LON, SCAN_RADIUS = 18.5392, -72.3350, 3000
    
    # Mock detection data for the researcher interface
    threats = [
        {"id": "V-ALPHA-9", "type": "Hypersonic Glide Vehicle", "dist": 1240, "brng": 32, "speed": 8500},
        {"id": "V-OMEGA-4", "type": "Ballistic ICBM", "dist": 2450, "brng": 210, "speed": 12000}
    ]

    with col_radar:
        st.subheader(t('radar_label'))
        fig = go.Figure()
        
        # Dual-Needle Sweep Animation (Updates on rerun)
        now = time.time()
        sweep_1 = (now * 110) % 360
        sweep_2 = (sweep_1 + 180) % 360
        
        for s_angle in [sweep_1, sweep_2]:
            fig.add_trace(go.Scatterpolar(
                r=[0, SCAN_RADIUS], theta=[s_angle, s_angle],
                mode='lines', line=dict(color='#00FF41', width=4), opacity=0.7, showlegend=False
            ))
        
        # Plot Radar Targets
        fig.add_trace(go.Scatterpolar(
            r=[m['dist'] for m in threats], 
            theta=[m['brng'] for m in threats],
            mode='markers+text', 
            marker=dict(size=18, color='red', symbol='triangle-up', line=dict(color='white', width=1)),
            text=[f"!! {m['id']} !!" for m in threats],
            textfont=dict(color="red", size=12), 
            textposition="top center",
            name="HIGH VELOCITY THREAT"
        ))

        fig.update_layout(
            polar=dict(
                bgcolor="black", 
                radialaxis=dict(gridcolor="#004400", color="#00FF41", range=[0, SCAN_RADIUS]),
                angularaxis=dict(gridcolor="#004400", color="#00FF41")
            ),
            paper_bgcolor="black", 
            font_color="#00FF41", 
            height=800, 
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_intel:
        st.error(t('threat_header'))
        st.caption(t('status'))
        
        intel_report = f"DSM STRATOSPHERIC INTELLIGENCE REPORT\nGENERATED: {datetime.now()}\nRESEARCHER: GESNER DESLANDES\n" + "="*40 + "\n"
        
        for m in threats:
            # Calculate impact relative to detection point
            i_lat, i_lon = calculate_impact(HOME_LAT, HOME_LON, m['dist']*0.12, m['brng'])
            
            with st.expander(f"🔴 TARGET ID: {m['id']}", expanded=True):
                st.write(f"**Class:** {m['type']}")
                st.write(f"**{t('speed')}:** {m['speed']} km/h (Mach {round(m['speed']/1234, 1)})")
                st.write(f"**{t('target')}:** `{i_lat:.4f}, {i_lon:.4f}`")
                st.progress(0.85) # Threat level
                
            intel_report += f"\n[TARGET: {m['id']}]\nType: {m['type']}\nVelocity: {m['speed']} km/h\nEst. Impact: {i_lat}, {i_lon}\n"
        
        st.divider()
        st.download_button(
            label=t('report'), 
            data=intel_report, 
            file_name=f"DSM_INTEL_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 
            mime="text/plain"
        )

    # Automatic Refresh for Radar Animation
    time.sleep(1)
    st.rerun()

# --- PLACEHOLDERS FOR AIRCRAFT & SATELLITE ---
elif mode == t('m1'):
    st.info(f"{t('m1')} - Global Airspace Feed")
    st.warning("Secure API Connection Required. Please configure OpenSky/FlightRadar24 keys in GitHub Secrets.")
    st.write("Aircraft tracking is temporarily paused to prioritize Tactical Missile Defense (Mode 3).")

elif mode == t('m2'):
    st.info(f"{t('m2')} - Orbital Tracking Feed")
    st.warning("TLE Data Stream Pending. Please configure N2YO API keys in GitHub Secrets.")
    st.write("Satellite ground tracks will appear here once the orbital engine is synced.")

st.sidebar.markdown("---")
st.sidebar.info("Deslandes Stratosphere Monitor (DSM) v3.0 - Global Surveillance Suite")
