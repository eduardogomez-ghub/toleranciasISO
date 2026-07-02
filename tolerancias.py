import streamlit as st
import re

# =====================================================================
# CONFIGURACIÓN DE PÁGINA STREAMLIT
# =====================================================================
st.set_page_config(page_title="FitsStudio Pro", layout="centered")

# =====================================================================
# PALETA DE COLORES PREMIUM (DARK MODE INDUSTRIAL)
# =====================================================================
COLOR_BG = "#0f172a"          # Fondo principal oscuro
COLOR_CARD = "#1e293b"        # Fondo de tarjetas
COLOR_TEXT_MAIN = "#f8fafc"   # Texto principal claro
COLOR_TEXT_MUTED = "#94a3b8"  # Texto secundario
COLOR_PRIMARY = "#3b82f6"     # Azul Eléctrico (Agujeros)
COLOR_ACCENT = "#f59e0b"      # Ámbar/Naranja Técnico (Ejes)
COLOR_SUCCESS = "#10b981"     # Verde Éxito (Holgura)
COLOR_WARNING = "#eab308"     # Amarillo/Oro (Indeterminado)
COLOR_ERROR = "#ef4444"       # Rojo Vibrante (Apriete / Errores)
COLOR_ZERO_LINE = "#64748b"   # Gris Línea Cero

# =====================================================================
# MAPEO EXACTO DE TU TABLA (Agujero, Eje) -> (Características, Ejemplos)
# =====================================================================
DICCIONARIO_APLICACIONES = {
    ('H8', 'x8'): ("Prensado duro. Montaje a prensa. No necesita seguro.", "Coronas de bronce, ruedas."),
    ('H8', 'u8'): ("Prensado duro. Montaje a prensa. No necesita seguro.", "Coronas de bronce, ruedas."),
    ('H7', 's6'): ("Prensado. Montaje a prensa.", "Piñón motor."),
    ('H7', 'r6'): ("Prensado ligero. Necesita seguro.", "Engranajes de máquinas."),
    ('H7', 'n6'): ("Muy forzado. Montaje a martillo.", "Casquillos especiales."),
    ('H7', 'k6'): ("Forzado. Montaje a martillo.", "Rodamientos a bolas."),
    ('H7', 'j6'): ("Forzado ligero. Montaje a mazo.", "Rodamientos a bolas."),
    ('H7', 'h6'): ("Deslizante con lubricación.", "Ejes de lira."),
    ('H8', 'h9'): ("Deslizante sin lubricación.", "Ejes de contrapunto."),
    ('H11', 'h9'): ("Deslizante. Ajuste corriente.", "Ejes de colocaciones."),
    ('H11', 'h11'): ("Deslizante. Ajuste ordinario.", "Ejes-guías atados."),
    ('H7', 'g6'): ("Giratorio sin juego apreciable.", "Émbolos de freno."),
    ('H7', 'f7'): ("Giratorio con poco juego.", "Bielas, cojinetes."),
    ('H8', 'f7'): ("Giratorio con poco juego.", "Bielas, cojinetes."),
    ('H8', 'e8'): ("Giratorio con gran juego.", "Cojinetes corrientes."),
    ('H8', 'd9'): ("Giratorio con mucho juego.", "Soportes múltiples."),
    ('H11', 'c11'): ("Libre (con holgura).", "Cojinetes de máquinas agrícolas."),
    ('H11', 'a11'): ("Muy libre.", "Avellanados, taladros de tornillos."),
    ('G7', 'h6'): ("Giratorio sin juego apreciable.", "Émbolos de freno."),
    ('F8', 'h6'): ("Giratorio con poco juego.", "Bielas, cojinetes."),
    ('F8', 'h9'): ("Giratorio con poco juego.", "Bielas, cojinetes."),
    ('E9', 'h9'): ("Giratorio con gran juego.", "Cojinetes corrientes."),
    ('D10', 'h9'): ("Giratorio con mucho juego.", "Soportes múltiples."),
    ('C11', 'h9'): ("Libre (con holgura).", "Cojinetes de máquinas agrícolas."),
    ('A11', 'h11'): ("Muy libre.", "Avellanados, taladros de tornillos.")
}

