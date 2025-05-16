import streamlit as st
import requests

# Configuración de URLs del backend
API_RESEÑAS_URL = "http://localhost:5000/reseñas"

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
opcion = st.sidebar.selectbox("Selecciona una opción", ["Listar Reseñas", "Agregar Reseña"])

# ==========================================
# 📋 LISTAR RESEÑAS
# ==========================================
if opcion == "Listar Reseñas":
    st.title("Lista de Reseñas")
    try:
        response = requests.get(API_RESEÑAS_URL, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            reseñas = data["reseñas"]
            for reseña in reseñas:
                st.write(f"📝 **ID Tratamiento:** {reseña['id_tratamiento']}")
                st.write(f"📝 **ID Enfermedad:** {reseña['id_enfermedad']}")
                st.write(f"📋 **Opinión:** {reseña['opinion']}")
                st.write(f"⭐ **Calificación:** {reseña['calificacion']}/5")
                st.divider()
        else:
            st.error(data.get("message", "Error al obtener reseñas"))
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# ==========================================
# ➕ AGREGAR RESEÑA
# ==========================================
elif opcion == "Agregar Reseña":
    st.title("Agregar Reseña")
    with st.form("form_reseña"):
        id_tratamiento = st.text_input("ID Tratamiento")
        id_enfermedad = st.text_input("ID Enfermedad")
        opinion = st.text_area("Opinión")
        calificacion = st.slider("Calificación", 1, 5, 3)
        submit = st.form_submit_button("Registrar Reseña")

    if submit:
        if not id_tratamiento or not id_enfermedad or not opinion or not calificacion:
            st.error("Todos los campos son obligatorios.")
        else:
            payload = {
                "id_tratamiento": id_tratamiento,
                "id_enfermedad": id_enfermedad,
                "opinion": opinion,
                "calificacion": calificacion
            }
            try:
                response = requests.post(API_RESEÑAS_URL, json=payload, headers=headers)
                data = response.json()
                if response.status_code == 201 and data.get("success"):
                    st.success(f"Reseña registrada con éxito. ID: {data.get('id')}")
                else:
                    st.error(data.get("message", "Error al registrar reseña"))
            except Exception as e:
                st.error(f"Error de conexión: {e}")
