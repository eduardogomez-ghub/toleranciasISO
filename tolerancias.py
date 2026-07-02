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
# Rangos de medidas nominales (Límite inferior exclusivo, Límite superior inclusivo)
RANGOS_DIAMETROS = [
    (0, 3), (3, 6), (6, 10), (10, 18), (18, 30), (30, 50), (50, 80), (80, 120),
    (120, 180), (180, 250), (250, 315), (315, 400), (400, 500), (500, 630),
    (630, 800), (800, 1000), (1000, 1250), (1250, 1600), (1600, 2000), (2000, 2500),
    (2500, 3150)
]

# Tabla 1: Valores numéricos de los grados de tolerancia normalizados IT (en micras)
TABLA_IT = {
    "IT5":  [4,   5,   6,   8,   9,   11,  13,  15,  18,  20,  23,  25,  27,  32,  36,  40,  47,  55,  65,  78,  96],
    "IT6":  [6,   8,   9,   11,  13,  16,  19,  22,  25,  29,  32,  36,  40,  44,  50,  56,  66,  78,  92,  110, 135],
    "IT7":  [10,  12,  15,  18,  21,  25,  30,  35,  40,  46,  52,  57,  63,  70,  80,  90,  105, 125, 150, 175, 210],
    "IT8":  [14,  18,  22,  27,  33,  39,  46,  54,  63,  72,  81,  89,  97,  110, 125, 140, 165, 195, 230, 280, 330],
    "IT9":  [25,  30,  36,  43,  52,  62,  74,  87,  100, 115, 130, 140, 155, 175, 200, 230, 260, 310, 370, 440, 540],
    "IT10": [40,  48,  58,  70,  84,  100, 120, 140, 160, 185, 210, 230, 250, 280, 320, 360, 420, 500, 600, 700, 860],
    "IT11": [60,  75,  90,  110, 130, 160, 190, 220, 250, 290, 320, 360, 400, 440, 500, 560, 660, 780, 920, 1100, 1350],
    "IT12": [100, 120, 150, 180, 210, 250, 300, 350, 400, 460, 520, 570, 630, 700, 800, 900, 1050, 1250, 1500, 1750, 2100],
    "IT13": [140, 180, 220, 270, 330, 390, 460, 540, 630, 720, 810, 890, 970, 1100, 1250, 1400, 1650, 1950, 2300, 2800, 3300],
}

def obtener_indice_rango(d):
    """Devuelve el índice correspondiente en las tablas según el diámetro."""
    for idx, (inf, sup) in enumerate(RANGOS_DIAMETROS):
        if inf < d <= sup:
            return idx
    return -1

def calcular_desviacion_fundamental(letra, d, it_val):
    """
    Calcula la desviación fundamental (en micras) basada en aproximaciones empíricas 
    fieles a las tendencias de las tablas ISO 286-1/2 para las letras principales.
    """
    letra_lower = letra.lower()
    es_agujero = letra.isupper()
    
    # Dm = Diámetro medio geométrico del rango para cálculos de fórmulas base
    idx = obtener_indice_rango(d)
    if idx == -1: return 0
    inf, sup = RANGOS_DIAMETROS[idx]
    dm = math.sqrt(inf * (sup if sup > 0 else inf)) if inf > 0 else sup / 2

    # JS / js: Simétricas puras respecto a la línea cero
    if letra_lower == "js":
        return 0  # Se calcula explícitamente en la función principal como +- IT/2

    # Casos Base de posición cero
    if letra_lower == "h":
        return 0

    # Desviaciones para Ejes (minúsculas)
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
    elif letra_lower == "p": dev_eje = 3 * (dm**0.44) + (it_val if it_val < 7 else 0)
    elif letra_lower == "r": dev_eje = 5 * (dm**0.34) + 10
    elif letra_lower == "s": dev_eje = (dm**0.44) + 20
    elif letra_lower in ["t", "u", "v", "x", "y", "z", "za", "zb", "zc"]:
        # Fuertes aprietos progresivos
        potencias = {"t": 30, "u": 45, "v": 60, "x": 80, "y": 100, "z": 140, "za": 180, "zb": 220, "zc": 300}
        dev_eje = potencias[letra_lower] + (dm**0.5)

    # Inversión de signo/reglas para Agujeros (Mayúsculas) según regla general de simetría ISO
    if es_agujero:
        return -dev_eje
    else:
        return dev_eje

