import streamlit as st
import pandas as pd
import math

# Configuración de página
st.set_page_config(
    page_title="Calculador ISO 286",
    page_icon="⚙️",
    layout="wide"
)

# --- MOTOR DE DATOS ---
RANGOS_DIAMETROS = [
    (0, 3), (3, 6), (6, 10), (10, 18), (18, 30), (30, 50), (50, 80), (80, 120),
    (120, 180), (180, 250), (250, 315), (315, 400), (400, 500), (500, 630),
    (630, 800), (800, 1000), (1000, 1250), (1250, 1600), (1600, 2000), (2000, 2500),
    (2500, 3150)
]

TABLA_IT = {
    "5":  [4, 5, 6, 8, 9, 11, 13, 15, 18, 20, 23, 25, 27, 32, 36, 40, 47, 55, 65, 78, 96],
    "6":  [6, 8, 9, 11, 13, 16, 19, 22, 25, 29, 32, 36, 40, 44, 50, 56, 66, 78, 92, 110, 135],
    "7":  [10, 12, 15, 18, 21, 25, 30, 35, 40, 46, 52, 57, 63, 70, 80, 90, 105, 125, 150, 175, 210],
    "8":  [14, 18, 22, 27, 33, 39, 46, 54, 63, 72, 81, 89, 97, 110, 125, 140, 165, 195, 230, 280, 330],
    "9":  [25, 30, 36, 43, 52, 62, 74, 87, 100, 115, 130, 140, 155, 175, 200, 230, 260, 310, 370, 440, 540],
    "10": [40, 48, 58, 70, 84, 100, 120, 140, 160, 185, 210, 230, 250, 280, 320, 360, 420, 500, 600, 700, 860],
    "11": [60, 75, 90, 110, 130, 160, 190, 220, 250, 290, 320, 360, 400, 440, 500, 560, 660, 780, 920, 1100, 1350],
    "12": [100, 120, 150, 180, 210, 250, 300, 350, 400, 460, 520, 570, 630, 700, 800, 900, 1050, 1250, 1500, 1750, 2100],
    "13": [140, 180, 220, 270, 330, 390, 460, 540, 630, 720, 810, 890, 970, 1100, 1250, 1400, 1650, 1950, 2300, 2800, 3300],
}

def obtener_indice_rango(d):
    for idx, (inf, sup) in enumerate(RANGOS_DIAMETROS):
        if inf < d <= sup: return idx
    return -1

def calcular_desviacion_fundamental(letra, d, it_val):
    letra_lower = letra.lower()
    es_agujero = letra.isupper()
    idx = obtener_indice_rango(d)
    if idx == -1: return 0
    inf, sup = RANGOS_DIAMETROS[idx]
    dm = math.sqrt(inf * (sup if sup > 0 else inf)) if inf > 0 else sup / 2
    if letra_lower in ["js", "h"]: return 0
    dev_eje = 0
    if letra_lower == "a":   dev_eje = -(265 + 1.3 * dm) if d <= 120 else -3.5 * dm
    elif letra_lower == "b": dev_eje = -(140 + 0.85 * dm) if d <= 160 else -1.8 * dm
    elif letra_lower == "c": dev_eje = -(52 * (dm**0.2))
    elif letra_lower == "d": dev_eje = -(16 * (dm**0.44))
    elif letra_lower == "e": dev_eje = -(11 * (dm**0.41))
    elif letra_lower == "f": dev_eje = -(5.5 * (dm**0.41))
    elif letra_lower == "g": dev_eje = -(2.5 * (dm**0.34))
    elif letra_lower == "k": dev_eje = 0.6 * (dm**(1/3))
    elif letra_lower == "m": dev_eje = 2.8 * (dm**0.41)
    elif letra_lower == "n": dev_eje = 5 * (dm**0.34)
    elif letra_lower == "p": dev_eje = 3 * (dm**0.44) + (it_val if int(it_val) < 7 else 0)
    elif letra_lower == "r": dev_eje = 5 * (dm**0.34) + 10
    elif letra_lower == "s": dev_eje = (dm**0.44) + 20
    elif letra_lower in ["t", "u", "v", "x", "y", "z", "za", "zb", "zc"]:
        potencias = {"t": 30, "u": 45, "v": 60, "x": 80, "y": 100, "z": 140, "za": 180, "zb": 220, "zc": 300}
        dev_eje = potencias[letra_lower] + (dm**0.5)
    return -dev_eje if es_agujero else dev_eje

