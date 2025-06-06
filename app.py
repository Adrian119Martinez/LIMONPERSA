import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

import bleach
import jwt
from flask import Flask, request, jsonify, session
from pymongo import MongoClient

# Importar la configuración de la conexión
from config import MONGO_URI

# Inicializar la conexión a MongoDB usando el URI del archivo de configuración
client = MongoClient(MONGO_URI)
db = client['LimonPersa-Proyect']
usuarios = db['usuarios']

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Para manejo de sesiones (opcional)
JWT_SECRET_KEY = secrets.token_hex(32)   # Clave para firmar los JWT

# Decorador para proteger endpoints con JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # El token debe venir en la cabecera Authorization con el formato: "Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({'success': False, 'message': 'Token no proporcionado'}), 401

        try:
            # Decodificar y validar el token
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            # Verificar que el usuario existe en la base de datos
            current_user = usuarios.find_one({"email": data["email"]})
            if not current_user:
                raise Exception("Usuario no encontrado")
        except Exception as e:
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 401

        return f(*args, **kwargs)
    return decorated

# Endpoint de login (sin protección, ya que se utiliza para obtener el token)
@app.route('/login', methods=['POST'])
def login():
    print("ESTA LLENGANDO LA CONSULTA")
    data = request.get_json()
    if not data or 'email' not in data or 'contrasena' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    # Sanitizar las entradas del usuario
    email = bleach.clean(data['email'])
    contrasena = bleach.clean(data['contrasena'])

    # Buscar el usuario en la base de datos
    user = usuarios.find_one({'email': email})

    if user and user.get('contrasena') == contrasena:
        # Generar un token JWT con expiración de 1 hora
        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, JWT_SECRET_KEY, algorithm='HS256')
        
        # Guardar el email en la sesión (opcional)
        session['username'] = email
        
        # Retornamos también el nombre y apellidos del usuario
        return jsonify({
            'success': True,
            'token': token,
            'nombre': user.get('nombre'),
            'apellido_pat': user.get('apellido_pat'),
            'apellido_mat': user.get('apellido_mat'),
            'message': 'Inicio de sesión exitoso'
        })
    else:
        return jsonify({'success': False, 'message': 'Usuario o contraseña inválidos'}), 401
    
# Endpoint para registrar un nuevo usuario (sin protección)
@app.route('/usuarios', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    if not data or 'nombre' not in data or 'apellido_pat' not in data or 'apellido_mat' not in data or 'direccion' not in data or 'email' not in data or 'contrasena' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    if usuarios.find_one({'email': data['email']}):
        return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400

    nuevo_usuario = {
        'nombre': bleach.clean(data['nombre']),
        'apellido_pat': bleach.clean(data['apellido_pat']),
        'apellido_mat': bleach.clean(data['apellido_mat']),
        'direccion': bleach.clean(data['direccion']),
        'email': bleach.clean(data['email']),
        'contrasena': bleach.clean(data['contrasena']),
        'fecha_registro': datetime.utcnow(),
        'gestion_cuenta': {
            'tipo': 'estandar',
            'estado': 'activo',
            'fecha_ultima_modificacion': datetime.utcnow()
        }
    }
    result = usuarios.insert_one(nuevo_usuario)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint raíz (protegido)
@app.route('/', methods=['GET'])
@token_required
def home():
    return jsonify({'success': True, 'message': 'Usuario autenticado'})

# Endpoint para listar usuarios (protegido)
@app.route('/usuarios', methods=['GET'])
@token_required
def listar_usuarios():
    all_users = usuarios.find()
    users_list = [
        {
            'id': str(user['_id']),  # 👈 Agregué esta línea para incluir el ID
            'nombre': user.get('nombre'),
            'apellido_pat': user.get('apellido_pat'),
            'apellido_mat': user.get('apellido_mat'),
            'email': user.get('email')
        } for user in all_users
    ]
    return jsonify({'success': True, 'usuarios': users_list})

# Endpoint para eliminar un usuario (protegido)
@app.route('/usuarios/<string:usuario_id>', methods=['DELETE'])
@token_required
def eliminar_usuario(usuario_id):
    result = usuarios.delete_one({'_id': ObjectId(usuario_id)})
    
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'}), 200
    else:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404


# Endpoint para eliminar un usuario por correo electrónico (protegido)
@app.route('/usuarios/email/<string:email>', methods=['DELETE'])
@token_required
def eliminar_usuario_por_email(email):
    result = usuarios.delete_one({'email': email})
    
    if result.deleted_count > 0:
        return jsonify({'success': True, 'message': f'Usuario con email {email} eliminado correctamente'}), 200
    else:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
# Endpoint para editar usuario por correo electrónico (protegido)
@app.route('/usuarios/email/<string:email>', methods=['PUT'])
@token_required
def editar_usuario_por_email(email):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No se enviaron datos para actualizar'}), 400

    # Construir un diccionario con los campos a actualizar, solo si están presentes
    campos_actualizables = ['nombre', 'apellido_pat', 'apellido_mat', 'direccion', 'contrasena']
    campos_limpios = {}

    for campo in campos_actualizables:
        if campo in data:
            campos_limpios[campo] = bleach.clean(data[campo])

    if not campos_limpios:
        return jsonify({'success': False, 'message': 'No se proporcionaron campos válidos para actualizar'}), 400

    # Actualizar el campo "fecha_ultima_modificacion"
    campos_limpios['gestion_cuenta.fecha_ultima_modificacion'] = datetime.utcnow()

    result = usuarios.update_one(
        {'email': email},
        {'$set': campos_limpios}
    )

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'}), 200



# Endpoint para cerrar sesión (protegido)
@app.route('/logout', methods=['GET'])
@token_required
def logout():
    session.pop('username', None)
    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})



