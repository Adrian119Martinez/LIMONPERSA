import streamlit as st
import requests

# Configuración de URLs del backend
API_TRATAMIENTOS_URL = "http://localhost:5000/tratamientos"
API_CATEGORIAS_URL = "http://localhost:5000/categorias_enfermedades"

# Estado de sesión para manejar el token
if "token" not in st.session_state:
    st.session_state.token = None

# ==========================================
# 🔐 AUTENTICACIÓN
# ==========================================
# Input para el token JWT
st.sidebar.title("Autenticación")
token_input = st.sidebar.text_input("Ingresa tu Token JWT", type="password")
if st.sidebar.button("Guardar Token"):
    st.session_state.token = token_input
    st.sidebar.success("Token guardado correctamente.")

# Verificación de autenticación
if not st.session_state.token:
    st.warning("⚠️ Debes autenticarte para acceder a las funcionalidades.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ==========================================
# 🚀 OPCIONES
# ==========================================
opcion = st.sidebar.selectbox("Selecciona una opción", ["Listar Tratamientos", "Agregar Tratamiento", "Listar Categorías", "Agregar Categoría"])

# ==========================================
# 📋 LISTAR TRATAMIENTOS
# ==========================================
if opcion == "Listar Tratamientos":
    st.title("Lista de Tratamientos")
    try:
        response = requests.get(API_TRATAMIENTOS_URL, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            tratamientos = data["tratamientos"]
            for tratamiento in tratamientos:
                st.write(f"📝 **Nombre:** {tratamiento['nombre']}")
                st.write(f"📋 **Descripción:** {tratamiento['descripcion']}")
                st.write(f"📌 **Instrucciones:** {tratamiento['instrucciones']}")
                st.write(f"🔗 **ID Enfermedad:** {tratamiento['id_enfermedad']}")
                st.divider()
        else:
            st.error(data.get("message", "Error al obtener tratamientos"))
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# ==========================================
# ➕ AGREGAR TRATAMIENTO
# ==========================================
elif opcion == "Agregar Tratamiento":
    st.title("Agregar Tratamiento")
    with st.form("form_tratamiento"):
        id_enfermedad = st.text_input("ID Enfermedad")
        nombre = st.text_input("Nombre del Tratamiento")
        descripcion = st.text_area("Descripción")
        instrucciones = st.text_area("Instrucciones")
        submit = st.form_submit_button("Registrar Tratamiento")

    if submit:
        payload = {
            "id_enfermedad": id_enfermedad,
            "nombre": nombre,
            "descripcion": descripcion,
            "instrucciones": instrucciones
        }
        try:
            response = requests.post(API_TRATAMIENTOS_URL, json=payload, headers=headers)
            data = response.json()
            if response.status_code == 201 and data.get("success"):
                st.success(f"Tratamiento registrado con éxito. ID: {data.get('id')}")
            else:
                st.error(data.get("message", "Error al registrar tratamiento"))
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# ==========================================
# 📋 LISTAR CATEGORÍAS DE ENFERMEDADES
# ==========================================
elif opcion == "Listar Categorías":
    st.title("Lista de Categorías de Enfermedades")
    try:
        response = requests.get(API_CATEGORIAS_URL, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            categorias = data["categorias"]
            for categoria in categorias:
                st.write(f"📝 **Nombre:** {categoria['nombre']}")
                st.write(f"📋 **Descripción:** {categoria['descripcion']}")
                st.write(f"🔗 **ID Enfermedad:** {categoria['id_enfermedad']}")
                st.divider()
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
