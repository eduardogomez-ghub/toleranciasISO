import streamlit as st
import pandas as pd
import math

# Configuración de página profesional
st.set_page_config(
    page_title="Calculador Avanzado de Tolerancias ISO 286",
    page_icon="⚙️",
    layout="wide"
)

# --- MOTOR DE DATOS OFICIALES UNE-EN 20286-2 ---
RANGOS_DIAMETROS = [
    (0, 3), (3, 6), (6, 10), (10, 18), (18, 30), (30, 50), (50, 80), (80, 120),
    (120, 180), (180, 250), (250, 315), (315, 400), (400, 500), (500, 630),
    (630, 800), (800, 1000), (1000, 1250), (1250, 1600), (1600, 2000), (2000, 2500),
    (2500, 3150)
]

TABLA_IT = {
    "5":  [4,   5,   6,   8,   9,   11,  13,  15,  18,  20,  23,  25,  27,  32,  36,  40,  47,  55,  65,  78,  96],
    "6":  [6,   8,   9,   11,  13,  16,  19,  22,  25,  29,  32,  36,  40,  44,  50,  56,  66,  78,  92,  110, 135],
    "7":  [10,  12,  15,  18,  21,  25,  30,  35,  40,  46,  52,  57,  63,  70,  80,  90,  105, 125, 150, 175, 210],
    "8":  [14,  18,  22,  27,  33,  39,  46,  54,  63,  72,  81,  89,  97,  110, 125, 140, 165, 195, 230, 280, 330],
    "9":  [25,  30,  36,  43,  52,  62,  74,  87,  100, 115, 130, 140, 155, 175, 200, 230, 260, 310, 370, 440, 540],
    "10": [40,  48,  58,  70,  84,  100, 120, 140, 160, 185, 210, 230, 250, 280, 320, 360, 420, 500, 600, 700, 860],
    "11": [60,  75,  90,  110, 130, 160, 190, 220, 250, 290, 320, 360, 400, 440, 500, 560, 660, 780, 920, 1100, 1350],
    "12": [100, 120, 150, 180, 210, 250, 300, 350, 400, 460, 520, 570, 630, 700, 800, 900, 1050, 1250, 1500, 1750, 2100],
    "13": [140, 180, 220, 270, 330, 390, 460, 540, 630, 720, 810, 890, 970, 1100, 1250, 1400, 1650, 1950, 2300, 2800, 3300],
}

def obtener_indice_rango(d):
    for idx, (inf, sup) in enumerate(RANGOS_DIAMETROS):
        if inf < d <= sup:
            return idx
    return -1

def calcular_desviacion_fundamental(letra, d, it_val):
    letra_lower = letra.lower()
    es_agujero = letra.isupper()
    
    idx = obtener_indice_rango(d)
    if idx == -1: return 0
    inf, sup = RANGOS_DIAMETROS[idx]
    dm = math.sqrt(inf * (sup if sup > 0 else inf)) if inf > 0 else sup / 2

    if letra_lower == "js":
        return 0
    if letra_lower == "h":
        return 0

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

    if es_agujero:
        return -dev_eje
    else:
        return dev_eje

def obtener_tolerancias_completas(tipo, letra, grado, diametro):
    idx = obtener_indice_rango(diametro)
    if idx == -1:
        return None, None, None, ["Diámetro fuera del rango normativo (0.000 - 3150.000 mm)."]
    
    alertas = []
    if diametro > 500 and letra.upper() in ["A", "B", "C", "V", "X", "Y", "Z", "ZA", "ZB", "ZC"]:
        alertas.append(f"⚠️ La posición '{letra}' no está prevista por la norma para diámetros mayores a 500.000 mm.")
    if diametro <= 24 and letra.upper() == "T" and grado in ["5", "6", "7", "8"]:
        alertas.append(f"⚠️ Las clases {letra}{grado} no se representan para <= 24.000 mm. Se recomienda usar U.")
    if diametro <= 14 and letra.upper() == "V" and grado in ["5", "6", "7", "8"]:
        alertas.append(f"⚠️ Las clases {letra}{grado} no se representan para <= 14.000 mm. Se recomienda usar X.")
    if diametro <= 18 and letra.upper() == "Y" and grado in ["6", "7", "8", "9", "10"]:
        alertas.append(f"⚠️ Las clases {letra}{grado} no se representan para <= 18.000 mm. Se recomienda usar Z.")

    it_val = TABLA_IT[grado][idx]
    
    if letra.lower() == "js":
        mitad = it_val / 2
        es_sup = mitad
        ei_inf = -mitad
    else:
        dev_fund = calcular_desviacion_fundamental(letra, diametro, it_val)
        if tipo == "Agujero":
            if letra.upper() <= "H":
                ei_inf = dev_fund
                es_sup = ei_inf + it_val
            else:
                es_sup = dev_fund
                ei_inf = es_sup - it_val
        else:
            if letra.lower() <= "h":
                es_sup = dev_fund
                ei_inf = es_sup - it_val
            else:
                ei_inf = dev_fund
                es_sup = ei_inf + it_val

    return es_sup / 1000.0, ei_inf / 1000.0, it_val / 1000.0, alertas

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.title("⚙️ Sistema Avanzado de Ajustes y Tolerancias ISO 286")
st.caption("Herramienta optimizada para entorno de producción mecánica en milímetros (mm).")