# Endpoint para listar tratamientos (protegido)
@app.route('/tratamientos', methods=['GET'])
@token_required
def listar_tratamientos():
    print("ESTA LLENGANDO LA CONSULTA")
    all_tratamientos = db['tratamientos'].find()
    tratamientos_list = [
        {
            'id': str(tratamiento['_id']),
            'id_enfermedad': str(tratamiento['id_enfermedad']),
            'nombre': tratamiento['nombre'],
            'descripcion': tratamiento['descripcion'],
            'instrucciones': tratamiento['instrucciones']
        } for tratamiento in all_tratamientos
    ]
    return jsonify({'success': True, 'tratamientos': tratamientos_list})

# Endpoint para agregar un nuevo tratamiento (protegido)
@app.route('/tratamientos', methods=['POST'])
@token_required
def agregar_tratamiento():
    data = request.get_json()
    if not data or 'id_enfermedad' not in data or 'nombre' not in data or 'descripcion' not in data or 'instrucciones' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nuevo_tratamiento = {
        'id_enfermedad': data['id_enfermedad'],
        'nombre': bleach.clean(data['nombre']),
        'descripcion': bleach.clean(data['descripcion']),
        'instrucciones': bleach.clean(data['instrucciones'])
    }
    result = db['tratamientos'].insert_one(nuevo_tratamiento)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint para listar categorías de enfermedades (protegido)
@app.route('/categorias_enfermedades', methods=['GET'])
@token_required
def listar_categorias_enfermedades():
    all_categorias = db['categorias_de_enfermedades'].find()
    categorias_list = [
        {
            'id': str(categoria['_id']),
            'id_enfermedad': str(categoria['id_enfermedad']),
            'nombre': categoria['nombre'],
            'descripcion': categoria['descripcion']
        } for categoria in all_categorias
    ]
    return jsonify({'success': True, 'categorias': categorias_list})

# Endpoint para agregar una nueva categoría de enfermedad (protegido)
@app.route('/categorias_enfermedades', methods=['POST'])
@token_required
def agregar_categoria_enfermedad():
    data = request.get_json()
    if not data or 'id_enfermedad' not in data or 'nombre' not in data or 'descripcion' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nueva_categoria = {
        'id_enfermedad': data['id_enfermedad'],
        'nombre': bleach.clean(data['nombre']),
        'descripcion': bleach.clean(data['descripcion'])
    }
    result = db['categorias_de_enfermedades'].insert_one(nueva_categoria)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

#Endpoint para listar enfermedades (protegido)
@app.route('/enfermedades', methods=['GET'])
@token_required
def listar_enfermedades():
    all_enfermedades = db['enfermedades'].find()
    enfermedades_list = [
        {
            'id': str(enfermedad['_id']),
            'nombre': enfermedad['nombre'],
            'descripcion': enfermedad['descripcion']
        } for enfermedad in all_enfermedades
    ]
    return jsonify({'success': True, 'enfermedades': enfermedades_list})

