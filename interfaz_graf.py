
import streamlit as st
import json
from datetime import datetime
from logs.logs import (registrar_error, registrar_info, registrar_warning)


from calculadora.materiales import (obtener_lista_materiales, obtener_resistividad)

from json_csv_registro.historial import (cargar_historial, guardar_calculo, limpiar_historial)

from calculadora.validaciones import (validar_todas_las_entradas)

from calculadora.calculos import (calcular_circuito)

from utilidades.generadores import (generar_registros_historial, generar_lineas_log)


from json_csv_registro.reportes_csv import (generar_csv_en_memoria, exportar_reporte_a_disco)

from pathlib import Path

#Config de la pagina
st.set_page_config(
    page_title = "Calculadora de corriente eléctrica y resistencia",
    page_icon = "✨",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

if "app_iniciada" not in st.session_state:
    registrar_info("interfaz_graf.py", "Aplicación Streamlit iniciada")
    st.session_state["app_iniciada"] = True


#Barra lateral
st.sidebar.title("Circuito DC Serie")
st.sidebar.caption("Programación l | Física ll")

menu = st.sidebar.radio(
    "Navegación:",
    [
        "⚡ Calculadora",
        "📜 Historial de Cálculos",
        "📋 Logs Técnicos",
        "💡 Fundamentos / Ayuda",
        "📊 Reportes CSV",
    ],
    index = 0, #Marca que se inicia en "Calculadora"
)

#Los calculos como tal perce
if menu == "⚡ Calculadora":
    st.title("⚡ Calculadora de Corriente y Resistencia (DC en Serie)")

    # Inicializar campos para cuando se limpie
    defaults = {
        "input_tension": "12.0",
        "input_rcarga": "10.0",
        "input_material": "Cobre",
        "input_longitud": "5.0",
        "input_seccion": "2.5 mm²",
    }

    
    for clave, valor_def in defaults.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor_def


    def limpiar_formulario():
        st.session_state["input_tension"] = "12.0"
        st.session_state["input_rcarga"] = "10.0"
        st.session_state["input_material"] = "Cobre"
        st.session_state["input_longitud"] = "5.0"
        st.session_state["input_seccion"] = "2.5 mm²"
        registrar_info("Calculadora.limpiar", "Formulario restablecido a valores por defecto")

    
    with st.container():
        colum_form, colum_resp = st.columns([1, 1], gap="large") #Divide la pantalla en dos para q se vea mas cute

        #Try out de la parte grafica, me guto
        with colum_form:
            st.subheader("📥 Parámetros de Entrada")

            tension_str = st.text_input(
                "1. Tensión de la fuente DC - V (Voltios):",
                value = st.session_state["input_tension"],
                help = "Debe ser un número finito estrictamente mayor que cero (V > 0)",
                key = "input_tension",
            )

            rcarga_str = st.text_input(
                "2. Resistencia de carga - R_carga (Ohmios - Ω):",
                value = st.session_state["input_rcarga"],
                help = "Resistencia del receptor. Debe ser mayor que cero (R_carga > 0)",
                key = "input_rcarga",
            )

            # Aparece comp aun no definido pero falta importar eso de la carpeta 
            materiales_lista = obtener_lista_materiales()
            idx_mat = (
                materiales_lista.index(st.session_state["input_material"])
                if st.session_state["input_material"] in materiales_lista
                else 0
            )
            material = st.selectbox(
                "3. Material del conductor (Resistividad a 20 °C):",
                options = materiales_lista,
                index = idx_mat,
                help = "Selector fijo con resistividades a 20 °C. No se permite escribir materiales no registrados",
                key = "input_material",
            )
            # Mostrar la resistividad asociada al material seleccionado
            rho_sel = obtener_resistividad(material)

            st.caption(f"Resistividad del {material}: **{rho_sel:.2e} Ω·m** a 20 °C")

            longitud_str = st.text_input(
                "4. Longitud de ida - L (Metros):",
                value = st.session_state["input_longitud"],
                help = "Distancia unidireccional fuente-carga. El conductor total será 2 * L (ida y retorno). L > 0",
                key = "input_longitud",
            )

            seccion_str = st.text_input(
                "5. Sección transversal - A (mm²):",
                value = st.session_state["input_seccion"],
                help = "Área en mm². Acepta formatos como '2.5', '2,5', '2.5 mm2', '2,5 mm²'. Se valida mediante Regex",
                key = "input_seccion",
            )

            # Los botones de limpiar o correr
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                boton_calcular = st.button("⚡ Calcular Circuito", type = "primary", use_container_width = True)
            with col_btn2:
                st.button(
                    "🧹 Limpiar Formulario",
                    use_container_width=True,
                    on_click=limpiar_formulario,
                )    


        with colum_resp:
            st.subheader("📊 Resultados del Circuito")
            
            if boton_calcular:
                try:
                    # 1. Validación de entradas (funciones puras sin dependencia de widgets)
                    rho_val = obtener_resistividad(material)
                    datos_validados = validar_todas_las_entradas(
                        voltaje = tension_str,
                        resistencia_carga = rcarga_str,
                        longitud = longitud_str,
                        seccion = seccion_str,
                        resistividad = rho_val,
                    )

                    v_val = datos_validados["voltaje"]
                    rc_val = datos_validados["resistencia_carga"]
                    l_val = datos_validados["longitud"]
                    a_val = datos_validados["seccion"]
                    rho_val = datos_validados["resistividad"]
                    mat_val = material


                    # 2. Cálculo físico sin redondeos intermedios
                    resultados = calcular_circuito(
                        voltaje=v_val,
                        resistencia_carga=rc_val,
                        material=mat_val,
                        longitud_inicial=l_val,
                        mm2=a_val,
                    )

                    # 3. Guardar en historial persistente
                    entradas_dict = {
                        "tension_V": v_val,
                        "resistencia_carga_ohm": rc_val,
                        "material": mat_val,
                        "resistividad_ohm_m": rho_val,
                        "longitud_ida_m": l_val,
                        "seccion_mm2": a_val,
                    }
                    registro_guardado = guardar_calculo(entradas_dict, resultados)

                    registrar_info(
                        "Calculadora.calcular",
                        f"Cálculo guardado ID={registro_guardado['id']} | V={v_val}V, Rcarga={rc_val}Ω, mat={mat_val}, L={l_val}m, A={a_val}mm²",
                    )

                    st.success(f"✅ Cálculo exitoso | Registrado con ID: `{registro_guardado['id']}`")

                    # Tarjetas métricas
                    m1, m2 = st.columns(2)
                    m1.metric("Resistencia del Cable (Rc)", f"{resultados['Rc']} Ω")
                    m2.metric("Resistencia Total (Rt)", f"{resultados['Rt']} Ω")

                    m3, m4 = st.columns(2)
                    m3.metric("Corriente del Circuito (I)", f"{resultados['I']} A")
                    m4.metric("Caída de Tensión (Vc)", f"{resultados['Vc']} V")

                    st.metric("Potencia Disipada en Cable (Pc)", f"{resultados['Pc']} W")

                    # Explicación resumida de cada magnitud
                    longitud_total_m = 2 * l_val
                    seccion_m2 = a_val * 1e-6
                    with st.expander("ℹ️ Detalle y significado de las magnitudes calculadas", expanded=True):
                        st.markdown(
                            f"""
                            - **Longitud Total del Conductor ($L_{{total}}$):** {longitud_total_m:.2f} m (ida {l_val:.2f} m + retorno {l_val:.2f} m).
                            - **Sección en metros cuadrados ($A$):** {seccion_m2:.2e} $\\text{{m}}^2$.
                            - **Resistencia del Cable ($R_c$):** Oposición eléctrica de los {longitud_total_m:.2f} m de cable de {mat_val}.
                            - **Resistencia Total ($R_t$):** Suma en serie ($R_{{carga}} + R_c = {rc_val} + {resultados['Rc']:.4f}\\,\\Omega$).
                            - **Corriente ($I$):** Intensidad según Ley de Ohm ($I = V / R_t$).
                            - **Caída de Tensión ($V_c$):** Voltaje absorbido por el cable ($I \\times R_c$).
                            - **Potencia Disipada ($P_c$):** Energía disipada como calor en el cable por efecto Joule ($I^2 \\times R_c$).
                            """
                        )

                except Exception as error_inesperado:
                    #logger.error(f"Error inesperado : {error_inesperado}")
                    registrar_error("Calculadora.calcular", f"Error inesperado: {error_inesperado}")
                    st.error(f"⚠️ Ocurrió un error inesperado: {error_inesperado}")
            else:
                st.info("Presione **'⚡ Calcular Circuito'** para ver las métricas y el desglose de resultados.")




#El historial con json (check this out)
#Para leer json.load, para subir json.dump
#Debo usar el .append para alargar la lista, pero im not sure donde
#Crear modulo con todas las funciones de json y ponerlas como tabla aca
#Se guarda la info en calculadora? o por variables y cargo todo luego aca? o solo esta parte es para ponerlo estilo de tabla?
#Conexion cn CSV -> Creo q el csv es el descargable de lo que json guarda, CREO  
elif menu == "📜 Historial de Cálculos":
    st.title("📜 Historial de cálculos realizados")

    datos_historial = cargar_historial()

    if not datos_historial:
        st.info("El historial de cálculos se encuentra actualmente vacío.")
    else:
        # Filtros usando generadores con yield
        st.subheader("🔍 Filtros de Consulta")
        fcol1, fcol2, fcol3 = st.columns([1, 1, 1])

        with fcol1:
            materiales_filtro = ["Todos"] + obtener_lista_materiales()
            filtro_mat = st.selectbox("Filtrar por Material:", options=materiales_filtro)

        with fcol2:
            filtro_fecha = st.text_input(
                "Filtrar por Fecha (YYYY-MM-DD):",
                placeholder = "ej. 2026-11-21",
                help = "Búsqueda por prefijo de fecha."
            )

        with fcol3:
            st.write("")
            st.write("")
            if st.button("🗑️ Vaciar Historial Completo", type="secondary"):
                if limpiar_historial():
                    st.success("Historial eliminado correctamente.")
                    st.rerun()

        # Uso explícito de la función generadora (utilidades/generadores.py)
        generador = generar_registros_historial(
            registros = datos_historial,
            filtro_material = filtro_mat if filtro_mat != "Todos" else None,
            filtro_fecha = filtro_fecha.strip() if filtro_fecha.strip() else None,
        )

        registros_filtrados = list(generador)

        st.caption(f"Mostrando **{len(registros_filtrados)}** de **{len(datos_historial)}** registros guardados.")

        if registros_filtrados:
            filas_tabla = []
            for r in registros_filtrados:
                ent = r.get("entradas", {})
                res = r.get("resultados", {})
                filas_tabla.append({
                    "ID": r.get("id"),
                    "Fecha y Hora": r.get("fecha_hora"),
                    "Tensión (V)": ent.get("tension_V"),
                    "R Carga (Ω)": ent.get("resistencia_carga_ohm"),
                    "Material": ent.get("material"),
                    "Longitud (m)": ent.get("longitud_ida_m"),
                    "Sección (mm²)": ent.get("seccion_mm2"),
                    "Rc Cable (Ω)": round(res.get("Rc", 0), 4),
                    "Rt Total (Ω)": round(res.get("Rt", 0), 4),
                    "Corriente (A)": round(res.get("I", 0), 4),
                    "Caída Vc (V)": round(res.get("Vc", 0), 4),
                    "Potencia Pc (W)": round(res.get("Pc", 0), 4),
                })
            st.dataframe(filas_tabla, use_container_width=True)
        else:
            st.warning("No se encontraron registros que coincidan con los filtros seleccionados.")

#Logs tecnicos (...)
#Don´t know bout this one
elif menu == "📋 Logs Técnicos":
    st.title("📋 Registros Técnicos de la Aplicación")
    ruta_log = Path("logs/app.log")

    if st.button("🔄 Actualizar Logs"):
        st.rerun()

    if ruta_log.exists():
        contenido_log = ruta_log.read_text(encoding="utf-8")
        st.code(contenido_log if contenido_log.strip() else "El archivo de log está vacío.", language="text")
    else:
        st.info("Aún no se ha generado el archivo `logs/app.log`.")



#Fundamentos -> Esta facilito
elif menu == "💡 Fundamentos / Ayuda":
    st.header("💡 Fundamentos Físicos, Matemáticos y Alcance del Simulador")

    tab1, tab2, tab3 = st.tabs(["📐 Modelo Matemático", "🔬 Resistividades a 20 °C", "🎯 Caso de Referencia y Supuestos"])

    with tab1:
        st.subheader("Secuencia Obligatoria de Cálculo (Circuito DC en Serie)")
        st.markdown(
            r"""
            El circuito modela una fuente de tensión continua, un conductor de ida, una carga resistiva y el conductor de retorno.

            1. **Conversión de sección transversal:**
               $$A(\text{m}^2) = A(\text{mm}^2) \times 10^{-6}$$
            2. **Longitud total del conductor (ida y vuelta):**
               $$L_{\text{total}} = 2 \times L$$
            3. **Resistencia eléctrica del cable conductor:**
               $$R_c = \rho \times \frac{L_{\text{total}}}{A(\text{m}^2)}$$
            4. **Resistencia equivalente total del circuito en serie:**
               $$R_t = R_{\text{carga}} + R_c$$
            5. **Corriente eléctrica circulante (Ley de Ohm):**
               $$I = \frac{V}{R_t}$$
            6. **Caída de tensión en el conductor:**
               $$V_c = I \times R_c$$
            7. **Potencia disipada por efecto Joule en el conductor:**
               $$P_c = I^2 \times R_c$$
            """
        )

    with tab2:
        st.subheader("Catálogo de Materiales y Resistividades ($\rho$) a 20 °C")
        materiales = obtener_lista_materiales()
        filas_mat = [
            {"Material": nombre, "Resistividad ρ (Ω·m)": f"{obtener_resistividad(nombre)}", "Valor Exacto": obtener_resistividad(nombre)}
            for nombre in materiales
        ]
        st.table(filas_mat)

    with tab3:
        st.subheader("Caso de Comprobación y Calibración Obligatorio")
        st.markdown(
            """
            Para verificar el cálculo correcto, utilice los siguientes valores:
            - **Tensión ($V$):** $12.0\\,\\text{V}$
            - **Resistencia de Carga ($R_{\\text{carga}}$):** $10.0\\,\\Omega$
            - **Material:** Cobre ($\\\\rho = 1.68 \\times 10^{-8}\\,\\Omega\\cdot\\text{m}$)
            - **Longitud de ida ($L$):** $5.0\\,\\text{m}$
            - **Sección transversal ($A$):** $2.5\\,\\text{mm}^2$

            **Resultados esperados:**
            - $R_c \\approx 0.0672\\,\\Omega$
            - $R_t \\approx 10.0672\\,\\Omega$
            - $I \\approx 1.1920\\,\\text{A}$
            - $V_c \\approx 0.0801\\,\\text{V}$
            - $P_c \\approx 0.0955\\,\\text{W}$

            ---
            ### ⚠️ Supuestos y Limitaciones Didácticas
            1. **Temperatura constante:** El cálculo asume $20\\,^\\circ\\text{C}$ invariable. No considera coeficiente térmico de resistividad $(\\alpha)$.
            2. **Condiciones ideales:** No se modelan inductancias, capacitancias parásitas, corrosión ni resistencias de contacto en bornes.
            3. **No es dimensionador de ampacidad:** Este software no verifica si el cable soporta térmicamente la corriente calculada conforme a normativas técnicas (ej. NEC / IEC).
            """
        )

#Reportes CSV, se dercarga a excel -> De la mano cn json? dont know
else:
    st.title("📊 Exportación de Reportes en Formato CSV")
    st.subheader("Genere y descargue reportes del historial de cálculos con encabezados estructurados "
        "y unidades físicas explícitas en cada columna")

    
    historial = cargar_historial()

    if not historial:
        st.warning("No hay registros en el historial para generar reportes.")
    else:
        st.subheader("Configuración de Exportación")

        materiales_opc = ["Todos"] + obtener_lista_materiales()
        filtro_rep_mat = st.selectbox("Exportar por Material:", materiales_opc, key="rep_mat")

        generador_reporte = generar_registros_historial(
            registros = historial,
            filtro_material = filtro_rep_mat if filtro_rep_mat != "Todos" else None,
        )
        registros_a_exportar = list(generador_reporte)

        st.caption(f"Registros listos para exportar: **{len(registros_a_exportar)}**")

        if registros_a_exportar:
            csv_data = generar_csv_en_memoria(registros_a_exportar)

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label = "📥 Descargar Reporte CSV",
                    data = csv_data,
                    file_name = f"reporte_circuito_dc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime = "text/csv",
                    type = "primary",
                    use_container_width = True,
                )

            with col_d2:
                if st.button("💾 Guardar Copia en Carpeta 'reportes/'", use_container_width=True):
                    ruta_guardada = exportar_reporte_a_disco(registros_a_exportar)
                    if ruta_guardada:
                        registrar_info("ReportesCSV.exportar", f"Reporte guardado en {ruta_guardada}")
                        st.success(f"Reporte archivado en: `{ruta_guardada}`")
                    else:
                        registrar_error("ReportesCSV.exportar", "No se pudo guardar el reporte CSV en disco")
                        st.error("No se pudo guardar el archivo en disco.")

            with st.expander("👁️ Vista Previa del Archivo CSV (Primeros 5 registros)"):
                st.code("\n".join(csv_data.splitlines()[:6]), language="text")
        else:
            st.info("No hay registros que coincidan con el filtro seleccionado.")