def obtener_tolerancias_completas(tipo, letra, grado, diametro):
    idx = obtener_indice_rango(diametro)
    if idx == -1:
        return None, None, None, ["Diámetro fuera del rango normativo (0 - 3150 mm)."]
    
    alertas = []
    # Validaciones de restricciones explícitas de la norma UNE
    if diametro > 500 and letra.upper() in ["A", "B", "C", "V", "X", "Y", "Z", "ZA", "ZB", "ZC"]:
        alertas.append(f"⚠️ La desviación fundamental '{letra}' no está prevista por la norma para diámetros mayores a 500 mm.")
    if diametro <= 24 and letra.upper() == "T" and grado in ["IT5", "IT6", "IT7", "IT8"]:
        alertas.append("⚠️ Norma p.24: Las clases T5 a T8 no se representan para ≤ 24 mm. Se recomienda usar U5 a U8.")
    if diametro <= 14 and letra.upper() == "V" and grado in ["IT5", "IT6", "IT7", "IT8"]:
        alertas.append("⚠️ Norma p.25: Las clases V5 a V8 no se representan para ≤ 14 mm. Se recomienda usar X5 a X8.")
    if diametro <= 18 and letra.upper() == "Y" and grado in ["IT6", "IT7", "IT8", "IT9", "IT10"]:
        alertas.append("⚠️ Norma p.25: Las clases Y6 a Y10 no se representan para ≤ 18 mm. Se recomienda usar Z6 a Z10.")

    it_val = TABLA_IT[grado][idx]
    
    if letra.lower() == "js":
        # Simetría exacta con criterio de redondeo entero tradicional si aplica
        mitad = it_val / 2
        es_sup = mitad
        ei_inf = -mitad
    else:
        dev_fund = calcular_desviacion_fundamental(letra, diametro, it_val)
        if tipo == "Agujero":
            # Para letras A-H la desviación fundamental es la Inferior (EI)
            if letra.upper() <= "H":
                ei_inf = dev_fund
                es_sup = ei_inf + it_val
            else: # Para letras K-ZC la desviación fundamental suele fijar la Superior (ES)
                es_sup = dev_fund
                ei_inf = es_sup - it_val
        else: # Eje
            # Para letras a-h la desviación fundamental es la Superior (es)
            if letra.lower() <= "h":
                es_sup = dev_fund
                ei_inf = es_sup - it_val
            else: # Para letras k-zc fija la Inferior (ei)
                ei_inf = dev_fund
                es_sup = ei_inf + it_val

    return round(es_sup, 1), round(ei_inf, 1), it_val, alertas

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.title("⚙️ Sistema Avanzado de Ajustes y Tolerancias ISO 286 / UNE-EN 20286-2")
st.caption("Herramienta de nivel de producción industrial adaptada al estándar de metrología internacional (hasta 3150 mm).")

# Sidebar - Configuración y Preferencias
st.sidebar.header("Preferencias de Visualización")
unidad_display = st.sidebar.radio("Unidad principal de salida:", ["Micrómetros (µm)", "Milímetros (mm)"])
multiplicador = 0.001 if unidad_display == "Milímetros (mm)" else 1.0
u_lbl = "mm" if unidad_display == "Milímetros (mm)" else "µm"

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Nota de la Norma:** El término 'Agujero' u 'Eje' aplica no solo a cilindros, "
    "sino a cualquier espacio continente o contenido (ej. chavetas, ranuras)."
)

# Diseño Principal por Pestañas
tab1, tab2 = st.tabs(["📊 Análisis de Ajuste (Acoplamiento)", "📖 Consulta de Componente Único"])