def obtener_tolerancias_completas(tipo, letra, grado, diametro):
    idx = obtener_indice_rango(diametro)
    if idx == -1: return None, None, None, ["Fuera de rango"]
    it_val = TABLA_IT[grado][idx]
    alertas = []
    if letra.lower() == "js":
        es_sup, ei_inf = it_val/2, -it_val/2
    else:
        dev_fund = calcular_desviacion_fundamental(letra, diametro, it_val)
        if tipo == "Agujero":
            if letra.upper() <= "H": ei_inf = dev_fund; es_sup = ei_inf + it_val
            else: es_sup = dev_fund; ei_inf = es_sup - it_val
        else:
            if letra.lower() <= "h": es_sup = dev_fund; ei_inf = es_sup - it_val
            else: ei_inf = dev_fund; es_sup = ei_inf + it_val
    return es_sup/1000.0, ei_inf/1000.0, it_val/1000.0, alertas

def dibujar_componente_svg(tipo, nominal, es, ei, real, status):
    escala_y = 3500.0
    origen_y = 150
    y_sup = origen_y - (es * escala_y)
    y_inf = origen_y - (ei * escala_y)
    y_real = origen_y - ((real - nominal) * escala_y)
    color = "#2ecc71" if tipo == "Agujero" else "#e67e22"
    color_real = "#2ecc71" if status else "#e74c3c"
    pattern = "diagonalHatchHole" if tipo == "Agujero" else "diagonalHatchShaft"
    
    svg = f"""
    <svg width="100%" height="220" viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" style="background-color: #1a1a1a; border-radius: 8px;">
        <defs>
            <pattern id="diagonalHatchHole" width="8" height="8" patternUnits="userSpaceOnUse">
                <line x1="0" y1="8" x2="8" y2="0" stroke="#2ecc71" stroke-width="1" />
            </pattern>
            <pattern id="diagonalHatchShaft" width="8" height="8" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="8" y2="8" stroke="#e67e22" stroke-width="1" />
            </pattern>
        </defs>
        <line x1="50" y1="{origen_y}" x2="550" y2="{origen_y}" stroke="#555" stroke-width="1" stroke-dasharray="4"/>
        <text x="560" y="{origen_y+4}" fill="#555" font-family="sans-serif" font-size="10">Ø Nominal</text>
        
        <rect x="200" y="{min(y_sup, y_inf)}" width="200" height="{max(2.0, abs(y_sup - y_inf))}" fill="url(#{pattern})" stroke="{color}" stroke-width="2" opacity="0.8"/>
        
        <line x1="150" y1="{y_real}" x2="450" y2="{y_real}" stroke="{color_real}" stroke-width="2" stroke-dasharray="3,3"/>
        <circle cx="300" cy="{y_real}" r="4" fill="{color_real}"/>
        <text x="310" y="{y_real-10}" fill="{color_real}" font-family="sans-serif" font-size="12" font-weight="bold">Medido: {real:.3f}</text>
        
        <text x="190" y="{y_sup+4}" fill="{color}" font-family="sans-serif" font-size="11" text-anchor="end">{nominal+es:.3f}</text>
        <text x="190" y="{y_inf+4}" fill="{color}" font-family="sans-serif" font-size="11" text-anchor="end">{nominal+ei:.3f}</text>
    </svg>
    """
    return svg

