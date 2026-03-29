import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2, pi, asin, degrees
import time
import random
from datetime import datetime

# -------------------------------------------------------------------
# Extended Language Dictionaries with Missile Mode
# -------------------------------------------------------------------
TRANSLATIONS = {
    'en': {
        'app_title': '🔴 GLOBAL SURVEILLANCE RADAR',
        'missile_mode': '🚀 Missile Detector',
        'threat_detected': '⚠️ THREAT DETECTED',
        'target_est': 'Target Destination',
        'impact_eta': 'Estimated Impact',
        'missile_id': 'Missile ID',
        'speed_mach': 'Speed (Mach/kmh)',
        'radar_sweep': '📡 RADAR SWEEP VIEW',
        'owner': '🇭🇹 Owner: Gesner Deslandes – Licensed Software',
    },
    'fr': {
        'app_title': '🔴 RADAR DE SURVEILLANCE GLOBAL',
        'missile_mode': '🚀 Détecteur de Missiles',
        'threat_detected': '⚠️ MENACE DÉTECTÉE',
        'target_est': 'Destination Cible',
        'impact_eta': 'Impact Estimé',
        'missile_id': 'ID du Missile',
        'speed_mach': 'Vitesse (Mach/kmh)',
        'radar_sweep': '📡 VUE RADAR (BALAYAGE)',
        'owner': '🇭🇹 Propriétaire : Gesner Deslandes',
    },
    'ht': {
        'app_title': '🔴 RADAR SIVEYANS GLOBAL',
        'missile_mode': '🚀 Detektè Misil',
        'threat_detected': '⚠️ MENAS DETEKTE',
        'target_est': 'Destinasyon Sib',
        'impact_eta': 'Tan Enpak',
        'missile_id': 'ID Misil',
        'speed_mach': 'Vitès (Mach/kmh)',
        'radar_sweep': '📡 VIZUALIZASYON RADAR',
        'owner': '🇭🇹 Pwopriyetè: Gesner Deslandes',
    }
}

def t(key, **kwargs):
    lang = st.session_state.get('language', 'en')
    text = TRANSLATIONS.get(lang, TRANSLATIONS.get('en', {})).get(key, key)
    return text.format(**kwargs) if kwargs else text

# -------------------------------------------------------------------
# Page Config & State
# -------------------------------------------------------------------
st.set_page_config(page_title="Global Surveillance - Missile Mode", layout="wide", page_icon="🔴")

if 'language' not in st.session_state:
    st.session_state.language = 'en'

# -------------------------------------------------------------------
# Missile Logic & Physics
# -------------------------------------------------------------------
def get_destination(lat, lon, dist_km, brng_deg):
    R = 6371
    lat1, lon1, brng = radians(lat), radians(lon), radians(brng_deg)
    d = dist_km / R
    lat2 = asin(sin(lat1)*cos(d) + cos(lat1)*sin(d)*cos(brng))
    lon2 = lon1 + atan2(sin(brng)*sin(d)*cos(lat1), cos(d)-sin(lat1)*sin(lat2))
    return degrees(lat2), degrees(lon2)

def generate_missiles(r_lat, r_lon, r_range):
    m_list = []
    types = ["ICBM", "Cruise", "Hypersonic"]
    for i in range(random.randint(1, 4)):
        m_type = random.choice(types)
        dist = random.uniform(50, r_range)
        brng = random.uniform(0, 360)
        m_lat, m_lon = get_destination(r_lat, r_lon, dist, brng)
        
        speed = random.uniform(2000, 7000) if m_type != "Cruise" else random.uniform(800, 1100)
        heading = (brng + 180 + random.uniform(-15, 15)) % 360
        
        dest_lat, dest_lon = get_destination(m_lat, m_lon, dist * 0.9, heading)
        
        m_list.append({
            "id": f"MSL-{random.randint(100, 999)}",
            "type": m_type,
            "lat": m_lat, "lon": m_lon,
            "speed": speed,
            "heading": heading,
            "dest": f"{dest_lat:.4f}, {dest_lon:.4f}",
            "dist": dist
        })
    return m_list

# -------------------------------------------------------------------
# Main UI
# -------------------------------------------------------------------
st.title(t('app_title'))
st.caption(t('owner'))

# Mode selector
mode = st.radio("", ["Aircraft Radar", "Satellite Tracker", t('missile_mode')], horizontal=True)

if mode == t('missile_mode'):
    col1, col2 = st.columns([2, 1])
    
    # Radar Parameters
    r_lat, r_lon = 18.5392, -72.3350 # Default (Haiti)
    r_range = 2000
    
    missiles = generate_missiles(r_lat, r_lon, r_range)
    
    with col1:
        st.subheader(t('radar_sweep'))
        
        # Plotly Polar Radar with Dual Needles
        fig = go.Figure()
        
        # Rotating Needles Animation
        angle = (time.time() * 60) % 360
        for offset in [0, 180]:
            fig.add_trace(go.Scatterpolar(r=[0, r_range], theta=[(angle+offset)%360]*2,
                                         mode='lines', line=dict(color='lime', width=4), opacity=0.6, showlegend=False))
        
        # Plot Missiles
        if missiles:
            rs = [m['dist'] for m in missiles]
            # Simple bearing calculation for polar plot
            thetas = [m['heading'] for m in missiles] 
            
            fig.add_trace(go.Scatterpolar(
                r=rs, theta=thetas, mode='markers+text',
                marker=dict(size=15, color='red', symbol='x'),
                text=[m['id'] for m in missiles],
                textposition="top center",
                name="THREAT"
            ))

        fig.update_layout(
            polar=dict(bgcolor="black", radialaxis=dict(visible=True, color="green", gridcolor="green"),
                      angularaxis=dict(color="green", gridcolor="green")),
            paper_bgcolor="black", font_color="green", height=700
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.error(t('threat_detected'))
        for m in missiles:
            with st.expander(f"🔴 {m['id']} - {m['type']}"):
                st.write(f"**{t('speed_mach')}:** {m['speed']:.0f} km/h")
                st.write(f"**Heading:** {m['heading']:.1f}°")
                st.write(f"**{t('target_est')}:** {m['dest']}")
                st.progress(min(m['speed']/7000, 1.0))
        
        if st.button("Manual Scour OpenSky"):
            st.rerun()

    # Auto-refresh loop
    time.sleep(3)
    st.rerun()

else:
    st.info("Switch to Missile Detector mode to see the new radar system.")