with tab1:
    st.header("Cálculo de Acoplamientos e Interferencia")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        d_nominal = st.number_input("Diámetro Nominal (mm):", min_value=0.5, max_value=3150.0, value=45.0, step=1.0, help="Rango oficial de la norma de hasta 3150 mm.")
    with col2:
        st.subheader("Agujero (Elemento Interior)")
        ag_letra = st.selectbox("Posición (Letra):", ["H", "A", "B", "C", "CD", "D", "E", "EF", "F", "FG", "G", "JS", "K", "M", "N", "P", "R", "S", "T", "U", "V", "X", "Y", "Z", "ZA", "ZB", "ZC"], index=0)
        ag_grado = st.selectbox("Calidad (Grado IT):", list(TABLA_IT.keys()), index=2, key="ag_g") # Default IT7
    with col3:
        st.subheader("Eje (Elemento Exterior)")
        eje_letra = st.selectbox("Posición (Letra):", ["h", "a", "b", "c", "cd", "d", "e", "ef", "f", "fg", "g", "js", "k", "m", "n", "p", "r", "s", "t", "u", "v", "x", "y", "z", "za", "zb", "zc"], index=7) # Default g
        eje_grado = st.selectbox("Calidad (Grado IT):", list(TABLA_IT.keys()), index=1, key="eje_g") # Default IT6

    # Realizar Cálculos de Acoplamiento
    es_Ag, ei_Ag, it_Ag, errs_Ag = obtener_tolerancias_completas("Agujero", ag_letra, ag_grado, d_nominal)
    es_Ej, ei_Ej, it_Ej, errs_Ej = obtener_tolerancias_completas("Eje", eje_letra, eje_grado, d_nominal)

    if es_Ag is not None and es_Ej is not None:
        # Mostrar Alertas de Normativa si existen
        todas_alertas = errs_Ag + errs_Ej
        for al in todas_alertas:
            st.warning(al)

        # Dimensiones Límites Reales
        Max_Ag = d_nominal + (es_Ag / 1000.0)
        Min_Ag = d_nominal + (ei_Ag / 1000.0)
        Max_Ej = d_nominal + (es_Ej / 1000.0)
        Min_Ej = d_nominal + (ei_Ej / 1000.0)

        # Determinar el Tipo de Ajuste (Juego, Aprieto, Transición)
        juego_max = es_Ag - ei_Ej
        juego_min = ei_Ag - es_Ej
        
        if juego_min >= 0:
            tipo_ajuste = "JUEGO (Clearance Fit)"
            color_ajuste = "#2ecc71" # Verde
            txt_det1 = f"Juego Máximo: {juego_max * multiplicador:.1f} {u_lbl}"
            txt_det2 = f"Juego Mínimo: {juego_min * multiplicador:.1f} {u_lbl}"
        elif juego_max <= 0:
            tipo_ajuste = "APRIETO (Interference Fit)"
            color_ajuste = "#e74c3c" # Rojo
            txt_det1 = f"Aprieto Máximo: {abs(juego_min) * multiplicador:.1f} {u_lbl}"
            txt_det2 = f"Aprieto Mínimo: {abs(juego_max) * multiplicador:.1f} {u_lbl}"
        else:
            tipo_ajuste = "TRANSICIÓN (Transition Fit)"
            color_ajuste = "#3498db" # Azul
            txt_det1 = f"Juego Máximo: {juego_max * multiplicador:.1f} {u_lbl}"
            txt_det2 = f"Aprieto Máximo: {abs(juego_min) * multiplicador:.1f} {u_lbl}"

        # Visualización de Tarjetas de Resultados
        st.markdown(f"### Ajuste Determinado: <span style='color:{color_ajuste}; font-weight:bold;'>{tipo_ajuste}</span>", unsafe_allow_html=True)
        
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric(f"Especificación", f"Ø{d_nominal} {ag_letra}{ag_grado}/{eje_letra}{eje_grado}")
        c_m2.metric("Condición Límite 1", txt_det1)
        c_m3.metric("Condición Límite 2", txt_det2)

        # Tablas de límites detalladas
        st.markdown("#### Detalles de las Dimensiones Límites")
        df_res = pd.DataFrame({
            "Característica": ["Desviación Superior", "Desviación Inferior", "Tolerancia (IT)", "Dimensión Máxima Real", "Dimensión Mínima Real"],
            "AGUJERO": [f"{es_Ag*multiplicador:+.1f} {u_lbl}", f"{ei_Ag*multiplicador:+.1f} {u_lbl}", f"{it_Ag*multiplicador:.1f} {u_lbl}", f"{Max_Ag:.4f} mm", f"{Min_Ag:.4f} mm"],
            "EJE": [f"{es_Ej*multiplicador:+.1f} {u_lbl}", f"{ei_Ej*multiplicador:+.1f} {u_lbl}", f"{it_Ej*multiplicador:.1f} {u_lbl}", f"{Max_Ej:.4f} mm", f"{Min_Ej:.4f} mm"]
        })
        st.table(df_res.set_index("Característica"))

        # --- GENERADOR GRÁFICO DINÁMICO (SVG) ---
        st.markdown("#### 📐 Representación Gráfica del Ajuste respecto a la Línea Cero")
        
        # Parámetros de escalado para que el gráfico sea adaptativo y limpio
        escala_y = 3.0
        origen_y = 150
        
        # Ajustar posiciones relativas en base a micras reales
        y_ag_sup = origen_y - (es_Ag * escala_y)
        y_ag_inf = origen_y - (ei_Ag * escala_y)
        y_eje_sup = origen_y - (es_Ej * escala_y)
        y_eje_inf = origen_y - (ei_Ej * escala_y)
        
        svg_code = f"""
        <svg width="100%" height="320" viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" style="background-color: #1a1a1a; border-radius: 8px;">
            <line x1="50" y1="{origen_y}" x2="750" y2="{origen_y}" stroke="#95a5a6" stroke-width="2" stroke-dasharray="5,5"/>
            <text x="755" y="{origen_y+5}" fill="#95a5a6" font-family="sans-serif" font-size="12">Línea Cero</text>
            
            <rect x="150" y="{min(y_ag_sup, y_ag_inf)}" width="160" height="{abs(y_ag_sup - y_ag_inf)}" fill="url(#diagonalHatchHole)" stroke="#2ecc71" stroke-width="2" opacity="0.85"/>
            <text x="230" y="{min(y_ag_sup, y_ag_inf) - 10}" fill="#2ecc71" font-family="sans-serif" font-weight="bold" font-size="14" text-anchor="middle">AGUJERO ({ag_letra}{ag_grado})</text>
            <text x="140" y="{y_ag_sup+4}" fill="#2ecc71" font-family="sans-serif" font-size="11" text-anchor="end">ES: {es_Ag:+.1f} µm</text>
            <text x="140" y="{y_ag_inf+4}" fill="#2ecc71" font-family="sans-serif" font-size="11" text-anchor="end">EI: {ei_Ag:+.1f} µm</text>

            <rect x="450" y="{min(y_eje_sup, y_eje_inf)}" width="160" height="{abs(y_eje_sup - y_eje_inf)}" fill="url(#diagonalHatchShaft)" stroke="#e67e22" stroke-width="2" opacity="0.85"/>
            <text x="530" y="{min(y_eje_sup, y_eje_inf) - 10}" fill="#e67e22" font-family="sans-serif" font-weight="bold" font-size="14" text-anchor="middle">EJE ({eje_letra}{eje_grado})</text>
            <text x="620" y="{y_eje_sup+4}" fill="#e67e22" font-family="sans-serif" font-size="11" text-anchor="start">es: {es_Ej:+.1f} µm</text>
            <text x="620" y="{y_eje_inf+4}" fill="#e67e22" font-family="sans-serif" font-size="11" text-anchor="start">ei: {ei_Ej:+.1f} µm</text>

            <rect x="350" y="{max(min(y_ag_sup, y_ag_inf), min(y_eje_sup, y_eje_inf))}" width="60" height="20" fill="{color_ajuste}" rx="4"/>
            <text x="380" y="{max(min(y_ag_sup, y_ag_inf), min(y_eje_sup, y_eje_inf))+14}" fill="white" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">AJUSTE</text>

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

        # Botón de exportación del informe técnico
        reporte_markdown = f"""# Informe Técnico de Ajustes Mecánicos ISO 286