TABLA_IT = {
    6:  [(0, 3, 6), (3, 6, 8), (6, 10, 9), (10, 18, 11), (18, 30, 13), (30, 50, 16), (50, 80, 19), (80, 120, 22), (120, 180, 25), (180, 250, 29), (250, 315, 32), (315, 400, 36), (400, 500, 40)],
    7:  [(0, 3, 10), (3, 6, 12), (6, 10, 15), (10, 18, 18), (18, 30, 21), (30, 50, 25), (50, 80, 30), (80, 120, 35), (120, 180, 40), (180, 250, 46), (250, 315, 52), (315, 400, 57), (400, 500, 63)],
    8:  [(0, 3, 14), (3, 6, 18), (6, 10, 22), (10, 18, 27), (18, 30, 33), (30, 50, 39), (50, 80, 46), (80, 120, 54), (120, 180, 63), (180, 250, 72), (250, 315, 81), (315, 400, 89), (400, 500, 97)],
    9:  [(0, 3, 25), (3, 6, 30), (6, 10, 36), (10, 18, 43), (18, 30, 52), (30, 50, 62), (50, 80, 74), (80, 120, 87), (120, 180, 100), (180, 250, 115), (250, 315, 130), (315, 400, 140), (400, 500, 155)],
    10: [(0, 3, 40), (3, 6, 48), (6, 10, 58), (10, 18, 70), (18, 30, 84), (30, 50, 100), (50, 80, 120), (80, 120, 140), (120, 180, 160), (180, 250, 185), (250, 315, 210), (315, 400, 230), (400, 500, 255)],
    11: [(0, 3, 60), (3, 6, 75), (6, 10, 90), (10, 18, 110), (18, 30, 130), (30, 50, 160), (50, 80, 190), (80, 120, 220), (120, 180, 250), (180, 250, 290), (250, 315, 320), (315, 400, 360), (400, 500, 400)]
}

def get_desv_agujero(letra, d, it):
    if letra == 'H': return it, 0
    if letra == 'G': des = 2 if d<=3 else 4 if d<=6 else 5 if d<=10 else 6 if d<=18 else 7 if d<=30 else 9 if d<=50 else 10 if d<=80 else 12 if d<=120 else 14 if d<=180 else 15 if d<=250 else 17 if d<=315 else 18 if d<=400 else 20
    elif letra == 'F': des = 6 if d<=3 else 10 if d<=6 else 13 if d<=10 else 16 if d<=18 else 20 if d<=30 else 25 if d<=50 else 30 if d<=80 else 36 if d<=120 else 43 if d<=180 else 50 if d<=250 else 56 if d<=315 else 62 if d<=400 else 68
    elif letra == 'E': des = 14 if d<=3 else 20 if d<=6 else 25 if d<=10 else 32 if d<=18 else 40 if d<=30 else 50 if d<=50 else 60 if d<=80 else 72 if d<=120 else 85 if d<=180 else 100 if d<=250 else 115 if d<=315 else 130 if d<=400 else 145
    elif letra == 'D': des = 20 if d<=3 else 30 if d<=6 else 40 if d<=10 else 50 if d<=18 else 65 if d<=30 else 80 if d<=50 else 100 if d<=80 else 120 if d<=120 else 145 if d<=180 else 170 if d<=250 else 190 if d<=315 else 210 if d<=400 else 230
    elif letra == 'C': des = 60 if d<=18 else 70 if d<=30 else 80 if d<=50 else 95 if d<=80 else 110 if d<=120 else 130 if d<=180 else 150 if d<=250 else 170 if d<=315 else 190 if d<=400 else 210
    elif letra == 'A': des = 270 if d<=3 else 270 if d<=6 else 280 if d<=10 else 290 if d<=18 else 300 if d<=30 else 320 if d<=50 else 340 if d<=80 else 360 if d<=120 else 400 if d<=180 else 460 if d<=250 else 520 if d<=315 else 580 if d<=400 else 660
    else: des = 0
    return it + des, des

