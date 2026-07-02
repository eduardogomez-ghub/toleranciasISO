import streamlit as st
from calculos import *

st.set_page_config(
    page_title="FitsStudio Pro",
    layout="centered"
)

st.title("🛠 FitsStudio Pro")
st.caption("Norma Completa ISO • Validador Estricto")

col1, col2 = st.columns(2)

with col1:
    agujero = st.text_input(
        "AGUJERO (MAYÚSCULA)",
        value="12.5H7"
    )

with col2:
    eje = st.text_input(
        "EJE (minúscula)",
        value="12.5g6"
    )

if st.button("PROCESAR AJUSTE INDUSTRIAL"):

    res_a = validar_y_calcular(agujero, es_agujero=True)
    res_e = validar_y_calcular(eje, es_agujero=False)

    if res_a[0] == "ERR_MAYUS":
        st.error("El agujero debe escribirse con letra MAYÚSCULA (Ej: H7)")
        st.stop()

    if res_e[0] == "ERR_MINUS":
        st.error("El eje debe escribirse con letra minúscula (Ej: g6)")
        st.stop()

    max_a, min_a, sup_um_a, inf_um_a = res_a
    max_e, min_e, sup_um_e, inf_um_e = res_e

    if not max_a or not max_e:
        st.error("Datos fuera de rango o formato inválido (0-500 mm)")
        st.stop()

    st.subheader("Resultados")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Máximo Agujero", max_a)
        st.metric("Mínimo Agujero", min_a)

    with c2:
        st.metric("Máximo Eje", max_e)
        st.metric("Mínimo Eje", min_e)

    juego_max = sup_um_a - inf_um_e
    juego_min = inf_um_a - sup_um_e

    if juego_min >= 0:
        st.success("🟢 AJUSTE MÓVIL (CON HOLGURA)")
    elif juego_max <= 0:
        st.error("🔴 AJUSTE FIJO (CON APRIETE / INTERFERENCIA)")
    else:
        st.warning("🟡 AJUSTE INDETERMINADO (TRANSICIÓN)")

    comp_aloj = descomponer_ajuste(agujero, True)
    comp_eje = descomponer_ajuste(eje, False)

    clave = (
        f"{comp_aloj[1]}{comp_aloj[2]}",
        f"{comp_eje[1]}{comp_eje[2]}"
    )

    st.divider()

    if clave in DICCIONARIO_APLICACIONES:

        caract, ejemplos = DICCIONARIO_APLICACIONES[clave]

        st.markdown("### Características")
        st.write(caract)

        st.markdown("### Ejemplos")
        st.write(ejemplos)

    else:
        st.info("Ajuste fuera de la tabla de referencia.")
