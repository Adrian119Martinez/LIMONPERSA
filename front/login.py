import streamlit as st
import requests

# Configuración
API_LOGIN_URL = "http://127.0.0.1:5000/login"
#API_USUARIOS_URL = "http://localhost:5000/usuarios"

# Variables de sesión
if "token" not in st.session_state:
    st.session_state.token = None

# Formulario de login
st.title("Login de Usuario")

with st.form("login_form"):
    email = st.text_input("Correo electrónico")
    contrasena = st.text_input("Contraseña", type="password")
    submit = st.form_submit_button("Iniciar sesión")

if submit:
    payload = {
        "email": email,
        "contrasena": contrasena
    }

    try:
        response = requests.post(API_LOGIN_URL, json=payload)
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            st.session_state.token = data.get("token")
            st.success("¡Inicio de sesión exitoso!")
            st.success(data.get("token"))
            st.switch_page("pages/logout.py")
        else:
            st.error(data.get("message", "Error en el login"))
    except Exception as e:
        st.error(f"Error al conectarse con el backend: {e}")