tab1, tab2 = st.tabs(["📊 Análisis de Ajuste", "📖 Consulta de Componente Único"])

with tab1:
    st.header("Cálculo de Acoplamientos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Step a 0.001 y format a %.3f para garantizar precisión de milésimas
        d_nominal = st.number_input("Diámetro Nominal (mm):", min_value=0.001, max_value=3150.000, value=45.000, step=0.001, format="%.3f")
    with col2:
        st.subheader("Agujero")
        ag_letra = st.selectbox("Posición (Letra):", ["H", "A", "B", "C", "CD", "D", "E", "EF", "F", "FG", "G", "JS", "K", "M", "N", "P", "R", "S", "T", "U", "V", "X", "Y", "Z", "ZA", "ZB", "ZC"], index=0, key="let_ag")
        ag_grado = st.selectbox("Calidad (Grado):", list(TABLA_IT.keys()), index=2, key="ag_g")
    with col3:
        st.subheader("Eje")
        eje_letra = st.selectbox("Posición (Letra):", ["h", "a", "b", "c", "cd", "d", "e", "ef", "f", "fg", "g", "js", "k", "m", "n", "p", "r", "s", "t", "u", "v", "x", "y", "z", "za", "zb", "zc"], index=7, key="let_ej")
        eje_grado = st.selectbox("Calidad (Grado):", list(TABLA_IT.keys()), index=1, key="eje_g")

    es_Ag, ei_Ag, it_Ag, errs_Ag = obtener_tolerancias_completas("Agujero", ag_letra, ag_grado, d_nominal)
    es_Ej, ei_Ej, it_Ej, errs_Ej = obtener_tolerancias_completas("Eje", eje_letra, eje_grado, d_nominal)

    if es_Ag is not None and es_Ej is not None:
        todas_alertas = errs_Ag + errs_Ej
        for al in todas_alertas:
            st.warning(al)

        Max_Ag = d_nominal + es_Ag
        Min_Ag = d_nominal + ei_Ag
        Max_Ej = d_nominal + es_Ej
        Min_Ej = d_nominal + ei_Ej

        juego_max = es_Ag - ei_Ej
        juego_min = ei_Ag - es_Ej
        
        if juego_min >= 0:
            tipo_ajuste = "JUEGO (Clearance Fit)"
            color_ajuste = "#2ecc71"
            txt_det1 = f"Juego Máximo: {juego_max:.3f} mm"
            txt_det2 = f"Juego Mínimo: {juego_min:.3f} mm"
        elif juego_max <= 0:
            tipo_ajuste = "APRIETO (Interference Fit)"
            color_ajuste = "#e74c3c"
            txt_det1 = f"Aprieto Máximo: {abs(juego_min):.3f} mm"
            txt_det2 = f"Aprieto Mínimo: {abs(juego_max):.3f} mm"
        else:
            tipo_ajuste = "TRANSICIÓN (Transition Fit)"
            color_ajuste = "#3498db"
            txt_det1 = f"Juego Máximo: {juego_max:.3f} mm"
            txt_det2 = f"Aprieto Máximo: {abs(juego_min):.3f} mm"

        st.markdown(f"### Ajuste Determinado: <span style='color:{color_ajuste}; font-weight:bold;'>{tipo_ajuste}</span>", unsafe_allow_html=True)
        
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Especificación", f"Ø{d_nominal:.3f} {ag_letra}{ag_grado}/{eje_letra}{eje_grado}")
        c_m2.metric("Condición Límite 1", txt_det1)
        c_m3.metric("Condición Límite 2", txt_det2)

        st.markdown("#### Detalles de las Dimensiones Límites")
        df_res = pd.DataFrame({
            "Característica": ["Desviación Superior", "Desviación Inferior", "Dimensión Máxima Real", "Dimensión Mínima Real"],
            "AGUJERO": [f"{es_Ag:+.3f} mm", f"{ei_Ag:+.3f} mm", f"{Max_Ag:.3f} mm", f"{Min_Ag:.3f} mm"],
            "EJE": [f"{es_Ej:+.3f} mm", f"{ei_Ej:+.3f} mm", f"{Max_Ej:.3f} mm", f"{Min_Ej:.3f} mm"]
        })
        st.table(df_res.set_index("Característica"))

        # --- SECCIÓN: VALIDACIÓN DE VALORES REALES (SIEMPRE ACTIVA) ---
        st.markdown("#### 📍 Validación de Piezas Reales (Metrología)")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            val_real_ag = st.number_input("Valor real medido - AGUJERO (mm):", min_value=0.000, max_value=4000.000, value=float(d_nominal), step=0.001, format="%.3f")
            status_ag = Min_Ag <= val_real_ag <= Max_Ag
            if status_ag:
                st.success(f"🟢 AGUJERO ({val_real_ag:.3f} mm): DENTRO de rango tolerado.")
            else:
                st.error(f"🔴 AGUJERO ({val_real_ag:.3f} mm): FUERA de rango tolerado.")
        with col_v2:
            val_real_ej = st.number_input("Valor real medido - EJE (mm):", min_value=0.000, max_value=4000.000, value=float(d_nominal), step=0.001, format="%.3f")
            status_ej = Min_Ej <= val_real_ej <= Max_Ej
            if status_ej:
                st.success(f"🟢 EJE ({val_real_ej:.3f} mm): DENTRO de rango tolerado.")
            else:
                st.error(f"🔴 EJE ({val_real_ej:.3f} mm): FUERA de rango tolerado.")

        # --- GENERADOR GRÁFICO (SVG redistribuido y optimizado) ---
        st.markdown("#### 📐 Representación Gráfica del Ajuste")
        escala_y = 3000.0  
        origen_y = 150
        
        y_ag_sup = origen_y - (es_Ag * escala_y)
        y_ag_inf = origen_y - (ei_Ag * escala_y)
        y_eje_sup = origen_y - (es_Ej * escala_y)
        y_eje_inf = origen_y - (ei_Ej * escala_y)
        
        svg_lineas_reales = ""
        
        # 1. Proyección del Valor Real del Agujero (Etiqueta a la DERECHA del rectángulo)
        dev_real_ag = val_real_ag - d_nominal
        y_real_ag = origen_y - (dev_real_ag * escala_y)
        color_real_ag = "#2ecc71" if status_ag else "#e74c3c"
        
        if 0 <= y_real_ag <= 320:
            svg_lineas_reales += f"""
            <line x1="100" y1="{y_real_ag}" x2="375" y2="{y_real_ag}" stroke="{color_real_ag}" stroke-width="2.5" stroke-dasharray="4,4"/>
            <circle cx="180" cy="{y_real_ag}" r="4" fill="{color_real_ag}"/>
            <rect x="265" y="{y_real_ag - 9}" width="110" height="18" fill="#1a1a1a" rx="4" stroke="{color_real_ag}" stroke-width="1"/>
            <text x="320" y="{y_real_ag}" fill="{color_real_ag}" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" dominant-baseline="middle">Real: {val_real_ag:.3f}</text>
            """
        else:
            svg_lineas_reales += f'<text x="180" y="{"20" if y_real_ag < 0 else "300"}" fill="#e74c3c" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">⚠️ Real fuera escala ({val_real_ag:.3f})</text>'

        # 2. Proyección del Valor Real del Eje (Etiqueta a la IZQUIERDA del rectángulo)
        dev_real_ej = val_real_ej - d_nominal
        y_real_ej = origen_y - (dev_real_ej * escala_y)
        color_real_ej = "#2ecc71" if status_ej else "#e74c3c"
        
        if 0 <= y_real_ej <= 320:
            svg_lineas_reales += f"""
            <line x1="425" y1="{y_real_ej}" x2="700" y2="{y_real_ej}" stroke="{color_real_ej}" stroke-width="2.5" stroke-dasharray="4,4"/>
            <circle cx="620" cy="{y_real_ej}" r="4" fill="{color_real_ej}"/>
            <rect x="425" y="{y_real_ej - 9}" width="110" height="18" fill="#1a1a1a" rx="4" stroke="{color_real_ej}" stroke-width="1"/>
            <text x="480" y="{y_real_ej}" fill="{color_real_ej}" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" dominant-baseline="middle">Real: {val_real_ej:.3f}</text>
            """
        else:
            svg_lineas_reales += f'<text x="620" y="{"20" if y_real_ej < 0 else "300"}" fill="#e74c3c" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">⚠️ Real fuera escala ({val_real_ej:.3f})</text>'

        # Código SVG con coordenadas X ensanchadas para dejar espacio en el centro
        svg_code = f"""
        <svg width="100%" height="320" viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" style="background-color: #1a1a1a; border-radius: 8px;">
            <line x1="50" y1="{origen_y}" x2="750" y2="{origen_y}" stroke="#95a5a6" stroke-width="2" stroke-dasharray="5,5"/>
            <text x="755" y="{origen_y+5}" fill="#95a5a6" font-family="sans-serif" font-size="12">Línea Cero</text>
            
            <rect x="100" y="{min(y_ag_sup, y_ag_inf)}" width="160" height="{max(1.0, abs(y_ag_sup - y_ag_inf))}" fill="url(#diagonalHatchHole)" stroke="#2ecc71" stroke-width="2" opacity="0.85"/>
            <text x="180" y="{min(y_ag_sup, y_ag_inf) - 10}" fill="#2ecc71" font-family="sans-serif" font-weight="bold" font-size="14" text-anchor="middle">AGUJERO ({ag_letra}{ag_grado})</text>
            <text x="90" y="{y_ag_sup+4}" fill="#2ecc71" font-family="sans-serif" font-size="11" text-anchor="end">ES: {es_Ag:+.3f} mm</text>
            <text x="90" y="{y_ag_inf+4}" fill="#2ecc71" font-family="sans-serif" font-size="11" text-anchor="end">EI: {ei_Ag:+.3f} mm</text>

            <rect x="540" y="{min(y_eje_sup, y_eje_inf)}" width="160" height="{max(1.0, abs(y_eje_sup - y_eje_inf))}" fill="url(#diagonalHatchShaft)" stroke="#e67e22" stroke-width="2" opacity="0.85"/>
            <text x="620" y="{min(y_eje_sup, y_eje_inf) - 10}" fill="#e67e22" font-family="sans-serif" font-weight="bold" font-size="14" text-anchor="middle">EJE ({eje_letra}{eje_grado})</text>
            <text x="710" y="{y_eje_sup+4}" fill="#e67e22" font-family="sans-serif" font-size="11" text-anchor="start">es: {es_Ej:+.3f} mm</text>
            <text x="710" y="{y_eje_inf+4}" fill="#e67e22" font-family="sans-serif" font-size="11" text-anchor="start">ei: {ei_Ej:+.3f} mm</text>

            {svg_lineas_reales}

            <defs>
                <pattern id="diagonalHatchHole" width="10" height="10" patternUnits="userSpaceOnUse">
                    <line x1="0" y1="10" x2="10" y2="0" stroke="#2ecc71" stroke-width="1.5" />
                </pattern>
                <pattern id="diagonalHatchShaft" width="10" height="10" patternUnits="userSpaceOnUse">
                    <line x1="0" y1="0" x2="10" y2="10" stroke="#e67e22" stroke-width="1.5" />
                </pattern>
            </defs>
        </svg>
        """
        st.components.v1.html(svg_code, height=340)

        reporte_markdown = f"""# Informe Técnico - Ø{d_nominal:.3f} {ag_letra}{ag_grado}/{eje_letra}{eje_grado}
- **Tipo de Ajuste:** {tipo_ajuste}
- **Agujero:** Superior = {es_Ag:+.3f} mm | Inferior = {ei_Ag:+.3f} mm
- **Eje:** Superior = {es_Ej:+.3f} mm | Inferior = {ei_Ej:+.3f} mm
"""
        st.download_button("📥 Descargar Informe", data=reporte_markdown, file_name=f"ajuste_Ø{d_nominal:.3f}.md")

with tab2:
    st.header("Consulta Rápida por Componente")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        tipo_c = st.radio("Tipo de Elemento:", ["Agujero", "Eje"])
        d_nom_c = st.number_input("Medida Nominal (mm):", min_value=0.001, max_value=3150.000, value=100.000, step=0.001, format="%.3f", key="comp_d")
    with col_c2:
        letra_c = st.text_input("Letra de Posición (ej. H, g, JS):", value="H" if tipo_c == "Agujero" else "h")
        grado_c = st.selectbox("Grado / Calidad:", list(TABLA_IT.keys()), index=3, key="comp_g")

    letra_valida = True
    if tipo_c == "Agujero" and not letra_c.isupper():
        st.error("💡 Para Agujeros, la letra de posición debe ser MAYÚSCULA.")
        letra_valida = False
    elif tipo_c == "Eje" and not letra_c.islower():
        st.error("💡 Para Ejes, la letra de posición debe ser minúscula.")
        letra_valida = False

    if letra_valida and letra_c != "":
        es_c, ei_c, it_c, errs_c = obtener_tolerancias_completas(tipo_c, letra_c, grado_c, d_nom_c)
        if es_c is not None:
            for al in errs_c:
                st.warning(al)
                
            st.markdown(f"### Resultados para **Ø{d_nom_c:.3f} {letra_c}{grado_c}**")
            
            cc1, cc2 = st.columns(2)
            cc1.metric("Desviación Superior", f"{es_c:+.3f} mm")
            cc2.metric("Desviación Inferior", f"{ei_c:+.3f} mm")
            
            st.info(f"📏 **Dimensión de Fabricación Conforme:** Entre **{(d_nom_c + ei_c):.3f} mm** y **{(d_nom_c + es_c):.3f} mm**.")
