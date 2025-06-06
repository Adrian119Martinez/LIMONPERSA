import streamlit as st
import requests

# Configuración de URLs del backend
API_LOGIN_URL = "http://localhost:5000/login"
API_REGISTER_URL = "http://localhost:5000/usuarios"
#API_TRATAMIENTOS_URL = "http://localhost:5000/tratamientos"
#API_CATEGORIAS_URL = "http://localhost:5000/categorias_enfermedades"

# Estado de sesión
if "token" not in st.session_state:
    st.session_state.token = None
if "nombre_completo" not in st.session_state:
    st.session_state.nombre_completo = None

# Función para cerrar sesión
def logout():
    st.session_state.token = None
    st.session_state.nombre_completo = None
    st.success("Has cerrado sesión correctamente.")

# Opciones: Login o Registro
opcion = st.sidebar.selectbox("Selecciona una opción", ["Iniciar Sesión", "Registrar Usuario"])

# ==========================================
# 🚀 SECCIÓN DE LOGIN
# ==========================================
if opcion == "Iniciar Sesión":
    st.title("Iniciar Sesión")

    with st.form("login_form"):
        email = st.text_input("Correo electrónico")
        contrasena = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

    if submit:
        payload = {"email": email, "contrasena": contrasena}
        try:
            response = requests.post(API_LOGIN_URL, json=payload)
            data = response.json()
            if response.status_code == 200 and data.get("success"):
                st.session_state.token = data.get("token")
                st.session_state.nombre_completo = f"{data.get('nombre')} {data.get('apellido_pat')} {data.get('apellido_mat')}"
                st.success(f"Bienvenido, {st.session_state.nombre_completo} 👋")
            else:
                st.error(data.get("message", "Credenciales inválidas"))
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    # Botón de Logout
    if st.session_state.token:
        if st.button("Cerrar sesión"):
            logout()

# ==========================================
# 🚀 SECCIÓN DE REGISTRO
# ==========================================
elif opcion == "Registrar Usuario":
    st.title("Registrar Usuario")

    with st.form("register_form"):
        nombre = st.text_input("Nombre")
        apellido_pat = st.text_input("Apellido Paterno")
        apellido_mat = st.text_input("Apellido Materno")
        direccion = st.text_input("Dirección")
        email = st.text_input("Correo Electrónico")
        contrasena = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Registrar")

    if submit:
        if not nombre or not apellido_pat or not apellido_mat or not direccion or not email or not contrasena:
            st.error("Todos los campos son obligatorios.")
        else:
            payload = {
                "nombre": nombre,
                "apellido_pat": apellido_pat,
                "apellido_mat": apellido_mat,
                "direccion": direccion,
                "email": email,
                "contrasena": contrasena
            }
            try:
                response = requests.post(API_REGISTER_URL, json=payload)
                data = response.json()
                if response.status_code == 201 and data.get("success"):
                    st.success(f"Usuario registrado con éxito. ID: {data.get('id')}")
                else:
                    st.error(data.get("message", "Error al registrar usuario"))
            except Exception as e:
                st.error(f"Error de conexión: {e}")
