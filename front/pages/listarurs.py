import streamlit as st
import requests

# Configuración de URLs del backend
API_USUARIOS_URL = "http://localhost:5000/usuarios"

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

# ==========================================
# 📋 LISTAR USUARIOS
# ==========================================
st.title("Lista de Usuarios Registrados")

# Definir los headers con el token
headers = {"Authorization": f"Bearer {st.session_state.token}"}

try:
    # Hacer la solicitud GET al backend
    response = requests.get(API_USUARIOS_URL, headers=headers)
    data = response.json()
    
    if response.status_code == 200 and data.get("success"):
        usuarios = data["usuarios"]
        
        if usuarios:
            for usuario in usuarios:
                st.write(f"👤 **Nombre Completo:** {usuario['nombre']} {usuario['apellido_pat']} {usuario['apellido_mat']}")
                st.write(f"✉️ **Email:** {usuario['email']}")
                st.divider()
        else:
            st.info("No hay usuarios registrados en el sistema.")
    else:
        st.error(data.get("message", "Error al obtener la lista de usuarios"))
except Exception as e:
    st.error(f"Error de conexión: {e}")