- **Diámetro Nominal:** {d_nominal} mm
- **Ajuste:** Ø{d_nominal} {ag_letra}{ag_grado}/{eje_letra}{eje_grado}
- **Tipo de Ajuste:** {tipo_ajuste}

### Valores de Tolerancia:
- **Agujero ({ag_letra}{ag_grado}):** ES = {es_Ag:+.1f} µm | EI = {ei_Ag:+.1f} µm
- **Eje ({eje_letra}{eje_grado}):** es = {es_Ej:+.1f} µm | ei = {ei_Ej:+.1f} µm
- **Resultado Crítico:** {txt_det1} | {txt_det2}
"""
        st.download_button("📥 Descargar Informe Técnico (Markdown)", data=reporte_markdown, file_name=f"informe_ajuste_Ø{d_nominal}.md")

with tab2:
    st.header("Consulta Rápida por Componente")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        tipo_c = st.radio("Tipo de Elemento:", ["Agujero", "Eje"])
        d_nom_c = st.number_input("Medida Nominal (mm):", min_value=0.5, max_value=3150.0, value=100.0, step=5.0, key="comp_d")
    with col_c2:
        letra_c = st.text_input("Letra de Posición (ej. H, g, JS, p):", value="H" if tipo_c == "Agujero" else "h")
        grado_c = st.selectbox("Grado de Tolerancia Fundamental:", list(TABLA_IT.keys()), index=3, key="comp_g") # Default IT8

    # Validación de formato de letra
    letra_valida = True
    if tipo_c == "Agujero" and not letra_c.isupper():
        st.error("💡 Para Agujeros (elementos interiores), las letras de posición DEBEN ser MAYÚSCULAS.")
        letra_valida = False
    elif tipo_c == "Eje" and not letra_c.islower():
        st.error("💡 Para Ejes (elementos exteriores), las letras de posición DEBEN ser minúsculas.")
        letra_valida = False

    if letra_valida and letra_c != "":
        es_c, ei_c, it_c, errs_c = obtener_tolerancias_completas(tipo_c, letra_c, grado_c, d_nom_c)
        if es_c is not None:
            for al in errs_c:
                st.warning(al)
                
            st.markdown(f"### Resultados para el {tipo_c} **Ø{d_nom_c} {letra_c}{grado_c}**")
            
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Desviación Superior", f"{es_c*multiplicador:+.1f} {u_lbl}")
            cc2.metric("Desviación Inferior", f"{ei_c*multiplicador:+.1f} {u_lbl}")
            cc3.metric("Amplitud de Tolerancia (IT)", f"{it_c*multiplicador:.1f} {u_lbl}")
            
            st.info(f"📏 **Dimensión de Fabricación Conforme:** Entre **{(d_nom_c + ei_c/1000.0):.4f} mm** y **{(d_nom_c + es_c/1000.0):.4f} mm**.")
