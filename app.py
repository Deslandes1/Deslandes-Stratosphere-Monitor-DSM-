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
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

# --- 2. TRANSLATION DICTIONARY ---
t = {
    "English": {
        "title": "DESLANDES STRATOSPHERE MONITOR", "sensor": "SENSORS", "radar": "RADAR CONTROL",
        "lat": "Latitude", "lon": "Longitude", "range": "Range Radius", "demo": "Demo Mode (Simulation)",
        "log": "TARGET LOG", "owner": "Owner", "company": "Company Name", "purchase": "PURCHASE THIS APP",
        "delivery": "Full package sent via email within 24 hours.", "export": "DOWNLOAD TACTICAL DATA",
        "air": "Aircraft", "sat": "Satellite", "mis": "Missile", "scan": "SCANNING", "lock": "SYSTEM SECURED",
        "api_user": "AIP Username", "api_key": "AIP Secret Key"
    },
    "Kreyòl Ayisyen": {
        "title": "MONITÈ STRATOSFÈ DESLANDES", "sensor": "KAPTÈ YO", "radar": "KONTWÒL RADAR",
        "lat": "Latitid", "lon": "Lonjitid", "range": "Reyon Deteksyon", "demo": "Mòd Demo (Similasyon)",
        "log": "LIS SIB YO", "owner": "Mèt Pwojè", "company": "Non Konpayi", "purchase": "ACHTE APP SA A",
        "delivery": "Pake konplè ap voye pa imel nan 24 èdtan.", "export": "TELECHAKE RAPÒ TAKTIK",
        "air": "Avyon", "sat": "Satelit", "mis": "Misil", "scan": "AP SKANE", "lock": "SISTÈM AN SEKIRITE",
        "api_user": "AIP Itilizatè", "api_key": "AIP Kòd Sekrè"
    },
    "Español": {
        "title": "MONITOR DE ESTRATOSFERA DESLANDES", "sensor": "SENSORES", "radar": "CONTROL DE RADAR",
        "lat": "Latitud", "lon": "Longitud", "range": "Radio de Alcance", "demo": "Modo Demo (Simulación)",
        "log": "REGISTRO DE OBJETIVOS", "owner": "Propietario", "company": "Nombre de la Empresa", "purchase": "COMPRAR ESTA APP",
        "delivery": "Paquete completo enviado por email en 24 horas.", "export": "DESCARGAR DATOS TÁCTICOS",
        "air": "Avión", "sat": "Satélite", "mis": "Misil", "scan": "ESCANEANDO", "lock": "SISTEMA ASEGURADO",
        "api_user": "Usuario AIP", "api_key": "Clave Secreta AIP"
    },
    "Français": {
        "title": "MONITEUR DE STRATOSPHÈRE DESLANDES", "sensor": "CAPTEURS", "radar": "CONTRÔLE RADAR",
        "lat": "Latitude", "lon": "Longitude", "range": "Rayon de Détection", "demo": "Mode Démo (Simulation)",
        "log": "REGISTRE DES CIBLES", "owner": "Propriétaire", "company": "Nom de l'Entreprise", "purchase": "ACHETER CETTE APP",
        "delivery": "Package complet envoyé par email sous 24 heures.", "export": "TÉLÉCHARGER DONNÉES TACTIQUES",
        "air": "Avion", "sat": "Satellite", "mis": "Missile", "scan": "BALAYAGE EN COURS", "lock": "SYSTÈME SÉCURISÉ",
        "api_user": "Utilisateur AIP", "api_key": "Clé Secrète AIP"
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
                <img src='https://flagcdn.com/w640/ht.png' width='400' style='border-radius: 8px; box-shadow: 0px 8px 25px rgba(0,0,0,0.7); border: 1px solid #333;'>
            </div>
            <h1 style='text-align: center; color: #00FF41;'>DSM-2026: {curr['lock']}</h1>
        """, unsafe_allow_html=True)
        st.text_input("PASSWORD", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()
curr = t[st.session_state.lang]

# --- 4. DATA ENGINE (AIRCRAFT API INTEGRATION) ---
def get_radar_data(mode, user, pw, lat, lon, r_max):
    if mode == "Aircraft" and not st.session_state.demo_mode:
        lat_delta = r_max / 111.0
        lon_delta = r_max / (111.0 * np.cos(np.radians(lat)))
        url = f"https://opensky-network.org/api/states/all?lamin={lat-lat_delta}&lomin={lon-lon_delta}&lamax={lat+lat_delta}&lomax={lon+lon_delta}"
        try:
            auth = (user, pw) if user and pw else None
            response = requests.get(url, auth=auth, timeout=5)
            if response.status_code == 200:
                states = response.json().get('states', [])[:25]
                return [{"ID": s[1] or s[0], "Dist": np.random.randint(5, r_max), "Deg": np.random.randint(0, 360), "Spd": int(s[9]*3.6) if s[9] else 0} for s in states]
        except: pass
    
    count = 18 if mode == "Satellite" else 7
    return [{"ID": f"TGT-{mode[:3].upper()}-{i}", "Dist": np.random.randint(10, r_max), "Deg": np.random.randint(0, 360), "Spd": np.random.randint(900, 28000)} for i in range(count)]

# --- 5. SIDEBAR (API INPUTS, LANGUAGE & LICENSE) ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><img src='https://flagcdn.com/w320/ht.png' width='220' style='border-radius: 4px; border: 1px solid #444;'></div>", unsafe_allow_html=True)
    
    # LANGUAGE SELECTOR
    st.session_state.lang = st.selectbox("🌐 SELECT LANGUAGE", ["English", "Kreyòl Ayisyen", "Español", "Français"], index=0)
    
    st.title(f"📡 {curr['radar']}")
    
    # LICENSE & PURCHASE INFO
    st.info(f"**📜 LICENSE**\n**{curr['company']}:** GlobalInternet.py\n**{curr['owner']}:** Gesner Deslandes\n**Email:** deslandes78@gmail.com")
    st.success(f"**🛒 {curr['purchase']}**\n{curr['delivery']}")
    
    st.markdown("---")
    # API CREDENTIALS SECTION
    st.markdown("### 🔑 API CREDENTIALS")
    api_user = st.text_input(curr['api_user'], placeholder="Enter AIP Username")
    api_key = st.text_input(curr['api_key'], type="password", placeholder="Enter Secret Key")
    
    st.markdown("---")
    st.markdown(f"### 📍 {curr['lat']} & {curr['lon']}")
    u_lat = st.number_input(curr['lat'], value=18.53, format="%.4f")
    u_lon = st.number_input(curr['lon'], value=-72.33, format="%.4f")
    m_range = st.slider(curr['range'], 50, 5000, 1500, 50)
    
    st.session_state.demo_mode = st.toggle(curr['demo'], value=True)
    
    if st.button("TERMINATE SESSION"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN RADAR INTERFACE ---
st.markdown(f"<h1 style='color: #00FF41; text-align: center; border-bottom: 2px solid #004400; padding-bottom: 10px;'>🔴 {curr['title']}</h1>", unsafe_allow_html=True)

# Application Mode Selector
app_mode_raw = st.radio("SENSORS", [f"✈️ {curr['air']}", f"🛰️ {curr['sat']}", f"🚀 {curr['mis']}"], horizontal=True, label_visibility="collapsed")
active_key = "Aircraft" if curr['air'] in app_mode_raw else ("Satellite" if curr['sat'] in app_mode_raw else "Missile")

# Retrieve Data
objects = get_radar_data(active_key, api_user, api_key, u_lat, u_lon, m_range)

col_radar, col_data = st.columns([2, 1])

with col_radar:
    st.subheader(f"📡 {active_key.upper()} {curr['scan']}... [CENTER: {u_lat}, {u_lon}]")
    fig = go.Figure()
    sweep_pos = (time.time() * 125) % 360 
    
    # Animated Radar Sweep
    fig.add_trace(go.Scatterpolar(r=[0, m_range], theta=[sweep_pos, sweep_pos], mode='lines', line=dict(color='#00FF41', width=7), opacity=0.9, showlegend=False))
    
    # Plot Targets
    fig.add_trace(go.Scatterpolar(
        r=[o['Dist'] for o in objects], theta=[o['Deg'] for o in objects],
        mode='markers+text', marker=dict(size=14, color='red', symbol='cross', line=dict(color='white', width=1)),
        text=[o['ID'] for o in objects], textposition="top right"
    ))

    fig.update_layout(
        polar=dict(bgcolor="black", 
                   radialaxis=dict(gridcolor="#004400", color="lime", range=[0, m_range], ticksuffix="km"),
                   angularaxis=dict(gridcolor="#004400", color="lime")),
        paper_bgcolor="black", font_color="lime", height=750, margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.error(f"🔴 {curr['log']}")
    st.dataframe(pd.DataFrame(objects), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    # BRANDING
    st.markdown("""
        <div style='background-color: #00209F; padding: 5px; text-align: center; border-radius: 5px 5px 0 0;'>
            <span style='color: white; font-weight: bold;'>MADE IN HAITI</span>
        </div>
        <div style='background-color: #D21034; padding: 5px; text-align: center; border-radius: 0 0 5px 5px;'>
            <span style='color: white; font-weight: bold;'>GLOBALINTERNET.PY</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.write(f"**Developer:** Gesner Deslandes")
        st.write(f"**License:** DSM-2026-PREMIUM")
        st.write(f"**Contact:** (509)-4738-5663")
    
    # Download Tactical Data
    report_data = pd.DataFrame(objects).to_csv(index=False)
    st.download_button(f"📥 {curr['export']}", report_data, f"DSM_INTEL_{active_key}.csv")

time.sleep(1)
st.rerun()
