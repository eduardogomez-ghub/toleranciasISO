import tkinter as tk
from tkinter import ttk
import re

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

# Tabla de Tolerancias IT Norma UNE-EN 20286-2 Completa (0-500 mm)
# Los valores internos están mapeados en milímetros de manera interna en los cálculos
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
# DIBUJO TÉCNICO EN CANVAS
# =====================================================================
def actualizar_grafico(sup_a, inf_a, sup_e, inf_e, error=False):
    canvas.delete("all")
    w, h = 640, 130
    linea_cero_y = h // 2
    
    canvas.create_line(20, linea_cero_y, w - 20, linea_cero_y, fill=COLOR_ZERO_LINE, dash=(4, 4), width=1.5)
    canvas.create_text(60, linea_cero_y - 10, text="LÍNEA CERO (Nominal)", fill=COLOR_TEXT_MUTED, font=("Segoe UI", 8, "bold"))

    if error: return

    max_val = max(abs(sup_a), abs(inf_a), abs(sup_e), abs(inf_e), 15)
    escala = 40 / max_val

    x_agujero_ini, x_agujero_fin = 160, 280
    x_eje_ini, x_eje_fin = 360, 480
    
    y_agujero_sup = linea_cero_y - (sup_a * escala)
    y_agujero_inf = linea_cero_y - (inf_a * escala)
    y_eje_sup = linea_cero_y - (sup_e * escala)
    y_eje_inf = linea_cero_y - (inf_e * escala)
    
    # Conversión de las desviaciones a mm para las etiquetas gráficas
    sup_a_mm = sup_a / 1000.0
    inf_a_mm = inf_a / 1000.0
    sup_e_mm = sup_e / 1000.0
    inf_e_mm = inf_e / 1000.0

    # Agujero (Azul)
    canvas.create_rectangle(x_agujero_ini, y_agujero_inf, x_agujero_fin, y_agujero_sup, fill="#1e3a8a", outline=COLOR_PRIMARY, width=2)
    canvas.create_text((x_agujero_ini + x_agujero_fin)//2, (y_agujero_sup + y_agujero_inf)//2, text="AGUJERO", fill="#93c5fd", font=("Segoe UI", 9, "bold"))
    canvas.create_text(x_agujero_ini - 40, y_agujero_sup, text=f"+{sup_a_mm:.4f} mm" if sup_a_mm >= 0 else f"{sup_a_mm:.4f} mm", fill=COLOR_PRIMARY, font=("Consolas", 8))
    canvas.create_text(x_agujero_ini - 40, y_agujero_inf, text=f"+{inf_a_mm:.4f} mm" if inf_a_mm >= 0 else f"{inf_a_mm:.4f} mm", fill=COLOR_PRIMARY, font=("Consolas", 8))

    # Eje (Naranja)
    canvas.create_rectangle(x_eje_ini, y_eje_inf, x_eje_fin, y_eje_sup, fill="#7c2d12", outline=COLOR_ACCENT, width=2)
    canvas.create_text((x_eje_ini + x_eje_fin)//2, (y_eje_sup + y_eje_inf)//2, text="EJE", fill="#fde047", font=("Segoe UI", 9, "bold"))
    canvas.create_text(x_eje_fin + 40, y_eje_sup, text=f"+{sup_e_mm:.4f} mm" if sup_e_mm >= 0 else f"{sup_e_mm:.4f} mm", fill=COLOR_ACCENT, font=("Consolas", 8))
    canvas.create_text(x_eje_fin + 40, y_eje_inf, text=f"+{inf_e_mm:.4f} mm" if inf_e_mm >= 0 else f"{inf_e_mm:.4f} mm", fill=COLOR_ACCENT, font=("Consolas", 8))

# =====================================================================
# CÓMPUTO GENERAL CON EVALUACIÓN DE CASE SENSITIVE
# =====================================================================
def ejecutar_calculo():
    res_a = validar_y_calcular(entry_aloj.get(), es_agujero=True)
    res_e = validar_y_calcular(entry_eje.get(), es_agujero=False)
    
    if res_a[0] == "ERR_MAYUS":
        lbl_semaforo.config(text="⚠ ERROR: EL AGUJERO DEBE IR EN MAYÚSCULA (Ej: H7)", fg=COLOR_ERROR)
        lbl_max_aloj_val.config(text="ERROR", fg=COLOR_ERROR); lbl_min_aloj_val.config(text="ERROR", fg=COLOR_ERROR)
        actualizar_grafico(0,0,0,0, error=True)
        return
        
    if res_e[0] == "ERR_MINUS":
        lbl_semaforo.config(text="⚠ ERROR: EL EJE DEBE IR EN MINÚSCULA (Ej: g6)", fg=COLOR_ERROR)
        lbl_max_eje_val.config(text="ERROR", fg=COLOR_ERROR); lbl_min_eje_val.config(text="ERROR", fg=COLOR_ERROR)
        actualizar_grafico(0,0,0,0, error=True)
        return

    max_a, min_a, sup_um_a, inf_um_a = res_a
    max_e, min_e, sup_um_e, inf_um_e = res_e
    
    lbl_max_aloj_val.config(text=max_a if max_a else "ERROR", fg=COLOR_PRIMARY)
    lbl_min_aloj_val.config(text=min_a if min_a else "ERROR", fg=COLOR_PRIMARY)
    lbl_max_eje_val.config(text=max_e if max_e else "ERROR", fg=COLOR_ACCENT)
    lbl_min_eje_val.config(text=min_e if min_e else "ERROR", fg=COLOR_ACCENT)
    
    comp_aloj = descomponer_ajuste(entry_aloj.get(), es_agujero=True)
    comp_eje = descomponer_ajuste(entry_eje.get(), es_agujero=False)
    
    if comp_aloj and comp_eje and max_a and max_e:
        actualizar_grafico(sup_um_a, inf_um_a, sup_um_e, inf_um_e)
        
        juego_max = sup_um_a - inf_um_e
        juego_min = inf_um_a - sup_um_e
        
        if juego_min >= 0:
            lbl_semaforo.config(text="🟢 AJUSTE MÓVIL (CON HOLGURA)", fg=COLOR_SUCCESS)
        elif juego_max <= 0:
            lbl_semaforo.config(text="🔴 AJUSTE FIJO (CON APRIETE / INTERFERENCIA)", fg=COLOR_ERROR)
        else:
            lbl_semaforo.config(text="🟡 AJUSTE INDETERMINADO (TRANSICIÓN)", fg=COLOR_WARNING)
            
        clave_combinacion = (f"{comp_aloj[1]}{comp_aloj[2]}", f"{comp_eje[1]}{comp_eje[2]}")
        if clave_combinacion in DICCIONARIO_APLICACIONES:
            caract, ejemplos = DICCIONARIO_APLICACIONES[clave_combinacion]
            lbl_caract_val.config(text=caract, fg=COLOR_TEXT_MAIN)
            lbl_ejemplos_val.config(text=ejemplos, fg=COLOR_TEXT_MAIN)
        else:
            lbl_caract_val.config(text="Ajuste fuera de la tabla de referencia de diámetros deslizantes estándar.", fg=COLOR_TEXT_MUTED)
            lbl_ejemplos_val.config(text="---", fg=COLOR_TEXT_MUTED)
    else:
        lbl_semaforo.config(text="⚠ DATOS FUERA DE RANGO O FORMATO INVÁLIDO (0 - 500 mm)", fg=COLOR_ERROR)
        lbl_caract_val.config(text="Códigos erróneos.", fg=COLOR_ERROR)
        lbl_ejemplos_val.config(text="---", fg=COLOR_TEXT_MUTED)

# =====================================================================
# INTERFAZ GRÁFICA INTERACTIVA
# =====================================================================
root = tk.Tk()
root.title("FitsStudio Pro + Strict Validator")
root.geometry("750x720")
root.configure(bg=COLOR_BG)

# Header
frame_header = tk.Frame(root, bg=COLOR_BG)
frame_header.pack(pady=10, fill=tk.X, padx=35)
tk.Label(frame_header, text="FitsStudio Pro 🛠️", font=("Segoe UI", 18, "bold"), bg=COLOR_BG, fg=COLOR_TEXT_MAIN).pack(anchor="w")
tk.Label(frame_header, text="Norma Completa ISO • Validador Estricto de Letras Base de Tolerancias", font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_TEXT_MUTED).pack(anchor="w")

# Inputs
frame_body = tk.Frame(root, bg=COLOR_BG)
frame_body.pack(fill=tk.X, padx=30, pady=2)

card_aloj = tk.Frame(frame_body, bg=COLOR_CARD, highlightbackground="#334155", highlightthickness=1)
card_aloj.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=2)
tk.Label(card_aloj, text="AGUJERO (Letra en MAYÚSCULA)", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(pady=6)
entry_aloj = tk.Entry(card_aloj, font=("Segoe UI", 18, "bold"), width=8, bg=COLOR_BG, fg=COLOR_TEXT_MAIN, bd=0, insertbackground="white", justify="center")
entry_aloj.pack(pady=2, padx=10)
entry_aloj.insert(0, "12.5H7")

card_eje = tk.Frame(frame_body, bg=COLOR_CARD, highlightbackground="#334155", highlightthickness=1)
card_eje.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=6, pady=2)
tk.Label(card_eje, text="EJE (Letra en minúscula)", font=("Segoe UI", 9, "bold"), bg=COLOR_CARD, fg=COLOR_ACCENT).pack(pady=6)
entry_eje = tk.Entry(card_eje, font=("Segoe UI", 18, "bold"), width=8, bg=COLOR_BG, fg=COLOR_TEXT_MAIN, bd=0, insertbackground="white", justify="center")
entry_eje.pack(pady=2, padx=10)
entry_eje.insert(0, "12.5g6")

btn_calcular = tk.Button(root, text="PROCESAR AJUSTE INDUSTRIAL", font=("Segoe UI", 10, "bold"), bg=COLOR_PRIMARY, fg="white", activebackground="#2563eb", activeforeground="white", bd=0, cursor="hand2", padx=20, pady=8, command=ejecutar_calculo)
btn_calcular.pack(pady=8)

# BANNER DEL SEMÁFORO INDUSTRIAL (Mejora de Estado / Alertas)
lbl_semaforo = tk.Label(root, text="SISTEMA LISTO • INTRODUCE LOS CÓDIGOS ISO", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, pady=6)
lbl_semaforo.pack(fill=tk.X, padx=35, pady=4)

# Resultados Numéricos
card_resultados = tk.Frame(root, bg=COLOR_CARD, highlightbackground="#334155", highlightthickness=1)
card_resultados.pack(fill=tk.X, padx=35, pady=4)

frame_grid_res = tk.Frame(card_resultados, bg=COLOR_CARD)
frame_grid_res.pack(pady=6)
tk.Label(frame_grid_res, text="Máximo:", font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).grid(row=0, column=0, padx=6, sticky="e")
lbl_max_aloj_val = tk.Label(frame_grid_res, text="---", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN)
lbl_max_aloj_val.grid(row=0, column=1, padx=6, sticky="w")
tk.Label(frame_grid_res, text="Mínimo:", font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).grid(row=1, column=0, padx=6, sticky="e")
lbl_min_aloj_val = tk.Label(frame_grid_res, text="---", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN)
lbl_min_aloj_val.grid(row=1, column=1, padx=6, sticky="w")

tk.Label(frame_grid_res, text="│", font=("Segoe UI", 18), bg=COLOR_CARD, fg="#334155").grid(row=0, column=2, rowspan=2, padx=20)

tk.Label(frame_grid_res, text="Máximo:", font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).grid(row=0, column=3, padx=6, sticky="e")
lbl_max_eje_val = tk.Label(frame_grid_res, text="---", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN)
lbl_max_eje_val.grid(row=0, column=4, padx=6, sticky="w")
tk.Label(frame_grid_res, text="Mínimo:", font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).grid(row=1, column=3, padx=6, sticky="e")
lbl_min_eje_val = tk.Label(frame_grid_res, text="---", font=("Segoe UI", 14, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN)
lbl_min_eje_val.grid(row=1, column=4, padx=6, sticky="w")

# PANEL GRÁFICO
card_grafico = tk.Frame(root, bg=COLOR_CARD, highlightbackground="#334155", highlightthickness=1)
card_grafico.pack(fill=tk.X, padx=35, pady=4)
tk.Label(card_grafico, text="DIAGRAMA DE POSICIÓN DE TOLERANCIAS", font=("Segoe UI", 8, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(pady=2)

canvas = tk.Canvas(card_grafico, width=640, height=130, bg=COLOR_BG, bd=0, highlightthickness=0)
canvas.pack(padx=10, pady=4)

# Textos de Tabla
frame_foto_data = tk.Frame(root, bg=COLOR_CARD, highlightbackground="#334155", highlightthickness=1)
frame_foto_data.pack(fill=tk.BOTH, expand=True, padx=35, pady=4)

tk.Label(frame_foto_data, text="Características del asiento (Según Tabla):", font=("Segoe UI", 8, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(anchor="w", padx=15, pady=(6,0))
lbl_caract_val = tk.Label(frame_foto_data, text="Presiona el botón para calcular.", font=("Segoe UI", 10), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN, wraplength=640, justify="left")
lbl_caract_val.pack(anchor="w", padx=15, pady=(2, 4))

tk.Label(frame_foto_data, text="Ejemplos de aplicación:", font=("Segoe UI", 8, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(anchor="w", padx=15)
lbl_ejemplos_val = tk.Label(frame_foto_data, text="---", font=("Segoe UI", 10), bg=COLOR_CARD, fg=COLOR_TEXT_MAIN, wraplength=640, justify="left")
lbl_ejemplos_val.pack(anchor="w", padx=15, pady=(2, 6))

root.mainloop()