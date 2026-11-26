
import streamlit as st
import json
from datetime import datetime

from calculadora.materiales import (obtener_lista_materiales, obtener_resistividad)

from json_csv_registro.historial import (cargar_historial, guardar_calculo, limpiar_historial)

from calculadora.validaciones import (validar_todas_las_entradas)

from calculadora.calculos import (calcular_circuito)

from utilidades.generadores import (generar_registros_historial, generar_lineas_log)


from json_csv_registro.reportes_csv import (generar_csv_en_memoria, exportar_reporte_a_disco)

#Config de la pagina
st.set_page_config(
    page_title = "Calculadora de corriente eléctrica y resistencia",
    page_icon = "✨",
    layout = "wide",
    initial_sidebar_state = "expanded"
)


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
                boton_limpiar = st.button("🧹 Limpiar Formulario", use_container_width = True)

            if boton_limpiar:

                st.session_state["input_tension"] = "12.0"
                st.session_state["input_rcarga"] = "10.0"
                st.session_state["input_material"] = "Cobre"
                st.session_state["input_longitud"] = "5.0"
                st.session_state["input_seccion"] = "2.5 mm²"
                st.rerun()


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
                    #logger.error(f"Error inesperado en cálculo: {error_inesperado}")
                    st.error(f"⚠️ Ocurrió un error inesperado al calcular: {error_inesperado}")
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


#Fundamentos -> Esta facilito
elif menu == "💡 Fundamentos / Ayuda":
    st.title("💡 Fundamentos Físicos, Matemáticos y Alcance del Simulador")
    tab1, tab2, tab3 = st.tabs(["📐 Modelo Matemático", "🔬 Resistividades a 20 °C", "🎯 Caso de Referencia y Supuestos"])

    #with tab1: -> Asi para ir de panel en panel solo poniendo info, este no es muy interactivo


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
                        st.success(f"Reporte archivado en: `{ruta_guardada}`")
                    else:
                        st.error("No se pudo guardar el archivo en disco.")

            with st.expander("👁️ Vista Previa del Archivo CSV (Primeros 5 registros)"):
                st.code("\n".join(csv_data.splitlines()[:6]), language="text")
        else:
            st.info("No hay registros que coincidan con el filtro seleccionado.")