# Endpoint para agregar una nueva enfermedad (protegido)
@app.route('/enfermedades', methods=['POST'])
@token_required
def agregar_enfermedad():
    data = request.get_json()
    if not data or 'nombre' not in data or 'descripcion' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nueva_enfermedad = {
        'nombre': bleach.clean(data['nombre']),
        'descripcion': bleach.clean(data['descripcion'])
    }
    result = db['enfermedades'].insert_one(nueva_enfermedad)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint para listar diagnósticos (protegido)
@app.route('/diagnosticos', methods=['GET'])
@token_required
def listar_diagnosticos():
    all_diagnosticos = db['diagnosticos'].find()
    diagnosticos_list = [
        {
            'id': str(diagnostico['_id']),
            'usuario_id': str(diagnostico['usuario_id']) if diagnostico['usuario_id'] else None,
            'imagen_id': str(diagnostico['imagen_id']),
            'enfermedad_id': str(diagnostico['enfermedad_id']),
            'fecha_hora': diagnostico['fecha_hora']
        } for diagnostico in all_diagnosticos
    ]
    return jsonify({'success': True, 'diagnosticos': diagnosticos_list})

# Endpoint para crear un nuevo diagnóstico (protegido)
@app.route('/diagnosticos', methods=['POST'])
@token_required
def crear_diagnostico():
    data = request.get_json()
    if not data or 'imagen_id' not in data or 'enfermedad_id' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nuevo_diagnostico = {
        'usuario_id': data.get('usuario_id'),
        'imagen_id': data['imagen_id'],
        'enfermedad_id': data['enfermedad_id'],
        'fecha_hora': datetime.utcnow()
    }
    result = db['diagnosticos'].insert_one(nuevo_diagnostico)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint para listar imágenes (protegido)
@app.route('/imagenes', methods=['GET'])
@token_required
def listar_imagenes():
    all_imagenes = db['imagenes'].find()
    imagenes_list = [
        {
            'id': str(imagen['_id']),
            'usuario_id': str(imagen['usuario_id']) if imagen['usuario_id'] else None,
            'url': imagen['url'],
            'fecha': imagen['fecha'],
            'coordenadas': imagen['coordenadas']
        } for imagen in all_imagenes
    ]
    return jsonify({'success': True, 'imagenes': imagenes_list})

# Endpoint para subir una nueva imagen (protegido)
@app.route('/imagenes', methods=['POST'])
@token_required
def subir_imagen():
    data = request.get_json()
    if not data or 'url' not in data or 'coordenadas' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nueva_imagen = {
        'usuario_id': data.get('usuario_id'),
        'url': bleach.clean(data['url']),
        'fecha': datetime.utcnow(),
        'coordenadas': {
            'latitud': data['coordenadas']['latitud'],
            'longitud': data['coordenadas']['longitud']
        }
    }
    result = db['imagenes'].insert_one(nueva_imagen)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint para listar reseñas (protegido)
@app.route('/reseñas', methods=['GET'])
@token_required
def listar_reseñas():
    all_reseñas = db['reseñas'].find()
    reseñas_list = [
        {
            'id': str(reseña['_id']),
            'id_tratamiento': str(reseña['id_tratamiento']),
            'id_enfermedad': str(reseña['id_enfermedad']),
            'opinion': reseña['opinion'],
            'calificacion': reseña['calificacion']
        } for reseña in all_reseñas
    ]
    return jsonify({'success': True, 'reseñas': reseñas_list})

# Endpoint para agregar una nueva reseña (protegido)
@app.route('/reseñas', methods=['POST'])
@token_required
def agregar_reseña():
    data = request.get_json()
    if not data or 'id_tratamiento' not in data or 'id_enfermedad' not in data or 'opinion' not in data or 'calificacion' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nueva_reseña = {
        'id_tratamiento': data['id_tratamiento'],
        'id_enfermedad': data['id_enfermedad'],
        'opinion': bleach.clean(data['opinion']),
        'calificacion': data['calificacion']
    }
    result = db['reseñas'].insert_one(nueva_reseña)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

if __name__ == '__main__':
    app.run(debug=True)