def get_desv_eje(letra, d, it):
    if letra == 'h': return 0, -it
    if letra == 'g': des = -2 if d<=3 else -4 if d<=6 else -5 if d<=10 else -6 if d<=18 else -7 if d<=30 else -9 if d<=50 else -10 if d<=80 else -12 if d<=120 else -14 if d<=180 else -15 if d<=250 else -17 if d<=315 else -18 if d<=400 else -20
    elif letra == 'f': des = -6 if d<=3 else -10 if d<=6 else -13 if d<=10 else -16 if d<=18 else -20 if d<=30 else -25 if d<=50 else -30 if d<=80 else -36 if d<=120 else -43 if d<=180 else -50 if d<=250 else -56 if d<=315 else -62 if d<=400 else -68
    elif letra == 'e': des = -14 if d<=3 else -20 if d<=6 else -25 if d<=10 else -32 if d<=18 else -40 if d<=30 else -50 if d<=50 else -60 if d<=80 else -72 if d<=120 else -85 if d<=180 else -100 if d<=250 else -115 if d<=315 else -130 if d<=400 else -145
    elif letra == 'd': des = -20 if d<=3 else -30 if d<=6 else -40 if d<=10 else -50 if d<=18 else -65 if d<=30 else -80 if d<=50 else -100 if d<=80 else -120 if d<=120 else -145 if d<=180 else -170 if d<=250 else -190 if d<=315 else -210 if d<=400 else -230
    elif letra == 'c': des = -60 if d<=18 else -70 if d<=30 else -80 if d<=50 else -95 if d<=80 else -110 if d<=120 else -130 if d<=180 else -150 if d<=250 else -170 if d<=315 else -190 if d<=400 else -210
    elif letra == 'a': des = -270 if d<=3 else -270 if d<=6 else -280 if d<=10 else -290 if d<=18 else -300 if d<=30 else -320 if d<=50 else -340 if d<=80 else -360 if d<=120 else -400 if d<=180 else -460 if d<=250 else -520 if d<=315 else -580 if d<=400 else -660
    elif letra == 'j': return (it - 2, -2) if d<=3 else (it - 4, -4)
    elif letra == 'k': des = 0 if d<=3 else 1 if d<=6 else 1 if d<=10 else 2
    elif letra == 'n': des = 4 if d<=3 else 8 if d<=6 else 10 if d<=10 else 12
    elif letra == 'r': des = 10 if d<=3 else 15 if d<=6 else 19 if d<=10 else 23
    elif letra == 's': des = 14 if d<=3 else 19 if d<=6 else 23 if d<=10 else 28
    elif letra == 'u': des = 18 if d<=3 else 23 if d<=6 else 28 if d<=10 else 33
    elif letra == 'x': des = 20 if d<=3 else 28 if d<=6 else 34 if d<=10 else 40
    else: des = 0
    return (des + it, des) if letra in ['k','n','r','s','u','x'] else (des, des - it)

def descomponer_ajuste(texto, es_agujero=True):
    texto = texto.strip().replace(',', '.')
    match = re.match(r"^([0-9]*\.?[0-9]+)\s*([a-zA-Z]+)([0-9]+)$", texto)
    if match:
        nominal = float(match.group(1))
        letra = match.group(2)
        grado = int(match.group(3))
        
        if es_agujero and not letra.isupper():
            return "ERR_MAYUS"
        if not es_agujero and not letra.islower():
            return "ERR_MINUS"
            
        return nominal, letra, grado
    return None

def validar_y_calcular(texto_ajuste, es_agujero=True):
    componentes = descomponer_ajuste(texto_ajuste, es_agujero)
    if componentes in ["ERR_MAYUS", "ERR_MINUS"]: return componentes, None, 0, 0
    if not componentes: return None, None, 0, 0
    
    nominal, letra, grado = componentes
    if nominal <= 0 or nominal > 500 or grado not in TABLA_IT: return None, None, 0, 0
        
    it_valor = 15
    for inf, sup, val in TABLA_IT[grado]:
        if inf < nominal <= sup:
            it_valor = val
            break

    if es_agujero:
        sup_um, inf_um = get_desv_agujero(letra, nominal, it_valor)
    else:
        sup_um, inf_um = get_desv_eje(letra, nominal, it_valor)

    max_real = nominal + (sup_um / 1000.0)
    min_real = nominal + (inf_um / 1000.0)
    return f"{max_real:.4f} mm", f"{min_real:.4f} mm", sup_um, inf_um