# --- INTERFAZ ---
st.title("⚙️ Tolerancias ISO 286")

# Pestañas: Se cambia el orden para que la de componente sea default
tab_comp, tab_ajuste = st.tabs(["📖 Consulta de Componente", "📊 Análisis de Ajuste"])

with tab_comp:
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c1:
        tipo_c = st.radio("Tipo:", ["Agujero", "Eje"], horizontal=True)
        d_nom_c = st.number_input("Nominal (mm):", 0.001, 3150.0, 100.0, 0.001, format="%.3f")
    with col_c2:
        letra_c = st.text_input("Posición:", "H" if tipo_c == "Agujero" else "h")
        grado_c = st.selectbox("Calidad:", list(TABLA_IT.keys()), index=3)
    with col_c3:
        val_real_c = st.number_input("Valor Real Medido:", 0.0, 3200.0, d_nom_c, 0.001, format="%.3f")

    es_c, ei_c, it_c, _ = obtener_tolerancias_completas(tipo_c, letra_c, grado_c, d_nom_c)
    
    if es_c is not None:
        c_max, c_min = d_nom_c + es_c, d_nom_c + ei_c
        dentro = c_min <= val_real_c <= c_max
        
        # Resultados compactos
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Cota Máxima", f"{c_max:.3f} mm")
        res_col2.metric("Cota Mínima", f"{c_min:.3f} mm")
        res_col3.metric("Estado", "DENTRO" if dentro else "FUERA", delta="OK" if dentro else "RECHAZO", delta_color="normal" if dentro else "inverse")
        
        st.components.v1.html(dibujar_componente_svg(tipo_c, d_nom_c, es_c, ei_c, val_real_c, dentro), height=230)

with tab_ajuste:
    st.header("Cálculo de Acoplamientos")
    col1, col2, col3 = st.columns(3)
    with col1:
        d_nom_a = st.number_input("Ø Nominal (mm):", 0.001, 3150.0, 45.0, 0.001, format="%.3f", key="dn_a")
    with col2:
        st.caption("Agujero")
        ag_l = st.selectbox("Letra:", ["H", "A", "B", "C", "D", "E", "F", "G", "JS", "K", "M", "N", "P", "R", "S", "T", "U", "V", "X", "Y", "Z"], key="al")
        ag_g = st.selectbox("Grado:", list(TABLA_IT.keys()), index=2, key="ag")
    with col3:
        st.caption("Eje")
        ej_l = st.selectbox("Letra:", ["h", "a", "b", "c", "d", "e", "f", "g", "js", "k", "m", "n", "p", "r", "s", "t", "u", "v", "x", "y", "z"], index=7, key="el")
        ej_g = st.selectbox("Grado:", list(TABLA_IT.keys()), index=1, key="eg")

    es_A, ei_A, _, _ = obtener_tolerancias_completas("Agujero", ag_l, ag_g, d_nom_a)
    es_E, ei_E, _, _ = obtener_tolerancias_completas("Eje", ej_l, ej_g, d_nom_a)

    if es_A is not None and es_E is not None:
        j_max, j_min = es_A - ei_E, ei_A - es_E
        if j_min >= 0: tipo, color = "JUEGO", "#2ecc71"
        elif j_max <= 0: tipo, color = "APRIETO", "#e74c3c"
        else: tipo, color = "TRANSICIÓN", "#3498db"

        st.markdown(f"### Ajuste: <span style='color:{color};'>{tipo}</span>", unsafe_allow_html=True)
        
        # Tabla compacta de límites
        data = {
            "Límite": ["Máximo", "Mínimo"],
            "Agujero": [f"{d_nom_a+es_A:.3f}", f"{d_nom_a+ei_A:.3f}"],
            "Eje": [f"{d_nom_a+es_E:.3f}", f"{d_nom_a+ei_E:.3f}"]
        }
        st.table(pd.DataFrame(data).set_index("Límite"))
