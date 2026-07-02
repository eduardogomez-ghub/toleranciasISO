import streamlit as st
import re

# =====================================================================
# CONFIGURACIÓN EQUILIBRADA
# =====================================================================
st.set_page_config(
    page_title="FitsStudio Pro",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 90% !important; }
    h2 { margin-top: 0rem !important; font-size: 28px !important; }
    div[data-testid="stMetricValue"] { font-family: 'Consolas', monospace; font-size: 24px !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; color: #94a3b8; }
    .stAlert { padding: 12px !important; font-size: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- TABLAS DE DATOS ---
DICCIONARIO_APLICACIONES = {
    ('H8', 'x8'): ("Prensado duro.", "Coronas de bronce."),
    ('H7', 's6'): ("Prensado.", "Piñón motor."),
    ('H7', 'r6'): ("Prensado ligero.", "Engranajes."),
    ('H7', 'k6'): ("Forzado.", "Rodamientos."),
    ('H7', 'h6'): ("Deslizante.", "Ejes de lira."),
    ('H8', 'f7'): ("Giratorio poco juego.", "Bielas."),
    ('H11', 'c11'): ("Libre.", "Máquinas agrícolas.")
}

TABLA_IT = {
    6: [(0, 3, 6), (3, 6, 8), (6, 10, 9), (10, 18, 11), (18, 30, 13), (30, 50, 16), (50, 80, 19), (80, 120, 22), (120, 180, 25), (180, 250, 29), (250, 315, 32), (315, 400, 36), (400, 500, 40)],
    7: [(0, 3, 10), (3, 6, 12), (6, 10, 15), (10, 18, 18), (18, 30, 21), (30, 50, 25), (50, 80, 30), (80, 120, 35), (120, 180, 40), (180, 250, 46), (250, 315, 52), (315, 400, 57), (400, 500, 63)],
    8: [(0, 3, 14), (3, 6, 18), (6, 10, 22), (10, 18, 27), (18, 30, 33), (30, 50, 39), (50, 80, 46), (80, 120, 54), (120, 180, 63), (180, 250, 72), (250, 315, 81), (315, 400, 89), (400, 500, 97)]
}

def get_desv_agujero(letra, d, it):
    if letra == 'H': return it, 0
    # Simplificado para brevedad del bloque
    des = 7 if letra == 'G' else 20 if letra == 'F' else 40 if letra == 'E' else 65 if letra == 'D' else 80 if letra == 'C' else 0
    return it + des, des

def get_desv_eje(letra, d, it):
    if letra == 'h': return 0, -it
    des = -7 if letra == 'g' else -20 if letra == 'f' else -40 if letra == 'e' else -65 if letra == 'd' else -80 if letra == 'c' else 0
    return (des + it, des) if letra in ['k','n','r','s','u','x'] else (des, des - it)

def calcular_limites(nominal, letra, grado, es_agujero):
    it_valor = 15
    for inf, sup, val in TABLA_IT.get(grado, [(0, 500, 15)]):
        if inf < nominal <= sup:
            it_valor = val
            break
    sup_um, inf_um = get_desv_agujero(letra, nominal, it_valor) if es_agujero else get_desv_eje(letra, nominal, it_valor)
    return nominal + (sup_um/1000), nominal + (inf_um/1000), sup_um, inf_um

# --- INTERFAZ ---
st.markdown("<h2>FitsStudio Pro 🛠️</h2>", unsafe_allow_html=True)
col_in1, col_in2 = st.columns(2)
entry_aloj = col_in1.text_input("Agujero (Ej: 12.5H7)", "12.5H7")
entry_eje = col_in2.text_input("Eje (Ej: 12.5g6)", "12.5g6")

match_a = re.match(r"(\d+\.?\d*)([A-Z]+)(\d+)", entry_aloj)
match_e = re.match(r"(\d+\.?\d*)([a-z]+)(\d+)", entry_eje)

if match_a and match_e:
    max_a, min_a, s_a, i_a = calcular_limites(float(match_a.group(1)), match_a.group(2), int(match_a.group(3)), True)
    max_e, min_e, s_e, i_e = calcular_limites(float(match_e.group(1)), match_e.group(2), int(match_e.group(3)), False)

    if i_a - s_e >= 0: st.success("🟢 AJUSTE MÓVIL (HOLGURA)")
    elif s_a - i_e <= 0: st.error("🔴 AJUSTE FIJO (APRIETE)")
    else: st.warning("🟡 AJUSTE INDETERMINADO")

    col_g, col_1, col_2 = st.columns([2, 1, 1])
    with col_g:
        st.markdown(f"""
        <div style="background:#1e293b; padding:20px; border-radius:8px; height:200px; display:flex; justify-content:center; align-items:center; border:1px solid #334155;">
            <div style="width:80px; height:{max(20, abs(s_a-i_a)*2)}px; background:blue; margin:10px;"></div>
            <div style="width:80px; height:{max(20, abs(s_e-i_e)*2)}px; background:orange; margin:10px;"></div>
        </div>
        """, unsafe_allow_html=True)
    with col_1:
        st.metric("Agujero Máx", f"{max_a:.4f}mm")
        st.metric("Agujero Mín", f"{min_a:.4f}mm")
    with col_2:
        st.metric("Eje Máx", f"{max_e:.4f}mm")
        st.metric("Eje Mín", f"{min_e:.4f}mm")
else:
    st.info("Introduce datos válidos para ver el gráfico.")
    
