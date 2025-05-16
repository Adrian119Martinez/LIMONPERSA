import streamlit as st
import requests

# Configuración de URLs del backend
API_IMAGENES_URL = "http://localhost:5000/imagenes"

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

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ==========================================
# 🚀 OPCIONES
# ==========================================
opcion = st.sidebar.selectbox("Selecciona una opción", ["Listar Imágenes", "Subir Imagen"])

# ==========================================
# 🖼️ LISTAR IMÁGENES
# ==========================================
if opcion == "Listar Imágenes":
    st.title("Lista de Imágenes")
    try:
        response = requests.get(API_IMAGENES_URL, headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            imagenes = data["imagenes"]
            for imagen in imagenes:
                st.write(f"👤 **Usuario ID:** {imagen['usuario_id']}")
                st.write(f"📅 **Fecha:** {imagen['fecha']}")
                st.write(f"🌎 **Coordenadas:** Latitud {imagen['coordenadas']['latitud']}, Longitud {imagen['coordenadas']['longitud']}")
                
                # Mostrar imagen
                st.image(imagen['url'], caption=imagen['url'], use_column_width=True)
                st.divider()
        else:
            st.error(data.get("message", "Error al obtener las imágenes"))
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# ==========================================
# ➕ SUBIR IMAGEN
# ==========================================
elif opcion == "Subir Imagen":
    st.title("Subir Imagen")
    with st.form("form_imagen"):
        usuario_id = st.text_input("Usuario ID (opcional)")
        url = st.text_input("URL de la Imagen")
        latitud = st.text_input("Latitud")
        longitud = st.text_input("Longitud")
        submit = st.form_submit_button("Subir Imagen")

    if submit:
        if not url or not latitud or not longitud:
            st.error("La URL de la imagen y las coordenadas son obligatorias.")
        else:
            payload = {
                "usuario_id": usuario_id if usuario_id else None,
                "url": url,
                "coordenadas": {
                    "latitud": latitud,
                    "longitud": longitud
                }
            }
            try:
                response = requests.post(API_IMAGENES_URL, json=payload, headers=headers)
                data = response.json()
                if response.status_code == 201 and data.get("success"):
                    st.success(f"Imagen subida con éxito. ID: {data.get('id')}")
                else:
                    st.error(data.get("message", "Error al subir imagen"))
            except Exception as e:
                st.error(f"Error de conexión: {e}")