# =====================================================================
# DIBUJO TÉCNICO VECTORIZADO (Sustituye al Canvas de Tkinter)
# =====================================================================
# =====================================================================
# DIBUJO TÉCNICO VECTORIZADO (Sustituye al Canvas de Tkinter)
# =====================================================================
def generar_grafico_svg(sup_a, inf_a, sup_e, inf_e, error=False):
    if error: return ""
    w, h = 640, 130
    linea_cero_y = h // 2
    
    max_val = max(abs(sup_a), abs(inf_a), abs(sup_e), abs(inf_e), 15)
    escala = 40 / max_val

    x_agujero_ini, x_agujero_fin = 160, 280
    x_eje_ini, x_eje_fin = 360, 480
    
    y_agujero_sup = linea_cero_y - (sup_a * escala)
    y_agujero_inf = linea_cero_y - (inf_a * escala)
    y_eje_sup = linea_cero_y - (sup_e * escala)
    y_eje_inf = linea_cero_y - (inf_e * escala)
    
    sup_a_mm = sup_a / 1000.0
    inf_a_mm = inf_a / 1000.0
    sup_e_mm = sup_e / 1000.0
    inf_e_mm = inf_e / 1000.0

    # HTML y SVG pegado a la izquierda para evitar que Markdown lo tome como código
    # Se ha cambiado x="60" por x="20" en la línea del texto "LÍNEA CERO"
    svg = f"""<div style="background-color: {COLOR_BG}; border: 1px solid #334155; padding: 10px; border-radius: 5px; text-align: center; overflow-x: auto;">
<svg width="{w}" height="{h}">
    <line x1="20" y1="{linea_cero_y}" x2="{w - 20}" y2="{linea_cero_y}" stroke="{COLOR_ZERO_LINE}" stroke-width="1.5" stroke-dasharray="4, 4" />
    <text x="20" y="{linea_cero_y - 10}" fill="{COLOR_TEXT_MUTED}" font-family="Segoe UI" font-size="10" font-weight="bold">Nominal</text>
    <rect x="{x_agujero_ini}" y="{min(y_agujero_sup, y_agujero_inf)}" width="{x_agujero_fin - x_agujero_ini}" height="{abs(y_agujero_sup - y_agujero_inf)}" fill="#1e3a8a" stroke="{COLOR_PRIMARY}" stroke-width="2" />
    <text x="{(x_agujero_ini + x_agujero_fin)//2}" y="{(y_agujero_sup + y_agujero_inf)//2 + 4}" fill="#93c5fd" font-family="Segoe UI" font-size="11" font-weight="bold" text-anchor="middle">AGUJERO</text>
    <text x="{x_agujero_ini - 10}" y="{y_agujero_sup + 4}" fill="{COLOR_PRIMARY}" font-family="Consolas" font-size="10" text-anchor="end">{f"+{sup_a_mm:.4f} mm" if sup_a_mm >= 0 else f"{sup_a_mm:.4f} mm"}</text>
    <text x="{x_agujero_ini - 10}" y="{y_agujero_inf + 4}" fill="{COLOR_PRIMARY}" font-family="Consolas" font-size="10" text-anchor="end">{f"+{inf_a_mm:.4f} mm" if inf_a_mm >= 0 else f"{inf_a_mm:.4f} mm"}</text>
    <rect x="{x_eje_ini}" y="{min(y_eje_sup, y_eje_inf)}" width="{x_eje_fin - x_eje_ini}" height="{abs(y_eje_sup - y_eje_inf)}" fill="#7c2d12" stroke="{COLOR_ACCENT}" stroke-width="2" />
    <text x="{(x_eje_ini + x_eje_fin)//2}" y="{(y_eje_sup + y_eje_inf)//2 + 4}" fill="#fde047" font-family="Segoe UI" font-size="11" font-weight="bold" text-anchor="middle">EJE</text>
    <text x="{x_eje_fin + 10}" y="{y_eje_sup + 4}" fill="{COLOR_ACCENT}" font-family="Consolas" font-size="10" text-anchor="start">{f"+{sup_e_mm:.4f} mm" if sup_e_mm >= 0 else f"{sup_e_mm:.4f} mm"}</text>
    <text x="{x_eje_fin + 10}" y="{y_eje_inf + 4}" fill="{COLOR_ACCENT}" font-family="Consolas" font-size="10" text-anchor="start">{f"+{inf_e_mm:.4f} mm" if inf_e_mm >= 0 else f"{inf_e_mm:.4f} mm"}</text>
</svg>
</div>"""
    return svg

