
import streamlit as st
import json


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
            material_sel = st.selectbox(
                "3. Material del conductor (Resistividad a 20 °C):",
                options = materiales_lista,
                index = idx_mat,
                help = "Selector fijo con resistividades a 20 °C. No se permite escribir materiales no registrados",
                key = "input_material",
            )
            # Mostrar la resistividad asociada al material seleccionado
            rho_sel = obtener_resistividad(material)
            st.caption(f"Resistividad del {material_sel}: **{rho_sel:.2e} Ω·m** a 20 °C")

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



#El historial con json (check this out)
#Para leer json.load, para subir json.dump
#Debo usar el .append para alargar la lista, pero im not sure donde
#Crear modulo con todas las funciones de json y ponerlas como tabla aca
#Se guarda la info en calculadora? o por variables y cargo todo luego aca? o solo esta parte es para ponerlo estilo de tabla?
#Conexion cn CSV -> Creo q el csv es el descargable de lo que json guarda, CREO  
elif menu == "📜 Historial de Cálculos":
    st.title("📜 Historial de cálculos realizados")

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
