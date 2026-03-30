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
if 'lang' not in st.session_state:
    st.session_state.lang = "English"

# --- 2. TRANSLATION DICTIONARY ---
t = {
    "English": {
        "title": "DESLANDES STRATOSPHERE MONITOR", "sensor": "SENSORS", "radar": "RADAR CONTROL",
        "lat": "Latitude", "lon": "Longitude", "range": "Range Radius", "demo": "Demo Mode",
        "log": "TARGET LOG", "owner": "Owner", "company": "Company Name", "purchase": "PURCHASE THIS APP",
        "delivery": "Full package sent via email within 24 hours.", "export": "DOWNLOAD TACTICAL DATA",
        "air": "Aircraft", "sat": "Satellite", "mis": "Missile", "scan": "SCANNING", "lock": "SYSTEM SECURED"
    },
    "Kreyòl Ayisyen": {
        "title": "MONITÈ STRATOSFÈ DESLANDES", "sensor": "KAPTÈ YO", "radar": "KONTWÒL RADAR",
        "lat": "Latitid", "lon": "Lonjitid", "range": "Reyon Deteksyon", "demo": "Mòd Demo",
        "log": "LIS SIB YO", "owner": "Mèt Pwojè", "company": "Non Konpayi", "purchase": "ACHTE APP SA A",
        "delivery": "Pake konplè ap voye pa imel nan 24 èdtan.", "export": "TELECHAKE RAPÒ TAKTIK",
        "air": "Avyon", "sat": "Satelit", "mis": "Misil", "scan": "AP SKANE", "lock": "SISTÈM AN SEKIRITE"
    },
    "Español": {
        "title": "MONITOR DE ESTRATOSFERA DESLANDES", "sensor": "SENSORES", "radar": "CONTROL DE RADAR",
        "lat": "Latitud", "lon": "Longitud", "range": "Radio de Alcance", "demo": "Modo Demo",
        "log": "REGISTRO DE OBJETIVOS", "owner": "Propietario", "company": "Nombre de la Empresa", "purchase": "COMPRAR ESTA APP",
        "delivery": "Paquete completo enviado por email en 24 horas.", "export": "DESCARGAR DATOS TÁCTICOS",
        "air": "Avión", "sat": "Satélite", "mis": "Misil", "scan": "ESCANEANDO", "lock": "SISTEMA ASEGURADO"
    },
    "Français": {
        "title": "MONITEUR DE STRATOSPHÈRE DESLANDES", "sensor": "CAPTEURS", "radar": "CONTRÔLE RADAR",
        "lat": "Latitude", "lon": "Longitude", "range": "Rayon de Détection", "demo": "Mode Démo",
        "log": "REGISTRE DES CIBLES", "owner": "Propriétaire", "company": "Nom de l'Entreprise", "purchase": "ACHETER CETTE APP",
        "delivery": "Package complet envoyé par email sous 24 heures.", "export": "TÉLÉCHARGER DONNÉES TACTIQUES",
        "air": "Avion", "sat": "Satellite", "mis": "Missile", "scan": "BALAYAGE EN COURS", "lock": "SYSTÈME SÉCURISÉ"
    }
}

# --- 3. AUTHENTICATION ---
def check_password():
    curr = t[st.session_state.lang]
    def password_entered():
        if "password" in st.session_state:
            if st.session_state["password"] == "20082010":
                st.session_state.authenticated = True
                del st.session_state["password"]
            else:
                st.error("❌ Access Denied")

    if not st.session_state.authenticated:
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src='https://flagcdn.com/w640/ht.png' width='400' style='border-radius: 8px;'>
            </div>
            <h1 style='text-align: center; color: #00FF41;'>DSM-2026: {curr['lock']}</h1>
        """, unsafe_allow_html=True)
        st.text_input("PASSWORD", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()
curr = t[st.session_state.lang]

# --- 4. DATA ENGINE ---
def get_radar_data(mode, r_max):
    count = 15 if mode == "Satellite" else 6
    return [{"ID": f"TGT-{mode[:3].upper()}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(900, 25000)} for i in range(count)]

# --- 5. SIDEBAR (LANGUAGE & LICENSE) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://flagcdn.com/w320/ht.png' width='200'></div>", unsafe_allow_html=True)
    
    # LANGUAGE SELECTOR
    st.session_state.lang = st.selectbox("🌐 SELECT LANGUAGE", ["English", "Kreyòl Ayisyen", "Español", "Français"], index=0)
    
    st.title(f"📡 {curr['radar']}")
    
    # LICENSE INFO
    st.info(f"**📜 LICENSE**\n**{curr['company']}:** GlobalInternet.py\n**{curr['owner']}:** Gesner Deslandes\n**Email:** deslandes78@gmail.com")
    st.success(f"**🛒 {curr['purchase']}**\n{curr['delivery']}")
    
    st.markdown("---")
    u_lat = st.number_input(curr['lat'], value=18.53)
    u_lon = st.number_input(curr['lon'], value=-72.33)
    m_range = st.slider(curr['range'], 50, 5000, 1500)
    
    if st.button("TERMINATE SESSION"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN INTERFACE ---
st.markdown(f"<h1 style='color: #00FF41; text-align: center;'>🔴 {curr['title']}</h1>", unsafe_allow_html=True)

app_mode = st.radio("MODES", [f"✈️ {curr['air']}", f"🛰️ {curr['sat']}", f"🚀 {curr['mis']}"], horizontal=True, label_visibility="collapsed")
active_key = app_mode.split(" ")[1]

objects = get_radar_data(active_key, m_range)
col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 {active_key.upper()} {curr['scan']}... [{u_lat}, {u_lon}]")
    fig = go.Figure()
    sweep = (time.time() * 120) % 360
    fig.add_trace(go.Scatterpolar(r=[0, m_range], theta=[sweep, sweep], mode='lines', line=dict(color='#00FF41', width=6), showlegend=False))
    fig.add_trace(go.Scatterpolar(r=[o['Dist'] for o in objects], theta=[o['Deg'] for o in objects], mode='markers+text', marker=dict(size=12, color='red', symbol='cross'), text=[o['ID'] for o in objects], textposition="top right"))
    fig.update_layout(polar=dict(bgcolor="black", radialaxis=dict(gridcolor="#004400", color="lime", range=[0, m_range]), angularaxis=dict(gridcolor="#004400", color="lime")), paper_bgcolor="black", font_color="lime", height=700)
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.error(f"🔴 {curr['log']}")
    st.dataframe(pd.DataFrame(objects), hide_index=True, use_container_width=True)
    st.markdown(f"""<div style='background-color:#00209F;padding:5px;text-align:center;color:white;font-weight:bold;'>MADE IN HAITI</div>
                    <div style='background-color:#D21034;padding:5px;text-align:center;color:white;font-weight:bold;'>GLOBALINTERNET.PY</div>""", unsafe_allow_html=True)
    
    # MULTILINGUAL REPORT DOWNLOAD
    report_csv = pd.DataFrame(objects).to_csv(index=False)
    st.download_button(f"📥 {curr['export']}", report_csv, f"DSM_REPORT_{st.session_state.lang}.csv")

time.sleep(1)
st.rerun()