# =====================================================================
# INTERFAZ WEB (Adaptación de Tkinter a Streamlit)
# =====================================================================

html_header = f"""<div style="background-color: {COLOR_BG}; padding: 20px; border-radius: 8px;">
<h1 style='color: {COLOR_TEXT_MAIN}; font-family: Segoe UI; margin-bottom: 0;'>FitsStudio Pro 🛠️</h1>
<p style='color: {COLOR_TEXT_MUTED}; font-family: Segoe UI; font-size: 14px;'>Norma Completa ISO • Validador Estricto de Letras Base de Tolerancias</p>
</div>"""
st.markdown(html_header, unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<p style='color: {COLOR_PRIMARY}; font-weight: bold; margin-bottom: 0;'>AGUJERO (Letra en MAYÚSCULA)</p>", unsafe_allow_html=True)
    entry_aloj = st.text_input("", value="12.5H7", key="agujero")

with col2:
    st.markdown(f"<p style='color: {COLOR_ACCENT}; font-weight: bold; margin-bottom: 0;'>EJE (Letra en minúscula)</p>", unsafe_allow_html=True)
    entry_eje = st.text_input("", value="12.5g6", key="eje")

# CSS para forzar el color de fondo en Streamlit
html_css = f"""<style>
.stApp {{ background-color: {COLOR_BG}; }}
</style>"""
st.markdown(html_css, unsafe_allow_html=True)

if st.button("PROCESAR AJUSTE INDUSTRIAL"):
    res_a = validar_y_calcular(entry_aloj, es_agujero=True)
    res_e = validar_y_calcular(entry_eje, es_agujero=False)
    
    if res_a[0] == "ERR_MAYUS":
        st.markdown(f"<div style='background-color: {COLOR_CARD}; padding: 10px; border-radius: 5px; color: {COLOR_ERROR}; font-weight: bold;'>⚠ ERROR: EL AGUJERO DEBE IR EN MAYÚSCULA (Ej: H7)</div>", unsafe_allow_html=True)
    elif res_e[0] == "ERR_MINUS":
        st.markdown(f"<div style='background-color: {COLOR_CARD}; padding: 10px; border-radius: 5px; color: {COLOR_ERROR}; font-weight: bold;'>⚠ ERROR: EL EJE DEBE IR EN MINÚSCULA (Ej: g6)</div>", unsafe_allow_html=True)
    else:
        max_a, min_a, sup_um_a, inf_um_a = res_a
        max_e, min_e, sup_um_e, inf_um_e = res_e
        
        comp_aloj = descomponer_ajuste(entry_aloj, es_agujero=True)
        comp_eje = descomponer_ajuste(entry_eje, es_agujero=False)
        
        if comp_aloj and comp_eje and max_a and max_e:
            juego_max = sup_um_a - inf_um_e
            juego_min = inf_um_a - sup_um_e
            
            # Semáforo de Estado
            if juego_min >= 0:
                semaforo_html = f"<div style='background-color: {COLOR_CARD}; padding: 10px; text-align: center; border-radius: 5px; color: {COLOR_SUCCESS}; font-weight: bold;'>🟢 AJUSTE MÓVIL (CON HOLGURA)</div>"
            elif juego_max <= 0:
                semaforo_html = f"<div style='background-color: {COLOR_CARD}; padding: 10px; text-align: center; border-radius: 5px; color: {COLOR_ERROR}; font-weight: bold;'>🔴 AJUSTE FIJO (CON APRIETE / INTERFERENCIA)</div>"
            else:
                semaforo_html = f"<div style='background-color: {COLOR_CARD}; padding: 10px; text-align: center; border-radius: 5px; color: {COLOR_WARNING}; font-weight: bold;'>🟡 AJUSTE INDETERMINADO (TRANSICIÓN)</div>"
            
            st.markdown(semaforo_html, unsafe_allow_html=True)
            
            # Grid de Resultados Numéricos
            html_grid = f"""<div style="background-color: {COLOR_CARD}; border: 1px solid #334155; padding: 15px; border-radius: 5px; display: flex; justify-content: space-around; margin-top: 15px;">
<div>
<span style="color: {COLOR_TEXT_MUTED}; font-size: 12px;">Máximo:</span> <span style="color: {COLOR_PRIMARY}; font-size: 20px; font-weight: bold;">{max_a}</span><br>
<span style="color: {COLOR_TEXT_MUTED}; font-size: 12px;">Mínimo:</span> <span style="color: {COLOR_PRIMARY}; font-size: 20px; font-weight: bold;">{min_a}</span>
</div>
<div style="color: #334155; font-size: 30px;">│</div>
<div>
<span style="color: {COLOR_TEXT_MUTED}; font-size: 12px;">Máximo:</span> <span style="color: {COLOR_ACCENT}; font-size: 20px; font-weight: bold;">{max_e}</span><br>
<span style="color: {COLOR_TEXT_MUTED}; font-size: 12px;">Mínimo:</span> <span style="color: {COLOR_ACCENT}; font-size: 20px; font-weight: bold;">{min_e}</span>
</div>
</div>"""
            st.markdown(html_grid, unsafe_allow_html=True)
            
            # Gráfico
            st.markdown(f"<p style='color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: bold; margin-top: 20px; text-align: center;'>DIAGRAMA DE POSICIÓN DE TOLERANCIAS</p>", unsafe_allow_html=True)
            st.markdown(generar_grafico_svg(sup_um_a, inf_um_a, sup_um_e, inf_um_e), unsafe_allow_html=True)
            
            # Diccionario de Aplicaciones
            clave_combinacion = (f"{comp_aloj[1]}{comp_aloj[2]}", f"{comp_eje[1]}{comp_eje[2]}")
            if clave_combinacion in DICCIONARIO_APLICACIONES:
                caract, ejemplos = DICCIONARIO_APLICACIONES[clave_combinacion]
            else:
                caract = "Ajuste fuera de la tabla de referencia de diámetros deslizantes estándar."
                ejemplos = "---"
                
            html_diccionario = f"""<div style="background-color: {COLOR_CARD}; border: 1px solid #334155; padding: 15px; border-radius: 5px; margin-top: 15px;">
<p style="color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: bold; margin-bottom: 5px;">Características del asiento (Según Tabla):</p>
<p style="color: {COLOR_TEXT_MAIN}; font-size: 14px; margin-bottom: 15px;">{caract}</p>
<p style="color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: bold; margin-bottom: 5px;">Ejemplos de aplicación:</p>
<p style="color: {COLOR_TEXT_MAIN}; font-size: 14px; margin-bottom: 0;">{ejemplos}</p>
</div>"""
            st.markdown(html_diccionario, unsafe_allow_html=True)
            
        else:
            st.markdown(f"<div style='background-color: {COLOR_CARD}; padding: 10px; text-align: center; border-radius: 5px; color: {COLOR_ERROR}; font-weight: bold;'>⚠ DATOS FUERA DE RANGO O FORMATO INVÁLIDO (0 - 500 mm)</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='background-color: {COLOR_CARD}; padding: 10px; text-align: center; border-radius: 5px; color: {COLOR_TEXT_MUTED}; font-weight: bold;'>SISTEMA LISTO • INTRODUCE LOS CÓDIGOS ISO</div>", unsafe_allow_html=True)
