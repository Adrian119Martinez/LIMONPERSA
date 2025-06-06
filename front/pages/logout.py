import streamlit as st
import requests

# Configuración de URLs del backend
API_USUARIOS_URL = "http://localhost:5000/usuarios"

API_USUARIOS_EMAIL_URL = "http://localhost:5000/usuarios/email"
API_BASE_URL = "http://localhost:5000"
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
opcion = st.sidebar.selectbox("Selecciona una opción", ["Listar Usuarios", "Registrar Usuario", "Actualizar Usuario", "Eliminar Usuario"])

# ==========================================
# 📋 LISTAR USUARIOS
# ==========================================
if opcion == "Listar Usuarios":
    st.title("Lista de Usuarios Registrados")
    try:
        response = requests.get(API_USUARIOS_URL, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            usuarios = data["usuarios"]
            if usuarios:
                for usuario in usuarios:
                    st.write(f"🆔 **ID Usuario:** {usuario.get('id')}")
                    st.write(f"👤 **Nombre:** {usuario.get('nombre')} {usuario.get('apellido_pat')} {usuario.get('apellido_mat')}")
                    st.write(f"📧 **Email:** {usuario.get('email')}")
                    st.write(f"🏡 **Dirección:** {usuario.get('direccion')}")
                    st.divider()
            else:
                st.info("No hay usuarios registrados.")
        else:
            st.error(data.get("message", "Error al obtener los usuarios"))
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# ==========================================
# ➕ REGISTRAR USUARIO
# ==========================================
elif opcion == "Registrar Usuario":
    st.title("Registrar un Nuevo Usuario")

    with st.form("form_usuario"):
        nombre = st.text_input("Nombre")
        apellido_pat = st.text_input("Apellido Paterno")
        apellido_mat = st.text_input("Apellido Materno")
        direccion = st.text_input("Dirección")
        email = st.text_input("Correo Electrónico")
        contrasena = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Registrar Usuario")

    if submit:
        if not (nombre and apellido_pat and apellido_mat and direccion and email and contrasena):
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
                response = requests.post(API_USUARIOS_URL, json=payload)
                data = response.json()
                if response.status_code == 201 and data.get("success"):
                    st.success(f"Usuario registrado con éxito. ID: {data.get('id')}")
                else:
                    st.error(data.get("message", "Error al registrar usuario"))
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# ==========================================
# ✏️ ACTUALIZAR USUARIO
# ==========================================
elif opcion == "Actualizar Usuario":
    st.title("Actualizar Información del Usuario")

   # ---------- FORMULARIO DE EDICIÓN ----------

    st.subheader("Editar información del usuario")

    email = st.text_input("Correo electrónico del usuario a editar")

    nombre = st.text_input("Nuevo nombre")
    apellido_pat = st.text_input("Nuevo apellido paterno")
    apellido_mat = st.text_input("Nuevo apellido materno")
    direccion = st.text_input("Nueva dirección")
    contrasena = st.text_input("Nueva contraseña", type="password")

    if st.button("Actualizar usuario"):
        if not email:
            st.error("Debes ingresar el correo del usuario.")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            payload = {}

            if nombre: payload["nombre"] = nombre
            if apellido_pat: payload["apellido_pat"] = apellido_pat
            if apellido_mat: payload["apellido_mat"] = apellido_mat
            if direccion: payload["direccion"] = direccion
            if contrasena: payload["contrasena"] = contrasena

            if not payload:
                st.warning("No se ingresaron cambios.")
            else:
                response = requests.put(
                    f"{API_BASE_URL}/usuarios/email/{email}",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    st.success("Usuario actualizado correctamente.")
                elif response.status_code == 404:
                    st.error("Usuario no encontrado.")
                elif response.status_code == 401:
                    st.error("Token inválido o expirado. Vuelve a iniciar sesión.")
                else:
                    st.error(f"Error inesperado: {response.status_code}")


# ==========================================
# 🚀 ELIMINAR USUARIO POR EMAIL
# ==========================================
elif opcion == "Eliminar Usuario":
    st.title("Eliminar Usuario")

# Ingresar el email del usuario a eliminar
    email_usuario = st.text_input("Correo electrónico del usuario a eliminar")

    if st.button("Eliminar Usuario"):   
        if email_usuario:
            # Realizar la petición DELETE
            response = requests.delete(f"{API_USUARIOS_EMAIL_URL}/{email_usuario}", headers=headers)
        
            if response.status_code == 200:
                st.success(f"Usuario con email {email_usuario} eliminado correctamente.")
            else:
             st.error("No se pudo eliminar el usuario. Verifica el correo electrónico.")
        else:
            st.error("Por favor, ingresa un correo electrónico válido.")