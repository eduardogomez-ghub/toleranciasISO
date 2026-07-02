import streamlit as st
import re

# =====================================================================
# CONFIGURACIÓN DE LA PÁGINA (Estilo Premium Industrial)
# =====================================================================
st.set_page_config(
    page_title="FitsStudio Pro",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS para mantener el Dark Mode Industrial
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    div[data-testid="stMetricValue"] { font-family: 'Consolas', monospace; font-size: 24px; font-weight: bold; }
    .stAlert { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- MAPEO DE TABLA ISO ---
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
        if es_agujero and not letra.isupper(): return "ERR_MAYUS"
        if not es_agujero and not letra.islower(): return "ERR_MINUS"
        return nominal, letra, grado
    return None

def calcular_limites(nominal, letra, grado, es_agujero):
    if nominal <= 0 or nominal > 500 or grado not in TABLA_IT: return None
    it_valor = 15
    for inf, sup, val in TABLA_IT[grado]:
        if inf < nominal <= sup:
            it_valor = val
            break
    sup_um, inf_um = get_desv_agujero(letra, nominal, it_valor) if es_agujero else get_desv_eje(letra, nominal, it_valor)
    max_real = nominal + (sup_um / 1000.0)
    min_real = nominal + (inf_um / 1000.0)
    return max_real, min_real, sup_um, inf_um

# --- HEADER INTERFAZ ---
st.title("FitsStudio Pro 🛠️")
st.caption("Norma Completa ISO • Validador de Ajustes Industriales en Milímetros")
st.hr()

# --- ENTRADA DE DATOS ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    entry_aloj = st.text_input("AGUJERO (Letra en MAYÚSCULA - Ej: 12.5H7)", "12.5H7")
with col_in2:
    entry_eje = st.text_input("EJE (Letra en minúscula - Ej: 12.5g6)", "12.5g6")

comp_aloj = descomponer_ajuste(entry_aloj, es_agujero=True)
comp_eje = descomponer_ajuste(entry_eje, es_agujero=False)

# --- PROCESAMIENTO Y VALIDACIÓN ---
error = False
if comp_aloj == "ERR_MAYUS":
    st.error("⚠ ERROR: EL AGUJERO DEBE IR EN MAYÚSCULA (Ej: H7)")
    error = True
elif comp_eje == "ERR_MINUS":
    st.error("⚠ ERROR: EL EJE DEBE IR EN MINÚSCULA (Ej: g6)")
    error = True
elif not comp_aloj or not comp_eje:
    st.warning("Introduce códigos ISO válidos para calcular (Formato: Diámetro + Letra + Calidad).")
    error = True

if not error:
    nom_a, letra_a, grado_a = comp_aloj
    nom_e, letra_e, grado_e = comp_eje
    
    res_a = calcular_limites(nom_a, letra_a, grado_a, es_agujero=True)
    res_e = calcular_limites(nom_e, letra_e, grado_e, es_agujero=False)
    
    if not res_a or not res_e:
        st.error("⚠ DATOS FUERA DE RANGO (0 - 500 mm) O CALIDAD ISO NO DISPONIBLE")
    else:
        max_a, min_a, sup_um_a, inf_um_a = res_a
        max_e, min_e, sup_um_e, inf_um_e = res_e
        
        # Evaluación del Ajuste
        juego_max = sup_um_a - inf_um_e
        juego_min = inf_um_a - sup_um_e
        
        if juego_min >= 0:
            st.success("🟢 AJUSTE MÓVIL (CON HOLGURA)")
        elif juego_max <= 0:
            st.error("🔴 AJUSTE FIJO (CON APRIETE / INTERFERENCIA)")
        else:
            st.warning("🟡 AJUSTE INDETERMINADO (TRANSICIÓN)")
            
        # --- TARJETAS DE RESULTADOS ---
        st.subheader("📋 Dimensiones Límites Computadas")
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("### **AGUJERO**")
            st.metric("Diámetro Máximo", f"{max_a:.4f} mm")
            st.metric("Diámetro Mínimo", f"{min_a:.4f} mm")
            st.caption(f"Desviaciones: Dsu: {sup_um_a/1000.0:+.4f} mm | Dinf: {inf_um_a/1000.0:+.4f} mm")
            
        with col_res2:
            st.markdown("### **EJE**")
            st.metric("Diámetro Máximo", f"{max_e:.4f} mm")
            st.metric("Diámetro Mínimo", f"{min_e:.4f} mm")
            st.caption(f"Desviaciones: dsu: {sup_um_e/1000.0:+.4f} mm | dinf: {inf_um_e/1000.0:+.4f} mm")
            
        # --- TABLA DE CARACTERÍSTICAS ---
        st.hr()
        st.subheader("⚙️ Aplicación Mecánica Recomendada")
        clave_combinacion = (f"{letra_a}{grado_a}", f"{letra_e}{grado_e}")
        
        if clave_combinacion in DICCIONARIO_APLICACIONES:
            caract, ejemplos = DICCIONARIO_APLICACIONES[clave_combinacion]
            st.info(f"**Características del asiento:** {caract}")
            st.markdown(f"**Ejemplos prácticos:** {ejemplos}")
        else:
            st.text("Ajuste fuera de la tabla de referencia de diámetros deslizantes estándar.")
