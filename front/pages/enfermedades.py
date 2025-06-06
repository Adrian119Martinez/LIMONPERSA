import streamlit as st
import requests

# Configuración de URLs del backend
API_CATEGORIAS_URL = "http://localhost:5000/categorias_enfermedades"

# Estado de sesión para manejar el token
if "token" not in st.session_state:
    st.session_state.token = None

# ==========================================
# 🔐 AUTENTICACIÓN
# ==========================================
st.sidebar.title("Autenticación")

# Verificar si ya hay un token guardado
if st.session_state.token:
    st.sidebar.success("Ya has iniciado sesión.")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.experimental_rerun()
else:
    token_input = st.sidebar.text_input("Ingresa tu Token JWT", type="password")
    if st.sidebar.button("Guardar Token"):
        st.session_state.token = token_input
        st.sidebar.success("Token guardado correctamente.")
        st.experimental_rerun()

# Verificación de autenticación
if not st.session_state.token:
    st.warning("⚠️ Debes autenticarte para acceder a las funcionalidades.")
    st.stop()

# Definir los headers con el token
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ==========================================
# 🚀 OPCIONES
# ==========================================
opcion = st.sidebar.selectbox("Selecciona una opción", ["Listar Categorías", "Agregar Categoría"])

# ==========================================
# 📋 LISTAR CATEGORÍAS
# ==========================================
if opcion == "Listar Categorías":
    st.title("Lista de Categorías de Enfermedades")
    try:
        response = requests.get(API_CATEGORIAS_URL, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            categorias = data["categorias"]
            if categorias:
                for categoria in categorias:
                    st.write(f"📝 **Nombre:** {categoria['nombre']}")
                    st.write(f"📋 **Descripción:** {categoria['descripcion']}")
                    st.write(f"🔗 **ID Enfermedad:** {categoria['id_enfermedad']}")
                    st.write(f"🆔 **ID Categoría:** {categoria['id']}")
                    st.divider()
            else:
                st.info("No hay categorías registradas en el sistema.")
        else:
            st.error(data.get("message", "Error al obtener categorías"))
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# ==========================================
# ➕ AGREGAR CATEGORÍA DE ENFERMEDAD
# ==========================================
elif opcion == "Agregar Categoría":
    st.title("Agregar Categoría de Enfermedad")
    
    with st.form("form_categoria"):
        id_enfermedad = st.text_input("ID Enfermedad")
        nombre = st.text_input("Nombre de la Categoría")
        descripcion = st.text_area("Descripción")
        submit = st.form_submit_button("Registrar Categoría")

    if submit:
        if not id_enfermedad or not nombre or not descripcion:
            st.error("Todos los campos son obligatorios.")
        else:
            payload = {
                "id_enfermedad": id_enfermedad,
                "nombre": nombre,
                "descripcion": descripcion
            }
            try:
                response = requests.post(API_CATEGORIAS_URL, json=payload, headers=headers)
                data = response.json()
                if response.status_code == 201 and data.get("success"):
                    st.success(f"Categoría registrada con éxito. ID: {data.get('id')}")
                else:
                    st.error(data.get("message", "Error al registrar categoría"))
            except Exception as e:
                st.error(f"Error de conexión: {e}")
